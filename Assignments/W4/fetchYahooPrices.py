# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 15:40:47 2017

@author: Derek G Nokes
"""

import pandas_datareader.data as web

import datetime

start = datetime.datetime(2010, 1, 1)

end = datetime.datetime.now()

f = web.DataReader("F", 'yahoo', start, end)

f