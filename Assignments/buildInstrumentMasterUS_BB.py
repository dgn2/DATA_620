# -*- coding: utf-8 -*-
"""
Created on Wed Nov 08 18:51:48 2017

@author: Derek G Nokes (dgn2)
"""
import json
import requests
import sys
import datetime
import pandas
import mysqlDatabaseToolbox
import MySQLdb

#==============================================================================
# 
#==============================================================================
# Example Call:
#
# Call:
# 
#
#------------------------------------------------------------------------------
def dbCreateInstrumentMasterTable(dbHandle,table):

    try:
        cursor = dbHandle.cursor()
        cursor.execute('CREATE TABLE '+str(table)+' (dbUpdateTimestamp TIMESTAMP, tickerBB VARCHAR(20) NOT NULL,compositeExchangeCodeBB VARCHAR(4) NOT NULL, companyDescription TEXT NOT NULL, instrumentNameBB VARCHAR(100) NOT NULL, bicsSector VARCHAR(40) NULL, bicsIndustry VARCHAR(60) NULL, bicsSubIndustry VARCHAR(60) NULL, PRIMARY KEY ( tickerBB,compositeExchangeCodeBB ) ) ENGINE=INNODB')
                   
    except MySQLdb.Error,e:
        print ("Error code:",e.args[0])
        print ("Error message:",e.args[1])

    return

#==============================================================================
# 
#==============================================================================
# Example Call:
#
# Call:
# 
#
#------------------------------------------------------------------------------
def dbBulkLoadInstrumentMasterTable(dbHandle,table,directoryName,fileName):
# 
    try:
        cursor = dbHandle.cursor()
        sql="LOAD DATA LOCAL INFILE '" + directoryName + fileName + "' REPLACE INTO TABLE "+str(table)+" FIELDS TERMINATED BY '|' LINES TERMINATED BY '\r\n' IGNORE 1 LINES (tickerBB, compositeExchangeCodeBB, companyDescription, instrumentNameBB, bicsSector, bicsIndustry, bicsSubIndustry);"
        #print(sql)
        cursor.execute(sql)
        dbHandle.commit()
    except MySQLdb.Error,e:
        print ("Error code:",e.args[0])
        print ("Error message:",e.args[1])
        dbHandle.rollback()

    return

#==============================================================================
# 
#==============================================================================
# Example Call:
#
# Call:
# 
#
#------------------------------------------------------------------------------
def dbCreateInstrumentMasterFIGITable(dbHandle,table):

    try:
        cursor = dbHandle.cursor()
        cursor.execute('CREATE TABLE '+str(table)+' (dbUpdateTimestamp TIMESTAMP, tickerBB VARCHAR(20) NOT NULL, compositeExchangeCodeBB VARCHAR(4) NOT NULL, companyDescription TEXT NOT NULL, instrumentNameBB VARCHAR(100) NOT NULL, bicsSector VARCHAR(40) NULL, bicsIndustry VARCHAR(60) NULL, bicsSubIndustry VARCHAR(60) NULL,	bbName VARCHAR(100) NOT NULL, bbTicker VARCHAR(20) NOT NULL, bbExchCode VARCHAR(4) NULL, bbCompositeFIGI VARCHAR(24) NOT NULL, bbFIGI VARCHAR(24) NOT NULL, bbMarketSector VARCHAR(12) NULL, bbSecurityDescription VARCHAR(16) NULL, bbSecurityType VARCHAR(24) NULL, bbSecurityType2 VARCHAR(40) NULL,	bbShareClassFIGI VARCHAR(24) NULL, bbUniqueID VARCHAR(40) NULL, PRIMARY KEY ( tickerBB,compositeExchangeCodeBB,bbCompositeFIGI ) ) ENGINE=INNODB')
                   
    except MySQLdb.Error,e:
        print ("Error code:",e.args[0])
        print ("Error message:",e.args[1])

    return

