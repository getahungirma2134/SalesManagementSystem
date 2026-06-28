import streamlit as st
import pandas as pd
import datetime
import io
from reportlab.platypus import SimpleDocTemplate, Table
from database import get_connection


def admin_dashboard():

    st.title("👑 Admin Dashboard")

    conn = get_connection()
    cursor = conn.cursor()


    # =====================
    # CREATE EMPLOYEE
    # =====================

    st.subheader("👤 Create Employee")

    name = st.text_input("Employee Name")

    department = st.selectbox(
        "Department",
        ["IT", "Finance", "Sales"]
    )

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )


    if st.button("Create Employee"):

        if name and username and password:

            cursor.execute(
                """
                INSERT INTO Employees
                (FullName, Department)
                VALUES (?,?)
                """,
                (
                    name,
                    department
                )
            )

            conn.commit()

            employee_id = cursor.lastrowid


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
                    employee_id
                )
            )

            conn.commit()

            st.success(
                "Employee Created ✅"
            )

        else:
            st.warning(
                "Fill all fields"
            )


    st.divider()



    # =====================
    # EMPLOYEE LIST
    # =====================

    st.subheader("📋 Employees List")


    employees = pd.read_sql(
        """
        SELECT *
        FROM Employees
        ORDER BY EmployeeID DESC
        """,
        conn
    )


    search = st.text_input(
        "🔍 Search Employee"
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
        use_container_width=True
    )


    st.divider()



    # =====================
    # SALES FILTER
    # =====================

    st.subheader("📅 Filter Sales")


    col1, col2 = st.columns(2)


    with col1:

        start_date = st.date_input(
            "Start Date",
            datetime.date(2026,6,27)
        )


    with col2:

        end_date = st.date_input(
            "End Date",
            datetime.date.today()
        )


    sales = pd.read_sql(
        """
        SELECT *
        FROM Sales
        WHERE SaleDate
        BETWEEN ? AND ?
        ORDER BY SaleDate DESC
        """,
        conn,
        params=(
            start_date,
            end_date
        )
    )


    st.subheader(
        "📊 All Sales"
    )


    st.write(
        "Sales rows:",
        len(sales)
    )


    st.dataframe(
        sales,
        use_container_width=True
    )


    st.download_button(
        "📥 Download Sales CSV",
        sales.to_csv(index=False),
        "sales.csv",
        "text/csv"
    )
    # =====================
    # EXPORT SALES
    # =====================

    if len(sales) > 0:

        buffer = io.BytesIO()


        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:

            sales.to_excel(
                writer,
                index=False,
                sheet_name="Sales"
            )


        st.download_button(
            label="📥 Download Sales Excel",
            data=buffer.getvalue(),
            file_name="sales_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="excel_download"
        )


        st.download_button(
            label="📄 Download Sales PDF",
            data=sales.to_csv(index=False),
            file_name="sales_report.pdf",
            mime="application/pdf",
            key="pdf_download"
        )



    # =====================
    # SALES SUMMARY
    # =====================

    if len(sales) > 0:

        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "💰 Total Sales",
                sales["Sales"].sum()
            )


        with col2:

            st.metric(
                "📈 Total Profit",
                sales["Profit"].sum()
            )



    st.divider()



    # =====================
    # SALES CHART
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


        st.subheader(
            "📊 Sales Chart"
        )


        st.bar_chart(
            chart.set_index(
                "Employee"
            )["TotalSales"]
        )


        st.subheader(
            "📈 Profit Chart"
        )


        st.line_chart(
            chart.set_index(
                "Employee"
            )["TotalProfit"]
        )


    # =====================
    # UPDATE EMPLOYEE
    # =====================

    st.divider()

    st.subheader("✏️ Update Employee")


    if len(employees) > 0:

        selected_id = st.selectbox(
            "Select Employee ID",
            employees["EmployeeID"]
        )


        new_name = st.text_input(
            "New Name"
        )


        new_department = st.selectbox(
            "New Department",
            ["IT","Finance","Sales"]
        )


        if st.button("Update Employee"):


            cursor.execute(
                """
                UPDATE Employees
                SET FullName=?,
                    Department=?
                WHERE EmployeeID=?
                """,
                (
                    new_name,
                    new_department,
                    selected_id
                )
            )


            conn.commit()


            st.success(
                "Employee Updated ✅"
            )



        # =====================
    # DELETE EMPLOYEE
    # =====================

    st.subheader("🗑️ Delete Employee")


    if len(employees) > 0:

        delete_id = st.selectbox(
            "Employee to delete",
            employees["EmployeeID"],
            key="delete"
        )


        if st.button("Delete Employee"):


            cursor.execute(
                """
                DELETE FROM Users
                WHERE EmployeeID=?
                """,
                (delete_id,)
            )


            cursor.execute(
                """
                DELETE FROM Employees
                WHERE EmployeeID=?
                """,
                (delete_id,)
            )


            conn.commit()


            st.warning(
                "Employee Deleted 🗑️"
            )



        # =====================
    # RESET EMPLOYEE PASSWORD
    # =====================

    st.divider()

    st.subheader("🔐 Reset Employee Password")


    if len(employees) > 0:


        reset_id = st.selectbox(
            "Select Employee",
            employees["EmployeeID"],
            key="reset_employee_select"
        )


        employee_new_password = st.text_input(
            "Employee New Password",
            type="password",
            key="employee_password_reset_input"
        )


        if st.button(
            "Reset Employee Password",
            key="employee_reset_button"
        ):


            if employee_new_password:


                cursor.execute(
                    """
                    UPDATE Users
                    SET Password=?
                    WHERE EmployeeID=?
                    """,
                    (
                        employee_new_password,
                        reset_id
                    )
                )


                conn.commit()


                st.success(
                    "Employee Password Reset ✅"
                )


            else:

                st.warning(
                    "Enter new password"
                )



    conn.close()