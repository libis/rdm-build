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
import urllib.parse
import shutil

useTest = True
if (useTest):
    apiUrl="https://lirias2.t.icts.kuleuven.be:8091/secure-api/v5.5"
    #any Elements API user with API read rights + read rights for HR data
    apiUser="kuleuvenread"
    apiPw="Wg70v$PZfXP8bnei"
    #vb = "2161118"
    #vb = "2139219"
    vb = "2164179"
else:
    apiUrl="https://lirias2.kuleuven.be:8091/secure-api/v5.5"
    #any Elements API user with API read rights + read rights for HR data
    apiUser="kuleuvenread"
    apiPw="Am14$6tSCZL2aiy1"
    vb = "3060312"



optie = 1

if optie == 1:
    #get datafields for dataset template
    resp = requests.get(apiUrl+"/publication/types",auth = HTTPBasicAuth(apiUser,apiPw))
    #print(resp)
    #print(resp.content)
    
    ns = {'atom': "http://www.w3.org/2005/Atom",
          'api': "http://www.symplectic.co.uk/publications/api"}

    fileName = 'c:/temp/rdm/out/datasetFields.xml'             
    f = open(fileName, 'w', encoding='utf-8')
    f.write('<?xml version="1.0" encoding="UTF-8"?>')
    
    root = ET.fromstring(resp.content)
    print(root.tag)
    for e in root.findall("./atom:entry", ns):
        t = e.find("./atom:title", ns)
        if (t.text == 'Dataset'):
            #ET.dump(e)
            f.write(ET.tostring(e).decode("utf-8"))
            
    f.close()            

if optie == 2:        
    resp = requests.get(apiUrl+"/publications?query=type='Dataset'",auth = HTTPBasicAuth(apiUser,apiPw))
    print(resp.content)

if optie == 5    :
    fromF = 'c:/temp/rdm/in/test.txt'
    toD   = 'c:/temp/rdm/out/'
    shutil.move(fromF,toD)

if optie == 3:        
    resp = requests.get(apiUrl+"/publications/"+vb,auth = HTTPBasicAuth(apiUser,apiPw))
    print(resp.content)

if optie == 4:    
    userId = 89908 #◘89908
    #https://lirias2.t.icts.kuleuven.be:8091/secure-api/v5.5/users?proprietary-id=89908
    #https://lirias2.t.icts.kuleuven.be:8091/secure-api/v5.5/users?username=U0001290
    # print(apiUrl+'/users?proprietary-id='+str(userId))
    # print(apiUser+' '+apiPw)
    resp = requests.get(apiUrl+'/users?proprietary-id='+str(userId), auth = HTTPBasicAuth(apiUser,apiPw))    
    #☺print(resp.content)
    ns = {'atom': "http://www.w3.org/2005/Atom",
          'api': "http://www.symplectic.co.uk/publications/api"}
    
# 		<api:object category="user" id="24565" proprietary-id="89908" authenticating-authority="KUL" username="U0089908" last-affected-when="2021-06-17T14:10:35.97+02:00" last-modified-when="2021-05-08T05:31:51.963+02:00" href="https://lirias2.t.icts.kuleuven.be:8091/secure-api/v5.5/users/24565" created-when="2017-09-06T16:57:02.73+02:00" type-id="1" type="person">
# 			<api:relationships href="https://lirias2.t.icts.kuleuven.be:8091/secure-api/v5.5/users/24565/relationships"/>
# 		</api:object>

    root = ET.fromstring(resp.content)
    resObj = root.find('./api:pagination', ns)
    resNbr = resObj.attrib['results-count']
    if (resNbr == "1"):
        usrObj = root.find("./atom:entry/api:object[@category='user']", ns).attrib['id']
    else:
        usrObj = -1
    print('userId = '+str(usrObj))
    #print(resp.content)
        


sys.exit()

#delete published dataset
#resp = requests.delete(baseUrl+"/api/datasets/:persistentId/destroy/?persistentId=doi:10.80442/FK2/VW95KI", headers=headers)
#x = resp.json()
#print(x)

#sys.exit()

# resp = api.get_request(baseUrl+"/api/dataverses/239/groups/KULGRP_99999999res")
# x = resp.json()
# print(x)
# print('--')

# resp = api.get_request(baseUrl+"/api/admin/authenticatedUsers/u0001290")
# x = resp.json()
# print(x)
# print('--')

