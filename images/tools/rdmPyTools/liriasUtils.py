# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 13:47:13 2021

@author: PieterDV
"""
import sys
from pyDataverse.api import NativeApi, Api
import json
import re 
import requests
import dataVerseUtils as dvu
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import errorUtils as eu
import logging
import urllib.parse
import generalUtils as gu

class liriasApi:
    def __init__(self, inBaseUrl, inApiUser, inApiPw, logName=''):
        self.logger = logging.getLogger(logName)
        self.logger.info('Creating an instance of liriasApi')
        self.baseUrl = inBaseUrl
        self.apiUser = inApiUser
        self.apiPw   = inApiPw
        self.headers = {'Content-Type': 'application/xml'}
        self.auth    = HTTPBasicAuth(self.apiUser, self.apiPw)
        self.ns      = {'atom': "http://www.w3.org/2005/Atom",
                        'api': "http://www.symplectic.co.uk/publications/api"}


    def getUsersApiURL(self):
        return(self.baseUrl+'/users/')

    def uploadRelationShip(self, inId, inXml):
        payLoad = inXml
        try:
            resp = requests.post(self.baseUrl+'/relationships', data=payLoad, headers=self.headers, auth=self.auth)
            self.logger.info('uploadRelationShip: post StatusCode = '+str(resp.status_code))
            if (resp.status_code == 200 or resp.status_code == 201):
                return(True)
            else:
                errDesc = self.interpretError(resp)
                self.logger.error(errDesc)
                raise eu.liriasApiError(str(resp.status_code)+':'+errDesc)
        except Exception as e:
            self.logger.error("uploadRelationShip: %s occured, inId = %s", e.__class__.__name__, inId)
            self.logger.error("uploadRelationShip: XML = %s", inXml)
            raise eu.liriasApiError()

    def uploadDataset(self, inDataSource, inId, inXml):
        payLoad = inXml
        try:        
            inIdQuoted = urllib.parse.quote_plus(inId)
            resp = requests.put(self.baseUrl+'/publication/records/'+inDataSource+'/'+inIdQuoted, data=payLoad, headers=self.headers, auth=self.auth)
            self.logger.info('uploadDataSet: put StatusCode '+str(resp.status_code))
            if (resp.status_code == 200 or resp.status_code == 201):
                pubId = self.interpretPutResponse(resp)
                return(pubId)
            else:
                errDesc = self.interpretError(resp)
                self.logger.error(errDesc)
                raise eu.liriasApiError(str(resp.status_code)+':'+errDesc)
        except Exception as e:
            self.logger.error("uploadDataSet: %s occured, inDataSource = %s, inId = %s", e.__class__.__name__, inDataSource, inId)
            self.logger.error("uploadDataSet: XML = %s", inXml)
            raise eu.liriasApiError()
        
    def interpretPutResponse(self, resp):
        ns = self.ns
        root = ET.fromstring(resp.content)
        #resError = root.find('./api:error', ns)
        for resError in root.findall('./atom:entry/api:warnings/api:warning',ns):
            errField = resError.attrib['associated-field']
            errTxt   = resError.text
            print('Field = '+errField+', Text = '+errTxt)
        apiObj = root.find('./atom:entry/api:object',ns)
        pubId  = apiObj.attrib['id']
        return(pubId)

    def interpretError(self, resp):
        ns = self.ns
        root = ET.fromstring(resp.content)    
        errDesc = ""
        #resError = root.find('./api:error', ns)
        for resError in root.findall('./atom:entry/api:error',ns):
            errCode = resError.attrib['code']
            errTxt  = resError.text
            if (errDesc != ''): 
                errDesc = errDesc + '\n'
            errDesc = errDesc+errTxt
            print('Code = '+errCode+', Text = '+errTxt)
        return(errDesc)
    
    def deleteDataset(self, inDataSource, inId):
        try:
            inIdQuoted = urllib.parse.quote_plus(inId)
            resp = requests.delete(self.baseUrl+'/publication/records/'+inDataSource+'/'+inIdQuoted, auth=self.auth)
            self.logger.info('delete '+inId+' finished '+str(resp.status_code))
            self.logger.info(self.baseUrl+'/publication/records/'+inDataSource+'/'+inIdQuoted)
        except Exception as e:
            self.logger.error("deleteDataSet: %s occured, inDataSource = %s, inId = %s",e.__class__.__name__, inDataSource, inId)
            raise eu.liriasApiError()

    def deleteRelationShips(self, inId):
        try:
            inIdQuoted = urllib.parse.quote_plus(inId)
            self.logger.info('deleteRelationShips: '+self.baseUrl+'/publications/'+inIdQuoted+'/relationships')
            resp = requests.get(self.baseUrl+'/publications/'+inIdQuoted+'/relationships', auth = self.auth)
            self.logger.info('deleteRelationShips: '+str(resp.content)[0:80])
            feed = ET.fromstring(resp.content)
            entries = feed.findall('./atom:entry', self.ns)
            for entry in entries:
                entId   = entry.find('./api:relationship', self.ns).attrib['id']
                entType = entry.find('./api:relationship', self.ns).attrib['type']
                self.logger.info('deleteRelationShips: Found id : '+entId)
                self.logger.info('deleteRelationShips: Found type : '+entType)
                if (entType in ['publication-user-authorship','publication-publication-supplement'] and 
                    entId != ''):
                    self.logger.info("deleteRelationships: relation id="+str(entId)+", type="+str(entType)+" to be deleted")
                    self.deleteRelationShip(entId)
        except Exception as e:
            self.logger.error("deleteRelationShips: %s occured, inId = %s",e.__class__.__name__,inId)
            raise eu.liriasApiError()
            
    def deleteRelationShip(self, inRelId):
        try:
            self.logger.info(self.baseUrl+'/relationships/'+str(inRelId))
            respR = requests.delete(self.baseUrl+'/relationships/'+inRelId, auth = self.auth)
            self.logger.info('deleteRelationShip '+inRelId+' deleted')
        except Exception as e:
            self.logger.error('deleteRelationShip: %s occured, inRelId = %s',e.__class__.__name__,inRelId)
            raise eu.liriasApiError()
            
    def getPublicationElementsId(self, inId, searchSourcesDict):
        #search for the inId in all elements sources defined in the searchSourcesDict dictionary
        Found       = False
        inIdQuoted  = urllib.parse.quote_plus(inId)
        #self.logger.error('getPublicationElementsID - '+inIdQuoted)
        for src in searchSourcesDict.values():
            #https://lirias2.t.icts.kuleuven.be:8091/secure-api/v5.5/publication/records/c-inst-1/RDR.CVHLQ2
            self.logger.error('getPublicationElementsID - Trying '+src+' : '+self.baseUrl+'/publication/records/'+src+'/'+inIdQuoted)
            resp = requests.get(self.baseUrl+'/publication/records/'+src+'/'+inIdQuoted, auth = self.auth)    
            root = ET.fromstring(resp.content)
            try:
                usrObj = root.find("./atom:entry/api:object[@category='publication']", self.ns).attrib['id']
                self.logger.info('getPublicationElementsId - Source '+src+' pubId = '+str(usrObj))
                return(str(usrObj))
                break
            except Exception as e:
                self.logger.info('getPublicationElementsId - Source '+src+' error '+self.interpretError(resp))
                #continuing with for loop
        if (not Found):
            self.logger.error('getPublicationElementsId - Error - could not find Elements id for '+inId)
            raise eu.liriasApiError()

    def getDataSetIdByDoi(self, inDataSource, inId):
        try:
            #https://lirias2.t.icts.kuleuven.be:8091/secure-api/v5.5/publication/records/c-inst-1/RDR.CVHLQ2
            inIdQuoted = urllib.parse.quote_plus(inId)
            resp = requests.get(self.baseUrl+'/publication/records/'+inDataSource+'/'+inIdQuoted, auth = self.auth)    
            ns = self.ns
            feed = ET.fromstring(resp.content)
            #☻usrObj = feed.find("./atom:entry/api:object[@category='publication' and @type='dataset']", ns).attrib['id']
            usrObj = feed.find("./atom:entry/api:object[@category='publication']", ns).attrib['id']
            self.logger.info('getDataSetByDoi('+inDataSource+','+inId+')')
            self.logger.info(self.baseUrl+'/publication/records/'+inDataSource+'/'+inIdQuoted)
            if (usrObj != ''):
                return(str(usrObj))
            else:
                raise eu.liriasApiError('Could not find DataSet '+inDataSource+' '+inId)
        except Exception as e:
            self.logger.error("getDataSetByDoi: %s occured, %s, %s",e.__class__.__name__,inDataSource,inId)
            raise eu.liriasApiError()
    
    def getUserByKulId(self, userId):
        try:
            resp = requests.get(self.baseUrl+'/users?proprietary-id='+str(userId), auth=self.auth)    
            ns = self.ns
            feed = ET.fromstring(resp.content)
            resObj = feed.find('./api:pagination', ns)
            resNbr = resObj.attrib['results-count']
            if (resNbr == "1"):
                usrObj = feed.find("./atom:entry/api:object[@category='user']", ns).attrib['id']
                if (usrObj != ''):
                    return(str(usrObj))
                else:
                    raise eu.liriasApiError('Found user '+str(userId)+' but not the Elements id')
            else:
                raise eu.liriasApiError('Could not find user '+str(userId))
        except Exception as e:
            self.logger.error("getUserByKulId: %s occured, userId = %s", e.__class__.__name__, userId)
            raise eu.liriasApiError()
    
    def getUserByKulUId(self, userId):
        try:
            resp = requests.get(self.baseUrl+'/users?username='+userId, auth=self.auth)    
            ns = self.ns
            feed = ET.fromstring(resp.content)
            resObj = feed.find('./api:pagination', ns)
            resNbr = resObj.attrib['results-count']
            if (resNbr == "1"):
                usrObj = feed.find("./atom:entry/api:object[@category='user']", ns).attrib['id']
                if (usrObj != ''):
                    return(str(usrObj))
                else:
                    raise eu.liriasApiError('Found user '+str(userId)+' but not the Elements id')
            else:
                raise eu.liriasApiError('Could not find user '+str(userId))
        except Exception as e:
            self.logger.error("getUserByKulUId: %s occured, userId = %s", e.__class__.__name__, userId)
            raise eu.liriasApiError()
    
    def getUserNameByKULUid(self, userId):
        try:
            resp = requests.get(self.baseUrl+'/users?username='+userId, auth=self.auth)    
            ns = self.ns
            feed = ET.fromstring(resp.content)
            resObj = feed.find('./api:pagination', ns)
            resNbr = resObj.attrib['results-count']
            if (resNbr == "1"):
                usrName = feed.find("./atom:entry/atom:title", ns).text
                if (usrName != ''):
                    nameDict = gu.splitName(usrName, self.logger)
                    return(nameDict)
                else:
                    raise eu.liriasApiError('Found user '+str(userId)+' but not the name')
            else:
                raise eu.liriasApiError('Could not find user '+str(userId))
        except Exception as e:
            self.logger.error("getUserNameByKulUId: %s occured, userId = %s", e.__class__.__name__, userId)
            raise eu.liriasApiError()

def liriasAccessRights(inAR):
    allowedAR = ["open", "restricted", "embargoed", "closed"]
    if (inAR.lower() in allowedAR):
        return(inAR.lower())
    else:
        raise eu.liriasError('Wrong Access Rights Entry '+inAR.lower())
        
def liriasLegitimateOptout(inLO):
    allowedLegitimateOptout = ["privacy", "intellectual property rights", "ethical aspects", "aspects of dual use", "other"]
    if (inLO.lower() in allowedLegitimateOptout):
        return(inLO.lower())
    else:
        raise eu.LiriasError('Wrong Legitimate Optout Entry '+inLO.lower())
            