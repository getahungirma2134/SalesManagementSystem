import streamlit as st
import pandas as pd

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


    # =====================
    # VIEW STOCK
    # =====================

    st.subheader("📦 Available Stock")


    stock = pd.read_sql(
        """
        SELECT 
        ProductName,
        Quantity,
        SellingPrice
        FROM Products
        """,
        conn
    )


    st.dataframe(stock)



    # =====================
    # MAKE SALE
    # =====================

    st.subheader("🛒 Make Sale")



    products = cursor.execute(
        """
        SELECT 
        ProductID,
        ProductName,
        Quantity,
        SellingPrice,
        CostPrice
        FROM Products
        WHERE Quantity > 0
        """
    ).fetchall()



    if products:


        product = st.selectbox(
            "Select Product",
            products,
            format_func=lambda x: x[1]
        )


        qty = st.number_input(
            "Quantity",
            min_value=1
        )


        if st.button("Sell Product"):


            if qty <= product[2]:


                total = qty * product[3]


                cost = product[4]

                profit = (product[3] - cost) * qty



                cursor.execute(
    """
    INSERT INTO Sales
    (
    EmployeeID,
    EmployeeName,
    ProductID,
    Quantity,
    Sales,
    Profit,
    SaleDate
    )
    VALUES(?,?,?,?,?,?,DATE('now'))
    """,
    (
    emp_id,
    name,
    product[0],
    qty,
    total,
    profit
    )
)



                cursor.execute(
                    """
                    UPDATE Products
                    SET Quantity = Quantity - ?
                    WHERE ProductID=?
                    """,
                    (
                    qty,
                    product[0]
                    )
                )



                conn.commit()


                st.success(
                    f"Sold Successfully ✅ Profit: {profit}"
                )


            else:

                st.error(
                    "Stock not enough ❌"
                )



    else:

        st.info(
            "No Products"
        )



    # =====================
    # MY SALES
    # =====================

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