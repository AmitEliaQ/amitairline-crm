"""Populate airline.db with hand-rolled synthetic data.

Safe to re-run: drops and recreates all tables each time, then reseeds.
"""

import random
from datetime import datetime, timedelta

from db import ensure_schema, get_connection

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin",
]

CITIES = [
    "Denver", "Lisbon", "Nairobi", "Toronto", "Austin", "Seattle", "Miami", "Chicago",
    "Berlin", "Osaka", "Dublin", "Auckland", "Vancouver", "Phoenix", "Atlanta",
]

DOMAINS = ["gmail.com", "outlook.com", "yahoo.com"]

AIRCRAFT = [
    "Boeing 737-800", "Boeing 787-9", "Airbus A320", "Airbus A321neo", "Embraer E190",
]

NUM_CUSTOMERS = 40
NUM_FLIGHTS = 20
NUM_BOOKINGS = 120


def gen_customers():
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}{i}@{random.choice(DOMAINS)}"
        phone = f"+1-555-{random.randint(1000, 9999)}"
        city = random.choice(CITIES)
        created_at = (
            datetime.now() - timedelta(days=random.randint(1, 400))
        ).strftime("%Y-%m-%d")
        customers.append((first, last, email, phone, city, created_at))
    return customers


def gen_flights():
    flights = []
    for _ in range(NUM_FLIGHTS):
        origin, destination = random.sample(CITIES, 2)
        departure = datetime.now() + timedelta(
            days=random.randint(-30, 45), hours=random.randint(0, 23)
        )
        arrival = departure + timedelta(hours=random.randint(1, 6))
        flight_number = f"AM{random.randint(100, 999)}"
        aircraft = random.choice(AIRCRAFT)
        capacity = random.randint(80, 220)
        flights.append(
            (
                flight_number,
                origin,
                destination,
                departure.strftime("%Y-%m-%d %H:%M"),
                arrival.strftime("%Y-%m-%d %H:%M"),
                aircraft,
                capacity,
            )
        )
    return flights


def gen_bookings(customer_ids, flight_rows):
    """flight_rows: list of (flight_id, departure_time) to compute a sane booking_date."""
    bookings = []
    now = datetime.now()
    for _ in range(NUM_BOOKINGS):
        customer_id = random.choice(customer_ids)
        flight_id, departure_time = random.choice(flight_rows)
        departure = datetime.strptime(departure_time, "%Y-%m-%d %H:%M")
        booking_date = departure - timedelta(days=random.randint(1, 120))
        if booking_date > now:
            booking_date = now - timedelta(days=random.randint(0, 5))
        seat = f"{random.randint(1, 30)}{random.choice('ABCDEF')}"
        fare = round(random.uniform(49.99, 899.99), 2)
        status = "Confirmed" if random.random() < 0.9 else "Cancelled"
        bookings.append(
            (
                customer_id,
                flight_id,
                booking_date.strftime("%Y-%m-%d"),
                seat,
                fare,
                status,
            )
        )
    return bookings


def main():
    conn = get_connection()
    ensure_schema(conn, drop_existing=True)

    cur = conn.cursor()

    cur.executemany(
        "INSERT INTO customers (first_name, last_name, email, phone, city, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        gen_customers(),
    )

    cur.executemany(
        "INSERT INTO flights (flight_number, origin, destination, departure_time, "
        "arrival_time, aircraft, capacity) VALUES (?, ?, ?, ?, ?, ?, ?)",
        gen_flights(),
    )
    conn.commit()

    customer_ids = [row[0] for row in cur.execute("SELECT customer_id FROM customers")]
    flight_rows = [
        (row[0], row[1])
        for row in cur.execute("SELECT flight_id, departure_time FROM flights")
    ]

    cur.executemany(
        "INSERT INTO bookings (customer_id, flight_id, booking_date, seat, fare, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        gen_bookings(customer_ids, flight_rows),
    )
    conn.commit()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    n_customers = cur.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    n_flights_upcoming = cur.execute(
        "SELECT COUNT(*) FROM flights WHERE departure_time > ?", (now_str,)
    ).fetchone()[0]
    n_flights_past = cur.execute(
        "SELECT COUNT(*) FROM flights WHERE departure_time <= ?", (now_str,)
    ).fetchone()[0]
    n_bookings_confirmed = cur.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = 'Confirmed'"
    ).fetchone()[0]
    n_bookings_cancelled = cur.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = 'Cancelled'"
    ).fetchone()[0]

    conn.close()

    print(f"Customers:            {n_customers}")
    print(f"Flights (upcoming):   {n_flights_upcoming}")
    print(f"Flights (past):       {n_flights_past}")
    print(f"Bookings (Confirmed): {n_bookings_confirmed}")
    print(f"Bookings (Cancelled): {n_bookings_cancelled}")


if __name__ == "__main__":
    main()