#==============================================================================
# 
#==============================================================================
# Example Call:
#
# Call:
# 
#
#------------------------------------------------------------------------------
def dbBulkLoadInstrumentMasterFIGITable(dbHandle,table,directoryName,fileName):
# 
    try:
        cursor = dbHandle.cursor()
        sql="LOAD DATA LOCAL INFILE '" + directoryName + fileName + "' REPLACE INTO TABLE "+str(table)+" FIELDS TERMINATED BY '|' LINES TERMINATED BY '\r\n' IGNORE 1 LINES (tickerBB, compositeExchangeCodeBB, companyDescription, instrumentNameBB, bicsSector, bicsIndustry, bicsSubIndustry, bbName, bbTicker, bbExchCode, bbCompositeFIGI, bbFIGI, bbMarketSector, bbSecurityDescription, bbSecurityType, bbSecurityType2, bbShareClassFIGI, bbUniqueID);"
        #print(sql)
        cursor.execute(sql)
        dbHandle.commit()
    except MySQLdb.Error,e:
        print ("Error code:",e.args[0])
        print ("Error message:",e.args[1])
        dbHandle.rollback()

    return


openfigi_url = 'https://api.openfigi.com/v1/mapping'
openfigi_apikey = 'db87e748-3ac5-44e4-af7a-c285d54254dc'  # Put API Key here
openfigi_headers = {'Content-Type': 'text/json'}

if openfigi_apikey:
    openfigi_headers['X-OPENFIGI-APIKEY'] = openfigi_apikey

def map_jobs(jobs):
    '''
    Send an collection of mapping jobs to the API in order to obtain the
    associated FIGI(s).

    Parameters
    ----------
    jobs : list(dict)
        A list of dicts that conform to the OpenFIGI API request structure. See
        https://www.openfigi.com/api#request-format for more information. Note
        rate-limiting requirements when considering length of `jobs`.

    Returns
    -------
    list(dict)
        One dict per item in `jobs` list that conform to the OpenFIGI API
        response structure.  See https://www.openfigi.com/api#response-fomats
        for more information.
    '''
    too_many_mapping_jobs = len(jobs) > (100 if openfigi_apikey else 10)
    assert not too_many_mapping_jobs, 'Too many mapping jobs'
    response = requests.post(url=openfigi_url, headers=openfigi_headers,
                             data=json.dumps(jobs))
    if response.status_code != 200:
        print(response.status_code)
        sys.exit(1)
    return response.json()


def pretty_dict(d):
    '''
    Format a dict for `print`ing.

    Parameters
    ----------
    d : dict
        The dict to format

    Returns
    -------
    string
        A "pretty" string represention of `d`.
    '''
    return '|'.join(['%s=%s' % (k, v) for k, v in d.iteritems() if v])


def job_results_handler(jobs, job_results,master,outputFileHandle):
    '''
    Handle the `map_jobs` results.  See `map_jobs` definition for more info.

    Parameters
    ----------
    jobs : list(dict)
        The original list of mapping jobs to perform.
    job_results : list(dict)
        The results of the mapping job.

    Returns
    -------
        None
    '''
        
    for job, result in zip(jobs, job_results):

        instrumentTicker=job['idValue']

        try:
            nResults=len(result['data'])
            #print(nResults)
            
            for i in range(0,nResults):

                instrumentDictionary=result['data'][i]
                #
                bbName=instrumentDictionary['name']
                bbTicker=instrumentDictionary['ticker']
                bbExchCode=instrumentDictionary['exchCode']
                bbCompositeFIGI=instrumentDictionary['compositeFIGI']
                bbFIGI=instrumentDictionary['figi']
                bbMarketSector=instrumentDictionary['marketSector']
                bbSecurityDescription=instrumentDictionary['securityDescription']
                bbSecurityType=instrumentDictionary['securityType']
                bbSecurityType2=instrumentDictionary['securityType2']
                bbShareClassFIGI=instrumentDictionary['shareClassFIGI']
                bbUniqueID=instrumentDictionary['uniqueID']
                
                outputList=[master[instrumentTicker],bbName,bbTicker,bbExchCode,bbCompositeFIGI,
                    bbFIGI,bbMarketSector,bbSecurityDescription,bbSecurityType,bbSecurityType2,
                    bbShareClassFIGI,bbUniqueID]
                output='|'.join(outputList)+'\n'
                #output=master[instrumentTicker]+'|'+bbName+'|'+bbTicker+'|'+bbExchCode+'|'+bbCompositeFIGI+'|'+bbFIGI+'|'+bbMarketSector+'|'+bbSecurityDescription+'|'+bbSecurityType+'|'+bbSecurityType2+'|'+bbShareClassFIGI+'|'+bbUniqueID+'\n'        
                outputFileHandle.write(output)
        except:
            pass

    return

