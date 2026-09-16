"""AmitAirline CRM — Customers: search customers and view booking history."""

from datetime import date

import pandas as pd
import streamlit as st

from db import ensure_schema, get_connection

st.set_page_config(page_title="Customers - AmitAirline CRM", page_icon="\U0001f9d1‍\U0001f4bc", layout="wide")

conn = get_connection()
ensure_schema(conn)

st.title("\U0001f9d1‍\U0001f4bc Customers")

with st.expander("Add New Customer"):
    with st.form("new_customer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        first_name = col1.text_input("First Name")
        last_name = col2.text_input("Last Name")

        col3, col4 = st.columns(2)
        email = col3.text_input("Email")
        phone = col4.text_input("Phone")

        city = st.text_input("City")

        submitted = st.form_submit_button("Add Customer")
        if submitted:
            if not first_name or not last_name or not email:
                st.error("First name, last name, and email are required.")
            else:
                conn.execute(
                    "INSERT INTO customers (first_name, last_name, email, phone, city, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (first_name, last_name, email, phone or None, city or None, date.today().isoformat()),
                )
                conn.commit()
                st.success(f"Added {first_name} {last_name}.")
                st.rerun()

st.divider()

search = st.text_input("Search (name / email / city)")

query = (
    "SELECT customer_id, first_name, last_name, email, phone, city, created_at "
    "FROM customers WHERE 1=1"
)
params: list = []
if search:
    like = f"%{search}%"
    query += " AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR city LIKE ?)"
    params += [like, like, like, like]
query += " ORDER BY last_name, first_name"

df = pd.read_sql_query(query, conn, params=params).fillna("")

st.write(f"{len(df)} customer(s) found")

df_display = df.drop(columns=["customer_id"]).rename(
    columns={
        "first_name": "First Name",
        "last_name": "Last Name",
        "email": "Email",
        "phone": "Phone",
        "city": "City",
        "created_at": "Registered",
    }
)

event = st.dataframe(
    df_display,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
)

st.divider()

selected_rows = event.selection.rows if event and event.selection else []
if selected_rows:
    customer = df.iloc[selected_rows[0]]
    st.subheader(f"Booking History — {customer['first_name']} {customer['last_name']}")
    history = pd.read_sql_query(
        """
        SELECT f.flight_number AS "Flight", f.origin AS "Origin",
               f.destination AS "Destination", f.departure_time AS "Departure",
               b.seat AS "Seat", b.fare AS "Fare", b.status AS "Status"
        FROM bookings b
        JOIN flights f USING(flight_id)
        WHERE b.customer_id = ?
        ORDER BY f.departure_time DESC
        """,
        conn,
        params=(int(customer["customer_id"]),),
    )
    if history.empty:
        st.info("This customer has no bookings yet.")
    else:
        st.dataframe(history, hide_index=True)
else:
    st.info("Select a customer above to see their booking history.")

conn.close()
