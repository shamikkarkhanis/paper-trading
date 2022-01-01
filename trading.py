# author: Shamik Karkhanis
# created: 11-22-21
# last edit: 11-22-21
# version: 1.0

# imports
from yahoo_fin import stock_info as si
import sqlite3

class Portfolio:

    # creates new portfolio database if not already created 
    def __init__(self, conn, identifier, cashBalance):
        self.conn = sqlite3.connect(conn)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS portfolio
            (ticker TEXT PRIMARY KEY NOT NULL,
            shares DOUBLE NOT NULL
            );''')

        # storing initial balance in database to allow access at future time
        self.identifier = identifier
        self.cashBalance = cashBalance
        # cheap way of getting around sqlite3 unique error (cannot insert if already exists)
        try:
            self.conn.execute("INSERT INTO PORTFOLIO VALUES (?, ?)", (identifier, cashBalance))
        except: 
            pass
    
        self.cleanup()

    # setters

    # creates database values
    def insert(self, ticker, shares):
        # cheap way of getting around sqlite3 unique error (cannot insert if already exists)
        try: 
            # had to use slightly edited version of update function and validate function
            self.conn.execute("INSERT INTO PORTFOLIO VALUES (?, ?)", (ticker, 0))
            self.validateAndProceeed(ticker, shares) 
        except: 
            self.validateAndProceeed(ticker, shares)

        self.cleanup()
        
    # checks if any stocks have 0 shares and removes them 
    def cleanup(self):
        for ticker in self.getValues():
            if self.getValues()[ticker] == 0:
                self.delete(ticker)
            else: pass

    # goes trough conditions and updates values in database accordingly
    def validateAndProceeed(self, ticker, shares): 
        if shares >= 0: # buy condition
            if self.getShares(self.identifier) >= self.getSharesToPrice(ticker, shares):
                self.update(ticker, shares)
                self.updateBalance(-self.getSharesToPrice(ticker, shares))
                print('--> Bought ' + str(shares) + ' share of ' + ticker + ' at ' + '$' + str(self.getSharesToPrice(ticker, shares)))
            else:
                print('INSUFFICIENT FUNDS')
        else: # sell condition (shares < 0)
            if abs(shares) <= self.getShares(ticker):
                self.update(ticker, shares) 
                self.updateBalance(self.getSharesToPrice(ticker, shares))
                print('--> Sold ' + str(abs(shares)) + ' share of ' + ticker + ' at ' + '$' + str(self.getSharesToPrice(ticker, shares)))
            else: 
                print('INSUFFICIENT SHARES')
        self.conn.commit()
                
    # deletes items in database
    def delete(self, ticker):
        self.conn.execute("DELETE from portfolio where ticker = ?", (ticker,))

    def resetCash(self, newBalance):
        self.conn.execute("UPDATE portfolio set shares = ? where ticker = ?", (newBalance, self.identifier))

    # updates already existing values in database
    def update(self, ticker, shares):
        self.conn.execute("UPDATE portfolio set shares = ? where ticker = ?", (self.getShares(ticker) + shares, ticker))
   
    # getters

    # returns balance
    def getCash(self):
        return round(self.getShares(self.identifier), 2)
    
    def updateBalance(self, amount):
        self.conn.execute("UPDATE portfolio set shares = ? where ticker = ?", (amount + self.getShares(self.identifier), self.identifier))
    
    # returns shares value
    def getSharesToPrice(self, ticker, shares):
        return round(si.get_live_price(ticker) * abs(shares), 2)
    
    def getPriceToShares(self, ticker, price):
        return round(price/si.get_live_price(ticker), 2)
    
    # portfolio value
    def getPortValue(self):
        pValue = 0.0
        for column in self.getValuesList()[1::]:
            pValue += self.getSharesToPrice(column[0], column[1])
        return pValue

    # combination of cashBalance and investments
    def getNetWorth(self):
        return round(self.getCash() + self.getPortValue(), 2)

    # returns all values from portfolio database in form of list with items in tuples
    def getValuesList(self):
        self.valuesList = []
        for item in self.conn.execute("SELECT ticker, shares from portfolio"):
            self.valuesList.append(item)
        return self.valuesList

    # returns stock portfolio in dictionary where a ticker points to number of shares owned
    def getValues(self):
        self.values = {}
        x = 0
        for items in self.getValuesList():
            self.values[self.getValuesList()[x][0]] = self.getValuesList()[x][1]
            x += 1
        return self.values

    # returns shares of specific ticker
    def getShares(self, ticker):
        return self.getValues()[ticker]

    # returns portfolio formatted as string
    def toString(self):
        pValue = 0
        print('\n--- Portfolio ---')
        for column in self.getValuesList()[1::]:
            stockValue = self.getSharesToPrice(column[0], column[1])
            pValue += stockValue
            print(column[0], str(column[1]), '--> $' + str(stockValue))
        print('--- \nPortfolio Value: $' + str(round(pValue, 2)) + '\n---\nCash Balance: $' + str(self.getCash()) + '\n---\nNet Worth: $' + str(round(self.getCash() + pValue, 2)) + '\n-----------------\n')

# playing functions

def startup():
    print('\n~~~~~~Happy Trading~~~~~~\n')
    while True:
        userInput = input('action: ').lower()
        if userInput == 'help' or userInput == 'h':
            help()
        elif userInput == 'p': # to check portfolio
            port.toString()
        elif userInput == 'b': # to buy stock
            stock = input('BUYING\nticker: ').lower()
            amount = input('shares or captial (eg. 10 or $1000): ').lower()
            if amount[0] == '$':
                port.insert(stock, port.getPriceToShares(stock, float(amount[1::])))
            elif amount == 'rest':
                port.insert(stock, port.getPriceToShares(stock, port.getCash()))
            else:
                port.insert(stock, float(amount))
        elif userInput == 's': # to sell stock
            stock = input('SELLING\nticker: ').lower()
            amount = input('shares or capital (eg. 10 or $1000): ').lower()
            if amount[0] == '$': # differentiating between number of shares to sell and amount of money in holding
                port.insert(stock, -port.getPriceToShares(stock, float(amount[1::])))
            elif amount == 'all':
                port.insert(stock, -port.getShares(stock))
            else:
                port.insert(stock, -float(amount))
        elif userInput == 's all': # sells all stocks
            x = 1
            for stock in port.getValuesList()[1::]:
                ticker = port.getValuesList()[x][0]
                shares = -port.getValuesList()[x][1]
                port.insert(ticker, shares)
        elif userInput == 'bal': # get balance
            print('--> Cash Balance: $' + str(port.getCash()))
        elif userInput == 'nw' or userInput == 'net worth':
            print('--> Net Worth: $' + str(port.getNetWorth()))
        elif userInput == 'e':
            break
            

    port.conn.close()


# creates a portfolio object 
port = Portfolio('portfolio.db', 'cashBalance', 500) 

startup()





