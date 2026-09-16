# Architecture

## File layout

```
CRM SQLite/
  app.py                  # dashboard (home page)
  db.py                   # DB_PATH, get_connection(), ensure_schema()
  generate_data.py        # hand-rolled synthetic data generator (idempotent)
  requirements.txt        # streamlit, pandas
  README.md
  airline.db              # generated, not hand-authored
  pages/
    1_Flights.py
    2_Customers.py
    3_Bookings.py          # added in Phase 3
  docs/
    00 - Project Hub.md
    01 - Architecture.md
    02 - Dev Log.md
```

## Schema

Three tables in `airline.db`. No separate airports/aircraft tables — kept as
plain strings since normalizing them wouldn't simplify anything at this scale.

**customers**
| column | type | notes |
|---|---|---|
| customer_id | INTEGER PK AUTOINCREMENT | |
| first_name, last_name | TEXT NOT NULL | |
| email | TEXT NOT NULL | not UNIQUE-enforced — generation guarantees no collisions |
| phone | TEXT | |
| city | TEXT | |
| created_at | TEXT | ISO date |

**flights**
| column | type | notes |
|---|---|---|
| flight_id | INTEGER PK AUTOINCREMENT | |
| flight_number | TEXT NOT NULL | e.g. `AM214`; not unique, real flight numbers repeat daily |
| origin, destination | TEXT NOT NULL | always different |
| departure_time, arrival_time | TEXT NOT NULL | ISO datetime; arrival = departure + 1-6h |
| aircraft | TEXT | cosmetic |
| capacity | INTEGER NOT NULL | 80-220; not enforced against booking counts |

**bookings**
| column | type | notes |
|---|---|---|
| booking_id | INTEGER PK AUTOINCREMENT | |
| customer_id | INTEGER NOT NULL REFERENCES customers | |
| flight_id | INTEGER NOT NULL REFERENCES flights | |
| booking_date | TEXT NOT NULL | ISO date |
| seat | TEXT | not unique-enforced |
| fare | REAL NOT NULL | |
| status | TEXT NOT NULL DEFAULT 'Confirmed' | `CHECK(status IN ('Confirmed','Cancelled'))` |

Indexes on `bookings(customer_id)` and `bookings(flight_id)` since every view
joins through bookings.

## Key decisions

- **Cancellation is a status flag, not a delete.** Keeps booking history
  intact for the customer's booking-history view and the bookings list.
- **`db.py` is the single source of truth for schema.** `ensure_schema(conn,
  drop_existing=False)` — `generate_data.py` calls it with `drop_existing=True`
  to reset and reseed; the app calls it with the default so tables always
  exist but a normal app launch never wipes data.
- **`DB_PATH` is computed from `Path(__file__).parent`**, not the current
  working directory, so `streamlit run` works regardless of where it's
  invoked from.
- **Explicit non-goals**: no overbooking checks, no seat-collision checks, no
  auth, no multi-leg itineraries, no delete of customers/flights.

## Pages (Streamlit `pages/` auto-discovery)

- `app.py` — dashboard: totals, upcoming flights, active bookings, revenue,
  a "Bookings by Status" bar chart, and small "next 5 upcoming flights" /
  "5 most recent bookings" tables.
- `pages/1_Flights.py` — search/filter flights, select a row to see its
  passenger manifest (Confirmed bookings joined with customers).
- `pages/2_Customers.py` — search customers, select a row to see booking
  history (all statuses); includes an "Add New Customer" form.
- `pages/3_Bookings.py` — new booking form + existing bookings list with
  filters + cancel action.

Display note: `pd.read_sql_query(...).fillna("")` is used before rendering
any table that may contain NULLs (e.g. an empty `phone` or `seat`), otherwise
pandas/Streamlit render the literal text "None" in the cell.
