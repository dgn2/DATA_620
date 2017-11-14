# -*- coding: utf-8 -*-
"""
Created on Sat Nov 04 15:53:49 2017

@author: Derek G Nokes (dgn2)
"""

import pandas
import numpy
import requests
import datetime
import MySQLdb
import mysqlDatabaseToolbox
from bs4 import BeautifulSoup
import pandas.io.sql as sql

# https://www.bloomberg.com/quote/IBM:US




# https://www.bloomberg.com/quote/0062761Q:US


def fetchCompanyDescription(tickerBB,compositeExchangeCodeBB):
    # build URL
    url='https://www.bloomberg.com/quote/'+tickerBB+':'+compositeExchangeCodeBB
    # start a session
    s = requests.session()
    # set parameters
    parameters = {'siteEntryPassthrough': True}
    # get page
    response = s.get(url, params=parameters)
    # extract page
    soup = BeautifulSoup(response.text,"lxml")
    # extract h1 content
    h1=soup.findAll("h1")
    # extract instrument name
    instrumentNameBB=str(h1[2].text).strip()
    #
    # create dictionary to hold instrument classifications
    classificationsDictionary=dict()
    # add instrument name
    classificationsDictionary['instrumentNameBB']=instrumentNameBB
    # extract body    
    divs=soup.findAll('div')
    # iterate over each section in 'body'
    for div in divs:
        if 'profile__description' in str(div):
            #print(div)
            chunk=div
        
    companyDescription=str(chunk.text).strip()
            
    classificationsDictionary['companyDescription']=companyDescription
#    # extract sector
#    bicsSector=classificationsDictionary['bicsSector']
#    # extract industry
#    bicsIndustry=classificationsDictionary['bicsIndustry']
#    # extract sub-industry
#    bicsSubIndustry=classificationsDictionary['bicsSubIndustry']
#    print(str(tickerBB)+"|"+str(instrumentNameBB)+"|"+str(bicsSector)+"|"+str(bicsIndustry)+"|"+str(bicsSubIndustry))

    return classificationsDictionary

def fetchInstrumentCharacteristics(tickerBB,compositeExchangeCodeBB):
    # build URL
    url='https://www.bloomberg.com/quote/'+tickerBB+':'+compositeExchangeCodeBB
    # start a session
    s = requests.session()
    # set parameters
    parameters = {'siteEntryPassthrough': True}
    # get page
    response = s.get(url, params=parameters)
    # extract page
    soup = BeautifulSoup(response.text,"lxml")
    # extract h1 content
    h1=soup.findAll("h1")
    # extract instrument name
    instrumentNameBB=str(h1[2].text).strip()
    #
    # create dictionary to hold instrument classifications
    classificationsDictionary=dict()
    # add instrument name
    classificationsDictionary['instrumentNameBB']=instrumentNameBB
    # extract body    
    body=soup.findAll('body')
    # iterate over each section in 'body'
    for line in body:
        # find line with 'bic'
        if 'bic' in str(line):
            # split on comma
            lines=str(line).split(',')
            # iterate over each chunk
            for chunk in lines:
                # if 'bic' in chunk
                if 'bic' in str(chunk):
                    # split field and value
                    classifications=chunk.split(':')
                    # remove quotes from field name
                    field=classifications[0].replace('"','')
                    # remove quotes from value
                    value=classifications[1].replace('"','')
                    # add field and value to classification dictionary
                    classificationsDictionary[str(field)]=str(value)
              
    # extract body    
    divs=soup.findAll('div')
    # iterate over each section in 'body'
    for div in divs:
        if 'profile__description' in str(div):
            #print(div)
            chunk=div
        
    companyDescription=str(chunk.text).strip()
            
    classificationsDictionary['companyDescription']=companyDescription                

#    # extract sector
#    bicsSector=classificationsDictionary['bicsSector']
#    # extract industry
#    bicsIndustry=classificationsDictionary['bicsIndustry']
#    # extract sub-industry
#    bicsSubIndustry=classificationsDictionary['bicsSubIndustry']
#    print(str(tickerBB)+"|"+str(instrumentNameBB)+"|"+str(bicsSector)+"|"+str(bicsIndustry)+"|"+str(bicsSubIndustry))

    return classificationsDictionary

