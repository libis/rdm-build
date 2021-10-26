# -*- coding: utf-8 -*-
"""
Created on Thu May  6 13:15:07 2021

@author: PieterDV
"""
import os
import sys
import pandas as pd
import numpy as np
import re

import logging
import math

import generalUtils as gu
import errorUtils as eu

def getPrevSapUsersFile(currFileBaseName):
    MAXDAYSBACK = -100
    daysBack = -1
    while (daysBack > MAXDAYSBACK):
        dateBack = gu.get_yyyymmddOffset(daysBack)
        if (os.path.exists(currFileBaseName+dateBack)):
            return(dateBack)
        daysBack = daysBack - 1
    return(gu.get_yyyymmdd())

def genOrcidFile(currFile, orcidFile, fileSep = ',', logName = ''):
    logH            = logging.getLogger(logName)
    currDf          = pd.read_table(currFile, sep=fileSep, dtype = str)
    #missing values
    missing_value_mask = (currDf == -999.000)
    missing_value_mask.value_counts()
    currDf[missing_value_mask] = None
    
    #remove the [] around the column names
    currDf.rename(columns=lambda x: re.sub('[\[\]]','',x),inplace=True)
    #rename Generic Columns
    nbrGeneric = 51
    idxGenerics = {}
    for g in range(1,nbrGeneric,1):
        colName = 'Generic%02d' % (g)
        idxGenerics[colName] = currDf.columns.get_loc(colName) + 1
    currDf.loc[currDf["Generic15"].notna(), ["Username","Generic15"]].to_csv(orcidFile, index=False)
        

def diffFile(currFile, prevFileBaseName, creUpdFile, delFile, inCurrDate, fileSep = ',', logName = ''):
        logH        = logging.getLogger(logName)
        if (os.path.exists(currFile)):
            nbrOfLines = gu.fileNbrOfLines(currFile)
            if (nbrOfLines >= 10000):
                logH.debug('inFile (currFile) = %s exists', currFile)
                logH.debug('Check for previous file with name like %s',prevFileBaseName)
                prevDate = getPrevSapUsersFile(prevFileBaseName)
                if (prevDate != inCurrDate):
                    prevFile = prevFileBaseName+prevDate
                    logH.debug('Prev SAP Users file was %s', prevFile)
                    try:
                        prevDf = pd.read_table(prevFile, sep=fileSep, dtype = str)
                    except:
                        logH.debug('Could not read %s', prevFile)
                        raise 
                    try:
                        currDf = pd.read_table(currFile, sep=fileSep, dtype = str)
                    except:
                        logH.debug('Could not read %s', currFile)
                        raise
                    delDf = currDf.merge(prevDf,indicator = True, how='outer').loc[lambda x : x['_merge']=='right_only']
                    creUpdDf = currDf.merge(prevDf,indicator = True, how='outer').loc[lambda x : x['_merge']=='left_only']
                    try:
                        delDf.to_csv(delFile, index=False)
                    except:
                        logH.debug('Could not convert dataframe with deletes to CSV')
                        raise
                    try:
                        creUpdDf.to_csv(creUpdFile, index=False)
                    except:
                        logH.debug('Could not convert dataframe with updates to CSV')
                        raise
                    logH.debug('Removed with respect to previous file: %s', delFile)
                    logH.debug('Ins/Upd with respect to previous file: %s', creUpdFile)
                    if (os.path.exists(delFile)):
                        logH.debug('File with removals created %s', delFile)
                    if (os.path.exists(creUpdFile)):
                        logH.debug('File with creates/updates created %s', creUpdFile)
                    #deltaDf = currDf.merge(prevDf,indicator = True, how='left').loc[lambda x : x['_merge']!='both']
                    #deltaDf = pd.concat([prevDf, currDf]).drop_duplicates(keep=False)
                else:
                    logH.debug('No previous Sap Users File found')
            else:
                logH.debug('Current File does not contain enough lines (%d) - sanity check failed', nbrOfLines)
        else:
            logH.debug('No file to work with : %s', currFile)

def getSapUsersFile(inConfigFile, logName = ''):
    #get loghandler
    logH        = logging.getLogger(logName)
    #read options from configurationfile
    logH.debug('Read Configuration File %s', inConfigFile)
    opts        = gu.readConfigFile(inConfigFile)
    #Protocol
    protocol    = opts.get('Protocol','protocol')
    if (protocol == 'SFTP'):
        #SAPSFtpHost
        hostName    = opts.get('SAPSFtpHost','hostName')
        portNumber  = opts.getint('SAPSFtpHost','portNumber')
        userName    = opts.get('SAPSFtpHost','userName')
        keyFile     = opts.get('SAPSFtpHost','keyFile')
    elif (protocol == 'FTP' or protocol == 'FTPTLS'):
        #SAPFtpHost
        hostName    = opts.get('SAPFtpHost','hostName')
        portNumber  = opts.getint('SAPFtpHost','portNumber')
        userName    = opts.get('SAPFtpHost','userName')
        password    = opts.get('SAPFtpHost','password')
    #SAPUserFile
    remotePath  = opts.get('SAPUsersFile','remotePath')
    remoteFile  = opts.get('SAPUsersFile','remoteFile')
    localPath   = opts.get('SAPUsersFile','localPath')
    fileSep     = opts.get('SAPUsersFile','fileSep')
    fileSuffixSep = opts.get('SAPUsersFile','fileSuffixSep')
    delFileBaseName = opts.get('SAPUsersFile','delFileBaseName')
    creUpdFileBaseName = opts.get('SAPUsersFile','creUpdFileBaseName')
    generateOrcidFile = opts.get('SAPUsersFile','generateOrcidFile', fallback = True)
    orcidFileBaseName = opts.get('SAPUsersFile','orcidFileBaseName')
    currDate    = gu.get_yyyymmdd()
    currFileBaseName = localPath+remoteFile+fileSuffixSep
    currFile    = currFileBaseName+currDate
    orcidFile   = orcidFileBaseName+currDate
    delFile     = delFileBaseName+fileSuffixSep+currDate
    creUpdFile  = creUpdFileBaseName+fileSuffixSep+currDate
    logH.debug('%s %s to %s',protocol, remotePath+remoteFile, currFile)
    
    try:
        #ftp the file
        if (protocol == 'FTP'):
            gu.ftpGetFile(hostName, portNumber, userName, password, remotePath, remoteFile, currFile, logName)
        elif (protocol == 'FTPTLS'):
            gu.ftpTlsGetFile(hostName, portNumber, userName, password, remotePath, remoteFile, currFile, logName)        
        elif (protocol == 'SFTP'):
            gu.sftpGetFile(hostName, userName, keyFile, remotePath, remoteFile, currFile, logName)
            
        if (generateOrcidFile):
            logH.debug('generating an Orcid file %s', orcidFile)
            genOrcidFile(currFile, orcidFile, fileSep, logName)
    
        #get additions/updates and removed users in 2 separate files
        try:
            diffFile(currFile, currFileBaseName, creUpdFile, delFile, currDate, fileSep, logName) 
        except:
            logH.debug('problem with creating files with deletes and/or updates')
            raise
        
    except eu.fileTransferError:
        logH.error('Could not transfer file %s over %s from host %s', remotePath+remoteFile, protocol, hostName)
        raise
    
        
    
    
