import pandas_datareader
import pandas
import numpy
from scipy import stats
import datetime
import time

import urllib2
from bs4 import BeautifulSoup
from timeit import default_timer as timer
import os

# inline matplotlib
#%matplotlib inline

def ensure_directory(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def fetchSP500_components_wiki(outputDirectory,endDate):

    outputFileName="sp-500_constituents_"+endDate.strftime('%Y%m%d_%H%M%S')
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
        CIK=str(line[8])

        lineArray=list()
        lineArray.append(instrumentTicker)
        lineArray.append(instrumentName)
        lineArray.append(sector)
        lineArray.append(subIndustry)
        lineArray.append(CIK)

        # write line to the output file
        try:
            lineString='|'.join(lineArray)
            print(lineString)
            outputFileHandle.write(lineString+"\n")
        except:
            print('cannot write')

    # close the output file
    outputFileHandle.close()

    return outputFileName

def price2momentum(y):
    x=numpy.arange(0,len(y))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,
        numpy.log(y))
    # adjust the momentum for smoothness and annualize
    momentum=(((1+slope)**252)-1)*(r_value**2)
    return momentum

def priceGapFilter(y):
    # set gap filter
    threshold=0.15
    # find gap flag
    gapFlag=numpy.max(numpy.abs(numpy.diff(numpy.log(y))))>=threshold

    return gapFlag

