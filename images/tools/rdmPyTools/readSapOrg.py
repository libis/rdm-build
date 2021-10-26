# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 14:43:28 2021

@author: PieterDV
"""
import pandas as pd
import numpy as np
import re
import requests

from pyDataverse.api import NativeApi
from pyDataverse.models import Dataverse
import json


aliasPrefix = "KULOID_"
groupPrefix = "KULGRP_"
groupsToDefine = [
    {'namePrefix': groupPrefix,
     'nameAppendix': ' Researchers Group',
     'nameSuffix':   'res',
     'roles': ['contributor','dsContributor']},
    {'namePrefix': groupPrefix,
     'nameAppendix': ' Reviewers Group',
     'nameSuffix':   'rev',
     'roles': ['curator']}]
create = False
if (create):
    createDV = True
    createGRP = True
    publishDV = True
    addUpperGroups = True
else:    
    createDV = False
    createGRP = False
    publishDV = False
    addUpperGroups = False

delete = True
if (delete):
    deleteDV = True
    deleteGRP = True
else:
    deleteDV = False
    deleteGRP = False
    
testLimit = False #True
isRootDV = False
testNbr  = 9999 #○3

baseUrl = "https://lirias2dev.libis.kuleuven.be"
apiKey  = "e38720c2-d06a-48e8-a910-6d60c1f9d138"
rootDVAlias = 'root'
headers = {'X-Dataverse-key':apiKey,'Content-Type':'application/json'}

api = NativeApi(baseUrl, apiKey)

filename = 'c:\\temp\\rdm\\bash\\loadOrgs'
sapOrg = pd.read_table(filename, sep='|')
print(sapOrg.columns)
#to show all rows/columns in console window
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
#or, alternatively:
print(sapOrg.dtypes.tolist())
print(sapOrg.columns.tolist())
# for col in sapHR.columns:
#     if (re.search("^Generic", col)):
#         sapHR.loc[:, col] = sapHR[col].astype(np.object)
# print(sapHR.dtypes.tolist())        
#sapHR = sapHR.set_index('Username')
#missing values
missing_value_mask = (sapOrg == -999.000)
missing_value_mask.value_counts()
sapOrg[missing_value_mask] = np.nan

def getUpperDVs(inDVAlias):
    retUpperDVs = []
    resp = api.get_dataverse(inDVAlias)
    x = resp.json()
    print(x)
    dvAlias = x['data']['alias']
    dvId    = x['data']['id']
    while (dvAlias != rootDVAlias):
        upperId = x['data']['ownerId']
        print(str(dvId)+' with parrent '+str(upperId))
        resp = api.get_dataverse(upperId)
        x = resp.json()
        dvAlias = x['data']['alias']
        dvId    = x['data']['id']
        dvOID  = re.sub(aliasPrefix,'',dvAlias)
        retUpperDVs.append({'alias':dvAlias,'id':dvId,'kulId':dvOID})
    return(retUpperDVs)

if (createDV):
    #iterate over rows
    cnt = 1
    for row in sapOrg.itertuples():
        print(row.orgNbr, row.orgName, row.upperNbr)
        data = {}
        data['name'] = row.orgName
        dvAlias = aliasPrefix+str(row.orgNbr)
        upAlias = aliasPrefix+str(row.upperNbr)
        data['alias'] = dvAlias
        dataContact = {}
        #dataContact['displayOrder'] = 0
        dataContact['contactEmail'] = 'rdm@libis.be'
        dataContacts = []
        dataContacts.append(dataContact)
        data['dataverseContacts'] = dataContacts
        #data['affiliation'] = row.upperNbr
        #data['description'] = row.orgName
        #data['dataverseType'] = 'ORGANIZATIONS_INSTITUTIONS'
        json_data = json.dumps(data)
        if (row.upperNbr == 0):
            resp = api.get_dataverse(rootDVAlias)
        else:
            resp = api.get_dataverse(upAlias)
        x = resp.json()
        upperId = x["data"]["alias"]
        dv = Dataverse()
        dv.from_json(json_data)
        resp = api.create_dataverse(upperId, dv.json())
        createDV_resp = resp.json()
        if (publishDV):
            resp = api.post_request(baseUrl+"/api/dataverses/"+dvAlias+"/actions/:publish")
            pubResp = resp.json()
            print(pubResp)
        
        if (isRootDV):
            #set the dataverse to be its own root - not to inherit from above
            resp = api.put_request(baseUrl+"/api/dataverses/"+dvAlias+"/metadatablocks/isRoot",'false')
            x = resp.json()
            print(x)
            #Add metadatablocks
            mdata = ["citation","geospatial"]
            json_mdata = json.dumps(mdata)
            resp = api.post_request(baseUrl+"/api/dataverses/"+dvAlias+"/metadatablocks",json_mdata)
            x = resp.json()
            print(x)  

        if (createGRP):
            #researchers group
            upperDVs = getUpperDVs(dvAlias)
            useRequests = True #does not work with pydataverse
            for g in groupsToDefine:
                gdata = {}
                gdata['description'] = row.orgName+g['nameAppendix']
                gdata['displayName'] = row.orgName+g['nameAppendix']
                gAlias = g['namePrefix']+str(row.orgNbr)+g['nameSuffix']
                gdata['aliasInOwner'] = gAlias
                json_gdata = json.dumps(gdata)
                if (useRequests):
                    resp = requests.post(baseUrl+'/api/dataverses/'+dvAlias+'/groups', headers=headers, data=json_gdata)            
                else:
                    resp = api.post_request(baseUrl+"/api/dataverses/"+dvAlias+"/groups",json_gdata)
                createGRP_resp = resp.json()
                print(createGRP_resp)
                print('id='+createGRP_resp['data']['identifier']) #contains the explicit group identifier needed to add roles
                print('alias='+createGRP_resp['data']['groupAliasInOwner'])
                print('owner='+str(createGRP_resp['data']['owner']))                
                #Assign the Group to the corresponding Role
                for r in g['roles']:
                    print("Add Role "+r+" to "+createGRP_resp['data']['identifier'])
                    roleData = {
                      "assignee": createGRP_resp['data']['identifier'],
                      "role": r
                    }
                    roleJson = json.dumps(roleData)
                    if (useRequests):                
                        resp = requests.post(baseUrl+"/api/dataverses/"+dvAlias+"/assignments", headers=headers, data=roleJson)
                    else:
                        resp = api.post_request(baseUrl+'/api/dataverses/'+dvAlias+'/assignments',roleJson)                
                    x = resp.json()
                    print(x)                
                #ADD UPPER GROUPS TO THE GROUP
                if (addUpperGroups):
                    groups2Add = []
                    for uDV in upperDVs:
                        #PUT http://$server/api/dataverses/$dv/groups/$groupAlias/roleAssignees/$roleAssigneeIdentifier
                        if (uDV['alias'] != rootDVAlias):
                            for ug in groupsToDefine:
                                #'&explicit/162-KULGRP_50000598rev'
                                ugAlias = '&explicit/'+str(uDV['id'])+'-'+g['namePrefix']+uDV['kulId']+g['nameSuffix']
                                groups2Add.append(ugAlias)
                    ug_json = json.dumps(groups2Add)
                    if (useRequests):
                        resp = requests.post(baseUrl+'/api/dataverses/'+dvAlias+'/groups/'+gAlias+'/roleAssignees', headers = headers,data=ug_json)
                    else:
                        resp = api.post_request(baseUrl+'/api/dataverses/'+dvAlias+'/groups/'+gAlias+'/roleAssignees',ug_json)
                    addUgResp = resp.json()
                    print(addUgResp)
        cnt = cnt + 1
        if (cnt == testNbr and testLimit):
            break

if (deleteDV):   
    #delete lower level first
    cnt = 1
    for row in sapOrg.itertuples():
        cnt = cnt + 1
        dvAlias = aliasPrefix+str(row.orgNbr)
        if (row.upperNbr != 0):
            if (deleteGRP):
                #delete groups
                for g in groupsToDefine:
                    api.delete_request(baseUrl+"/api/dataverses"+dvAlias+"/groups/"+g['namePrefix']+str(row.orgNbr)+g['nameSuffix'])
            #delete dataverse
            api.delete_dataverse(dvAlias)
        if (cnt == testNbr and testLimit):
            break
    #delete upper level
    cnt = 1
    for row in sapOrg.itertuples():
        cnt = cnt + 1
        dvAlias = aliasPrefix+str(row.orgNbr)
        if (row.upperNbr == 0):
            if (deleteGRP):
                #delete groups
                for g in groupsToDefine:
                    api.delete_request(baseUrl+"/api/dataverses"+dvAlias+"/groups/"+g['namePrefix']+str(row.orgNbr)+g['nameSuffix'])
            #delete dataverse
            api.delete_dataverse(dvAlias)
        if (cnt == testNbr and testLimit):
            break



