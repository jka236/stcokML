import getFMPdata
import getSPYList
import pandas as pd
import model

if __name__ == '__main__':
    apikey = getFMPdata.fmpAPIKey()
    spyList = getSPYList.getSPYlist()

    # Get Financial Data from fmp
    ratio = getFMPdata.getPandasData('ratio', spyList, apikey, limit="83")
    profile = getFMPdata.getPandasData('profile', spyList, apikey)
    finincialGrowth = getFMPdata.getPandasData('financial-growth', spyList, apikey, limit="83")
    individualPrice = getFMPdata.getPandasData('historical-price', spyList, apikey, startDate="2000-01-01", endDate="2021-09-25")
    spyPrice = getFMPdata.getPandasData('historical-price', ["SPY"], apikey, startDate="2000-01-01", endDate="2021-09-25")

    # Add a new column: 45 days after the last day of each quarter
    getFMPdata.getForwarDate(ratio)

    #drop unnecessary columns and change names for consistency
    ratio = ratio.drop(columns='period')
    finincialGrowth = finincialGrowth.drop(columns='period')
    profile = profile[['symbol','industry','sector']]
    individualPrice = individualPrice[['date','adjClose','symbol']]
    individualPrice = individualPrice.rename(columns={"date":"forward_date", 'adjClose':'tickerP'})
    spyPrice = spyPrice[['date','adjClose']]
    spyPrice = spyPrice.rename(columns={"date":"forward_date", "adjClose": "spyP"})

    # merge all data
    spyKeyData = ratio.merge(profile, how='left', on='symbol')
    spyKeyData = spyKeyData.merge(finincialGrowth, how='left', on=['symbol', 'date'])
    spyKeyData = spyKeyData.merge(individualPrice, on=['symbol', 'forward_date'])
    spyKeyData = spyKeyData.merge(spyPrice, on='forward_date')

    # Drop if more than 10% of data is missing
    tooManyMissing = pd.DataFrame(spyKeyData.isnull().sum() > spyKeyData.shape[0] / 10)
    tooManyMissing = tooManyMissing[tooManyMissing[0] == True].index.tolist()

    # Keep current/quick/cash Ratio
    del tooManyMissing[:3]

    spyKeyData = spyKeyData.drop(tooManyMissing, axis=1)
    # spyKeyData = spyKeyData.dropna()

    # Exclude 2021 2Q data
    spyKeyData2Q = spyKeyData[spyKeyData.date == '2021-06-30']
    spyKeyData = spyKeyData[spyKeyData.date != '2021-06-30']

    spyKeyData = getFMPdata.getOutPerform(spyKeyData)

    rfModel = model.transformFit(spyKeyData)