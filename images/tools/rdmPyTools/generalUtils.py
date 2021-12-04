# -*- coding: utf-8 -*-
"""
Created on Thu May  6 13:40:16 2021

@author: PieterDV
"""
import os
import re
import sys
import configparser
from ftplib import FTP, FTP_TLS
from datetime import date, timedelta
import glob
import time
import pysftp
import logging
import errorUtils as eu
from pathlib import Path   
import shutil

def isDir(inDir):
    return(os.path.isdir(inDir))

def isFile(inFile):
    return(os.path.isfile(inFile))

def getDirFromFileName(inFileName):
    dirname = os.path.dirname(inFileName)
    return(dirname)

def readFile2String(inFile):
    try:
        myFile = open(inFile,"r")
        data   = ""
        lines  = myFile.readlines()
        for line in lines:
            data = data + line.strip();
        return(data)
    except Exception:
        raise eu.readFile2StringError
        
def dirMostRecentFile(inGlob):
    try:
        filesFound = dirByDate(inGlob)
        if (filesFound is not None):
            return(filesFound[-1])
        else:
            return(None)
    except:
        return(None)

def dirByDate(inDir):        
    try:
        # Get list of all files only in the given directory
        list_of_files = filter( os.path.isfile,glob.glob(inDir + '*') )
        # Sort list of files based on last modification time in ascending order
        list_of_files = sorted( list_of_files, key = os.path.getmtime)
        return(list_of_files)
    except:
        return(None)

def moveFile(file2Move, toDir, logName):
    logH        = logging.getLogger(logName)
    file2MoveName = Path(file2Move).name
    try:
        os.remove(toDir+file2MoveName)
    except OSError:
        pass
    try:
        shutil.move(file2Move, toDir)
    except Exception as e:
        logH.error(e.__class__.__name__+" occurred.")
        logH.error('Error Moving file '+file2Move+' to '+toDir+', extracted filename = '+file2MoveName)
        raise eu.moveFileError

def fileNbrOfLines (inFile):
    file = open(inFile, "r", encoding='utf-8')
    line_count = 0
    for line in file:
        if (line != os.linesep):
            line_count += 1
    file.close()
    return(line_count)

def get_yyyymmddOffset(offset):
    today = date.today() + timedelta(offset)
    # dd/mm/YY
    dtstr = today.strftime("%Y%m%d")
    return(dtstr)

def get_yyyymmdd():
    return(get_yyyymmddOffset(0))

def readConfigFile(inConfigFile):
   parser = configparser.ConfigParser()
   parser.read(inConfigFile)
   return(parser)

def ftpGetFile(inHost, inPort, inUser, inPwd, inRemotePath, inRemoteFile, inLocalFile, logName = ''):
    #get loghandler
    logH        = logging.getLogger(logName)
    try:
        ftp = FTP(inHost, inPort)
        ftp.login(user=inUser, passwd = inPwd)
        ftp.cwd(inRemotePath)
        ftp.retrbinary("RETR " + inRemoteFile, open(inLocalFile, 'wb').write)
        ftp.quit()
    except Exception as e:
        logH.error(e.__class__.__name__+" occurred.")
        raise eu.fileTransferError
    
def ftpTlsGetFile(inHost, inPort, inUser, inPwd, inRemotePath, inRemoteFile, inLocalFile, logName = ''):
    #get loghandler
    logH        = logging.getLogger(logName)
    try:
        ftps = FTP_TLS(inHost, inPort, timeout=80)
        ftps.set_debuglevel(0)
        ftps.set_pasv(False)
        ftps.connect(port=inPort, timeout=80)
        ftps.login(inUser,inPwd)
        ftps.prot_p()
        ftps.ccc()    
        localFile = inLocalFile
        logH.debug('Opening local file ' + localFile)
        myfile = open(localFile, 'wb')
        ftps.retrbinary('RETR %s' % inRemotePath+inRemoteFile, myfile.write)
        ftps.close()    
    except Exception as e:
        logH.error(e.__class__.__name__+" occurred.")
        raise eu.fileTransferError
    
def sftpGetFile(inHost, inUser, inKeyFile, inRemotePath, inRemoteFile, inLocalFile, logName = ''):
    #get loghandler
    logH        = logging.getLogger(logName)
    logH.debug('host=%s, user=%s, keyfile=%s' % (inHost, inUser, inKeyFile))
    try:
        srv = pysftp.Connection(host=inHost, username=inUser, private_key=inKeyFile)
        if (srv.exists(inRemotePath+inRemoteFile)):
            srv.get(inRemotePath+inRemoteFile, inLocalFile)
        srv.close()
    except Exception as e:
        logH.error(e.__class__.__name__+" occurred.")
        raise eu.fileTransferError

def splitName(inString, logName = ''):
    logH        = logging.getLogger(logName)
    try:
        namesplit   = inString.split(", ", 1)
        lastname    = namesplit[0]
        if (len(namesplit)>1):
            firstname = namesplit[1]
            initials  = firstname[0]
        else:
            firstname = ''
            initials  = ''
        nameDict = {'lastname': lastname,
                    'firstname': firstname,
                    'initials': initials}
        logH.info('Name '+inString+' split into '+nameDict['lastname']+','+nameDict['firstname']+','+nameDict['initials'])
        return(nameDict)
    except Exception as e:
        logH.info(e.__class__.__name__+" occured.  Returning: "+inString+" as lastname")
        nameDict = {'lastname': inString,
                    'firstname': '',
                    'initials': ''}
        return(nameDict)

def parseDOI(inDOI, logName = ''):
    logH   = logging.getLogger(logName)
    try:
        tmpDOI = re.findall(r"[^/]+/[^/]+$", inDOI)
        outDOI = re.sub(r"\s*[dD][oO][iI]\s*:\s*","",tmpDOI[0])
        return(outDOI)
    except Exception as e:
        logH.info(e.__class__.__name__+" occured.  No valid DOI: "+inDOI)
        raise eu.doiParseError

def parseHandle(inHandle, logName = ''):
    logH = logging.getLogger(logName)
    try:
        outHandle = tmpDOI = re.findall(r"[^/]+/[^/]+$", inHandle)
        return(outHandle[0])
    except Exception as e:
        logH.info(e.__class__.__name__+" occured.  No valid handle: "+inHandle)
        raise eu.handleParseError
        
    