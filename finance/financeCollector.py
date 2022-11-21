import yfinance as yf
import pandas as pd
import argparse
from ta import add_all_ta_features

def collectPrice(crypto_name, start_date, end_date, interval, output):
    # collecting daily price of filecoin from 2021-09-01 to 2022-09-30
    filPrice = yf.download(tickers=crypto_name, start=start_date, end=end_date, interval=interval)
    print(filPrice)
    df = add_all_ta_features(
        filPrice, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True)
    df.to_csv("Finance/{output}.csv".format(output=output), encoding='utf-8')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input File Name")
    args = parser.parse_args()
    metadata = pd.read_csv(args.input)
    crypto_name = metadata.iloc[0]['crypto_name']
    # defining start date
    start_date = metadata.iloc[0]['start_date']
    # defining end date
    end_date = metadata.iloc[0]['end_date']
    interval = metadata.iloc[0]['interval']
    output = metadata.iloc[0]['output']
    collectPrice(crypto_name, start_date, end_date, interval, output)
