import streamlit as st
from database import get_connection


def login(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT Username, Role, EmployeeID
        FROM Users
        WHERE Username=?
        AND Password=?
        """,
        (
            username.strip(),
            password.strip()
        )
    )

    user = cursor.fetchone()

    conn.close()


    if user:

        st.session_state.login = True
        st.session_state.username = user[0]
        st.session_state.role = user[1]
        st.session_state.employee_id = user[2]

        return True


    return False