#r = requests.get(baseUrl+"/api/admin/authenticatedUsers/u0001290", headers=headers)
#r = requests.get(baseUrl+"/api/admin/assignments/assignees/&explicit/239-KULGRP_99999999res", headers=headers)
#r = requests.get(baseUrl+"/api/admin/assignee/@u0001290", headers=headers)
#r = requests.get(baseUrl+"/api/roles/9", headers=headers)
#r = requests.get(baseUrl+"/api/dataverses/239/groups",headers=headers)
# print(r.content)
# usr = r.json()
# print(usr)
# if (usr['status']!='ERROR'):
#     ud = usr['data']
#     for k in ud:
#             print(str(k)+":"+str(ud[k]))
# else:
#     print(usr['message'])

# sys.exit()

# r = requests.delete(baseUrl+"/api/admin/authenticatedUsers/U0001290", headers=headers)
# print(r.content)

# sys.exit()

aliasPrefix = "KULOID_"
groupPrefix = "KULGRP_"
researchGrpSuffix = 'res'
reviewGrpSuffix = 'rev'
groupsToDefine = [
    {'namePrefix': groupPrefix,
     'nameAppendix': ' Researchers Group',
     'nameSuffix':   researchGrpSuffix,
     'role': 'contributor'},
    {'namePrefix': groupPrefix,
     'nameAppendix': ' Reviewers Group',
     'nameSuffix':   reviewGrpSuffix,
     'role': 'curator'}]

def get_dataverseId(inAlias):
    resp = api.get_request(baseUrl+"/api/dataverses/"+inAlias)
    dv = resp.json()
    return(dv['data']['id'])

def get_dataverseAlias(inId):
    resp = api.get_request(baseUrl+"/api/dataverses/"+str(inId))
    dv = resp.json()
    #print(dv['data']['alias'])
    return(dv['data']['alias'])

def get_dataverseGroups(inId):
    grps = {}
    #GET http://$server/api/dataverses/$id/groups        
    resp = api.get_request(baseUrl+"/api/dataverses/"+str(inId)+"/groups")
    dvGrps = resp.json()
    print(dvGrps)
    for g in dvGrps['data']:
        for d in groupsToDefine:
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

def get_dataverses(dvDict, inId, level):
    dvAlias = get_dataverseAlias(inId)
    print(str(level)+":"+dvAlias)
    aliasPattern = re.compile(aliasPrefix)
    if (aliasPattern.match(dvAlias)):
        grpOid = re.sub(aliasPattern, '', dvAlias)
        grps = {}
        grps = get_dataverseGroups(inId)
        dvDict[grpOid] = {'level':level,
                          'id':inId,
                          'alias':dvAlias,
                          'groups':grps}
        print("added "+grpOid+": level="+str(level)+",alias="+dvAlias+", id="+str(inId))
    resp = api.get_request(baseUrl+"/api/dataverses/"+str(inId)+"/contents")
    dvContents = resp.json()
    #print(dvContents)
    for c in dvContents['data']:
        if (c['type'] == 'dataverse'):
            get_dataverses(dvDict, c['id'], level+1)

def buildDVDict(inRootAlias):
    dvDict = {}
    rootId = get_dataverseId(inRootAlias)
    get_dataverses(dvDict,rootId,0)
    return(dvDict)

doBuildDVDict = True
if (doBuildDVDict):
    rootDVAlias = 'root'
    print("Building DataVerse Dictionary Object")
    dvDict = buildDVDict(rootDVAlias)
    print("End of Dataverse Dictionary Build")
    
for dv in dvDict:
    print("publish "+dvDict[dv]['alias']+" ["+str(dvDict[dv]['id'])+"]")
    #POST /api/dataverses/$ID/actions/:publish
    resp = api.post_request(baseUrl+"/api/dataverses/"+str(dvDict[dv]['alias'])+"/actions/:publish")
    pubResp = resp.json()
    print(pubResp)
    
sys.exit()

#GET http://$SERVER/api/admin/authenticatedUsers/$identifier
#/api/admin/settings
resp = api.get_request(baseUrl+"/api/admin/settings")
x = resp.json()
print(x)
#DELETE http://$SERVER/api/admin/authenticatedUsers/$identifier
# resp = api.delete_request(baseUrl+"/api/admin/authenticatedUsers/u0001290")
# x = resp.json()
# print(x)
resp = api.get_request(baseUrl+"/api/admin/authenticatedUsers/u0001290")
x = resp.json()
print(x)
print('authenticationProviderId='+x['data']['authenticationProviderId'])
print('identifier='+x['data']['identifier'])
print('firstName='+x['data']['firstName'])
print('lastName='+x['data']['lastName'])
print('email='+x['data']['email'])
print('persistentUserId='+x['data']['persistentUserId'])
sys.exit()

