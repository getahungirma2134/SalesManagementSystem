import sqlite3
import os


def get_connection():

    path = os.path.join(
        os.path.dirname(__file__),
        "sales.db"
    )

    return sqlite3.connect(path)



def create_tables():

    conn = get_connection()
    cursor = conn.cursor()


    # PRODUCTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
        ProductName TEXT NOT NULL,
        Category TEXT,
        Quantity INTEGER DEFAULT 0,
        CostPrice REAL DEFAULT 0,
        SellingPrice REAL DEFAULT 0,
        Supplier TEXT,
        DateAdded TEXT
    )
    """)


    conn.commit()
    conn.close()