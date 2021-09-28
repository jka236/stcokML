import os
from dotenv import load_dotenv
from urllib.request import urlopen
import json
import pandas as pd
from datetime import datetime, timedelta
from pandas.tseries.holiday import USFederalHolidayCalendar
import numpy as np

def fmpAPIKey():
    load_dotenv()
    apikey = os.environ.get("apikey")
    return apikey

#!/usr/bin/env python
def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def getJsonData(dataType, ticker, apikey, period=None, startDate=None, endDate=None, limit=None):
    if dataType == 'ratio':
        url = ("https://fmpcloud.io/api/v3/ratios/"+ticker+"?period=quarter&limit="+limit+"&apikey="+apikey)
    elif dataType == 'profile':
        url = ("https://fmpcloud.io/api/v3/profile/"+ticker+"?apikey="+apikey)
    elif dataType == 'financial-growth':
        url = ("https://fmpcloud.io/api/v3/financial-growth/"+ticker+"?period=quarter&limit="+limit+"&apikey="+apikey)
    elif dataType == 'historical-price':
        url = ("https://fmpcloud.io/api/v3/historical-price-full/" + ticker + "?from=" + startDate + "&to=" + endDate + "&apikey="+apikey)
    jsonData = get_jsonparsed_data(url)
    return jsonData

def getPandasData(dataType, tickers, apikey, period=None, startDate=None, endDate=None, limit=None):
    pandasData = pd.DataFrame()
    failTickers = []
    for ticker in tickers:
        try:
          jsonData = getJsonData(dataType, ticker, apikey, period, startDate, endDate, limit)
          #price data is nested json. it can't extract directly from Json
          if dataType == 'historical-price':
            df = pd.DataFrame.from_dict(jsonData['historical'], orient='columns')
            df['symbol'] = jsonData['symbol']
          else:
            df = pd.DataFrame.from_dict(jsonData, orient='columns')
          pandasData = pd.concat([pandasData, df], axis=0)
        except:
          failTickers.append(ticker)
          pass
    return pandasData

def getForwarDate(pandasData):
    #Generate market closure date array
    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start='2000-01-01', end='2021-12-31')
    holidays = np.array(holidays, dtype='datetime64[D]')
    #Get the first busday 45 after the quater ends
    pandasData['forward_date'] = pandasData['date'].apply(lambda x: np.busday_offset(x, 45, roll='forward', holidays=holidays))
    pandasData['forward_date'] = pandasData['forward_date'].astype('str')

def getOutPerform(mergedPandas):
    mergedPandas = mergedPandas.sort_values(by=['symbol','date']).reset_index(drop=True)
    shifted = mergedPandas.shift(periods=-1, axis="rows", fill_value=0)
    mergedPandas['eq'] = mergedPandas['symbol'].eq(shifted['symbol'])
    subtract = mergedPandas[['spyP','tickerP']].subtract(shifted[['spyP','tickerP']])
    mergedPandas[['spyC','tickerC']] = subtract[['spyP','tickerP']] / shifted[['spyP','tickerP']]
    mergedPandas = mergedPandas[mergedPandas['eq'] == True]
    mergedPandas['diff'] = mergedPandas['tickerC'].subtract(mergedPandas['spyC'])
    mergedPandas['outPerform'] = mergedPandas['diff'] >= 0.1
    return mergedPandas