# voorbeeld
#   "authenticationProviderId": "orcid",
#   "persistentUserId": "0000-0002-3283-0661",
#   "identifier": "@pete",
#   "firstName": "Pete K.",
#   "lastName": "Dataversky",
#   "email": "pete@mailinator.com"

for i in range(1, 13):
    if (i != 10 and i != 11):
        resp = api.get_request(baseUrl+"/api/roles/"+str(i))
        x = resp.json()
        print(str(x['data']['id'])+" "+x['data']['name'])
        print(x)

toDel = [9,12]
for i in toDel:
    resp = api.delete_request(baseUrl+"/api/roles/9")
    x = resp.json()
    print(x)


sys.exit()

dataVerses = {}
level = 0
topDVAlias = 1
resp = api.get_request(baseUrl+"/api/dataverses/"+str(topDV)+"/contents")
dvContents = resp.json()
print(dvContents)
print('--')

sys.exit()

resp = api.get_request(baseUrl+"/api/dataverses/80/groups")
x = resp.json()
print(x)
print('--')



gdata = {}
gdata['description'] = 'pdvGrpDesc'
gdata['displayName'] = 'pdvGrpDisp'
gAlias = 'pdvGrp'
gdata['aliasInOwner'] = gAlias
json_gdata = json.dumps(gdata)
resp = requests.post(baseUrl+'/api/dataverses/testdv/groups', headers=headers, data=json_gdata)            
createGRP_resp = resp.json()
print(createGRP_resp)
print('--')
print('id='+createGRP_resp['data']['identifier'])
print('alias='+createGRP_resp['data']['groupAliasInOwner'])
print('owner='+str(createGRP_resp['data']['owner']))

sys.exit()

roleData = {
  "assignee": "&explicit/80-testdataversegrp",
  "role": "contributor"
}
roleJson = json.dumps(roleData)
#resp = api.post_request(baseUrl+'/api/dataverses/80/assignments',roleJson)
resp = requests.post(baseUrl+"/api/dataverses/80/assignments", headers=headers, data=roleJson)
x = resp.json()
print(x)

sys.exit()

resp = api.get_request(baseUrl+"/api/dataverses/80/groups/testdataversegrp")
x = resp.json()
print(x['data'])
y={}
y['displayName'] = 'dsppdv'
y['description'] = 'despdv'
y['aliasInOwner'] = 'tstpdv'
print(y)
json_data = json.dumps(y)
resp = requests.post(baseUrl+"/api/dataverses/KULOID_50000635/groups",headers=headers,data=json_data)
x = resp.json()
print(x)

y=[]
y.append('&explicit/162-KULGRP_50000598rev')
json_data = json.dumps(y)
print(y)
#PUT http://$server/api/dataverses/$dv/groups/$groupAlias/roleAssignees/$roleAssigneeIdentifier
resp = requests.post(baseUrl+"/api/dataverses/KULOID_50000635/groups/tstpdv/roleAssignees",headers=headers,data=json_data)
x = resp.json()
print(x)

sys.exit()

#delete roles
#DELETE http://$SERVER/api/roles/$id
baseUrlProd = "https://www.rdm.libis.kuleuven.be"
apiKeyProd  = "eefc05e4-8fbd-4cdd-9118-b24e0aaf68c2"
apiProd = NativeApi(baseUrlProd, apiKeyProd)
# resp = apiProd.get_dataverse('kul')
# x = resp.json()
# print(x)


import requests
headers = {'X-Dataverse-key':apiKeyProd,
               'Content-Type':'application/json'}
r = requests.get(baseUrlProd+'/api/roles/11', headers=headers)
print(r.content)
r = requests.delete(baseUrlProd+'/api/roles/11', headers=headers)
print(r.content)

sys.exit()


resp = apiProd.get_request(baseUrlProd+"/api/roles/10")
x = resp.json()
print(x)
resp = apiProd.delete_request(baseUrlProd+"/api/roles/10")
x = resp.json()
print(x)
resp = apiProd.get_request(baseUrlProd+"/api/roles/11")
x = resp.json()
print(x)
resp = apiProd.delete_request(baseUrlProd+"/api/roles/11")
x = resp.json()
print(x)

sys.exit()

