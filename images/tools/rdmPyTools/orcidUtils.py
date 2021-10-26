# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 14:35:15 2021

@author: PieterDV
"""

import sys
import re 
import pandas as pd
import errorUtils as eu

def readOrcidFile(inFile, fileSep=','):
    #inFile  = 'c:/temp/rdm/out/Orcid20210603'
    outDict = pd.read_csv(inFile, sep=fileSep, dtype = str, index_col=1, squeeze=True).to_dict()
    return(outDict)

def generateCheckDigit(baseDigits):
    total = 0
    for i in range(0, len(baseDigits)):
        digit = int(baseDigits[i])
        total = (total + digit) * 2

    remainder = total % 11
    result = (12 - remainder) % 11
    if (result == 10):
        return("X")
    else:
        return(result)

def checkOrcid(inOrcid):
    try:
        strippedOrcid = re.sub(r'[- ]',r'',inOrcid)
        if (len(strippedOrcid)==16):
            orcidToCheck = strippedOrcid[0:15]
            orcidCheckDigit = strippedOrcid[15]
            orcidGenerated  = generateCheckDigit(orcidToCheck)
            if (orcidCheckDigit == str(orcidGenerated)):
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        raise eu.orcidError()
    
# #main
# oD = readOrcidFile('c:/temp/rdm/out/Orcid20210603')
# cnt = 1
# for k in oD.keys():
#         if (checkOrcid(k)):
#             #print(k+' is a valid Orcid')
#             cnt = cnt
#         else:
#             print(k+' invalid Orcid')
#         cnt = cnt + 1
    
   


  