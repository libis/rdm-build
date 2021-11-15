# -*- coding: utf-8 -*-
"""
Created on Thu May  6 13:15:07 2021

@author: PieterDV
"""
import os
import glob as gl
import sys
import pandas as pd
import numpy as np
import re

import logging
import math

import generalUtils as gu
import errorUtils as eu
import dataVerseDataSet2Elements as ds2el

def dataVerse2Elements(inConfigFile, logName = ''):
    #get loghandler
    logH        = logging.getLogger(logName)
    #read options from configurationfile
    logH.debug('Read Configuration File %s', inConfigFile)
    opts        = gu.readConfigFile(inConfigFile)
    #Directory
    inDir       = opts.get('datasets','inDir')
    #Protocol
    logH.debug('inDir set : %s',inDir)
    
    try:
        #from os import path

        logH.info('dataVerse2Elements : reading directory '+inDir)
        for dataSet in gl.glob(inDir+"*.json"):
            if (os.path.isfile(dataSet)):
                dataSetFileName = os.path.abspath(dataSet)
                logH.info('dataVerse2Elements : current File '+dataSetFileName)
                try:
                    ds2el.dataVerseDataSet2Elements(inConfigFile, dataSetFileName, logName)
                except Exception as e:
                    #logH.warning("Error dataVerse2Elements : %s calling dataVerseDataSet2Elements (%s,%s,%s)",e.__class_name, inConfigFile, dataSetFileName, logName)
                    logH.warning("Error dataVerse2Elements : calling dataVerseDataSet2Elements (%s,%s,%s)", inConfigFile, dataSetFileName, logName)

    except Exception as e:
        logH.error('Error dataVerse2Elements: %s',e.__class__.__name__)
        print(type(e).__name__,__file__,e.__traceback__.tb_lineno)
        logH.error('Error dataVerse2Elements: when going through '+inDir+' looking for json files')
        raise
