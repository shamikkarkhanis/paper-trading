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
    # just testing vim :]
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
                self.conn.execute("UPDATE portfolio set shares = ? where ticker = ?", (self.getValues()[ticker] + shares, ticker))
                # updates balance accordingly
        self.conn.commit()

        print('commited successfully')

    # getters

    # returns balance
    def getCash(self):
        return self.getShares(self.identifier)
    
    # portfolio value
    def getPortValue(self):
        return 1000.0 # needs to use the value of stocks times amount of owned shares ()

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
        print('')
        print('--- Portfolio ---')
        for column in self.getValuesList()[1::]:
            print(column[0], ' ', column[1]) # add value of shares for each ticker
        print('--- \nPortfolio Value: $' + str(self.getPortValue()) + '\n---\nCash Balance: $' + str(self.getCash()) + '\n---\nNet Worth: $' + str(self.getNetWorth()) + '\n-----------------')
        
# test cases

port = Portfolio('portfolio.db', 'cashBalance', 10000)
port.insert('amzn', -10)
port.toString()
port.conn.close()
print('closed successfully')
