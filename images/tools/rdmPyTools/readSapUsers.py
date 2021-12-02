# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 14:43:28 2021

@author: PieterDV
"""
import os
import sys
import pandas as pd
import numpy as np
import re
import requests
import configparser
import logging
import math

import dataVerseUtils

from pyDataverse.api import NativeApi
from pyDataverse.models import Dataverse
import json

import generalUtils as gu

def printTuple(inTuple, colDict, errCnt, sep = ','):
    outstring = ''
    if (errCnt ==1):
        for colKey in colDict:
                outstring = outstring + colKey + sep
        outstring = outstring + os.linesep
    for colKey in colDict:
            if (pd.isnull(inTuple[colDict[colKey]])):
                outstring = outstring + "NULL" + sep            
            else:
                outstring = outstring + str(inTuple[colDict[colKey]]) + sep
    return(outstring)

def readSapFile(inInputFile, inConfigFile, logName = ''):
    try:    
        #get loghandler
        logH        = logging.getLogger(logName)
        #read options from configurationfile
        logH.debug('readSapUsers: Read Configuration File %s', inConfigFile)
        opts        = gu.readConfigFile(inConfigFile)
        #dataVerse settings
        baseUrl     = opts.get('DataVerse','baseUrl')
        apiKey      = opts.get('DataVerse','apiKey', fallback = None)
        apiKeyFile  = opts.get('DataVerse','apiKeyFile')
        if (apiKey is None):
            try:
                apiKey = gu.readFile2String(apiKeyFile)
                logH.info("readSapUsers: apiKeyFile=%s revealed apiKey", apiKeyFile)
            except Exception as e:
                logH.error("readSapUsers: %s occured. apiKeyFile=%s",e.__class__.__name__,apiKeyFile)
                raise 
        apiToken    = opts.get('DataVerse','apiToken')
        signedCertificate = opts.getboolean('DataVerse', 'signedCertificate', fallback = False)
        if (signedCertificate):
            logH.info('readSapUsers: will be expecting signed certificate for DataVerse API')
        else:   
            logH.info('readSapUsers: allowing UNsigned certificate for DataVerse API')
        rootDVAlias = opts.get('DataVerse','rootDV')
        singleDVSetup = opts.getboolean('DataVerse','singleDVSetup', fallback = True)
        singleDV    = opts.get('DataVerse','singleDV')
        singleGroupSetup = opts.getboolean('DataVerse','singleGroupSetup', fallback = True)
        singleGroup = opts.get('DataVerse','singleGroup')
        if (not singleGroupSetup):
            groupsToDefineStr = opts.get('DataVerse','groupsToDefine')
            groupsToDefine = json.loads(groupsToDefineStr)
        else:
            groupsToDefine = {}
        #SHIB
        shibProviderId = opts.get('Shib','shibProviderId')
        userScope   = opts.get('Shib','userScope')
        userSep     = opts.get('Shib','userSep')
        #USERFILE
        fileSep     = opts.get('InputFile','fileSep')
        #USERDATA
        ORCIDRequired = opts.getboolean('UserData','ORCIDRequired', fallback = True)
        #runSettings
        useRequests = opts.getboolean('runSettings','useRequests')   
        selectedUsersStr = opts.get('runSettings','selectedUsers', fallback="")
        if (selectedUsersStr != ""):
            selectedUsers = selectedUsersStr.split(',')
        else:
            selectedUsers = []
        create = opts.getboolean('runSettings','create', fallback = True)
        delete = not create
        testLimit = opts.getboolean('runSettings','testLimit', fallback = False)
        testNbr   = opts.getint('runSettings','testNbr', fallback = 99999)
        
        #dataVerseUtils object
        dvu = dataVerseUtils.dataVerseApi(baseUrl,apiKey,apiToken,signedCertificate,logName)
        
        #Get the defined Organisational structure from the existing dataverses
        if (delete):
            doBuildDVDict     = False
            doGetGroupMembers = False
        else:
            doBuildDVDict     = True
            doGetGroupMembers = True
        if (not singleGroupSetup):
            if (doBuildDVDict):
                logH.debug("Building DataVerse Dictionary Object")
                dvDict = dvu.buildDVDict(rootDVAlias)
                logH.debug("End of Dataverse Dictionary Build")
            if (doGetGroupMembers):
                logH.debug("Get Group Members")
                groupMembers = dvu.getGroupsMembers(dvDict)
                logH.debug("End of Get Group Members")
        else:
            singleDVId   = dvu.get_dataverseId(singleDV)
            groupMembers = dvu.getGroupMembers(singleDVId, singleGroup)
    
        # read inputfile as string and raise any error
        try:
            sapUsers = pd.read_table(inInputFile, sep=fileSep, dtype = str)
            logH.debug(sapUsers.columns)
            logH.debug(sapUsers.dtypes.tolist())
            logH.debug(sapUsers.columns.tolist())
            #missing values
            missing_value_mask = (sapUsers == -999.000)
            missing_value_mask.value_counts()
            sapUsers[missing_value_mask] = None
            
            #remove the [] around the column names
            sapUsers.rename(columns=lambda x: re.sub('[\[\]]','',x),inplace=True)
            logH.debug(sapUsers.columns.tolist())
            #rename Generic Columns
            nbrGeneric = 51
            idxGenerics = {}
            for g in range(1,nbrGeneric,1):
                colName = 'Generic%02d' % (g)
                idxGenerics[colName] = sapUsers.columns.get_loc(colName) + 1
        except Exception as e:
            logH.error("readSapUsers: %s occured. inInputFile=%s",e.__class__.__name__,inInputFile)
            raise

        try:
            colNames = sapUsers.columns
            colDict  = {}
            for cN in colNames:
                colDict[cN] = sapUsers.columns.get_loc(cN)
        except Exception as e:
            logH.error("readSapUsers: %s occured at colDict.",e.__class__.__name__)
            raise
            
        errCnt = 0

        orgPattern = re.compile('5[0-9][0-9][0-9][0-9][0-9][0-9][0-9]')
        if (create):
            #iterate over rows
            cnt = 1
            for row in sapUsers.itertuples():
                logH.debug("Username = %s, Prim.Group = %s, Position = %s, dept = %s, orcid = %s", row.Username, row.PrimaryGroupDescriptor, str(row.Position), str(row.Department), str(row.Generic15))
                try:
                    if (len(selectedUsers) > 0 and not(row.Username.lower() in selectedUsers)):
                        logH.debug("User %s not in selected Users List", row.Username.lower())
                    else:
                        if (ORCIDRequired and (str(row.Generic15) == '' or str(row.Generic15) == 'nan')):
                            logH.debug('ORCID is required but missing for User %s', row.Username)
                        else:
                            if (not singleGroupSetup):
                                usrOrgs = []
                                for g in range(1,nbrGeneric):
                                    colName = 'Generic%02d' % (g)
                                    #logH.debug(colName+':'+str(row[idxGenerics[colName]]))
                                    if (not row[idxGenerics[colName]] is None):
                                        if (re.match(orgPattern,str(row[idxGenerics[colName]]))):
                                            logH.debug("%s : %s",colName,str(row[idxGenerics[colName]]))
                                            usrOrgs.append(str(row[idxGenerics[colName]]))
                                usrOrg = {}
                                usrOrg = dvu.getLowestOrg(dvDict, usrOrgs)
                                logH.debug('User Attached to %s, level %s', str(usrOrg['id']), str(usrOrg['level']))
                                
                            affiliation = 'default'
                            if (not pd.isnull(row.Department)):
                                affiliation = row.Department
                            else:
                                if (not pd.isnull(row.PrimaryGroupDescriptor)):
                                    affiliation = row.PrimaryGroupDescriptor
                            logH.debug('User %s - affiliation will be: %s', row.Username.lower(), str(affiliation))
                    
                            #Create User Dictionary
                            usrId = row.Username.lower()
                            usrAtId = '@'+usrId
                            usrD = {}
                            usrD['identifier'] = usrAtId
                            usrD['firstName']  = row.Firstname
                            usrD['lastName']   = row.Lastname
                            usrD['displayName'] = row.Firstname+' '+row.Lastname
                            usrD['email']       = row.Email
                            usrD['superuser']   = 'False'
                            usrD['affiliation'] = affiliation
                            usrD['persistentUserId'] = shibProviderId+userSep+usrId+userScope
                            usrD['authenticationProviderId'] = 'shib'
                    
                            if (dvu.userExists(usrId)):
                                #Update User
                                logH.debug("User %s already exists",usrId)
                                json_usrData = json.dumps(usrD)
                                #http://$SERVER/api/admin/authenticatedUsers
                                #DOES NOT SUPPORT UPDATE YET???
                                APIUsrUpdate = False
                                if (APIUsrUpdate):
                                    updateUSR_resp = dvu.updUser(json_usrData)
                                    logH.debug(updateUSR_resp)
                                #Add user to right group(s)
                                alreadyInGrp = False
                                #Group the user should be linked to:
                                if (not singleGroupSetup):
                                    grpDV = str(dvDict[usrOrg['id']]['id'])
                                    grpAl = dvDict[usrOrg['id']]['groups']['res']['groupAliasInOwner']
                                else:
                                    grpDV = singleDVId
                                    grpAl = singleGroup
                                logH.debug("User %s should be member of group %s in dataVerse %s", usrId, grpAl, str(grpDV))
                                for g in groupMembers:
                                    if usrAtId in groupMembers[g]['members']:
                                        existGrpDV = str(groupMembers[g]['owner'])
                                        existGrpAl = g
                                        if (grpAl != existGrpAl or str(grpDV) != str(existGrpDV)):
                                            logH.debug("User %s found in wrong group %s ... deleting membership", usrId, g)
                                            #DELETE http://$server/api/dataverses/$dv/groups/$groupAlias/roleAssignees/$roleAssigneeIdentifier
                                            #resp = api.get_request(baseUrl+"/api/dataverses/239/groups/KULGRP_99999999res")
                                            DELGrpMemberResp = dvu.delUsrFromGroup(existGrpDV, existGrpAl, usrAtId, useRequests)
                                            logH.debug(DELGrpMemberResp)
                                        else: 
                                            logH.debug("User %s already member of group %s in dataVerse %s - no action needed", usrId, grpAl, grpDV)                            
                                            alreadyInGrp = True
                                if (not alreadyInGrp):
                                    logH.debug("Add user %s to group %s in dataVerse %s", usrId, grpAl, str(grpDV))
                                    putGRP_resp = dvu.addUserToGroup(grpDV, grpAl, usrAtId)
                                    logH.debug(putGRP_resp)
                            else:
                                #Add user
                                logH.debug("User %s is new and will be created", usrId)
                                logH.debug("Affiliation %s", usrD['affiliation'])
                                json_usrData = json.dumps(usrD)
                                #http://$SERVER/api/admin/authenticatedUsers
                                createUSR_resp = dvu.addUser(json_usrData)
                                logH.debug(createUSR_resp)
                                if (not singleGroupSetup):
                                    grpDV = dvDict[usrOrg['id']]['alias']
                                    grpAl = dvDict[usrOrg['id']]['groups']['res']['groupAliasInOwner']
                                else:
                                    grpDV = singleDVId
                                    grpAl = singleGroup
                                logH.debug("Add user %s to group %s in dataVerse %s", row.Username.lower(), grpAl, str(grpDV))
                                putGRP_resp = dvu.addUserToGroup(grpDV, grpAl, usrAtId)
                                logH.debug(putGRP_resp)
                            #count as processed user
                            cnt = cnt + 1
                except Exception as e:
                    errCnt = errCnt + 1
                    if (pd.isnull(row.Username)):
                        logH.debug("User %s could not be processed correctly.  Error: %s", str(row.Proprietary_ID), e.__class__.__name__)                        
                    else:
                        logH.debug("User %s could not be processed correctly.  Error: %s", row.Username, e.__class__.__name__)
                    logH.error(printTuple(row, colDict, errCnt, fileSep))
                    
                    #count as processed user nevertheless
                    cnt = cnt + 1
                    #error caught - procede with other users
                if (cnt == testNbr and testLimit):
                    break
        
        if (delete):   
            cnt = 1
            #DELETE DOES NOT REQUIRE TO REMOVE GROUP MEMBERSHIPS FIRST
            for row in sapUsers.itertuples():
                try:
                    usrId = row.Username.lower()
                    logH.debug("Username = %s",usrId)
                    if (len(selectedUsers) > 0 and not(row.Username.lower() in selectedUsers)):
                        logH.debug("User %s not in selected Users List", row.Username.lower())
                    else:
                        logH.debug(row.Username, row.PrimaryGroupDescriptor, row.Position, row.Department)
                        if (dvu.userExists(usrId)):
                            logH.debug("Deleting... user %s", usrId)
                            r = dvu.delUser(usrId)
                            logH.debug(r.content)
                            cnt = cnt + 1
                except Exception as e:
                    logH.error("User %s could not be properly deleted", row.Username)
                    logH.error("ERROR RECORD %s", row)
                if (cnt == testNbr and testLimit):
                    break

    except Exception as e:
        logH.error("Error %s occured - unexpected Exception", e.__class__.__name__)
        raise
        
        # identifier:@u0001290
        # displayName:Pieter De Veuster
        # firstName:Pieter
        # lastName:De Veuster
        # email:pieter.deveuster@kuleuven.be
        # superuser:False
        # affiliation:default/"Dataverse.org"
        # persistentUserId:urn:mace:kuleuven.be:kulassoc:kuleuven.be|u0001290@kuleuven.be
        # authenticationProviderId:shib
        
