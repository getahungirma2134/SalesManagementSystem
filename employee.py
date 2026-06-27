import streamlit as st
import pandas as pd
from datetime import date

from database import get_connection


def employee_dashboard():

    emp_id = st.session_state.employee_id


    st.title("👤 Employee Dashboard")


    conn = get_connection()
    cursor = conn.cursor()


    employee = pd.read_sql(
        """
        SELECT *
        FROM Employees
        WHERE EmployeeID=?
        """,
        conn,
        params=(emp_id,)
    )


    if len(employee) == 0:

        st.error("Employee not found")
        conn.close()
        return


    name = employee.iloc[0]["FullName"]
    dept = employee.iloc[0]["Department"]


    st.write("Name:", name)
    st.write("Department:", dept)



    st.subheader("➕ Add My Sale")


    sales = st.number_input(
        "Sales",
        min_value=0
    )


    profit = st.number_input(
        "Profit",
        min_value=0
    )


    sale_date = st.date_input(
        "Sale Date",
        date.today()
    )



    if st.button("Save Sale"):


        cursor.execute(
            """
            INSERT INTO Sales
            (
            EmployeeID,
            Sales,
            Profit,
            SaleDate
            )
            VALUES(?,?,?,?)
            """,
            (
                emp_id,
                sales,
                profit,
                sale_date
            )
        )


        conn.commit()

        st.success("Sale Saved Successfully ✅")



    st.subheader("📊 My Sales")


    df = pd.read_sql(
        """
        SELECT *
        FROM Sales
        WHERE EmployeeID=?
        """,
        conn,
        params=(emp_id,)
    )


    st.dataframe(df)


    if len(df) > 0:

        col1, col2 = st.columns(2)


        with col1:
            st.metric(
                "💰 Total Sales",
                df["Sales"].sum()
            )


        with col2:
            st.metric(
                "📈 Total Profit",
                df["Profit"].sum()
            )


    conn.close()