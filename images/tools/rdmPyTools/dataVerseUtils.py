# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 12:13:31 2021

@author: PieterDV
"""
import requests
import re
import logging

from pyDataverse.api import NativeApi
from pyDataverse.models import Dataverse
import json
import errorUtils as eu
import urllib.parse


# =============================================================================
# UNBLOCKED API ENDPOINTS TO GET ACCESS TO USER APIs
#   curl -k -X GET https://localhost/api/admin/settings
#   curl -k -X PUT -d "test" http://localhost/api/admin/settings/:BlockedApiEndpoints
# 
# =============================================================================

class dataVerseApi:
    def __init__(self, inBaseUrl, inApiKey, inApiToken, inSignedCertificate = False, logName = ''):
        self.logger = logging.getLogger(logName)
        self.logger.info('creating an instance of dataVerseUtils')
        self.baseUrl = inBaseUrl
        self.apiKey  = inApiKey
        self.apiToken = inApiToken
        self.signedCertificate = inSignedCertificate #False--> verify = False; True--> verify = True
        #Remark: nativeApi will not work with unsigned Certificate
        self.api     = NativeApi(self.baseUrl, self.apiKey)
        self.headers = {'X-Dataverse-key':inApiKey,'Content-Type':'application/json'}

    def get_dataverseId(self, inAlias, inUseRequests = True):
        try:
            if (inUseRequests):
                resp = requests.get(self.baseUrl+"/api/dataverses/"+urllib.parse.quote(inAlias), verify = self.signedCertificate, headers=self.headers)
            else:
                if (self.signedCertificate):
                    resp = self.api.get_request(self.baseUrl+"/api/dataverses/"+urllib.parse.quote(inAlias))
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
            dv   = resp.json()
            return(dv['data']['id'])
        except Exception as e:
            self.logger.error("get_dataverseId: %s occurred.  inAlias = %s", e.__class__.__name__, urllib.parse.quote(inAlias))
            raise eu.apiError
    
    def get_dataverseAlias(self, inId, inUseRequests = True):
        try:
            if (inUseRequests):
                resp = requests.get(self.baseUrl+"/api/dataverses/"+str(inId), verify = self.signedCertificate, headers=self.headers)
            else:
                if (self.signedCertificate):
                    resp = self.api.get_request(self.baseUrl+"/api/dataverses/"+str(inId))
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
            dv = resp.json()
            return(dv['data']['alias'])
        except Exception as e:
            self.logger.error("get_dataverseAlias: %s occurred.  inId = %s", e.__class__.__name__, str(inId))
            raise eu.apiError
    
    def get_dataverseGroups(self, inId, inGroupsToDefine, inUseRequests = True):
        grps = {}
        try: 
            if (inUseRequests):
                resp = requests.get(self.baseUrl+"/api/dataverses/"+str(inId)+"/groups", verify = self.signedCertificate, headers=self.headers)
            else:
                if (self.signedCertificate):
                    resp = self.api.get_request(self.baseUrl+"/api/dataverses/"+str(inId)+"/groups")
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
            dvGrps = resp.json()
            for g in dvGrps['data']:
                for d in inGroupsToDefine:
                    grpPattern = re.compile(d['namePrefix']+'.*'+d['nameSuffix'])
                    if (grpPattern.match(g['groupAliasInOwner'])):
                        grpIdPattern = re.compile(d['namePrefix']+"(?P<groupId>\w+)"+d['nameSuffix'])
                        m = re.match(grpIdPattern, g['groupAliasInOwner'])
                        grpId = m.group('groupId')
                        grps[d['nameSuffix']] = {
                            'groupAliasInOwner':g['groupAliasInOwner'],
                            'identifier':g['identifier'],
                            'owner':g['owner'],
                            'KULId':grpId
                            }
            return(grps)
        except Exception as e:
            self.logger.error("get_dataverseGroups: %s occurred.  inId = %s", e.__class__.__name__, str(inId))
            raise eu.apiError
    
    def get_dataverses(self, inDvDict, inId, inLevel, inAliasPrefix, inUseRequests = True):
        dvAlias = self.get_dataverseAlias(inId, inUseRequests)
        self.logger.info("level %s: alias %s",str(inLevel),dvAlias)
        aliasPattern = re.compile(inAliasPrefix)
        if (aliasPattern.match(dvAlias)):
            grpOid = re.sub(aliasPattern, '', dvAlias)
            grps = {}
            try:
                grps = self.get_dataverseGroups(inId, inUseRequests)
            except:
                raise
            inDvDict[grpOid] = {'level':inLevel,
                              'id':inId,
                              'alias':dvAlias,
                              'groups':grps}
            self.logger.info("added %s : level %s, alias %s, id %s",grpOid,str(inLevel),dvAlias,str(inId))
        try:
            if (inUseRequests):
                resp = requests.get(self.baseUrl+"/api/dataverses/"+str(inId)+"/contents", verify = self.signedCertificate, headers=self.headers)
            else:
                if (self.signedCertificate):
                    resp = self.api.get_request(self.baseUrl+"/api/dataverses/"+str(inId)+"/contents")
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
        except Exception as e:
            self.logger.error("get_dataverses: %s occurred.  inId = %s, inLevel = %s, inAliasPrefix=%s", e.__class__.__name__, str(inId), str(inLevel), inAliasPrefix)
            raise eu.apiError
            
        dvContents = resp.json()
        for c in dvContents['data']:
            if (c['type'] == 'dataverse'):
                try:
                    self.get_dataverses(inDvDict, c['id'], inLevel+1, inAliasPrefix, inUseRequests)
                except:
                    raise
    
    def buildDVDict(self, inRootAlias, inUseRequests = True):
        dvDict = {}
        try:
            rootId = self.get_dataverseId(inRootAlias, inUseRequests)
            self.get_dataverses(dvDict, rootId, 0, inUseRequests)
            return(dvDict)
        except: 
            raise
    
    def getGroupMembers(self, inGrpOwnerDVId, inGrpAlias, inUseRequests = True):
        grpMembers = {}
        try:
            if (inUseRequests):
                resp = requests.get(self.baseUrl+"/api/dataverses/"+str(inGrpOwnerDVId)+"/groups/"+inGrpAlias, verify = self.signedCertificate, headers=self.headers)
            else:
                if (self.signedCertificate):
                    resp = self.api.get_request(self.baseUrl+"/api/dataverses/"+str(inGrpOwnerDVId)+"/groups/"+inGrpAlias)
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
            x    = resp.json()
            grpMembers[inGrpAlias] = {
                'owner': inGrpOwnerDVId,
                'members': x['data']['containedRoleAssignees']}
            return(grpMembers)
        except Exception as e:
            self.logger.error("getGroupMembers: %s occured.  inGrpOwnerDVId = %s, inGrpAlias=%s", e.__class__.__name__, inGrpOwnerDVId, inGrpAlias)
            raise eu.apiError
    
    def getGroupsMembers(self, inDVDict, inUseRequests = True):
        grpMembers = {}
        try:
            for k in inDVDict:
                kGrpMembers = {}
                resGrpOwner = inDVDict[k]['groups']['res']['owner']
                resGrpAlias = inDVDict[k]['groups']['res']['groupAliasInOwner']
                kGrpMembers = self.getGroupMembers(resGrpOwner, resGrpAlias, inUseRequests = True)
                grpMembers[resGrpAlias] = kGrpMembers
            return(grpMembers)
        except:
            raise
    
    def getOrgLevel(self, inDvDict,inUO):
        try:
            return(inDvDict[inUO]['level'])
        except:
            raise
    
    def getLowestOrg(self, inDvDict, inUsrOrgs):
        lowestLevelOrg = {'level':1,'id':'99999999'}
        try:
            for uo in inUsrOrgs:
                if (uo in inDvDict.keys()):
                    level = self.getOrgLevel(inDvDict,uo)
                    if (level >= lowestLevelOrg['level']):
                        lowestLevelOrg['level'] = level
                        lowestLevelOrg['id'] = uo
            return(lowestLevelOrg)
        except:
            raise 
            
    def userExists(self, inUserId, inUseRequests = True):
        try:
            if (inUseRequests):
                r = requests.get(self.baseUrl+"/api/admin/authenticatedUsers/"+inUserId+"?unblock-key="+self.apiToken, verify = self.signedCertificate, headers=self.headers)
            else:
                if (self.signedCertificate):
                    r = self.api.get_request(self.baseUrl+"/api/admin/authenticatedUsers/"+inUserId+"?unblock-key="+self.apiToken)
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
            usr = r.json()
            if (usr['status']!='ERROR'):
                return(True)
            else:
                return(False)
        except Exception as e:
            self.logger.error("userExists: %s occured. inUserId = %s", e.__class__.__name__, inUserId)
            raise eu.apiError
    
    def delUser(self, inUsrId, inUseRequests = True):
        try:
            if (inUseRequests):
                r = requests.delete(self.baseUrl+"/api/admin/authenticatedUsers/"+inUsrId+"?unblock-key="+self.apiToken, verify = self.signedCertificate, headers=self.headers)
            else:
                if (self.signedCertificate):
                    r = self.api.delete_request(self.baseUrl+"/api/admin/authenticatedUsers/"+inUsrId+"?unblock-key="+self.apiToken)
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
            return(r)
        except Exception as e:
            self.logger.error("delUser: %s occured. inUserId = %s", e.__class__.__name__, inUsrId)
            raise eu.apiError
    
    def updUser(self, inUserData, inUseRequests = True):
        try:
            if (inUseRequests):
                resp = requests.put(self.baseUrl+'/api/admin/authenticatedUsers'+"?unblock-key="+self.apiToken, verify = self.signedCertificate, headers=self.headers, data=inUserData)            
            else:
                if (self.signedCertificate):
                    resp = self.api.put_request(self.baseUrl+"/api/admin/authenticatedUsers"+"?unblock-key="+self.apiToken,inUserData)
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
            updateUSR_resp = resp.json()
            return(updateUSR_resp)
        except Exception as e:
            self.logger.error("updUser: %s occured. inUserData = %s", e.__class__.__name__, inUserData)
            raise eu.apiError
    
    def addUser(self, inUserData, inUseRequests = True):
        try:
            if (inUseRequests):
                resp = requests.post(self.baseUrl+'/api/admin/authenticatedUsers'+"?unblock-key="+self.apiToken, verify = self.signedCertificate, headers=self.headers, data=inUserData)
            else:
                if (self.signedCertificate):
                    resp = self.api.post_request(self.baseUrl+"/api/admin/authenticatedUsers"+"?unblock-key="+self.apiToken,inUserData)
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
            createUSR_resp = resp.content
            return(createUSR_resp)
        except Exception as e:
            self.logger.error("addUser: %s occured. inUserData = %s", e.__class__.__name__, inUserData)
            raise eu.apiError
        
    def delUsrFromGroup(self, inGrpDV, inGrpAlias, inUserAtId, inUseRequests = True):
        try:
            if (inUseRequests):
                resp = requests.delete(self.baseUrl+"/api/dataverses/"+str(inGrpDV)+"/groups/"+inGrpAlias+"/roleAssignees/"+inUserAtId, verify = self.signedCertificate, headers=self.headers)
            else:
                if (self.signedCertificate):
                    resp = self.api.delete_request(self.baseUrl+"/api/dataverses/"+str(inGrpDV)+"/groups/"+inGrpAlias+"/roleAssignees/"+inUserAtId)
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
            DELGrpMemberResp = resp.json()
            return(DELGrpMemberResp)
        except Exception as e:
            self.logger.error("delUsrFromGroup: %s occured. inGrpDV, inGrpAlias, inUserAtId = %s", e.__class__.__name__, inGrpDV, inGrpAlias, inUserAtId)
            raise eu.apiError
        
    
    def addUserToGroup(self, inGrpDV, inGrpAlias, inUserAtId, inUseRequests = True):
        #add a user to a group
        #PUT http://$server/api/dataverses/$dv/groups/$groupAlias/roleAssignees/$roleAssigneeIdentifier
        try:
            if (inUseRequests):
                resp = requests.put(self.baseUrl+"/api/dataverses/"+str(inGrpDV)+"/groups/"+inGrpAlias+"/roleAssignees/"+inUserAtId, verify = self.signedCertificate, headers=self.headers)
            else:
                if (self.signedCertificate):
                    resp = self.api.put_request(self.baseUrl+"/api/dataverses/"+str(inGrpDV)+"/groups/"+inGrpAlias+"/roleAssignees/"+inUserAtId)
                else:
                    raise(eu.unsignedCertificateError('dataVerseApi - nativeApi will not work with unsigned certificates'))
            putGRP_resp = resp.json()
            return(putGRP_resp)
        except Exception as e:
            self.logger.error("addUsrToGroup: %s occured. inGrpDV, inGrpAlias, inUserAtId = %s", e.__class__.__name__, inGrpDV, inGrpAlias, inUserAtId)
            raise eu.apiError