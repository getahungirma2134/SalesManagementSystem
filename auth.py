import streamlit as st
import hashlib
from database import get_connection


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()



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
            username,
            hash_password(password)
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



def logout():

    st.session_state.login = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.employee_id = None