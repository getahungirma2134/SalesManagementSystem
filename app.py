import streamlit as st

from auth import login, logout
from employee import employee_dashboard
from admin_dashboard import admin_dashboard

st.set_page_config(
    page_title="Sales Management System",
    page_icon="📊",
    layout="wide"
)

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
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if login(username, password):
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Username or Password ❌")

    st.stop()

# ==========================
# AFTER LOGIN
# ==========================

st.sidebar.success(f"Welcome {st.session_state.username}")
st.sidebar.write("Role:", st.session_state.role)

if st.sidebar.button("🚪 Logout"):
    logout()
    st.rerun()

if st.session_state.role == "Admin":
    admin_dashboard()

elif st.session_state.role == "Employee":
    employee_dashboard()

else:
    st.error("Unknown role")
    # =====================
# CHANGE PASSWORD
# =====================

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