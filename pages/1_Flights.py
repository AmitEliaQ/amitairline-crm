"""AmitAirline CRM — Flights: search flights and view a passenger manifest."""

import pandas as pd
import streamlit as st

from db import ensure_schema, get_connection

st.set_page_config(page_title="Flights - AmitAirline CRM", page_icon="\U0001f6eb", layout="wide")

conn = get_connection()
ensure_schema(conn)

st.title("\U0001f6eb Flights")

col1, col2, col3 = st.columns(3)
search = col1.text_input("Search (flight number / origin / destination)")
date_from = col2.date_input("Departure from", value=None)
date_to = col3.date_input("Departure to", value=None)

query = (
    "SELECT flight_id, flight_number, origin, destination, departure_time, "
    "arrival_time, aircraft, capacity FROM flights WHERE 1=1"
)
params: list = []
if search:
    like = f"%{search}%"
    query += " AND (flight_number LIKE ? OR origin LIKE ? OR destination LIKE ?)"
    params += [like, like, like]
if date_from:
    query += " AND date(departure_time) >= ?"
    params.append(date_from.strftime("%Y-%m-%d"))
if date_to:
    query += " AND date(departure_time) <= ?"
    params.append(date_to.strftime("%Y-%m-%d"))
query += " ORDER BY departure_time"

df = pd.read_sql_query(query, conn, params=params)

st.write(f"{len(df)} flight(s) found")

df_display = df.drop(columns=["flight_id"]).rename(
    columns={
        "flight_number": "Flight",
        "origin": "Origin",
        "destination": "Destination",
        "departure_time": "Departure",
        "arrival_time": "Arrival",
        "aircraft": "Aircraft",
        "capacity": "Capacity",
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
    flight = df.iloc[selected_rows[0]]
    st.subheader(
        f"Manifest — {flight['flight_number']} "
        f"({flight['origin']} → {flight['destination']})"
    )
    manifest = pd.read_sql_query(
        """
        SELECT c.first_name || ' ' || c.last_name AS "Passenger",
               b.seat AS "Seat", b.fare AS "Fare", b.booking_date AS "Booked On"
        FROM bookings b
        JOIN customers c USING(customer_id)
        WHERE b.flight_id = ? AND b.status = 'Confirmed'
        ORDER BY b.seat
        """,
        conn,
        params=(int(flight["flight_id"]),),
    )
    if manifest.empty:
        st.info("No confirmed passengers for this flight yet.")
    else:
        st.dataframe(manifest, hide_index=True)
else:
    st.info("Select a flight above to see its passenger manifest.")

conn.close()
