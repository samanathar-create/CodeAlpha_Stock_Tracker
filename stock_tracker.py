# ==========================================
# STOCK PORTFOLIO MANAGEMENT SYSTEM
# PART 1
# ==========================================

import sqlite3
import hashlib
import random
from datetime import datetime


# ================= DATABASE =================

class Database:

    def __init__(self):
        self.conn = sqlite3.connect("stock_manager.db")
        self.cursor = self.conn.cursor()
        self.create_tables()


    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
        """)


        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            stock TEXT,
            quantity INTEGER,
            buy_price REAL
        )
        """)


        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            stock TEXT,
            quantity INTEGER,
            price REAL,
            date TEXT
        )
        """)


        self.conn.commit()



# ================= USER CLASS =================

class User:

    def __init__(self, username, password):

        self.username = username
        self.password = self.encrypt(password)


    def encrypt(self, password):

        return hashlib.sha256(
            password.encode()
        ).hexdigest()



    def register(self, db):

        try:

            db.cursor.execute(
                """
                INSERT INTO users(username,password)
                VALUES(?,?)
                """,
                (self.username,self.password)
            )

            db.conn.commit()

            print("\nAccount created successfully!")

        except sqlite3.IntegrityError:

            print("\nUsername already exists!")




    def login(self, db):

        db.cursor.execute(
            """
            SELECT * FROM users
            WHERE username=? AND password=?
            """,
            (self.username,self.password)
        )


        result = db.cursor.fetchone()


        return result is not None




# ================= STOCK MARKET =================

class StockMarket:


    def __init__(self):

        self.prices = {

            "AAPL":180,
            "TSLA":250,
            "GOOGL":140,
            "MSFT":330,
            "AMZN":150,
            "META":300

        }



    def update_prices(self):

        for stock in self.prices:

            change = random.randint(-5,5)

            self.prices[stock] += change


            if self.prices[stock] < 1:

                self.prices[stock] = 1




    def show_market(self):

        self.update_prices()


        print("\n====== STOCK MARKET ======")


        for stock,price in self.prices.items():

            print(
                stock,
                ": $",
                price
            )





# ================= PORTFOLIO CLASS =================

class Portfolio:


    def __init__(self, db):

        self.db = db



    def buy_stock(self,user,market):


        market.show_market()


        stock = input(
            "\nEnter stock name: "
        ).upper()



        if stock not in market.prices:

            print("Stock not available!")

            return



        try:

            quantity = int(
                input("Enter quantity: ")
            )

        except:

            print("Invalid quantity!")

            return



        price = market.prices[stock]



        self.db.cursor.execute(
            """
            INSERT INTO portfolio
            VALUES(NULL,?,?,?,?)
            """,
            (
                user,
                stock,
                quantity,
                price
            )
        )



        self.db.cursor.execute(
            """
            INSERT INTO transactions
            VALUES(NULL,?,?,?,?,?,?)
            """,
            (
                user,
                "BUY",
                stock,
                quantity,
                price,
                datetime.now().strftime("%Y-%m-%d")
            )
        )


        self.db.conn.commit()


        print("Stock bought successfully!")




    def sell_stock(self,user,market):


        stock = input(
            "Enter stock name: "
        ).upper()



        self.db.cursor.execute(
            """
            SELECT quantity
            FROM portfolio
            WHERE username=? AND stock=?
            """,
            (
                user,
                stock
            )
        )


        data = self.db.cursor.fetchone()



        if not data:

            print("Stock not found!")

            return



        quantity = int(
            input("Quantity to sell: ")
        )



        if quantity > data[0]:

            print("Not enough shares!")

            return



        self.db.cursor.execute(
            """
            UPDATE portfolio
            SET quantity = quantity - ?
            WHERE username=? AND stock=?
            """,
            (
                quantity,
                user,
                stock
            )
        )



        price = market.prices[stock]


        self.db.cursor.execute(
            """
            INSERT INTO transactions
            VALUES(NULL,?,?,?,?,?,?)
            """,
            (
                user,
                "SELL",
                stock,
                quantity,
                price,
                datetime.now().strftime("%Y-%m-%d")
            )
        )



        self.db.conn.commit()


        print("Stock sold successfully!")
        # ==========================================

# ANALYTICS + MENU SYSTEM
# ==========================================

import csv



# ================= ANALYTICS CLASS =================

class Analytics:


    def __init__(self, db):

        self.db = db



    def view_portfolio(self,user,market):


        self.db.cursor.execute(
            """
            SELECT stock,quantity,buy_price
            FROM portfolio
            WHERE username=?
            """,
            (user,)
        )


        data = self.db.cursor.fetchall()


        if not data:

            print("\nPortfolio is empty!")

            return



        total = 0


        print("\n========== MY PORTFOLIO ==========")


        for stock,quantity,buy_price in data:


            current = market.prices[stock] * quantity

            total += current


            profit = current - (buy_price * quantity)


            print(
                f"{stock} | Quantity: {quantity} | "
                f"Value: ${current} | Profit/Loss: ${profit}"
            )


        print("----------------------------")

        print(
            "Current Portfolio Value: $",
            total
        )





    def transaction_history(self,user):


        self.db.cursor.execute(
            """
            SELECT action,stock,quantity,price,date
            FROM transactions
            WHERE username=?
            """,
            (user,)
        )


        data = self.db.cursor.fetchall()



        print("\n====== TRANSACTION HISTORY ======")



        if not data:

            print("No transactions found!")

            return



        for row in data:

            print(row)





    def export_csv(self,user):


        self.db.cursor.execute(
            """
            SELECT stock,quantity,buy_price
            FROM portfolio
            WHERE username=?
            """,
            (user,)
        )


        data = self.db.cursor.fetchall()



        with open(
            "portfolio_report.csv",
            "w",
            newline=""
        ) as file:


            writer = csv.writer(file)


            writer.writerow(
                [
                    "Stock",
                    "Quantity",
                    "Buy Price"
                ]
            )


            writer.writerows(data)



        print(
            "\nCSV report created successfully!"
        )






# ================= MAIN MENU =================


def user_menu(username,db):


    market = StockMarket()

    portfolio = Portfolio(db)

    analytics = Analytics(db)



    while True:


        print("""
