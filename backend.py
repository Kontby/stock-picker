import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf


def get_undervalued(days):
    url = 'https://raw.githubusercontent.com/datasets/nasdaq-listings/master/data/nasdaq-listed.csv'
    df = pd.read_csv(url)
    date = dt.date.today()
    three_d = date - dt.timedelta(days=days)
    #six_d = three_d - dt.timedelta(days=30)
    list_symbol = []
    list_mean = []
    list_close = []

    for s in df['Symbol'].unique()[150:180]:
        tickerSymbol = s
        tickerData = yf.Ticker(tickerSymbol)
        tickerDf = tickerData.history(period='id', start=three_d.strftime("%Y-%m-%d"), end=date.strftime("%Y-%m-%d"))

        tickerMean = tickerDf['Close'].mean()
        try:
            tickerClose = tickerDf['Close'][-1]
        except:
            tickerClose = 0

        list_symbol.append(s)
        list_mean.append(tickerMean)
        list_close.append(tickerClose)

    equity_df = pd.DataFrame({'Ticker':list_symbol,
                             'Close':list_close,
                             'Mean30':list_mean})

    equity_df['Percentage30'] = equity_df['Close']/equity_df['Mean30'] - 1

    return equity_df.sort_values(by='Percentage30').iloc[:10], equity_df.sort_values(by='Percentage30',ascending=False).iloc[:10]