resp = api.get_dataverse("ScienceEngineeringTechnologyGroup")
x = resp.json()
print(x)

resp = api.get_dataverse("root")
x = resp.json()
print(x)

#start at current dv
resp = api.get_dataverse('testdvtestdv')
x = resp.json()
print(x)
dvAlias = x['data']['alias']
dvId    = x['data']['id']
while (dvAlias != 'root'):
    upperId = x['data']['ownerId']
    print(str(dvId)+' with parrent '+str(upperId))
    resp = api.get_dataverse(upperId)
    x = resp.json()
    dvAlias = x['data']['alias']
    dvId    = x['data']['id']


#get metadatablocks
resp = api.get_request(baseUrl+"/api/dataverses/testdv/metadatablocks")
x = resp.json()
print(x)

#GET http://$server/api/dataverses/$dv/groups/$groupAlias
resp = api.get_request(baseUrl+"/api/dataverses/root/groups/LIBIS_team")
x = resp.json()
print(x)

resp = api.get_request(baseUrl+"/api/dataverses/testdv/groups")
x = resp.json()
print(x)

useRequest = False
if (useRequest):
    import requests
    gdata = {
     "description":"pdv req desc",
     "displayName":"pdv req dname",
     "aliasInOwner":"pdvreqalias"
    }
    json_gdata = json.dumps(gdata)
    headers = {'X-Dataverse-key':'e38720c2-d06a-48e8-a910-6d60c1f9d138',
               'Content-Type':'application/json'}
    r = requests.post(baseUrl+'/api/dataverses/testdv/groups', headers=headers, data=json_gdata)
    print(r.content)
    
usePyDataverse = False
if (usePyDataverse):
    gdata = {
     "description":"pdv req desc",
     "displayName":"pdv req dname",
     "aliasInOwner":"pdvreqalias"
    }
    json_gdata = json.dumps(gdata)
    api2 = Api(baseUrl, apiKey)   
    resp = api2.post_request(baseUrl+"/api/dataverses/testdv/groups",json_gdata)
    x=resp
    print(x)    

usePyCurl = False
if (usePyCurl):
    from urllib.parse import urlencode
    import pycurl
    gdata = {
     "description":"pdv pyc desc",
     "displayName":"pdv pyc dname",
     "aliasInOwner":"pdvpycalias"
    }
    json_gdata = json.dumps(gdata)
    c = pycurl.Curl()
    c.setopt(pycurl.URL, baseUrl+'/api/dataverses/testdv/groups')
    c.setopt(pycurl.POST, 1)
    post_data = {'data': json_gdata}
    # Form data must be provided already urlencoded.
    postfields = urlencode(post_data)
    c.setopt(pycurl.POSTFIELDS, postfields)
    c.setopt(pycurl.HTTPHEADER, ['X-Dataverse-key: e38720c2-d06a-48e8-a910-6d60c1f9d138',
                             'Content-Type: application/json'])
    c.perform()
    print(c.errstr())
    print('Status: %d' % c.getinfo(c.RESPONSE_CODE))
    print('Time: %f' % c.getinfo(c.TOTAL_TIME))
#gdata['containedRoleAssignees'] = []
#gdata['identifier'] = "KULGRP_"+str("50000598")+"_rs"
#gdata['owner'] = "testdv"
#json_gdata = json.dumps(gdata)
#resp = api.post_request(baseUrl+"/api/dataverses/testdv/groups",json_gdata)
#x = resp.json()
#print(x)

#{'status': 'OK', 'data': {'id': 44, 'alias': 'ScienceEngineeringTechnologyGroup', 'name': 'Science, Engineering and Technology Group', 'affiliation': 'Dataverse.org', 'dataverseContacts': [{'displayOrder': 0, 'contactEmail': 'rachel.geenens@kuleuven.be'}], 'permissionRoot': True, 'description': 'This dataverse contains the research data from KU Leuven researchers from the Science, Engineering and Technology Group', 'dataverseType': 'ORGANIZATIONS_INSTITUTIONS', 'ownerId': 31, 'creationDate': '2020-07-27T06:54:12Z'}}
#{'status': 'OK', 'data': {'id': 1, 'alias': 'root', 'name': 'KU Leuven TEST', 'dataverseContacts': [{'displayOrder': 0, 'contactEmail': 'root@mailinator.com'}], 'permissionRoot': True, 'description': 'The root dataverse.', 'dataverseType': 'UNCATEGORIZED', 'creationDate': '2020-05-28T14:13:01Z'}}