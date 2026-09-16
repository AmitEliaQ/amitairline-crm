"""AmitAirline CRM — Dashboard (home page)."""

from datetime import datetime

import pandas as pd
import streamlit as st

from db import ensure_schema, get_connection

st.set_page_config(page_title="AmitAirline CRM", page_icon="✈️", layout="wide")

conn = get_connection()
ensure_schema(conn)

st.title("✈️ AmitAirline CRM")
st.caption("Dashboard")

now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

total_customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
total_flights = conn.execute("SELECT COUNT(*) FROM flights").fetchone()[0]
upcoming_flights = conn.execute(
    "SELECT COUNT(*) FROM flights WHERE departure_time > ?", (now_str,)
).fetchone()[0]
active_bookings = conn.execute(
    "SELECT COUNT(*) FROM bookings WHERE status = 'Confirmed'"
).fetchone()[0]
total_revenue = conn.execute(
    "SELECT COALESCE(SUM(fare), 0) FROM bookings WHERE status = 'Confirmed'"
).fetchone()[0]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Customers", total_customers)
col2.metric("Flights", total_flights)
col3.metric("Upcoming Flights", upcoming_flights)
col4.metric("Active Bookings", active_bookings)
col5.metric("Revenue (Confirmed)", f"${total_revenue:,.2f}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Next 5 Upcoming Flights")
    df = pd.read_sql_query(
        """
        SELECT flight_number AS "Flight", origin AS "Origin",
               destination AS "Destination", departure_time AS "Departure"
        FROM flights
        WHERE departure_time > ?
        ORDER BY departure_time ASC
        LIMIT 5
        """,
        conn,
        params=(now_str,),
    )
    if df.empty:
        st.info("No upcoming flights.")
    else:
        st.dataframe(df, hide_index=True)

with right:
    st.subheader("5 Most Recent Bookings")
    df = pd.read_sql_query(
        """
        SELECT b.booking_id AS "ID",
               c.first_name || ' ' || c.last_name AS "Customer",
               f.flight_number AS "Flight",
               b.booking_date AS "Booked On",
               b.status AS "Status"
        FROM bookings b
        JOIN customers c USING(customer_id)
        JOIN flights f USING(flight_id)
        ORDER BY b.booking_date DESC, b.booking_id DESC
        LIMIT 5
        """,
        conn,
    )
    if df.empty:
        st.info("No bookings yet.")
    else:
        st.dataframe(df, hide_index=True)

conn.close()