# fetch yahoo data for ticker between start and end dates
def fetchYahooData(yahooTicker,instrumentName,gicsSectorName,gicsSubIndustryName,
    cik,startDate,endDate,momentumLookback=80,momentumLookback0=90,
    momentumLookback1=100,momentumLookback2=110,momentumLookback3=120,
    gapLookback=80,gapLookback0=90,gapLookback1=100,gapLookback2=110,
    gapLookback3=120,emaLookback=90,emaLookback0=100,emaLookback1=120,
    emaLookback2=150,emaLookback3=200):

    # fetch historical data
    df = pandas_datareader.data.DataReader(yahooTicker, 'yahoo', startDate, 
        endDate)

    # iterate backwards over the prices and compute the adj factor
    df1=df.copy(deep=True)

    #dateTime=df1.index
    openPrice=numpy.array(df1['Open'].values, dtype='d')
    highPrice=numpy.array(df1['High'].values, dtype='d')
    lowPrice=numpy.array(df1['Low'].values, dtype='d')
    closePrice=numpy.array(df1['Close'].values, dtype='d')
    adjustedClosePrice=numpy.array(df1['Adj Close'].values, dtype='d')
        
    T=len(df)
    adjustCount=0
    for t in xrange(T-1,-1,-1):
       
        if closePrice[t] != adjustedClosePrice[t]:
            factor = adjustedClosePrice[t]/closePrice[t]
            adjustCount=adjustCount+1
            
            for tt in xrange(t,-1,-1):
                openPrice[tt]=openPrice[tt]*factor
                highPrice[tt]=highPrice[tt]*factor
                lowPrice[tt]=lowPrice[tt]*factor
                closePrice[tt]=closePrice[tt]*factor                

    df['adjOpen']=numpy.array(openPrice, dtype='d')
    df['adjHigh']=numpy.array(highPrice, dtype='d')
    df['adjLow']=numpy.array(lowPrice, dtype='d')
    df['adjClose']=numpy.array(closePrice, dtype='d')
                            
    # add true range and 20d ATR
    previousClosePrice=df['adjClose'].shift(1)
    a=df['adjHigh']-df['adjLow']
    b=abs(df['adjHigh']-previousClosePrice)
    c=abs(previousClosePrice-df['adjLow'])
    test=pandas.concat([a,b,c],axis=1)
    # compute true range
    trueRange=test.max(axis=1,skipna=False)
    trueRange.reindex(df.index,method='ffill')
    df['trueRange']=trueRange
    # compute the 20d atr
    atrLookback=20
    
    atr=trueRange.ewm(span=atrLookback,min_periods=atrLookback,adjust=True,
        ignore_na=True).mean()
    
    df['atr_20d']=numpy.array(numpy.around(atr, decimals=2, out=None), 
      dtype='d')

    # add momentum
    df['momentum_'+str(momentumLookback)+'d']=df['adjClose'].rolling(center=False,
       window=momentumLookback).apply(func=price2momentum)
    # add momentum
    df['momentum_'+str(momentumLookback0)+'d']=df['adjClose'].rolling(center=False,
       window=momentumLookback0).apply(func=price2momentum)    
    # add momentum
    df['momentum_'+str(momentumLookback1)+'d']=df['adjClose'].rolling(center=False,
       window=momentumLookback1).apply(func=price2momentum)
    # add momentum
    df['momentum_'+str(momentumLookback2)+'d']=df['adjClose'].rolling(center=False,
       window=momentumLookback2).apply(func=price2momentum)
    # add momentum
    df['momentum_'+str(momentumLookback3)+'d']=df['adjClose'].rolling(center=False,
       window=momentumLookback3).apply(func=price2momentum)    
        
    # add gap flag
    df['gapFlag_'+str(gapLookback)+'d']=df['adjClose'].rolling(center=False,
       window=gapLookback).apply(func=priceGapFilter)    
    # add gap flag
    df['gapFlag_'+str(gapLookback0)+'d']=df['adjClose'].rolling(center=False,
       window=gapLookback0).apply(func=priceGapFilter)
    # add gap flag
    df['gapFlag_'+str(gapLookback1)+'d']=df['adjClose'].rolling(center=False,
       window=gapLookback1).apply(func=priceGapFilter)    
    # add gap flag
    df['gapFlag_'+str(gapLookback2)+'d']=df['adjClose'].rolling(center=False,
       window=gapLookback2).apply(func=priceGapFilter)    
    # add gap flag
    df['gapFlag_'+str(gapLookback3)+'d']=df['adjClose'].rolling(center=False,
       window=gapLookback3).apply(func=priceGapFilter)

    # compute EMA price
    df['emaPrice_'+str(emaLookback)+'d']=df['adjClose'].ewm(span=emaLookback,
       min_periods=0,ignore_na=True).mean()
    # compute EMA price
    df['emaPrice_'+str(emaLookback0)+'d']=df['adjClose'].ewm(span=emaLookback0,
       min_periods=0,ignore_na=True).mean()
    # compute EMA price
    df['emaPrice_'+str(emaLookback1)+'d']=df['adjClose'].ewm(span=emaLookback1,
       min_periods=0,ignore_na=True).mean()
    # compute EMA price
    df['emaPrice_'+str(emaLookback2)+'d']=df['adjClose'].ewm(span=emaLookback2,
       min_periods=0,ignore_na=True).mean()
    # compute EMA price
    df['emaPrice_'+str(emaLookback3)+'d']=df['adjClose'].ewm(span=emaLookback3,
       min_periods=0,ignore_na=True).mean()

    # add trend flag
    columnLabelA='trendFlag_'+str(emaLookback)+'d'
    columnLabelB='emaPrice_'+str(emaLookback)+'d'
    df[columnLabelA]=df['adjClose']>df[columnLabelB].shift(periods=-1,axis=0)
    # add trend flag
    columnLabelA='trendFlag_'+str(emaLookback0)+'d'
    columnLabelB='emaPrice_'+str(emaLookback0)+'d'
    df[columnLabelA]=df['adjClose']>df[columnLabelB].shift(periods=-1,axis=0)
    # add trend flag
    columnLabelA='trendFlag_'+str(emaLookback1)+'d'
    columnLabelB='emaPrice_'+str(emaLookback1)+'d'
    df[columnLabelA]=df['adjClose']>df[columnLabelB].shift(periods=-1,axis=0)
    # add trend flag
    columnLabelA='trendFlag_'+str(emaLookback2)+'d'
    columnLabelB='emaPrice_'+str(emaLookback2)+'d'
    df[columnLabelA]=df['adjClose']>df[columnLabelB].shift(periods=-1,axis=0)
    # add trend flag
    columnLabelA='trendFlag_'+str(emaLookback3)+'d'
    columnLabelB='emaPrice_'+str(emaLookback3)+'d'
    df[columnLabelA]=df['adjClose']>df[columnLabelB].shift(periods=-1,axis=0)
        
    # add NA for last point to ensure causal
    df['trendFlag_'+str(emaLookback)+'d'].iloc[T-1]=numpy.nan
    # add NA for last point to ensure causal
    df['trendFlag_'+str(emaLookback0)+'d'].iloc[T-1]=numpy.nan
    # add NA for last point to ensure causal
    df['trendFlag_'+str(emaLookback1)+'d'].iloc[T-1]=numpy.nan
    # add NA for last point to ensure causal
    df['trendFlag_'+str(emaLookback2)+'d'].iloc[T-1]=numpy.nan
    # add NA for last point to ensure causal
    df['trendFlag_'+str(emaLookback3)+'d'].iloc[T-1]=numpy.nan    
    
    # add instrument info
    df['yahooTicker']=str(yahooTicker)
    df['instrumentName']=str(instrumentName)
    df['gicsSectorName']=str(gicsSectorName)
    df['gicsSubIndustryName']=str(gicsSubIndustryName)
    df['cik']=str(cik)
    
    return df

