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
        print("Table created successfully")
        print("Opened database successfully")

        # storing initial balance in database to allow access at future time
        self.identifier = identifier
        self.cashBalance = cashBalance
        # cheap way of getting around sqlite3 unique error (cannot insert if already exists)
        try:
            self.conn.execute("INSERT INTO PORTFOLIO VALUES (?, ?)", (identifier, cashBalance))
        except: 
            pass

    # misc functions

    # lalalalala
    # aww hell nawwwwwww
    # setters

    # creates database values
    def insert(self, ticker, shares):
        # cheap way of getting around sqlite3 unique error (cannot insert if already exists)
        try: 
            self.conn.execute("INSERT INTO PORTFOLIO (ticker, shares) VALUES (?, ?)", (ticker, shares))
            # updates cash balance accordingly
        except: 
            # checks for allowed values (eg. cannot sell more than you have)
            if -1*self.getShares(ticker) > shares:
                print('INSUFFICIENT FUNDS')
            else:
                if 0 > shares:
                    self.update(ticker, shares)
                    self.update(self.identifier, self.getSharesValue(ticker, shares))
                else:
                    self.update(ticker, shares)
                    self.update(self.identifier, self.getSharesValue(ticker, -shares))
        self.conn.commit()

        print('commited successfully')

    # updates database values
    def update(self, ticker, shares):
        self.conn.execute("UPDATE portfolio set shares = ? where ticker = ?", (self.getShares(ticker) + shares, ticker))

    # getters

    # returns balance
    def getCash(self):
        return round(self.getShares(self.identifier), 2)
    
    # returns shares value
    def getSharesValue(self, ticker, shares):
        return round(si.get_live_price(ticker) * shares, 2)
    
    # portfolio value
    def getPortValue(self):
        pValue = 0.0
        for column in self.getValuesList()[1::]:
            pValue += self.getSharesValue(column[0], column[1])
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
            stockValue = self.getSharesValue(column[0], column[1])
            pValue += stockValue
            print(column[0], str(column[1]), '--> $' + str(stockValue))
        print('--- \nPortfolio Value: $' + str(pValue) + '\n---\nCash Balance: $' + str(self.getCash()) + '\n---\nNet Worth: $' + str(round(self.getCash() + pValue, 2)) + '\n-----------------\n')

port = Portfolio('portfolio.db', 'cashBalance', 1000) 

port.insert('aapl', 3)
port.toString()

port.conn.close()






