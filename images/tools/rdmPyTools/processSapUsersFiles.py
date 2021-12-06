# -*- coding: utf-8 -*-
"""
Created on Thu May  6 13:15:07 2021

@author: PieterDV
"""

import logging

import readSapUsers as rsu
import generalUtils as gu
import errorUtils as eu

def handleFile(inputFile, configFile, logName = ''):
    logHLocal        = logging.getLogger(logName)
    try:
        logHLocal.info('processSapUsersFiles : handleFile %s, configFile %s, task %s', inputFile, configFile, logName)
        rsu.readSapFile(inputFile, configFile, logName)
    except eu.apiError:
        logHLocal.error('Api Error')
    except Exception as e:
        logHLocal.error(e.__class__.__name__+" occurred.")

def processSapUsersFiles(inConfigFile, logName = ''):
    #get loghandler
    logH        = logging.getLogger(logName)
    #read options from configurationfile
    logH.debug('processSapUsersFiles: Read Configuration File %s', inConfigFile)
    opts        = gu.readConfigFile(inConfigFile)
    logH.debug('processSapUsersFiles: Read (after) Configuration File %s', inConfigFile)
    #SAPUsersFile
    fileSep             = opts.get('SAPUsersFiles','fileSep')
    fileSuffixSep       = opts.get('SAPUsersFiles','fileSuffixSep')
    delFileBaseName     = opts.get('SAPUsersFiles','delFileBaseName')
    creUpdFileBaseName  = opts.get('SAPUsersFiles','creUpdFileBaseName')
    delHandledDir       = opts.get('SAPUsersFiles','delHandledDir')
    delErrorDir         = opts.get('SAPUsersFiles','delErrorDir')
    creUpdHandledDir    = opts.get('SAPUsersFiles','creUpdHandledDir')
    creUpdErrorDir      = opts.get('SAPUsersFiles','creUpdErrorDir')
    delFileConfigFile   = opts.get('SAPUsersFiles','delFileConfigFile')
    creUpdFileConfigFile= opts.get('SAPUsersFiles','creUpdFileConfigFile')
    handleDeletes       = opts.getboolean('SAPUsersFiles','handleDeletes', fallback = False)
    currDate            = gu.get_yyyymmdd()
    delFileGlob         = delFileBaseName+fileSuffixSep
    creUpdFileGlob      = creUpdFileBaseName+fileSuffixSep
    delFiles            = gu.dirByDate(delFileGlob)
    creUpdFiles         = gu.dirByDate(creUpdFileGlob)
    
    checkDirs = [creUpdHandledDir, creUpdErrorDir, delHandledDir, delErrorDir]
    for cD in checkDirs:
        if (not(gu.isDir(cD))):
            raise eu.configParamError('processSapUsersFiles: directory check %s does not exist', cD)
        else:
            logH.info('processSapUsersFiles: directory %s checked', cD)
            
    checkFiles = [delFileConfigFile, creUpdFileConfigFile]
    for cF in checkFiles:
        if (not(gu.isFile(cF))):
            raise eu.configParamError('processSapUsersFiles: file check %s does not exist', cD)
        else:
            logH.info('processSapUsersFiles: file %s checked', cD)
    
    logH.info('processSapUsersFiles: %s, %s', delFileBaseName, creUpdFileBaseName)

    if (handleDeletes):
        #DEL    
        cnt = 0
        for dF in delFiles:
            cnt = cnt + 1
            logH.info('processSapUsersFiles: DelFile %d - %s',cnt,dF)
            #handle file
            try:
                handleFile(dF, delFileConfigFile, logName)
                #move afterwards
                gu.moveFile(dF, delHandledDir, logName)
            except Exception as e:
                #move afterwards
                logH.error('processSapUsersFiles : DelFile %s moved to Error directory', dF)
                gu.moveFile(dF, delErrorDir, logName)
        if (cnt > 0):
            logH.info('processSapUsersFiles: %d delFiles handled', cnt)
        else:
            logH.info('processSapUsersFiles: No delFiles to be handled')
    else:
        logH.info('processSapUsersFiles: not handling DelFiles - ini setting handleDeletes = False')
        
    #CRE/UPD    
    cnt = 0
    for cuF in creUpdFiles:
        cnt = cnt + 1
        logH.info('processSapUsersFiles: creUpdFile %d - %s',cnt,cuF)
        #handle file
        try:
            handleFile(cuF, creUpdFileConfigFile, logName)
            #move afterwards
            gu.moveFile(cuF, creUpdHandledDir, logName)
        except Exception as e:
            #move afterwards
            logH.error('processSapUsersFiles : creUpdFile %s moved to Error directory', cuF)
            gu.moveFile(cuF, creUpdErrorDir, logName)
    if (cnt > 0):
        logH.info('processSapUsersFiles: %d creUpdFiles handled', cnt)
    else:
        logH.info('processSapUsersFiles: No creUpdFiles to be handled')
        
  
    #get additions/updates and removed users in 2 separate files
    # try:
    #      diffFile(currFile, currFileBaseName, creUpdFile, delFile, currDate, fileSep, logName) 
    # except:
    #      logH.debug('problem with creating files with deletes and/or updates')
    #      raise
        
    
        
    
    
