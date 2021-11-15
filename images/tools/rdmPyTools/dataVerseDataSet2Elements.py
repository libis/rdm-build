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
import generalUtils as gu 
import logging
import xml.etree.ElementTree as ET
import errorUtils as eu

def extractLicenseInfo(inTOU):
    retLicInfo = inTOU
    
    return(retLicInfo)
    

def dataVerseDataSet2Elements(inConfigFile, inDataSetFile, logName = ''):
    #get loghandler
    logH        = logging.getLogger(logName)

    #read options from configurationfile
    logH.info('Read Configuration File %s', inConfigFile)
    opts        = gu.readConfigFile(inConfigFile)
    #Directories
    inDir       = opts.get('datasets','inDir')
    handledDir  = opts.get('datasets','handledDir')
    errorDir    = opts.get('datasets','errorDir')
    workDir     = opts.get('datasets','workDir')
    #
    inlineRelations = opts.getboolean('flags', 'inlineRelations', fallback = False)
    doDelete        = opts.getboolean('flags', 'doDelete', fallback = True)
    altIdentifiers  = opts.getboolean('flags', 'altIdentifiers', fallback = False)
    mergeLanguages  = opts.getboolean('flags', 'mergeLanguages', fallback = True)
    mergeAltTitles  = opts.getboolean('flags', 'mergeAltTitles', fallback = True)
    useContributorType = opts.getboolean('flags', 'useContributorType', fallback = False)
    getUserNameViaApi = opts.getboolean('flags', 'getUserNameViaApi', fallback = True)
    #
    languagesSep    = opts.get('flags','languagesSep', fallback = '|')
    altTitlesSep    = opts.get('flags','altTitlesSep', fallback = '|')
    #limits
    nbrAltTitles    = opts.getint('limits','nbrAltTitles')
    nbrAbstracts    = opts.getint('limits','nbrAbstracts')    
    #defaults
    defPublisher    = opts.get('defaults','publisher', fallback = 'RDR KU Leuven')
    defCAffiliation = opts.get('defaults','c-affiliation', fallback = 'This is a dataset by (a) KU Leuven author(s)')
    #ORCID
    orcidDir    = opts.get('ORCID','orcidDir')
    orcidFile   = opts.get('ORCID','orcidFile')
    #ElementsApi
    dataSource  = opts.get('elementsApi','dataSource')
    apiUrl      = opts.get('elementsApi','apiURL')
    readApiUser = opts.get('elementsApi','readApiUser')
    readApiPw   = opts.get('elementsApi','readApiPw', raw=True)
    writeApiUser= opts.get('elementsApi','writeApiUser')
    writeApiPw  = opts.get('elementsApi','writeApiPw', raw=True)
    
    logH.info('dataVerseDataSet2Elements config settings loaded')
    
    try:    
        readLiriasApi  = lu.liriasApi(apiUrl, readApiUser, readApiPw, logName)
        writeLiriasApi = lu.liriasApi(apiUrl, writeApiUser, writeApiPw, logName)
    except Exception as e:
        logH.error('Error dataVerseDataSet2Elements: %s',e.__class__.__name__)
        logH.error('Error dataVerseDataSet2Elements: could not create a Lirias Api client')
        raise
            
    orcidList = ou.readOrcidFile(orcidDir+orcidFile)
    
    inFile = inDataSetFile
    inFileName = Path(inFile).name
    with open(inFile, encoding='utf-8') as f:
      data = json.load(f)

    relations = []
    liriasId  = ''
    
    if (doDelete):
        try:
            writeLiriasApi.deleteDataset(dataSource, data['identifier'])
        except Exception as e:
            logH.warning("Error dataVerseDataSet2Elements: %s occured. Trying to Delete %s in dataSource %s" % (e.__class__.__name__, data['identifier'], dataSource))
            logH.warning("dataVerseDataSet2Elements: Execution will proceed regardless")
    else:
            logH.warning("dataVerseDataSet2Elements: doDelete = FALSE but looking for existence and possibly deleting existing relationships")  
            try:
                liriasId = readLiriasApi.getDataSetIdByDoi(dataSource, data['identifier'])
                if (liriasId != ''):
                    #delete existing relations
                    try:
                        writeLiriasApi.deleteRelationShips(liriasId)
                    except Exception as e:
                        logH.warning("Error dataVerseDataSet2Elements: %s occured.  Trying to Delete relaionships for %s",e.__class__.__name__,liriasId)
                        logH.warning("dataVerseDataSet2Elements: Execution will proceed regardless")
            except Exception as e:
                logH.warning("Error dataVerseDataSet2Elements: %s occured. Trying to Find %s in dataSource %s" % (e.__class__.__name__, data['identifier'], dataSource))
                logH.warning("dataVerseDataSet2Elements: Execution will proceed regardless")
            
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
    logH.info('dataVerseDataSet2Elements affiliation')     
    af = ET.SubElement(native, "field", name = "c-affiliation")
    af.set('type', 'boolean')
    af.set('display-name',defCAffiliation)
    afB = ET.SubElement(af, "boolean")
    afB.text = "true"
    #Title
    logH.info('dataVerseDataSet2Elements title')         
    if ('title' in data['metadata']):
        title = ET.SubElement(native, 'field', name='title')
        titleT = ET.SubElement(title, "text")
        titleT.text = data['metadata']['title']
    #AlternativeTitle 
    logH.info('dataVerseDataSet2Elements alt.title')         
    if ('alternativeTitle' in data['metadata']):
        cntAltTitles = 0
        allAltTitles = ''
        for at in data['metadata']['alternativeTitle']:
            logH.info('dataVerseDataSet2Elements alt.Title '+at)     
            cntAltTitles = cntAltTitles + 1
            if (cntAltTitles <= nbrAltTitles):
                if (mergeAltTitles):
                    if (allAltTitles == ''):
                        allAltTitles = at
                    else:
                        allAltTitles = allAltTitles+altTitlesSep+at
                else:
                    altTitle = ET.SubElement(native, 'field', name='c-alttitle')
                    altTitleT = ET.SubElement(altTitle, 'field', name = 'text')
                    altTitleT.text = at
        if (allAltTitles != '' and mergeAltTitles):
            altTitle  = ET.SubElement(native, 'field', name = 'c-alttitle')
            altTitleT = ET.SubElement(altTitle, 'field', name = 'text')
            altTitleT.text = allAltTitles
    #DOI
    logH.info('dataVerseDataSet2Elements authority')         
    if ('authority' in data and 'identifier' in data):
        doi = ET.SubElement(native, 'field', name='doi')
        doiT = ET.SubElement(doi, 'field', name='text')
        doiT.text = data['authority']+'/'+data['identifier']
        if ('persistentUrl' in data):
            doiLinks = ET.SubElement(doi, 'links')
            doiLink  = ET.SubElement(doiLinks, 'link')
            doiLink.set('type', 'text')
            doiLink.set('href', data['persistentUrl'])
    #other ids
    logH.info('dataVerseDataSet2Elements alternative identifiers')         
    if (altIdentifiers):
        if ('otherId' in data['metadata']):
            addId = ET.SubElement(native, 'field', name = 'c-additional-identifier')
            addId.set('type','list')
            addIdIts = ET.SubElement(addId, 'items')
            for id in data['metadata']['otherId']:
                addIdIt = ET.SubElement(addIdIts, 'item')
                addIdIt.text = id['otherIdAgency']+'-'+id['otherIdValue']
    logH.info('dataVerseDataSet2Elements check authors')    
    #Authors
    if ('author' in data['metadata']):
        auts = ET.SubElement(native, 'field', name = 'authors')
        auts.set('type','person-list')
        ppl  = ET.SubElement(auts, 'people')
        for aut in data['metadata']['author']:
            logH.info('dataVerseDataSet2Elements: name = '+aut['authorName'])
            nameDict  = gu.splitName(aut['authorName'], logName)
            prs = ET.SubElement(ppl, 'person')
            if ('authorIdentifierScheme' in aut and 'authorIdentifier' in aut):
                if (aut['authorIdentifierScheme'] == "ORCID"):
                    if (ou.checkOrcid(aut['authorIdentifier'])):
                        logH.info("dataVerseDataSet2Elements: Orcid "+aut['authorIdentifier']+" checked")
                        if (aut['authorIdentifier'] in orcidList):
                            userUId = orcidList[aut['authorIdentifier']]
                            logH.info("dataVerseDataSet2Elements: userId found : "+userUId)
                            try:
                                liriasUserId = readLiriasApi.getUserByKulUId(userUId)
                                logH.info('dataVerseDataSet2Elements: liriasUserId = '+liriasUserId)
                                if (getUserNameViaApi):
                                    try:
                                        userNameDict = readLiriasApi.getUserNameByKULUid(userUId)
                                        nameDict     = userNameDict
                                    except Exception as e:
                                        logH.info('dataVerseDataSet2Elements: could not get username via Lirias APi '+str(userUId))
                                if (inlineRelations):
                                    logH.info('dataVerseDataSet2Elements: inlineRelations')
                                    lks = ET.SubElement(prs, "links")
                                    lk  = ET.SubElement(lks, "link", id = liriasUserId)
                                    lk.set('type',"elements/user")
                                    lk.set('href',readLiriasApi.getUsersApiURL()+liriasUserId)
                                else:
                                    logH.info('dataVerseDataSet2Elements: relationObject')
                                    relationObject = {
                                        'to-object': liriasUserId,
                                        'type-name': 'publication-user-authorship'}
                                    relations.append(relationObject)
                            except Exception as e:
                                logH.warning("Error dataVerseDataSet2Elements: %s occured. userId=%s" % (e.__class__.__name__, userUId))
                                logH.warning("Warning dataVerseDataSet2Elements - trouble finding lirias userid based upon Kul Userid")
            lastname  = nameDict['lastname']
            firstname = nameDict['firstname']
            initials  = nameDict['initials']
            logH.info('dataVerseDataSet2Elements: nameSplit = '+lastname+','+firstname+','+initials)
            ln = ET.SubElement(prs, 'last-name')
            ln.text = lastname
            if (firstname != ''):
                fn = ET.SubElement(prs, 'first-names')
                fn.text = firstname
                ins = ET.SubElement(prs, 'initials')
                ins.text = initials
    logH.info('dataVerseDataSet2Elements check publications')    
    #related publications
    if ('publication' in data['metadata']):
        logH.info('related publications')
        for pub in data['metadata']['publication']:
            if ('liriasSourceID' in pub):
                logH.info('related publication: '+str(pub['liriasSourceID']))
                relationObject = {
                    'to-object': str(pub['liriasSourceID']),
                    'type-name' : 'publication-publication-supplement'}
                relations.append(relationObject)
    #abstract
    cntAbstracts = 0
    if ('dsDescription' in data['metadata']):
        abstractText = ""
        for ds in data['metadata']['dsDescription']:
            cntAbstracts = cntAbstracts + 1
            if (cntAbstracts <= nbrAbstracts):
                if (abstractText == ""):
                    abstractText = ds['dsDescriptionValue']
                else:
                    abstractText = abstractText+" ; "+ds['dsDescriptionValue']
        if (abstractText != ""):
            abstr = ET.SubElement(native, 'field', name="abstract")
            abstrT = ET.SubElement(abstr, 'text')
            abstrT.text = abstractText
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
    logH.info('dataVerseDataSet2Elements check contributors')    
    #contributor
    if ('contributor' in data['metadata']):
        cs = ET.SubElement(native, 'field',name='c-contributor')
        cs.set('type','person-list')
        csp = ET.SubElement(cs, 'people')
        for c in data['metadata']['contributor']:
            nameDict  = gu.nameSplit(c['contributorName'], logName)
            lastname  = nameDict['lastname']
            firstname = nameDict['firstname']
            initials  = nameDict['initials']
            cspp = ET.SubElement(csp, 'person')
            csppln = ET.SubElement(cspp, 'last-name')
            csppln.text = lastname
            if (firstname != ''):
                csppfn = ET.SubElement(cspp, 'first-names')
                csppfn.text = firstname
            if (initials != ''):
                csppin = ET.SubElement(cspp, 'initials')
                csppin.text = initials
        if (useContributorType):
            cst = ET.SubElement(native, 'field',name='c-contributor-type')
            cst.set('type','list')
            cstis = ET.SubElement(cst, 'items')
            for c in data['metadata']['contributor']:
                csti = ET.SubElement(cstis, 'item')
                csti.text = c['contributorType']
    logH.info('dataVerseDataSet2Elements check grants')    
    #fund/grand
    if ('grantNumber' in data['metadata']):
        fas = ET.SubElement(native, 'field', name='funding-acknowledgements')
        fas.set('type','funding-acknowledgements')
        fass = ET.SubElement(fas, 'funding-acknowledgements')
        fassgs = ET.SubElement(fass, 'grants')
        for g in data['metadata']['grantNumber']:
            if ('grantNumberValue' in g and 'grantNumberAgency' in g):
                fassg = ET.SubElement(fassgs, 'grant')
                fassgid = ET.SubElement(fassg, 'grant-id')
                fassgid.text = g['grantNumberValue']
                fassgorg = ET.SubElement(fassgs, 'organization')
                fassgorg.text = g['grantNumberAgency']
    #language
    if ('language' in data['metadata']):
        if (mergeLanguages):
            langs = ""
            for l in data['metadata']['language']:
                if (langs == ""):
                    langs = l
                else:
                    langs = langs+languagesSep+l
            lan = ET.SubElement(native, 'field', name ='language')
            lanT = ET.SubElement(lan, 'text')
            lanT.text = langs
        else:
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
        #use default setting anyway - this 'if' statement is in fact unnecessary
        pub = ET.SubElement(native, 'field', name='publisher')
        pubT = ET.SubElement(pub, 'text')
        pubT.text = defPublisher     
    else:
        pub = ET.SubElement(native, 'field', name='publisher')
        pubT = ET.SubElement(pub, 'text')
        pubT.text = defPublisher     
        #Access
    logH.info('dataVerseDataSet2Elements check accessrights')            
    accessRights = ''
    if ('access' in data['metadata']):
        if ('accessRights' in data['metadata']['access']):
            try:
                accessRights = lu.liriasAccessRights(data['metadata']['access']['accessRights'])
                accR = ET.SubElement(native, 'field', name='c-accessrights')
                accRT = ET.SubElement(accR, 'text')
                accRT.text = accessRights
            except Exception as eAR:
                logH.warning('Error dataVerseDataSet2Elements: %s occured at liriasAccessRights %s' % (eAR.__class__.__name__,data['metadata']['access']['accessRights']))
                logH.warning('\tContinuting regardless')
        if ('legitimateOptout' in data['metadata']['access']):
            try:
                legOptOut = lu.liriasLegitimateOptout(data['metadata']['access']['legitimateOptout'])
                legOU = ET.SubElement(native, 'field', name='c-access-legitimateoptout')
                legOUT = ET.SubElement(legOU, 'text')
                legOUT.text = legOptOut
            except Exception as eLOU:
                logH.warning('Error dataVerseDataSet2Elements: %s occured at liriasLegitimateOptOut %s' % (eLOU.__class__.__name__,data['metadata']['access']['legitimateOptout']))
                logH.warning('\tContinuting regardless')
    #embargoDate
    logH.info('dataVerseDataSet2Elements check embargoDate')    
    datum = ''
    if (accessRights == 'embargoed' and 'dateAvailable' in data['metadata']['access']):
        datum = dt.datetime.strptime(data['metadata']['access']['dateAvailable'], '%Y-%m-%d')
    if (datum != ''):
        embD = ET.SubElement(native, 'field', name='c-date-end-of-embargo')
        embD.set('type','date')
        embDt = ET.SubElement(embD, 'date')
        embDd = ET.SubElement(embDt, 'day')
        embDd.text = datum.strftime('%d').lstrip('0')
        embDm = ET.SubElement(embDt, 'month')
        embDm.text = datum.strftime('%m').lstrip('0')
        embDy = ET.SubElement(embDt, 'year')
        embDy.text = datum.strftime('%Y')

    #publication date
    logH.info('dataVerseDataSet2Elements check publicationDate')    
    datum = ''
    if ('publicationDate' in data):
        datum = dt.datetime.strptime(data['publicationDate'], '%Y-%m-%d')
    if (datum != ''):
        pubD = ET.SubElement(native, 'field', name='online-publication-date')
        pubD.set('type','date')
        pubDt = ET.SubElement(pubD, 'date')
        pubDd = ET.SubElement(pubDt, 'day')
        pubDd.text = datum.strftime('%d').lstrip('0')
        pubDm = ET.SubElement(pubDt, 'month')
        pubDm.text = datum.strftime('%m').lstrip('0')
        pubDy = ET.SubElement(pubDt, 'year')
        pubDy.text = datum.strftime('%Y')
    #License
    logH.info('dataVerseDataSet2Elements check license')    
    if ('termsOfUse' in data):
        lic = ET.SubElement(native, 'field', name='c-license-data')
        licT = ET.SubElement(lic, 'text')
        licInfo = extractLicenseInfo(data['termsOfUse'])
        licT.text = licInfo
    
    # wrap it in an ElementTree instance, and save as XML
    logH.info('dataVerseDataSet2Elements create XML tree')    
    tree = ET.ElementTree(impRecord)
    
    logH.info("dataVerseDataSet2Elements: Writing xml to "+workDir+inFileName+'.xml')
    f = open(workDir+inFileName+'.xml', 'w', encoding='utf-8')
    f.write('<?xml version="1.0" encoding="UTF-8"?>')
    f.write(ET.tostring(impRecord).decode("utf-8"))
    f.close()
    
    try:
        newId = writeLiriasApi.uploadDataset(dataSource, data['identifier'], ET.tostring(impRecord))
        if (liriasId != ''):
            logH.info('dataVerseDataSet2Elements: loaded dataset '+data['identifier']+': '+newId+' should equal '+liriasId)
        else:
            logH.info('dataVerseDataSet2Elements: loaded dataset '+data['identifier']+': '+newId)            
    except Exception as e:
        logH.error("Error dataVerseDataSet2Elements: %s occured. dataVerseId=%s" % (e.__class__.__name__, data['identifier']))
        logH.error('Error dataVerseDataSet2Elements: uploadDataSet Failed')
        try:
            gu.moveFile(inFile, errorDir, logName)
        except Exception as eMove:
            logH.error('Error dataVerseDataSet2Eleements: %s occured at gu.moveFile('+inFile+','+handledDir+')', eMove.__class__.__name__)        
            logH.error('File '+inFile+' not moved to '+handledDir)
        raise
    
    #relations
    logH.info('relations')    
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
            elif (rel['type-name'] == 'publication-publication-supplement'):
                toRel   = ET.SubElement(impRel, "to-object")
                toRel.text = "publication("+rel['to-object']+")"
            try:
                writeLiriasApi.uploadRelationShip(newId, ET.tostring(impRel))
            except Exception as e:
                logH.error("Error dataVerseDataSet2Elements: %s occured. Relationship=%s,%s,%s" % (e.__class__.__name__,newId,rel['type-name'],rel['to-object']))
                logH.error("Error dataVerseDataSet2Elements: uploadRelationship Failed")
                logH.info('shutil.move('+inFile+','+errorDir+')')
                try:
                    gu.moveFile(inFile,errorDir,logName)
                except Exception as eMove:
                    logH.error('Error dataVerseDataSet2Eleements: %s occured at gu.moveFile('+inFile+','+handledDir+')', eMove.__class__.__name__)        
                    logH.error('File '+inFile+' not moved to '+handledDir)
                raise
    
    #move input file to handled directory
    try:
        logH.info('Info dataVerseDataSet2Elements: Move '+inFile+' to '+handledDir)
        gu.moveFile(inFile, handledDir, logName)
    except Exception as e:
        logH.error('Error dataVerseDataSet2Eleements: %s occured at gu.moveFile('+inFile+','+handledDir+')', e.__class__.__name__)        
        logH.error('File '+inFile+' not moved to '+handledDir)