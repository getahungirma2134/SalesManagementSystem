import streamlit as st
import pandas as pd
import datetime as dt
from datetime import datetime
import io
import random

from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

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
            dt.date(2026,6,27)
        )


    with col2:

        end_date = st.date_input(
            "End Date",
            dt.date.today()
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
    width="stretch"
    )
    # =====================
    # EXPORT SALES
    # =====================

    st.subheader("📥 Export Reports")


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
            "📊 Download Excel (.xlsx)",
            buffer.getvalue(),
            "sales_report.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


        st.download_button(
            "📑 Download CSV",
            sales.to_csv(index=False),
            "sales_report.csv",
            "text/csv"
        )
    # =====================
    # PDF REPORT
    # =====================

    if len(sales) > 0:

        pdf_buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            pdf_buffer
        )

        elements = []

        styles = getSampleStyleSheet()


        elements.append(
            Paragraph(
                "Sales Report",
                styles["Title"]
            )
        )

        elements.append(
            Spacer(1,12)
        )


        data = [
            list(sales.columns)
        ]


        for row in sales.values.tolist():
            data.append(row)


        table = Table(data)

        elements.append(table)


        doc.build(elements)


        pdf_buffer.seek(0)


        st.download_button(
            "📄 Download PDF Report",
            pdf_buffer,
            "sales_report.pdf",
            "application/pdf",
            key="pdf_report"
        )
    # =====================
# RECEIPT STYLE INVOICE
# =====================

if len(sales) > 0:

    invoice_buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        invoice_buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    content = []


    invoice_no = datetime.now().strftime("%Y%m%d%H%M")


    content.append(
        Paragraph(
            "🏪 SALES MANAGEMENT SYSTEM",
            styles["Title"]
        )
    )


    content.append(
        Paragraph(
            f"Invoice No: INV-{invoice_no}",
            styles["Normal"]
        )
    )


    content.append(
        Paragraph(
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"]
        )
    )


    content.append(
        Spacer(1,12)
    )


    invoice_data = [
        [
            "Product ID",
            "Qty",
            "Amount"
        ]
    ]


    for row in sales.itertuples():

        invoice_data.append(
            [
                str(row.ProductID),
                str(row.Quantity),
                str(row.Sales)
            ]
        )


    invoice_data.append(
        [
            "",
            "TOTAL",
            str(sales["Sales"].sum())
        ]
    )


    table = Table(invoice_data)

    content.append(table)


    content.append(
        Spacer(1,20)
    )


    content.append(
        Paragraph(
            "Thank you for shopping with us 🙏",
            styles["Heading2"]
        )
    )


    doc.build(content)


    invoice_buffer.seek(0)


    st.download_button(
        "🧾 Download Invoice Receipt",
        invoice_buffer,
        "invoice_receipt.pdf",
        "application/pdf",
        key="invoice_receipt"
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
    # USER MANAGEMENT
    # =====================

    st.subheader("👥 User Management")

    users = pd.read_sql(
        "SELECT Username FROM Users",
        conn
    )

    if len(users) > 0:

        reset_user = st.selectbox(
            "Select User",
            users["Username"],
            key="reset_user"
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            key="new_password"
        )


        if st.button(
            "Reset Password",
            key="reset_btn"
        ):

            cursor.execute(
                """
                UPDATE Users
                SET Password=?
                WHERE Username=?
                """,
                (
                    new_password,
                    reset_user
                )
            )

            conn.commit()

            st.success("Password Reset")






    # =====================
    # CLOSE DATABASE
    # =====================

    conn.close()
