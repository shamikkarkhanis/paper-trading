# author: Shamik Karkhanis
# created: 11-22-21
# last edit: 11-22-21
# version: 1.0

# imports
from yahoo_fin import stock_info as si
import sqlite3

# stock class containing all actions concerning the user
class User:

     # takes in initial balance value
    def __init__(self, bal):
        self.bal = bal

    def getBal(self):
        return self.bal
    
    def balToString(self):
        return "Balance: $" + str(self.bal)

    def editBal(self, amount):
        self.bal += amount

class Portfolio:

    def __init__(self, conn):
        
        # db objects 
        self.conn = sqlite3.connect(conn)
        self.c = self.conn.cursor()

        print('connected to database')

        # creating db if not already created 
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
        ticker TEXT PRIMARY KEY NOT NULL,
        shares DOUBLE NOT NULL
        );''')
        print('table created')
    
    def close(self):
        self.conn.close()

    def addStock(self, ticker, shares):
        self.conn.execute('INSERT INTO portfolio VALUES (?, ?)', (ticker, shares))
        print('added')
        
        self.conn.commit()

    def getPortfolio(self):
        self.conn.execute('''SELECT ticker, shares from portfolio;''')


# testing 
shamik = User(200)
print(shamik.getBal())
print(shamik.balToString())

port = Portfolio('portfolio.db') 
port.addStock('goog', 100)
print(port.getPortfolio())





