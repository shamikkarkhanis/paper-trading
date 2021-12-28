# author: Shamik Karkhanis
# created: 11-23-21
# last edit: 11-23-21
# version: 1.0

# imports
from yahoo_fin import stock_info as si
import time


def trajectoryIndicator():
    
    
    x = 0
    while x < 10:
        stockPrices.append(si.get_live_price('aapl')) 
        time.sleep(1)
        x += 1

    avgPrice = 0

    for price in stockPrices:
        avgPrice += price/len(stockPrices)

    if avgPrice >= stockPrices[0]:
        return "buy"
    else:
        return "sell"

print(trajectoryIndicator())
print(stockPrices)
