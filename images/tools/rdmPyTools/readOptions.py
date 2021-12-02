# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 13:37:39 2021

@author: PieterDV
"""
import sys, getopt
import logging
import os.path

import readSapUsers as rsu
import processSapUsersFiles as psuf
import getSapUsersFile as gsu
import errorUtils as eu
import dataVerse2Elements as dv2el

def check_file(checkF):
    if (checkF == ''):
        print('Filename not specified')
        logging.error('FileName was not specified')
        return False
    else:
        if (not os.path.isfile(checkF)):
            print('File % does not exist', checkF)
            logging.error('File % does not exist', checkF)
            return False
        else:
            return True

def crLogger(logF, logName = '', logL = logging.DEBUG):
    logging.root.setLevel(logging.NOTSET)    
    # create logger
    logger = logging.getLogger(logName)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

    fh     = logging.FileHandler(filename=logF, encoding='utf-8', mode="w")
    fh.setFormatter(formatter)
    fh.setLevel(logL)
    
    errF   = logF+".err"
    eh     = logging.FileHandler(filename=errF, encoding='utf-8', mode="w")
    eh.setFormatter(logging.Formatter('%(message)s'))
    eh.setLevel(logging.ERROR)
    
    # create console handler and set level
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    
    # add handlers to logger
    logger.addHandler(ch)    
    logger.addHandler(fh)
    logger.addHandler(eh)

    return(logger)
    
def closeLogger(inLog):
    handlers = inLog.handlers[:]
    for handler in handlers:
        handler.close()
        inLog.removeHandler(handler)    
    
def main(argv):
  
    configfile = ''
    inputfile  = ''
    outputfile = ''
    logfile    = ''
    logLevel   = ''
    task       = ''
    try:
        opts, args = getopt.getopt(argv,"ht:i:c:o:l:L:",["task=","ifile=","cfile=","ofile=","lfile="])
    except getopt.GetoptError:
        print('readOptions.py -t <task> -i <inputfile> -c <configfile> -o <outputfile> -l <logfile> -L <logLevel>')
        sys.exit(2)
    for opt, arg in opts:
          if opt == '-h':
              print('readOptions.py -t <task> -i <inputfile> -c <configfile> -o <outputfile> -l <logfile> -L <logLevel>')
              sys.exit()
          elif opt in ("-t", "--task"):
              task = arg
          elif opt in ("-i", "--ifile"):
              inputfile = arg
          elif opt in ("-o", "--ofile"):
              outputfile = arg
          elif opt in ("-l", "--lfile"):
              logfile = arg
          elif opt in ("-c", "--cfile"):
              configfile = arg
    print("task is ", task)
    print('Input file is ', inputfile)
    print('Output file is ', outputfile)
    print('Log file is ', logfile)
    print('Config file is ', configfile)
    if (task == ''):
        print('Task option must be specified')
        print('Exiting...')
        sys.exit()
    else:
        task = task.upper()

    if (logfile != ''):
        if (logLevel == ''):
            logLevel = logging.DEBUG
        else: #DEBUG/INFO/ERROR/CRITICAL/WARNING/NOTSET 
            logLevel = logLevel.upper()
    else:
        print('LogFile must be specifried...')
        print('Exiting...')
        sys.exit()

    logger = crLogger(logfile, task, logLevel)

    if (task == 'SAPUSERLOAD'):
        if (not (check_file(inputfile))):
            logger.error('InputFile (%s) was not correctly specified for task %s', inputfile, task)
            sys.exit()
        if (not (check_file(configfile))):
            logger.error('ConfigFile (%s) was not correctly specified for task %s', configfile, task)
            sys.exit()
            
        logger.debug('Starting task %s',task)
        #print('Starting task ',task)
        try:
            rsu.readSapFile(inputfile, configfile, task)
        except eu.apiError:
            logger.error('Api Error')
        except Exception as e:
            logger.error(e.__class__.__name__+" occurred.")
    elif (task == 'PROCESSSAPUSERSFILES'):
        if (not (check_file(configfile))):
            logger.error('ConfigFile (%s) was not correctly specified for task %s', configfile, task)
            sys.exit()
            
        logger.debug('Starting task %s',task)
        #print('Starting task ',task)
        try:
            psuf.processSapUsersFiles(configfile, task)
        except Exception as e:
            logger.error(e.__class__.__name__+" occurred.")
    elif (task == 'GETSAPUSERSFILE'):
        if (not (check_file(configfile))):
            logger.error('ConfigFile (%s) was not correctly specified for task %s', configfile, task)
            sys.exit()
            
        logger.debug('Starting task %s',task)
        #print('Starting task ',task)
        try:
            gsu.getSapUsersFile(configfile, task)
        except eu.fileTransferError:
            logger.error("File transfer Error")
        except Exception as e:
            logger.error(e.__class__.__name__+" occurred.")
    elif (task == 'DATAVERSE2ELEMENTS'):
        if (not (check_file(configfile))):
            logger.error('ConfigFile (%s) was not correctly specified for task %s', configfile, task)
            sys.exit()
            
        logger.debug('Starting task %s',task)
        try: 
            dv2el.dataVerse2Elements(configfile, task)
        except Exception as e:
            logger.error(e.__class__.__name__+" occurred.")

        
    closeLogger(logger)
        
if __name__ == "__main__":
   main(sys.argv[1:])