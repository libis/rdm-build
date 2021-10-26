# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 13:36:30 2021

@author: PieterDV
"""
import sys
import json
import orcidUtils as ou
import liriasUtils as lu
import datetime as dt
import shutil
from pathlib import Path    

orcidList = ou.readOrcidFile('c:/temp/rdm/out/Orcid20210603')

handledDir = 'c:/temp/rdm/in/dataVerse/handled/'
errorDir   = 'c:/temp/rdm/in/dataVerse/error/'
workDir    = 'c:/temp/rdm/in/dataVerse/work/'
inFile = 'c:/temp/rdm/in/dataVerse/CLAMCI.json'
inFile = 'c:/temp/rdm/in/dataVerse/RDR.CVHLQ2.json'
inFileName = Path(inFile).name
with open(inFile, encoding='utf-8') as f:
  data = json.load(f)

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
#print(data)

inlineRelations = False
relations = []

doDelete = True
if (doDelete):
    lu.deleteDataset(data['identifier'], True)
    #sys.exit()

import xml.etree.ElementTree as ET
apiNameSpace = 'http://www.symplectic.co.uk/publications/api'
apiNameSpacePrefix = 'xmlns'
ns =  {apiNameSpacePrefix:apiNameSpace}

for prefix, uri in ns.items():
		ET.register_namespace(prefix, uri)

# build a tree structure
impRecord = ET.Element("import-record")
impRecord.set(apiNameSpacePrefix,apiNameSpace)
impRecord.set('type-name','dataset')
native = ET.SubElement(impRecord, "native")
#Affiliation
af = ET.SubElement(native, "field", name = "c-affiliation")
af.set('type', 'boolean')
af.set('display-name',"This is a dataset by (a) KU Leuven author(s)")
afB = ET.SubElement(af, "boolean")
afB.text = "true"
#Title
title = ET.SubElement(native, 'field', name='title')
titleT = ET.SubElement(title, "text")
titleT.text = data['metadata']['title']
#AlternativeTitle 
##??HERHAALBAARHEID??
for at in data['metadata']['alternativeTitle']:
    altTitle = ET.SubElement(native, 'field', name='c-alttitle')
    altTitleT = ET.SubElement(altTitle, "field", name = "text")
    altTitleT.text = at
    
#DOI
doi = ET.SubElement(native, 'field', name='doi')
doiT = ET.SubElement(doi, 'field', name='text')
doiT.text = data['authority']+'/'+data['identifier']
doiLinks = ET.SubElement(doi, 'links')
doiLink  = ET.SubElement(doiLinks, 'link')
doiLink.set('type', 'text')
doiLink.set('href', data['persistentUrl'])
#other ids
if ('otherId' in data['metadata']):
    addId = ET.SubElement(native, 'field', name = 'c-additional-identifier')
    addId.set('type','list')
    addIdIts = ET.SubElement(addId, 'items')
    for id in data['metadata']['otherId']:
        addIdIt = ET.SubElement(addIdIts, 'item')
        addIdIt.text = id['otherIdAgency']+'-'+id['otherIdValue']

#Authors
if ('author' in data['metadata']):
    auts = ET.SubElement(native, 'field', name = 'authors')
    auts.set('type','person-list')
    ppl  = ET.SubElement(auts, 'people')
    for aut in data['metadata']['author']:
        namesplit = aut['authorName'].split(", ", 1)
        lastname = namesplit[0]
        firstname = namesplit[1]
        prs = ET.SubElement(ppl, 'person')
        ln = ET.SubElement(prs, 'last-name')
        ln.text = lastname
        fn = ET.SubElement(prs, 'first-name')
        fn.text = firstname
        if (aut['authorIdentifierScheme'] == "ORCID"):
            if (ou.checkOrcid(aut['authorIdentifier'])):
                print("Orcid checked")
                if (aut['authorIdentifier'] in orcidList):
                    userUId = orcidList[aut['authorIdentifier']]
                    print(userUId)
                    try:
                        liriasUserId = lu.getUserByKulUId(userUId)
                        if (inlineRelations):
                            lks = ET.SubElement(prs, "links")
                            lk  = ET.SubElement(lks, "link", id = liriasUserId)
                            lk.set('type',"elements/user")
                            lk.set('href',lu.getUsersApiURL()+liriasUserId)
                        else:
                            relationObject = {
                                'to-object': liriasUserId,
                                'type-name': 'publication-user-authorship'}
                            relations.append(relationObject)
                    except Exception as e:
                        print("Error: %s occured. userId=%s" % (e.__class__.__name__, userUId))

#abstract
if ('dsDescription' in data['metadata']):
    for ds in data['metadata']['dsDescription']:
        abstr = ET.SubElement(native, 'field', name="abstract")
        abstrT = ET.SubElement(abstr, 'text')
        abstrT.text = ds['dsDescriptionValue']
#keywords/subjects
if ('keyword' in data['metadata']):
    kwL = ET.SubElement(native, 'field', name='keywords')
    kwL.set('type','keyword-list')
    kwLs = ET.SubElement(kwL, 'keywords')
    for kw in data['metadata']['keyword']:
        if (kw['keywordValue'] != ''):
            kwE = ET.SubElement(kwLs, 'keyword')
            kwE.text = kw['keywordValue']
#Format
if ('technicalFormat' in data['metadata']):
    tf = ET.SubElement(native, 'field', name="medium")
    tfT = ET.SubElement(tf, 'text')
    tfT.text = data['metadata']['technicalFormat']
#contributor
if ('contributor' in data['metadata']):
    cs = ET.SubElement(native, 'field',name='c-contributor')
    cs.set('type','person-list')
    csp = ET.SubElement(cs, 'people')
    for c in data['metadata']['contributor']:
        namesplit = c['contributorName'].split(", ", 1)
        lastname = namesplit[0]
        if (len(namesplit)>1):
            firstname = namesplit[1]
        else:
            firstname = ''
        cspp = ET.SubElement(csp, 'person')
        csppln = ET.SubElement(cspp, 'last-name')
        csppln.text = lastname
        if (firstname != ''):
            csppfn = ET.SubElement(cspp, 'first-name')
            csppfn.text = firstname
    cst = ET.SubElement(native, 'field',name='c-contributor-type')
    cst.set('type','list')
    cstis = ET.SubElement(cst, 'items')
    for c in data['metadata']['contributor']:
        csti = ET.SubElement(cstis, 'item')
        csti.text = c['contributorType']
#fund/grand
if ('grantNumber' in data['metadata']):
    fas = ET.SubElement(native, 'field', name='funding-acknowledgements')
    fas.set('type','funding-acknowledgements')
    fass = ET.SubElement(fas, 'funding-acknowledgements')
    fassgs = ET.SubElement(fass, 'grants')
    for g in data['metadata']['grantNumber']:
        fassg = ET.SubElement(fassgs, 'grant')
        fassgid = ET.SubElement(fassgs, 'grant-id')
        fassgid.text = g['grantNumberValue']
        fassgorg = ET.SubElement(fassgs, 'organization')
        fassgorg.text = g['grantNumberAgency']
#language
if ('language' in data['metadata']):
    for l in data['metadata']['language']:
        lan = ET.SubElement(native, 'field', name ='language')
        lanT = ET.SubElement(lan, 'text')
        lanT.text = l
#technical info
if ('technicalInformation' in data['metadata']):
    ti = ET.SubElement(native, 'field', name='c-technicalinfo')
    tiT = ET.SubElement(ti, 'text')
    tiT.text = data['metadata']['technicalInformation']                        
#virtual collection
if ('virtualCollection' in data['metadata']):
    flds = ET.SubElement(native, 'fields')
    fld  = ET.SubElement(flds, 'field', name='labels')
    fld.set('type','keyword-list')
    fldkws = ET.SubElement(fld, 'keywords')
    for vc in data['metadata']['virtualCollection']:
        fldkw = ET.SubElement(fldkws, 'keyword', scheme=vc)
        fldkw.text = vc
#Publisher
if ('publisher' in data):
    pub = ET.SubElement(native, 'field', name='publisher')
    pubT = ET.SubElement(pub, 'text')
    pubT.text = data['publisher']        
#publication date
if ('publicationDate' in data):
    datum = dt.datetime.strptime(data['publicationDate'], '%Y-%m-%d')
    pubD = ET.SubElement(native, 'field', name='online-publication-date')
    pubD.set('type','date')
    pubDt = ET.SubElement(pubD, 'date')
    pubDd = ET.SubElement(pubDt, 'day')
    pubDd.text = datum.strftime('%d').lstrip('0')
    pubDm = ET.SubElement(pubDt, 'month')
    pubDm.text = datum.strftime('%m').lstrip('0')
    pubDy = ET.SubElement(pubDt, 'year')
    pubDy.text = datum.strftime('%Y')
#Access
if ('termsOfUse' in data):
    lic = ET.SubElement(native, 'field', name='c-license-data')
    licT = ET.SubElement(lic, 'text')
    licT.text = data['termsOfUse']        

# wrap it in an ElementTree instance, and save as XML
tree = ET.ElementTree(impRecord)

print("Writing xml to "+workDir+inFileName+'.xml')
f = open(workDir+inFileName+'.xml', 'w', encoding='utf-8')
f.write('<?xml version="1.0" encoding="UTF-8"?>')
f.write(ET.tostring(impRecord).decode("utf-8"))
f.close()

try:
    newId = lu.uploadDataset(data['identifier'], ET.tostring(impRecord), True)
    print('newly loaded dataset : '+newId)
except Exception as e:
    print("Error: %s occured. dataVerseId=%s" % (e.__class__.__name__, data['identifier']))
    shutil.move(inFile, errorDir)
    raise

#relations
if (not(inlineRelations)):
    for rel in relations:
        dataSource = "c-inst-1"
        impRel = ET.Element("import-relationship")
        impRel.set(apiNameSpacePrefix,apiNameSpace)
        fromRel = ET.SubElement(impRel, "from-object")
        fromRel.text = "publication(source-"+dataSource+",pid-"+data['identifier']+")"
        typeRel = ET.SubElement(impRel, "type-name")
        typeRel.text = rel['type-name']
        if (rel['type-name'] == 'publication-user-authorship'):
            toRel   = ET.SubElement(impRel, "to-object")
            toRel.text = "user("+rel['to-object']+")"
        #print(ET.tostring(impRel))
        try:
            lu.uploadRelationShip(newId, ET.tostring(impRel), True)
        except Exception as e:
            print("Error: %s occured. Relationship=%s,%s,%s" % (e.__class__.__name__,newId,rel['type-name'],rel['to-object']))
            shutil.move(inFile,errorDir)
            #raise

#move input file to handled directory
shutil.move(inFile, handledDir)        

#print(ET.tostring(impRecord))