def mapIndexMember2OpenFIGI(dbHandle,table,outputDirectory):
    # determine effective datetime
    effectiveDateTime=datetime.datetime.now()
    # define output file name
    outputFileName='instrument_master_figi-'+effectiveDateTime.strftime('%Y%m%d_%H%M%S')
    # open output file handle
    outputFileHandle=open(outputDirectory+outputFileName,'w')
    # define header
    header="tickerBB|compositeExchangeCodeBB|companyDescription|instrumentNameBB|bicsSector|bicsIndustry|bicsSubIndustry|bbName|bbTicker|bbExchCode|bbCompositeFIGI|bbFIGI|bbMarketSector|bbSecurityDescription|bbSecurityType|bbSecurityType2|bbShareClassFIGI|bbUniqueID\n"
    # write header
    outputFileHandle.write(header)
    # get database cursor
    cursor = dbHandle.cursor()
    # define SQL query
    query="SELECT tickerBB,compositeExchangeCodeBB,companyDescription,instrumentNameBB,bicsSector,bicsIndustry,bicsSubIndustry FROM "+str(table)+";"
    # define row limit (set by Bloomberg)
    rowLimit=100
    # exectute query, return number of rows
    nRows = cursor.execute(query)
    # while there are records
    while True:
        # fetch rowLimit number of records
        limitedRows = cursor.fetchmany(rowLimit)
        # find number of rows
        n=len(limitedRows)
        # if empty
        if limitedRows == ():
            # stop
            break
        # if not empty
        else:
            # define dictionary for storing jobs
            jobs=list()
            # define dictionary for storing master data
            master=dict()
            # iterate over each record
            for i in range(0,n):
                # extract the record into line
                line=limitedRows[i]
                # convert to pipe-delimited string
                lineString='|'.join(line)
                # print the line string
                print(lineString)
                # store job for line
                jobs.append({'idType': 'TICKER', 'idValue': str(line[0]),'exchCode': 'US'})
                # line string
                master[line[0]]=lineString
                                    
            # map jobs into results
            job_results = map_jobs(jobs)
            # handle the job results
            job_results_handler(jobs, job_results, master,outputFileHandle)
        
    # close output file handle
    outputFileHandle.close()
    
    # return output file name
    return outputFileName,nRows


# CONNECT TO DB
# data server database parameters
dbHost='localhost'
dbPort=3306
dbUser='root'
dbPassword='password'
databaseName='global_monitoring'

## connect to the 'global_monitoring' MySQL database 
dbHandle=mysqlDatabaseToolbox.dbConnect(dbHost,dbPort,dbUser,dbPassword,
    databaseName)

# define input directory
inputDirectory='D:/marketData/global_monitoring/instrument_universe/index_member/instrument_master/raw/'
# define output directory
outputDirectory='D:/marketData/global_monitoring/instrument_universe/index_member/instrument_master/preprocess/'
# define input file name
inputFileName='instrumentMaster-20171107_232325'
# define instrument master table name
instrument_master_table='bb_instrument_master'
# define FIGI instrument master table name
instrument_figi_master_table='bb_figi_instrument_master'
# define output file name
outputFileName=instrument_master_table

# define output column names
columnNames=['tickerBB','compositeExchangeCodeBB','companyDescription',
    'instrumentNameBB','bicsSector','bicsIndustry','bicsSubIndustry']
# read instrument master
instrumentMaster=pandas.read_csv(inputDirectory+inputFileName,sep='|',
    header=None,names=columnNames,keep_default_na=False)
# write instrument master with header
instrumentMaster.to_csv(outputDirectory+outputFileName,sep='|',index=False)
# create the database table
if not mysqlDatabaseToolbox.doesTableExist(dbHandle,instrument_master_table):
    # create table
    dbCreateInstrumentMasterTable(dbHandle,instrument_master_table)

# create the database table
if not mysqlDatabaseToolbox.doesTableExist(dbHandle,instrument_figi_master_table):
    # create table
    dbCreateInstrumentMasterFIGITable(dbHandle,instrument_figi_master_table)

# bulk load table
dbBulkLoadInstrumentMasterTable(dbHandle,instrument_master_table,
    outputDirectory,outputFileName)

# map instrument master to FIGI
outputFMapileName,nRows=mapIndexMember2OpenFIGI(dbHandle,instrument_master_table,
    outputDirectory)

# bulk load table
dbBulkLoadInstrumentMasterFIGITable(dbHandle,instrument_figi_master_table,
    outputDirectory,outputFMapileName)

# disconnect from MySQL
mysqlDatabaseToolbox.dbDisconnect(dbHandle)