================================
 STOCK PORTFOLIO SYSTEM
================================

1. View Stock Market
2. Buy Stock
3. Sell Stock
4. My Portfolio
5. Transaction History
6. Export CSV Report
7. Logout

""")


        choice = input("Enter choice: ")




        if choice == "1":

            market.show_market()



        elif choice == "2":

            portfolio.buy_stock(
                username,
                market
            )



        elif choice == "3":

            portfolio.sell_stock(
                username,
                market
            )



        elif choice == "4":

            analytics.view_portfolio(
                username,
                market
            )



        elif choice == "5":

            analytics.transaction_history(
                username
            )



        elif choice == "6":

            analytics.export_csv(
                username
            )



        elif choice == "7":

            print("Logged out!")

            break



        else:

            print("Invalid choice!")





# ================= PROGRAM START =================


db = Database()



while True:


    print("""
========================

1. Register
2. Login
3. Exit

========================
""")


    option = input("Select option: ")




    if option == "1":


        username = input("Create username: ")

        password = input("Create password: ")


        user = User(
            username,
            password
        )


        user.register(db)




    elif option == "2":


        username = input("Username: ")

        password = input("Password: ")



        user = User(
            username,
            password
        )



        if user.login(db):

            print(
                "\nWelcome",
                username
            )


            user_menu(
                username,
                db
            )


        else:

            print(
                "Invalid login!"
            )




    elif option == "3":


        print(
            "Thank you for using Stock System!"
        )

        break



    else:

        print(
            "Invalid option!"
        )