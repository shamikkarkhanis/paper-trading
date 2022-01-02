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

        
        
    # checks if any stocks have 0 shares and removes them 
    def cleanup(self):
        for ticker in self.getValuesList()[1::]:
            if self.getValues()[ticker[0]] == 0:
                self.delete(ticker[0])
            else: pass
    
    def deletePortfolio(self):
        pass

    # goes trough conditions and updates values in database accordingly
    def validateAndProceeed(self, ticker, shares): 
        if shares >= 0: # buy condition
            if self.getShares(self.identifier) >= self.getSharesToPrice(ticker, shares):
                self.update(ticker, shares)
                self.updateBalance(-self.getSharesToPrice(ticker, shares))
                print('--> Bought ' + str(round(shares, 2)) + ' share of ' + ticker + ' at ' + '$' + str(round(self.getSharesToPrice(ticker, shares), 2)))
            else:
                print('INSUFFICIENT FUNDS')
        else: # sell condition (shares < 0)
            if abs(shares) <= self.getShares(ticker):
                self.update(ticker, shares) 
                self.updateBalance(self.getSharesToPrice(ticker, shares))
                print('--> Sold ' + str(abs(round(shares, 2))) + ' share of ' + ticker + ' at ' + '$' + str(round(self.getSharesToPrice(ticker, shares), 2)))
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
        return self.getShares(self.identifier)
    
    def updateBalance(self, amount):
        self.conn.execute("UPDATE portfolio set shares = ? where ticker = ?", (amount + self.getShares(self.identifier), self.identifier))
    
    # returns shares value
    def getSharesToPrice(self, ticker, shares):
        return si.get_live_price(ticker) * abs(shares)
    
    def getPriceToShares(self, ticker, price):
        return price/si.get_live_price(ticker)
    
    # portfolio value
    def getPortValue(self):
        pValue = 0.0
        for column in self.getValuesList()[1::]:
            pValue += self.getSharesToPrice(column[0], column[1])
        return pValue

    # combination of cashBalance and investments
    def getNetWorth(self):
        return self.getCash() + self.getPortValue()

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
        port.cleanup()
        pValue = 0
        print('\n--- Portfolio ---')
        for column in self.getValuesList()[1::]:
            stockValue = self.getSharesToPrice(column[0], column[1])
            pValue += stockValue
            print(column[0], str(round(column[1], 2)), '--> $' + str(round(stockValue, 2)))
        print('--- \nPortfolio Value: $' + str(round(pValue, 2)) + '\n---\nCash Balance: $' + str(round(self.getCash(), 2)) + '\n---\nNet Worth: $' + str(round(self.getCash() + pValue, 2)) + '\n-----------------\n')

# playing functions

def help():
    print("\nAvailable options: \n  'p' - view portfolip \n  'bal' - view cash balance \n  'nw' or 'net worth - view net worth")
    print("  'b' - buy \n  's' - sell\n")
    print("Buying: \n  hit 'b' then the stock you wish to purchase \n  and then the amount of shares or money you wish to invest")
    print("  putting a '$' in front of the amount you wish to invest means dollars and without means shares")
    print("  alternatively putting 'rest' as the amount will lead to spending the rest of your cash balance\n")
    print("Selling: ")
    print("  click 's' and then the stock you would like to sell follwed by the amount")
    print("  just like buying, putting a dollar sign means you will gain that amount of money with the sale")
    print("  and without means shares")
    print("  putting 'all' as the amount will sell all owned shares of that one stock\n")

def buy():
    stock = input('BUYING\nticker: ').lower()
    amount = input('shares or captial (eg. 10 or $1000): ').lower()
    if amount[0] == '$':
        port.insert(stock, port.getPriceToShares(stock, float(amount[1::])))
    elif amount == 'rest':
        port.insert(stock, port.getPriceToShares(stock, port.getCash()))
    else:
        port.insert(stock, float(amount))

def sell():
    stock = input('SELLING\nticker: ').lower()
    amount = input('shares or capital (eg. 10 or $1000): ').lower()
    if amount[0] == '$': # differentiating between number of shares to sell and amount of money in holding
        port.insert(stock, -port.getPriceToShares(stock, float(amount[1::])))
    elif amount == 'all':
        port.insert(stock, -port.getShares(stock))
    else:
        port.insert(stock, -float(amount))

def sellAll():
    x = 1
    for stock in port.getValuesList()[1::]:
        ticker = port.getValuesList()[x][0]
        shares = -port.getValuesList()[x][1]
        port.insert(ticker, shares)

def startup():
    print('\n~~~~~~Happy Trading~~~~~~\n')
    while True:
        userInput = input('action: ').lower()
        if userInput == 'help' or userInput == 'h':
            help()
        elif userInput == 'p': # to check portfolio
            port.toString()
        elif userInput == 'b': # to buy stock
            buy()
        elif userInput == 's': # to sell stock
            sell()
        elif userInput == 's all': # sells all stocks
            sellAll()
        elif userInput == 'bal': # get balance
            print('--> Cash Balance: $' + str(round(port.getCash(), 2)))
        elif userInput == 'nw' or userInput == 'net worth':
            print('--> Net Worth: $' + str(round(port.getNetWorth(), 2)))
        elif userInput == 'e':
            break
        
    port.conn.close()

    


# creates a portfolio object 
port = Portfolio('portfolio.db', 'cashBalance', 500) 

startup()









