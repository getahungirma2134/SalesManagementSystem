import streamlit as st

from auth import login, logout
from employee import employee_dashboard
from admin_dashboard import admin_dashboard
from database import get_connection
from database import create_tables

create_tables()


st.set_page_config(
    page_title="Sales Management System",
    page_icon="📊",
    layout="wide"
)


# ==========================
# DEBUG - CHECK USERS
# ==========================

conn = get_connection()
cursor = conn.cursor()



conn.close()



# ==========================
# SESSION
# ==========================

if "login" not in st.session_state:
    st.session_state.login = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "employee_id" not in st.session_state:
    st.session_state.employee_id = None



# ==========================
# LOGIN PAGE
# ==========================

if not st.session_state.login:

    st.title("🔐 Sales Management System")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )


    if st.button("Login"):

        if login(username, password):

            st.success(
                "Login Successful ✅"
            )

            st.rerun()

        else:

            st.error(
                "Invalid Username or Password ❌"
            )


    st.stop()



# ==========================
# AFTER LOGIN
# ==========================


st.sidebar.success(
    f"Welcome {st.session_state.username}"
)

st.sidebar.write(
    "Role:",
    st.session_state.role
)



if st.sidebar.button("🚪 Logout"):

    logout()

    st.rerun()



# ==========================
# DASHBOARD
# ==========================


if st.session_state.role == "Admin":

    admin_dashboard()



elif st.session_state.role == "Employee":

    employee_dashboard()



else:

    st.error(
        "Unknown role"
    )



# =====================
# PRODUCT MANAGEMENT
# =====================

if st.session_state.role == "Admin":

    st.divider()

    st.subheader("📦 Product Management")


    product_name = st.text_input("Product Name")

    category = st.text_input("Category")


    quantity = st.number_input(
        "Quantity",
        min_value=0
    )


    cost = st.number_input(
        "Cost Price",
        min_value=0.0
    )


    selling = st.number_input(
        "Selling Price",
        min_value=0.0
    )


    supplier = st.text_input(
        "Supplier"
    )


    if st.button("Save Product"):

        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute(
            """
            INSERT INTO Products
            (
            ProductName,
            Category,
            Quantity,
            CostPrice,
            SellingPrice,
            Supplier,
            DateAdded
            )
            VALUES
            (?, ?, ?, ?, ?, ?, DATE('now'))
            """,
            (
                product_name,
                category,
                quantity,
                cost,
                selling,
                supplier
            )
        )


        conn.commit()
        conn.close()


        st.success(
            "Product Saved ✅"
        )

# =====================
# VIEW PRODUCTS
# =====================

st.divider()

st.subheader("📋 Products List")


conn = get_connection()

products = conn.execute(
    """
    SELECT
    ProductID,
    ProductName,
    Category,
    Quantity,
    CostPrice,
    SellingPrice,
    Supplier,
    DateAdded
    FROM Products
    """
).fetchall()

conn.close()


if products:

    import pandas as pd

    df = pd.DataFrame(
        products,
        columns=[
            "ID",
            "Product",
            "Category",
            "Qty",
            "Cost",
            "Selling",
            "Supplier",
            "Date"
        ]
    )


    st.dataframe(
        df,
        use_container_width=True
    )


else:

    st.info(
        "No products found"
    )


# =====================
# UPDATE STOCK
# =====================

if st.session_state.role == "Admin":

    st.divider()

    st.subheader("📦 Update Stock")


    conn = get_connection()

    products = conn.execute(
        """
        SELECT ProductID, ProductName, Quantity
        FROM Products
        """
    ).fetchall()

    conn.close()


    if products:

        product_names = [
            f"{p[0]} - {p[1]} (Stock: {p[2]})"
            for p in products
        ]


        selected = st.selectbox(
            "Select Product",
            product_names
        )


        add_qty = st.number_input(
            "Add Quantity",
            min_value=0
        )


        if st.button("Update Stock"):

            product_id = int(
                selected.split("-")[0]
            )


            conn = get_connection()
            cursor = conn.cursor()


            cursor.execute(
                """
                UPDATE Products
                SET Quantity = Quantity + ?
                WHERE ProductID=?
                """,
                (
                    add_qty,
                    product_id
                )
            )


            conn.commit()
            conn.close()


            st.success("Stock Updated ✅")

# =====================
# CHANGE PASSWORD
# =====================


st.divider()

st.subheader("🔐 Change Password")


old_password = st.text_input(
    "Old Password",
    type="password"
)


new_password = st.text_input(
    "New Password",
    type="password"
)


confirm_password = st.text_input(
    "Confirm Password",
    type="password"
)



if st.button("Change Password"):


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM Users
        WHERE Username=?
        AND Password=?
        """,
        (
            st.session_state.username,
            old_password
        )
    )


    user = cursor.fetchone()



    if user:


        if new_password == confirm_password:


            cursor.execute(
                """
                UPDATE Users
                SET Password=?
                WHERE Username=?
                """,
                (
                    new_password,
                    st.session_state.username
                )
            )


            conn.commit()


            st.success(
                "Password Changed ✅"
            )


        else:

            st.error(
                "New passwords do not match"
            )


    else:

        st.error(
            "Old password incorrect"
        )


    conn.close()