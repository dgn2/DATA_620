# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 18:56:44 2017

@author: Derek G Nokes
"""
import pandas
import numpy
from timeit import default_timer as timer

def ensure_directory(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def priceMomentum2UniverseRelativeRank(momentum,nPositions):
    # find T and number of instruments
    T,nInstruments=momentum.shape

    # create data frames to store results
    momentumRank=momentum.copy()
    momentumFlag=momentum.copy()
    # iterate over each instant in time, t
    for t in range(0,T):
        # find sort index for momentum of each instrument in universe
        momentumIndex=numpy.argsort(momentum.iloc[t,:].values*-1,axis=0)
        # based on sorted momentum, determine relative rank
        momentumRank.iloc[t,momentumIndex]=numpy.arange(1,nInstruments+1)
        # If the rank is less than target number of positions, then condition 
        # is met (i.e., stock is considered to have 'momentum') over defined 
        # lookback period
        momentumFlag.iloc[t,:]=momentumRank.iloc[t,:]<=nPositions
    
    return momentumRank,momentumFlag

nPositions=30
# set the HDF5 output file directory
h5Directory='C:/Users/Derek/Documents/GitHub/DATA_620/Projects/W7/'
# define the input file name for prices and true range
h5FileName='sp500_wiki_yahoo-20171014_120847.h5'
h5OutputFileName='sp500_signal_wiki_yahoo-20171014_120847.h5'

# read the price data from the HDF5 data store
prices = pandas.read_hdf(h5Directory+h5FileName,'price')
# read 'true ranges' data frame in the HDF5 data store
trueRanges = pandas.read_hdf(h5Directory+h5FileName,'trueRange')
# read 'error tickers' data frame in the HDF5 data store
errorData = pandas.read_hdf(h5Directory+h5FileName,'error')
# read instrument master
instrumentMaster = pandas.read_hdf(h5Directory+h5FileName,'instrumentMaster')

# read 80-day momentum data frame in the HDF5 data store
momentum_80d = pandas.read_hdf(h5Directory+h5FileName,'momentum_80d')
# read 90-day momentum data frame in the HDF5 data store
momentum_90d = pandas.read_hdf(h5Directory+h5FileName,'momentum_90d')
# read 100-day momentum data frame in the HDF5 data store
momentum_100d = pandas.read_hdf(h5Directory+h5FileName,'momentum_100d')
# read 110-day momentum data frame in the HDF5 data store
momentum_110d = pandas.read_hdf(h5Directory+h5FileName,'momentum_110d')
# read 120-day momentum data frame in the HDF5 data store
momentum_120d = pandas.read_hdf(h5Directory+h5FileName,'momentum_120d')

# read 80-day gap filter data frame in the HDF5 data store
gapFlag_80d = pandas.read_hdf(h5Directory+h5FileName,'gapFlag_80d')
# read 90-day gap filter data frame in the HDF5 data store
gapFlag_90d = pandas.read_hdf(h5Directory+h5FileName,'gapFlag_90d')
# read 100-day gap filter data frame in the HDF5 data store
gapFlag_100d = pandas.read_hdf(h5Directory+h5FileName,'gapFlag_100d')
# read 110-day gap filter data frame in the HDF5 data store
gapFlag_110d = pandas.read_hdf(h5Directory+h5FileName,'gapFlag_110d')
# read 120-day gap filter data frame in the HDF5 data store
gapFlag_120d = pandas.read_hdf(h5Directory+h5FileName,'gapFlag_120d')

# read 90-day EMA price data frame in the HDF5 data store
emaPrice_90d = pandas.read_hdf(h5Directory+h5FileName,'emaPrice_90d')
# store the 100-day EMA price data frame in the HDF5 data store
emaPrice_100d = pandas.read_hdf(h5Directory+h5FileName,'emaPrice_100d')
# read 120-day EMA price data frame in the HDF5 data store
emaPrice_120d = pandas.read_hdf(h5Directory+h5FileName,'emaPrice_120d')
# read 150-day EMA price data frame in the HDF5 data store
emaPrice_150d = pandas.read_hdf(h5Directory+h5FileName,'emaPrice_150d')
# read 200-day EMA price data frame in the HDF5 data store
emaPrice_200d = pandas.read_hdf(h5Directory+h5FileName,'emaPrice_200d')

# read 90-day trend flag data frame in the HDF5 data store
trendFlag_90d = pandas.read_hdf(h5Directory+h5FileName,'trendFlag_90d')
# read 100-day trend flag data frame in the HDF5 data store
trendFlag_100d = pandas.read_hdf(h5Directory+h5FileName,'trendFlag_100d')
# read 120-day trend flag data frame in the HDF5 data store
trendFlag_120d = pandas.read_hdf(h5Directory+h5FileName,'trendFlag_120d')
# read 150-day trend flag data frame in the HDF5 data store
trendFlag_150d = pandas.read_hdf(h5Directory+h5FileName,'trendFlag_150d')
# read 200-day trend flag data frame in the HDF5 data store
trendFlag_200d = pandas.read_hdf(h5Directory+h5FileName,'trendFlag_200d')

# compute the relative momentum

# start timer (relative momentum)
ts_relativeMomentum = timer()

# compute relative momentum (80 day)
momentumRank_80d,momentumFlag_80d=priceMomentum2UniverseRelativeRank(momentum_80d,
    nPositions)
# compute relative momentum
momentumRank_90d,momentumFlag_90d=priceMomentum2UniverseRelativeRank(momentum_90d,
    nPositions)
# compute relative momentum (100 day)
momentumRank_100d,momentumFlag_100d=priceMomentum2UniverseRelativeRank(momentum_100d,
    nPositions)
# compute relative momentum (110 day)
momentumRank_110d,momentumFlag_110d=priceMomentum2UniverseRelativeRank(momentum_110d,
    nPositions)
# compute relative momentum (120 day)
momentumRank_120d,momentumFlag_120d=priceMomentum2UniverseRelativeRank(momentum_120d,
    nPositions)

# end timer (relative momentum)
te_relativeMomentum = timer()
# compute time elasped
timeElasped_relativeMomentum=te_relativeMomentum-ts_relativeMomentum
# display time elasped
print('Time Elasped: '+str(timeElasped_relativeMomentum))

# create HDF5 file


# create the HDF5 data store
data_store = pandas.HDFStore(h5Directory+h5OutputFileName)
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

# add 80-day momentum rank
data_store['momentumRank_80d'] = momentumRank_80d
# add 80-day momentum flag
data_store['momentumFlag_80d'] = momentumFlag_80d
# add 90-day momentum rank
data_store['momentumRank_90d'] = momentumRank_90d
# add 90-day momentum flag
data_store['momentumFlag_90d'] = momentumFlag_90d
# add 100-day momentum rank
data_store['momentumRank_100d'] = momentumRank_100d
# add 100-day momentum flag
data_store['momentumFlag_100d'] = momentumFlag_100d
# add 110-day momentum rank
data_store['momentumRank_110d'] = momentumRank_110d
# add 110-day momentum flag
data_store['momentumFlag_110d'] = momentumFlag_110d
# add 120-day momentum rank
data_store['momentumRank_120d'] = momentumRank_120d
# add 120-day momentum flag
data_store['momentumFlag_120d'] = momentumFlag_120d

# store the 'true ranges' data frame in the HDF5 data store
data_store['trueRange'] = trueRanges
# store the 'error tickers' data frame in the HDF5 data store
data_store['error'] = errorData
# store instrument master
data_store['instrumentMaster'] = instrumentMaster
# close the HDF5 data store
data_store.close()