import mysqlDatabaseToolbox
import MySQLdb

import pandas as pd
import pandas.io.sql as sql

import urllib2
from bs4 import BeautifulSoup

import datetime

#==========================================================================================================================================================
# dbCreateSP500ConstituentTable()
#==========================================================================================================================================================
# Example Call:
#
# Call:
# dbCreateSP500ConstituentTable(dbHandle)
#
#-------------------------------------------------------------------------------
def dbCreateSP500ConstituentBySectorTable(dbHandle):

    try:
        cursor = dbHandle.cursor()
        cursor.execute('CREATE TABLE sp500_constituents_by_sector (dbUpdateTimestamp TIMESTAMP, instrumentTicker VARCHAR(30) NOT NULL, instrumentName VARCHAR(60) NOT NULL, sectorGICS VARCHAR(40) NOT NULL, subIndustryGICS VARCHAR(60) NOT NULL, CIK VARCHAR(20) NOT NULL, PRIMARY KEY ( instrumentTicker,sectorGICS,subIndustryGICS,CIK ) ) ENGINE=INNODB')
                   
    except MySQLdb.Error,e:
        print ("Error code:",e.args[0])
        print ("Error message:",e.args[1])

    return

#==========================================================================================================================================================
# dbBulkLoadSP500ConstituentTable
#==========================================================================================================================================================
# Example Call:
#
# Call:
# dbBulkLoadSP500ConstituentTable(dbHandle,directoryName,fileName)
#
#----------------------------------------------------------------------------------------------------------------------------------------------------------
def dbBulkLoadSP500ConstituentBySectorTable(dbHandle,directoryName,fileName):
# instrumentName,instrumentTicker,sectorName,sectorId,industryName
    try:
        cursor = dbHandle.cursor()
        sql="LOAD DATA LOCAL INFILE '" + directoryName + fileName + "' REPLACE INTO TABLE sp500_constituents_by_sector FIELDS TERMINATED BY '|' LINES TERMINATED BY '\r\n' IGNORE 1 LINES (instrumentTicker,instrumentName,sectorGICS,subIndustryGICS,CIK);"
        #print(sql)
        cursor.execute(sql)
        dbHandle.commit()
    except MySQLdb.Error,e:
        print ("Error code:",e.args[0])
        print ("Error message:",e.args[1])
        dbHandle.rollback()

    return

# CONNECT TO DB
# data server database parameters
dbHost='localhost'
dbPort=3306
dbUser='root'
dbPassword='password'
databaseName='global_monitoring'

## connect to the 'global_monitoring' MySQL database 
dbHandle=mysqlDatabaseToolbox.dbConnect(dbHost,dbPort,dbUser,dbPassword,databaseName)

# create the database table
if not mysqlDatabaseToolbox.doesTableExist(dbHandle,"sp500_constituents_by_sector"):
    # create table
    dbCreateSP500ConstituentBySectorTable(dbHandle)

endDate=datetime.date.today()
outputDirectory="D:/marketData/global_monitoring/instrument_universe/wiki/sp-500/"
outputFileName="sp-500_constituents_"+str(endDate)

#
outputFileHandle = open( outputDirectory + outputFileName,'w')

url="http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# fetch the url
req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
response = urllib2.urlopen( req ) 
s = response.read()
response.close()
# 
soup = BeautifulSoup(s, "lxml")
        
# fetch the table
table = soup.find("table", attrs={"class":"wikitable sortable"})    
# fetch the returns
records = table.find_all(["tr"])

# iterate over the table line for each component
for record in records:
    # parse the line    
    line=record.text.split('\n')
    instrumentTicker=str(line[1])
    instrumentName=str(line[2])
    sector=str(line[4])
    subIndustry=str(line[5])        
    dateFirstAdded=str(line[7])
    CIK=str(line[8])

    # write line to the output file
    try:
        outputFileHandle.write(instrumentTicker+"|"+instrumentName+"|"+sector+"|"+subIndustry+"|"+CIK+"\n")
    except:
        print('cannot write')

# close the output file
outputFileHandle.close()

dbBulkLoadSP500ConstituentBySectorTable(dbHandle,outputDirectory,outputFileName)

# disconnect from MySQL
mysqlDatabaseToolbox.dbDisconnect(dbHandle)