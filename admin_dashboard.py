import streamlit as st
import pandas as pd

from database import get_connection


def admin_dashboard():

    st.title("👑 Admin Dashboard")


    conn = get_connection()
    cursor = conn.cursor()


    # CREATE EMPLOYEE

    st.subheader("👤 Create Employee")


    name = st.text_input("Employee Name")

    department = st.selectbox(
        "Department",
        ["IT","Finance","Sales"]
    )

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )


    if st.button("Create Employee"):


        cursor.execute(
            """
            INSERT INTO Employees
            (FullName, Department)
            OUTPUT INSERTED.EmployeeID
            VALUES (?,?)
            """,
            (
                name,
                department
            )
        )


        emp_id = cursor.fetchone()[0]


        cursor.execute(
            """
            INSERT INTO Users
            (Username, Password, Role, EmployeeID)
            VALUES (?,?,?,?)
            """,
            (
                username,
                password,
                "Employee",
                emp_id
            )
        )


        conn.commit()


        st.success("Employee Created ✅")



    st.divider()


    # =====================
    # SEARCH EMPLOYEE
    # =====================

    st.subheader("🔍 Search Employee")

    employees = pd.read_sql(
        "SELECT * FROM Employees",
        conn
    )

    search = st.text_input(
        "Search by name"
    )


    if search:

        employees = employees[
            employees["FullName"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]


    st.dataframe(
        employees,
        width="stretch"
    )


    # =====================
    # DATE FILTER
    # =====================

    st.subheader("📅 Filter Sales")

    col1, col2 = st.columns(2)


    with col1:
        start_date = st.date_input(
            "Start Date"
        )


    with col2:
        end_date = st.date_input(
            "End Date"
        )


    # =====================
    # SALES
    # =====================

    st.subheader("📊 All Sales")


    sales = pd.read_sql(
        """
        SELECT *
        FROM Sales
        WHERE SaleDate BETWEEN ? AND ?
        ORDER BY SaleDate DESC
        """,
        conn,
        params=(
            start_date,
            end_date
        )
    )


    st.dataframe(
        sales,
        width="stretch"
    )


    if len(sales) > 0:

        col1,col2 = st.columns(2)


        with col1:
            st.metric(
                "Total Sales",
                sales["Sales"].sum()
            )


        with col2:
            st.metric(
                "Total Profit",
                sales["Profit"].sum()
            )


    # =====================
    # CHARTS
    # =====================

    if len(sales) > 0:

        chart = pd.read_sql(
            """
            SELECT 
                E.FullName AS Employee,
                SUM(S.Sales) AS TotalSales,
                SUM(S.Profit) AS TotalProfit
            FROM Sales S
            JOIN Employees E
            ON S.EmployeeID = E.EmployeeID
            GROUP BY E.FullName
            """,
            conn
        )


        st.subheader("📊 Sales Chart")

        st.bar_chart(
            chart.set_index("Employee")["TotalSales"]
        )


        st.subheader("📈 Profit Chart")

        st.line_chart(
            chart.set_index("Employee")["TotalProfit"]
        )


    conn.close()