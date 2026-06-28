import sqlite3
import os

def get_connection():

    path = os.path.join(
        os.path.dirname(__file__),
        "sales.db"
    )

    return sqlite3.connect(path)