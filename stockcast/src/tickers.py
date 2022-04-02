# pip3 install get_all_tickers

from get_all_tickers import get_tickers as gt

list_of_tickers = gt.get_tickers()
# or if you want to save them to a CSV file
#get.save_tickers()
print(list_of_tickers[:50])
