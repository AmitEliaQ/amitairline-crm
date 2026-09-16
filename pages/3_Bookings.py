"""AmitAirline CRM — Bookings: create new bookings and manage existing ones."""

from datetime import date

import pandas as pd
import streamlit as st

from db import ensure_schema, get_connection

st.set_page_config(page_title="Bookings - AmitAirline CRM", page_icon="\U0001f4dd", layout="wide")

conn = get_connection()
ensure_schema(conn)

st.title("\U0001f4dd Bookings")

st.subheader("New Booking")

customers_df = pd.read_sql_query(
    "SELECT customer_id, first_name || ' ' || last_name || ' (' || email || ')' AS label "
    "FROM customers ORDER BY last_name, first_name",
    conn,
)
flights_df = pd.read_sql_query(
    "SELECT flight_id, flight_number || ': ' || origin || ' → ' || destination || "
    "' (' || departure_time || ')' AS label FROM flights ORDER BY departure_time",
    conn,
)

if customers_df.empty or flights_df.empty:
    st.warning("Need at least one customer and one flight before creating a booking.")
else:
    with st.form("new_booking_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        customer_label = col1.selectbox("Customer", customers_df["label"])
        flight_label = col2.selectbox("Flight", flights_df["label"])

        col3, col4 = st.columns(2)
        seat = col3.text_input("Seat (e.g. 14C)")
        fare = col4.number_input("Fare ($)", min_value=0.0, step=10.0, value=199.99)

        submitted = st.form_submit_button("Create Booking")
        if submitted:
            customer_id = int(
                customers_df.loc[customers_df["label"] == customer_label, "customer_id"].iloc[0]
            )
            flight_id = int(
                flights_df.loc[flights_df["label"] == flight_label, "flight_id"].iloc[0]
            )
            conn.execute(
                "INSERT INTO bookings (customer_id, flight_id, booking_date, seat, fare, status) "
                "VALUES (?, ?, ?, ?, ?, 'Confirmed')",
                (customer_id, flight_id, date.today().isoformat(), seat or None, fare),
            )
            conn.commit()
            st.success("Booking created.")
            st.rerun()

st.divider()

st.subheader("Existing Bookings")

col1, col2 = st.columns(2)
status_filter = col1.selectbox("Status", ["All", "Confirmed", "Cancelled"])
search = col2.text_input("Search (customer name / flight number)")

query = """
    SELECT b.booking_id, c.first_name || ' ' || c.last_name AS customer_name,
           f.flight_number, f.origin, f.destination, f.departure_time,
           b.seat, b.fare, b.status, b.booking_date
    FROM bookings b
    JOIN customers c USING(customer_id)
    JOIN flights f USING(flight_id)
    WHERE 1=1
"""
params: list = []
if status_filter != "All":
    query += " AND b.status = ?"
    params.append(status_filter)
if search:
    like = f"%{search}%"
    query += " AND (c.first_name LIKE ? OR c.last_name LIKE ? OR f.flight_number LIKE ?)"
    params += [like, like, like]
query += " ORDER BY b.booking_date DESC, b.booking_id DESC"

df = pd.read_sql_query(query, conn, params=params).fillna("")
st.write(f"{len(df)} booking(s) found")

if df.empty:
    st.info("No bookings match your filters.")
    selected_rows = []
else:
    df_display = df.rename(
        columns={
            "booking_id": "ID",
            "customer_name": "Customer",
            "flight_number": "Flight",
            "origin": "Origin",
            "destination": "Destination",
            "departure_time": "Departure",
            "seat": "Seat",
            "fare": "Fare",
            "status": "Status",
            "booking_date": "Booked On",
        }
    )

    event = st.dataframe(
        df_display,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={"Fare": st.column_config.NumberColumn(format="$%.2f")},
    )
    selected_rows = event.selection.rows if event and event.selection else []

if selected_rows:
    booking = df.iloc[selected_rows[0]]
    st.write(
        f"Selected booking #{int(booking['booking_id'])}: {booking['customer_name']} "
        f"on {booking['flight_number']} — status **{booking['status']}**"
    )
    if booking["status"] == "Confirmed":
        if st.button("Cancel this booking"):
            conn.execute(
                "UPDATE bookings SET status = 'Cancelled' WHERE booking_id = ?",
                (int(booking["booking_id"]),),
            )
            conn.commit()
            st.success("Booking cancelled.")
            st.rerun()
    else:
        st.info("This booking is already cancelled.")
else:
    st.info("Select a booking above to cancel it.")

conn.close()