def iterateFetchInstrumentCharacteristics(outputDirectory,errorDirectory,tickerListBB):
    # find current datetime (timestamp)
    dateTime=datetime.datetime.now()
    # create instrument output file name
    outputFileName='instrumentMaster-'+dateTime.strftime('%Y%m%d_%H%M%S')
    # create error output file name
    errorFileName='instrumentMasterError-'+dateTime.strftime('%Y%m%d_%H%M%S')
    # open output file handle
    outputFileHandle=open(outputDirectory+outputFileName,'w')
    # open error file handle
    errorFileHandle=open(errorDirectory+errorFileName,'w')    
    
    # create dictionary to hold errors
    errorDictionary=dict()    
    # create dictionary to hold instrument characteristics
    instrumentDictionary=dict()
    # iterate over each instrument
    for instrumentTicker in tickerListBB:
        # extract ticker and composite exchange code
        tickerBB,compositeExchangeCodeBB=instrumentTicker.split()
        
        try:
            # fetch instrument characteristics
            classificationsDictionary=fetchInstrumentCharacteristics(tickerBB,compositeExchangeCodeBB)
            # extract instrument name
            instrumentNameBB=classificationsDictionary['instrumentNameBB']
            #
            companyDescription=classificationsDictionary['companyDescription']
            # extract sector
            bicsSector=classificationsDictionary['bicsSector']
            # extract industry
            bicsIndustry=classificationsDictionary['bicsIndustry']
            # extract sub-industry
            bicsSubIndustry=classificationsDictionary['bicsSubIndustry']
            # write to output file
            outputFileHandle.write(str(tickerBB)+"|"+str(compositeExchangeCodeBB)+"|"+str(companyDescription)+"|"+str(instrumentNameBB)+"|"+str(bicsSector)+"|"+str(bicsIndustry)+"|"+str(bicsSubIndustry)+"\n")
            # add dictionary 
            instrumentDictionary[tickerBB]=classificationsDictionary
        except:    
            print('==>Could not fetch:'+ str(instrumentTicker))
            #
            errorFileHandle.write(str(tickerBB)+"|"+str(compositeExchangeCodeBB)+"\n")
            # add to dictionary
            errorDictionary['tickerBB']=tickerBB
            
    
    # close output file handle
    outputFileHandle.close()
    # close error file handle
    errorFileHandle.close()
    
    return instrumentDictionary,errorDictionary

# load data to database



#tickerBB='AMZN'
#compositeExchangeCodeBB='US'
#
#tickerListBB=list()
#tickerListBB.append('NVDA US')
#tickerListBB.append('AMZN US')
#tickerListBB.append('IBM US')
#tickerListBB.append('RY CN')
#tickerListBB.append('0062761Q US')

# CONNECT TO DB
# data server database parameters
dbHost='localhost'
dbPort=3306
dbUser='root'
dbPassword='password'
databaseName='global_monitoring'

## connect to the 'global_monitoring' MySQL database 
dbHandle=mysqlDatabaseToolbox.dbConnect(dbHost,dbPort,dbUser,dbPassword,databaseName)


outputDirectory="D:/marketData/global_monitoring/instrument_universe/index_member/Russell_3000/instrument_master/"

errorDirectory="D:/marketData/global_monitoring/instrument_universe/index_member/Russell_3000/instrument_master/"


query="SELECT DISTINCT index_member_ticker_bb FROM global_monitoring.bb_index_members ORDER BY index_member_ticker_bb;"

instrumentDf=sql.read_sql(query,dbHandle)

f=lambda x : x.replace(' UN',' US').replace(' UQ',' US').replace(' UW',' US').replace(' UA',' US').replace(' UU',' US').replace(' UR',' US').replace(' UP',' US').replace(' UV',' US')



instrumentDf['tickerBB']=instrumentDf['index_member_ticker_bb'].apply(f)

instrumentDf.drop_duplicates(subset=['tickerBB'],inplace=True)

tickerListBB=instrumentDf['tickerBB'].values.tolist()

instrumentDictionary,errorDictionary=iterateFetchInstrumentCharacteristics(outputDirectory,errorDirectory,tickerListBB)

# disconnect from MySQL
mysqlDatabaseToolbox.dbDisconnect(dbHandle)