def buildMomentumData(priceDirectory,instrumentMaster,startDate,endDate):

    # create data dictionary
    dataDictionary=dict()
    # create error dictionary
    error=dict()
    
    # iterate over each instrument
    for instrument_index, instrument in instrumentMaster.iterrows():
        # extract instrument details
        instrumentTicker=instrument[0]
        instrumentName=instrument[1]
        gicsSectorName=instrument[2]
        gicsSubIndustryName=instrument[3]
        cik=instrument[4]
    
        rowList=list()

        try:

            # create output file name
            priceFileName=instrumentTicker+'_'+endDate.strftime('%Y%m%d_%H%M%S')
            # fetch price from yahoo
            price=fetchYahooData(instrumentTicker,instrumentName,gicsSectorName,
                gicsSubIndustryName,cik,startDate,endDate)
            # write price
            price.to_csv(priceDirectory+priceFileName,sep='|',index=True,
                index_label='asOfDate',float_format='%g',na_rep='\N')

            # store fields in array
            rowList.append("COMPLETE")
            rowList.append(instrumentTicker)
            rowList.append(instrumentName)
            rowList.append(gicsSectorName)
            rowList.append(gicsSubIndustryName)
            rowList.append(endDate.strftime('%Y-%m-%d %H:%M:%S'))
            # create row string
            rowString='|'.join(rowList)

            # log complete
            print(rowString)
            errorHandle.write(rowString+"\n")
            # sleep for 10 seconds
            time.sleep(10)
            # add price dataframe to data dictionary 
            dataDictionary[instrumentTicker]=price

        except:  
            # store in array
            rowList.append("ERROR")
            rowList.append(instrumentTicker)
            rowList.append(instrumentName)
            rowList.append(gicsSectorName)
            rowList.append(gicsSubIndustryName)
            rowList.append(endDate.strftime('%Y-%m-%d %H:%M:%S'))        
            # create row string
            rowString='|'.join(rowList)
        
            # log error
            print(rowString)
            errorHandle.write(rowString+"\n")
            # add instrument name to error dictionary
            error[instrumentTicker]=instrumentName
        
    # close error log
    errorHandle.close()  
        
    # convert the error dictionary to a dataframe
    errorData=pandas.DataFrame.from_dict(error,orient='index')            
   
    # create the data panel
    groupData=pandas.Panel.from_dict(dataDictionary,orient='minor')    
    
    return groupData,errorData

