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

def getUsersApiURL(useTest = True):
    api = getEnv(useTest)
    return(api['apiUrl']+'/users/')


def getEnv(useTest = True):
    api = {}
    if (useTest):
        apiUrl="https://lirias2.t.icts.kuleuven.be:8091/secure-api/v5.5"
        #any Elements API user with API read rights + read rights for HR data
        apiUser="kuleuvenread"
        apiPw="Wg70v$PZfXP8bnei"
        apiUser="kuleuvenapi"
        apiPw="xN02G4E4XJodA%W5"
    else:
        apiUrl="https://lirias2.kuleuven.be:8091/secure-api/v5.5"
        #any Elements API user with API read rights + read rights for HR data
        apiUser="kuleuvenread"
        apiPw="Am14$6tSCZL2aiy1"
        # elementsApiUser=kuleuvenapi
        # elementsApiPw=Lq89^qeTgBbGVR8t
    api['apiUrl'] = apiUrl
    api['apiUser'] = apiUser
    api['apiPw'] = apiPw
    return(api)

def uploadRelationShip(inId, inXml, useTest = True):
    api = getEnv(useTest)
    headers = {'Content-Type': 'application/xml'}
    payLoad = inXml
    #publications/2161118/relationships?detail=full
    resp = requests.post(api['apiUrl']+'/relationships', data=payLoad, headers=headers, auth=HTTPBasicAuth(api['apiUser'], api['apiPw']))
    #resp = requests.post(api['apiUrl']+'/publications/'+inId+'/relationships', data=payLoad, headers=headers, auth=HTTPBasicAuth(api['apiUser'], api['apiPw']))
    print('post finished '+str(resp.status_code))
    if (resp.status_code == 200 or resp.status_code == 201):
        #print(resp.content)
        return(True)
    else:
        errDesc = interpretError(resp)
        raise eu.liriasApiError(str(resp.status_code)+':'+errDesc)


def uploadDataset(inId, inXml, useTest = True):
    api = getEnv(useTest)
    headers = {'Content-Type': 'application/xml'}
    dataSource = 'c-inst-1'
    #print(api['apiUrl']+'/publication/records/'+dataSource+'/'+inId)
    #print(inXml)
    #payLoad = {'data',inXml}
    payLoad = inXml
    resp = requests.put(api['apiUrl']+'/publication/records/'+dataSource+'/'+inId, data=payLoad, headers=headers, auth=HTTPBasicAuth(api['apiUser'], api['apiPw']))
    print('put finished '+str(resp.status_code))
    if (resp.status_code == 200 or resp.status_code == 201):
        pubId = interpretPutResponse(resp)
        return(pubId)
    else:
        errDesc = interpretError(resp)
        raise eu.liriasApiError(str(resp.status_code)+':'+errDesc)
        
def interpretPutResponse(resp):
    ns = {'atom': "http://www.w3.org/2005/Atom",
          'api': "http://www.symplectic.co.uk/publications/api"}
    root = ET.fromstring(resp.content)
    #resError = root.find('./api:error', ns)
    for resError in root.findall('./atom:entry/api:warnings/api:warning',ns):
        errField = resError.attrib['associated-field']
        errTxt   = resError.text
        print('Field = '+errField+', Text = '+errTxt)
    apiObj = root.find('./atom:entry/api:object',ns)
    pubId  = apiObj.attrib['id']
    return(pubId)

def interpretError(resp):
    ns = {'atom': "http://www.w3.org/2005/Atom",
          'api': "http://www.symplectic.co.uk/publications/api"}
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
    
def deleteDataset(inId, useTest = True):
    api = getEnv(useTest)
    dataSource = 'c-inst-1'
    resp = requests.delete(api['apiUrl']+'/publication/records/'+dataSource+'/'+inId, auth=HTTPBasicAuth(api['apiUser'], api['apiPw']))
    print('delete finished '+str(resp.status_code))
    print(resp.content)

def getUserByKulId(userId, useTest = True):
    api = getEnv(useTest)
    resp = requests.get(api['apiUrl']+'/users?proprietary-id='+str(userId), auth=HTTPBasicAuth(api['apiUser'], api['apiPw']))    
    ns = {'atom': "http://www.w3.org/2005/Atom",
          'api': "http://www.symplectic.co.uk/publications/api"}
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


def getUserByKulUId(userId, useTest = True):
    api = getEnv(useTest)
    resp = requests.get(api['apiUrl']+'/users?username='+userId, auth=HTTPBasicAuth(api['apiUser'], api['apiPw']))    
    ns = {'atom': "http://www.w3.org/2005/Atom",
          'api': "http://www.symplectic.co.uk/publications/api"}
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
        