import pandas as pd
import mplfinance as mpf

df = pd.read_csv('DOGE_price_data.csv')

df['datetime'] = pd.to_datetime(df['datetime'])

df.set_index('datetime', inplace=True)

mpf.plot(df, 
         type='candle', 
         volume=True, 
         style='charles', 
         title='Dogecoin Price Chart (Candlestick + Volume)',
         ylabel='Price',
         ylabel_lower='Volume',
         figsize=(12, 6),
         savefig='dogecoin_chart.png')