def writeMomentumData2h5(baseDirectory,groupData):
    # extract the prices
    prices=groupData['adjClose']
    # extract the true ranges
    trueRanges=groupData['trueRange']

    # momentumLookback=80
    # extract the 80-day momentum
    momentum_80d=groupData['momentum_80d']
    # momentumLookback0=90
    # extract the 90-day momentum
    momentum_90d=groupData['momentum_90d']
    # momentumLookback1=100
    # extract the 100-day momentum
    momentum_100d=groupData['momentum_100d']
    # momentumLookback2=110
    # extract the 110-day momentum
    momentum_110d=groupData['momentum_110d']
    # momentumLookback3=120
    # extract the 120-day momentum
    momentum_120d=groupData['momentum_120d']
    
    # gapLookback=80
    # extract the 80-day gap flag
    gapFlag_80d=groupData['gapFlag_80d']
    # gapLookback0=90
    # extract the 90-day gap flag
    gapFlag_90d=groupData['gapFlag_90d']
    # gapLookback1=100
    # extract the 100-day gap flag
    gapFlag_100d=groupData['gapFlag_100d']
    # gapLookback2=110
    # extract the 110-day gap flag
    gapFlag_110d=groupData['gapFlag_110d']
    # gapLookback3=120
    # extract the 120-day gap flag
    gapFlag_120d=groupData['gapFlag_120d']

    # emaLookback=90
    # extract the 90-day EMA price
    emaPrice_90d=groupData['emaPrice_90d']
    # emaLookback0=100
    # extract the 100-day EMA price
    emaPrice_100d=groupData['emaPrice_100d']
    # emaLookback1=120
    # extract the 120-day EMA price
    emaPrice_120d=groupData['emaPrice_120d']
    # emaLookback2=150
    # extract the 150-day EMA price
    emaPrice_150d=groupData['emaPrice_150d']
    # emaLookback3=200
    # extract the 200-day EMA price
    emaPrice_200d=groupData['emaPrice_200d']

    # emaLookback=90
    # extract the 90-day trend flag
    trendFlag_90d=groupData['trendFlag_90d']
    # emaLookback0=100
    # extract the 100-day trend flag
    trendFlag_100d=groupData['trendFlag_100d']
    # emaLookback1=120
    # extract the 120-day trend flag
    trendFlag_120d=groupData['trendFlag_120d']
    # emaLookback2=150
    # extract the 150-day trend flag
    trendFlag_150d=groupData['trendFlag_150d']
    # emaLookback3=200
    # extract the 200-day trend flag
    trendFlag_200d=groupData['trendFlag_200d']

    # set the HDF5 output file directory
    output_directory=baseDirectory
    # create the directory if it does not exist
    ensure_directory(output_directory)      
    output_file='sp500_wiki_yahoo-'+endDate.strftime('%Y%m%d_%H%M%S')+'.h5'

    # create the HDF5 data store
    data_store = pandas.HDFStore(output_directory+output_file)
    # store the 'prices' data frame in the HDF5 data store
    data_store['price'] = prices

    # store the 80-day momentum data frame in the HDF5 data store
    data_store['momentum_80d'] = momentum_80d
    # store the 90-day momentum data frame in the HDF5 data store
    data_store['momentum_90d'] = momentum_90d
    # store the 100-day momentum data frame in the HDF5 data store
    data_store['momentum_100d'] = momentum_100d
    # store the 110-day momentum data frame in the HDF5 data store
    data_store['momentum_110d'] = momentum_110d
    # store the 120-day momentum data frame in the HDF5 data store
    data_store['momentum_120d'] = momentum_120d

    # store the 80-day gap filter data frame in the HDF5 data store
    data_store['gapFlag_80d'] = gapFlag_80d
    # store the 90-day gap filter data frame in the HDF5 data store
    data_store['gapFlag_90d'] = gapFlag_90d
    # store the 100-day gap filter data frame in the HDF5 data store
    data_store['gapFlag_100d'] = gapFlag_100d
    # store the 110-day gap filter data frame in the HDF5 data store
    data_store['gapFlag_110d'] = gapFlag_110d
    # store the 120-day gap filter data frame in the HDF5 data store
    data_store['gapFlag_120d'] = gapFlag_120d

    # store the 90-day EMA price data frame in the HDF5 data store
    data_store['emaPrice_90d'] = emaPrice_90d
    # store the 100-day EMA price data frame in the HDF5 data store
    data_store['emaPrice_100d'] = emaPrice_100d
    # store the 120-day EMA price data frame in the HDF5 data store
    data_store['emaPrice_120d'] = emaPrice_120d
    # store the 150-day EMA price data frame in the HDF5 data store
    data_store['emaPrice_150d'] = emaPrice_150d
    # store the 200-day EMA price data frame in the HDF5 data store
    data_store['emaPrice_200d'] = emaPrice_200d

    # store the 90-day trend flag data frame in the HDF5 data store
    data_store['trendFlag_90d'] = trendFlag_90d
    # store the 100-day trend flag data frame in the HDF5 data store
    data_store['trendFlag_100d'] = trendFlag_100d
    # store the 120-day trend flag data frame in the HDF5 data store
    data_store['trendFlag_120d'] = trendFlag_120d
    # store the 150-day trend flag data frame in the HDF5 data store
    data_store['trendFlag_150d'] = trendFlag_150d
    # store the 200-day trend flag data frame in the HDF5 data store
    data_store['trendFlag_200d'] = trendFlag_200d

    # store the 'true ranges' data frame in the HDF5 data store
    data_store['trueRange'] = trueRanges
    # store the 'error tickers' data frame in the HDF5 data store
    data_store['error'] = errorData
    # store instrument master
    data_store['instrumentMaster'] = instrumentMaster
    # close the HDF5 data store
    data_store.close()    
    
    return output_directory,output_file

