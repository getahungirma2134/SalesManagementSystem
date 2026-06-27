import pyodbc


def get_connection():

    conn = pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost\\SQLEXPRESS;"
        "Database=SalesManagementSystem;"
        "Trusted_Connection=yes;"
    )

    return conn


def execute_query(query, params=()):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        query,
        params
    )

    conn.commit()

    conn.close()



def fetch_data(query, params=()):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        query,
        params
    )

    rows = cursor.fetchall()

    conn.close()

    return rows