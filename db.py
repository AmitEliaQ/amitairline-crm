"""Shared SQLite connection and schema for the AmitAirline CRM."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "airline.db"

SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    email       TEXT NOT NULL,
    phone       TEXT,
    city        TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE flights (
    flight_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number  TEXT NOT NULL,
    origin         TEXT NOT NULL,
    destination    TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time   TEXT NOT NULL,
    aircraft       TEXT,
    capacity       INTEGER NOT NULL
);

CREATE TABLE bookings (
    booking_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id  INTEGER NOT NULL REFERENCES customers(customer_id),
    flight_id    INTEGER NOT NULL REFERENCES flights(flight_id),
    booking_date TEXT NOT NULL,
    seat         TEXT,
    fare         REAL NOT NULL,
    status       TEXT NOT NULL DEFAULT 'Confirmed' CHECK (status IN ('Confirmed', 'Cancelled'))
);

CREATE INDEX idx_bookings_customer_id ON bookings(customer_id);
CREATE INDEX idx_bookings_flight_id ON bookings(flight_id);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_schema(conn: sqlite3.Connection, drop_existing: bool = False) -> None:
    """Create tables if they don't exist. If drop_existing, wipe and recreate them."""
    if drop_existing:
        conn.executescript(
            """
            DROP TABLE IF EXISTS bookings;
            DROP TABLE IF EXISTS flights;
            DROP TABLE IF EXISTS customers;
            """
        )
        conn.executescript(SCHEMA)
        conn.commit()
        return

    existing = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if {"customers", "flights", "bookings"} - existing:
        conn.executescript(SCHEMA)
        conn.commit()