#===================================================================================================
# MAIN
#===================================================================================================
# set start date
startDate = datetime.datetime(1990, 1, 1)
# set end date
endDate = datetime.datetime.now()
# fetch price flag
fetchPriceFlag=False
# set error directory
errorDirectory="D:/marketData/global_monitoring/yahoo/"
# set output directory
outputDirectory="D:/marketData/global_monitoring/instrument_universe/wiki/sp-500/"
# set base directory
baseDirectory="D:/marketData/global_monitoring/yahoo/sp500_wiki/"

if fetchPriceFlag:

    # define price output directory
    priceDirectory=baseDirectory+endDate.strftime('%Y%m%d_%H%M%S')+"/"
    # create price file output directory if does not exist
    ensure_directory(priceDirectory)
    # define error file name
    errorFileName="error_sp500_"+endDate.strftime('%Y%m%d_%H%M%S')
    # open error file handle
    errorHandle = open( errorDirectory + errorFileName,'w')

    # define type dictionary
    dTypeDictionary={'Ticker symbol' : str,
                     'Security' : str,
                     'GICS Sector' : str,
                     'GICS Sub Industry' : str,
                     'CIK' : str}

    # fetch the S&P500 components from wikipedia
    outputFileName=fetchSP500_components_wiki(outputDirectory,endDate)
    # read the instrument master into dataframe
    instrumentMaster=pandas.read_csv(outputDirectory+outputFileName,sep='|',
        dtype=dTypeDictionary)

    # uncomment for testing
    #instrumentMaster=instrumentMaster.iloc[0:2]
    
    # start timer (prices)
    ts_fetchPrices = timer()

    # fetch yahoo prices and compute indicators for each instrument in master
    groupData,errorData=buildMomentumData(priceDirectory,instrumentMaster,
        startDate,endDate)

    # end timer (prices)
    te_fetchPrices = timer()
    # compute time elasped
    timeElasped_fetchPrices=te_fetchPrices-ts_fetchPrices
    # display time elasped
    print('Time Elasped: '+str(timeElasped_fetchPrices))

    # write momentum data set  to HDF5
    output_directory,output_file=writeMomentumData2h5(baseDirectory,groupData)
