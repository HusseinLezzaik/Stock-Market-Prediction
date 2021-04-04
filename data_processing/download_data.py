import yahoo_fin.stock_info as si
import pandas as pd
import os

def download_data(etfs, time_frames):
    # 获取数据并存储
    if not os.path.exists('./Data'):
        os.makedirs('./Data')
    if not os.path.exists('./Data/rawdata'):
        os.makedirs('./Data/rawdata')

    for ticker in etfs:
        for interval in time_frames:
            historical_price = pd.DataFrame()
            print("This is a ticker ",ticker, interval)
            historical_price = si.get_data(ticker, interval=interval)

            # delete column 'ticker'
            historical_price = historical_price.drop(["ticker"], axis=1)

            # use date as index of the dataframe
            historical_price.index.name = "date"

            if interval == "1d":
                interval = "daily"

            elif interval == "1wk":
                interval = "weekly"
                # 删除最后一行或者倒数第二行
                if historical_price.isnull().any().sum() > 0:
                    historical_price.dropna(how='any', inplace=True)
                else:
                    historical_price = historical_price.iloc[:-1]

            else:
                # 删除最后一行或者倒数第二行
                if historical_price.isnull().any().sum() > 0:
                    historical_price.dropna(how='any', inplace=True)
                else:
                    historical_price = historical_price.iloc[:-1]
                interval = "monthly"
             # sava files
            historical_price.to_csv("./data/rawdata/" + ticker + "_" + interval + ".csv")