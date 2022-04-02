import yfinance as yf
from datetime import date
from pprint import pprint

START = "2020-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

msft = yf.Ticker("MSFT")

# get stock info
pprint(msft.info)


# get list of tickers with company name for companies with a market cap > $1B
tickers = yf.download(
    # tickers list
    tickers="AAPL,AMZN,FB,GOOG,MSFT",
    # starting date
    start=START,
    # ending date
    end=TODAY,
    # interval - 1d, 1wk, 1mo
    interval="1d",
    # drop columns with these strings
    drop_cols=["Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"],
    # save data to file
    # dest="data/aapl_data.csv"
)

print(tickers)
print(tickers.columns)

