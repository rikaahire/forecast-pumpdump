import requests
import pandas as pd
from datetime import datetime, timedelta

# Get OHLCV data
def get_ohlcv_data(symbol, currency, start_date, end_date, api_key):
    base_url = 'https://min-api.cryptocompare.com/data/v2/histohour'
    limit = 2000
    all_data = []

    # Convert dates to Unix timestamps
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())

    toTs = end_timestamp

    while toTs > start_timestamp:
        params = {
            'fsym': symbol,
            'tsym': currency,
            'limit': limit,
            'toTs': toTs,
            'api_key': api_key
        }
        response = requests.get(base_url, params=params)
        data = response.json()['Data']['Data']
        if not data:
            break
        all_data.extend(data)
        toTs = data[0]['time'] - 1

    # Convert to dataframe
    df = pd.DataFrame(all_data)
    df['datetime'] = pd.to_datetime(df['time'], unit='s')
    df = df[['datetime', 'open', 'high', 'low', 'close', 'volumefrom']]
    df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
    df.rename(columns={'volumefrom': 'volume'}, inplace=True)
    return df

# CryptoCompare API key
api_key = '150d28f4feb1c65c500263bcb260d8ebfb491a7c7f2d8c67c2851eaf6407651e'

# Parameters
symbols = ['DOGE', 'SHIB', 'PEPE']
currency = 'USD'
start_date = '2023-04-17'
end_date = '2023-06-30'

# Get price data
for symbol in symbols:
    df = get_ohlcv_data(symbol, currency, start_date, end_date, api_key)
    df.to_csv(f'{symbol}_price_data.csv', index=False)
    print(f'Data for {symbol} saved to {symbol}_price_data.csv')
