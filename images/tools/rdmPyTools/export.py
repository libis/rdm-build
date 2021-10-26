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

baseUrl = "https://lirias2dev.libis.kuleuven.be"
apiKey  = "e38720c2-d06a-48e8-a910-6d60c1f9d138"
api = NativeApi(baseUrl, apiKey)
headers = {'X-Dataverse-key':apiKey,'Content-Type':'application/json'}

# resp = api.get_request(baseUrl+"/api/dataverses/1/groups/LIBIS_team")
# x = resp.json()
# # the result is a Python dictionary:
# print(x["data"]["identifier"])

#ddi, oai_ddi, dcterms, oai_dc, schema.org , OAI_ORE , Datacite, oai_datacite and dataverse_json

resp = api.get_request(baseUrl+"/api/datasets/export?exporter=dataverse_json&persistentId=doi:10.80442/FK2/3PKOTO")
x = resp.json()
print(x)
print('--')

sys.exit()


#r = requests.get(baseUrl+"/api/admin/authenticatedUsers/u0001290", headers=headers)
#r = requests.get(baseUrl+"/api/admin/assignments/assignees/&explicit/239-KULGRP_99999999res", headers=headers)
r = requests.get(baseUrl+"/api/admin/assignee/@u0001290", headers=headers)
#r = requests.get(baseUrl+"/api/roles/9", headers=headers)
#r = requests.get(baseUrl+"/api/dataverses/239/groups",headers=headers)
print(r.content)
usr = r.json()
print(usr)
if (usr['status']!='ERROR'):
    ud = usr['data']
    for k in ud:
            print(str(k)+":"+str(ud[k]))
else:
    print(usr['message'])

sys.exit()
