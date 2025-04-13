import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('DOGE_price_data.csv')

df['datetime'] = pd.to_datetime(df['datetime'])

df.set_index('datetime', inplace=True)

plt.figure(figsize=(12, 6))
plt.plot(df.index, df['close'])

plt.title('Dogecoin Close Price')
plt.xlabel('Time')
plt.ylabel('Close Price')
plt.grid(True)
plt.savefig('dogecoin_graph.png')
plt.close()
