# Dev Log

## 2026-09-16 — Phase 1: Scaffolding, schema, synthetic data

Built:
- `db.py` — schema (customers/flights/bookings) + `get_connection()` /
  `ensure_schema()`.
- `generate_data.py` — hand-rolled synthetic data generator (no Faker):
  40 customers, 20 flights, 120 bookings.
- `requirements.txt`.

Tested:
- Ran `generate_data.py`, confirmed via `sqlite3` that row counts matched the
  script's printed summary and a joined query
  (bookings ⋈ customers ⋈ flights) returned sane rows.
- Re-ran the script a second time — no errors, fresh consistent counts each
  time, confirming `ensure_schema(drop_existing=True)` is safe to re-run.

Next: Phase 2 — read-only Streamlit skeleton (dashboard, flights, customers).

## 2026-09-16 — Phase 2: Read-only Streamlit skeleton

Built:
- `app.py` — dashboard with metrics (customers, flights, upcoming flights,
  active bookings, revenue) and "next 5 upcoming flights" / "5 most recent
  bookings" tables.
- `pages/1_Flights.py` — search/filter flights (number, origin, destination,
  date range), row-select to view a flight's passenger manifest.
- `pages/2_Customers.py` — search customers (name/email/city), row-select to
  view booking history.

Tested:
- Ran `streamlit run app.py` and drove it in a real browser (Claude in
  Chrome).
- Confirmed dashboard metrics matched the counts from `generate_data.py`'s
  printed summary.
- Selected a flight on the Flights page and confirmed the passenger
  manifest populated correctly (Confirmed bookings only).
- Searched "Smith" on the Customers page (3 matches), selected a customer,
  confirmed booking history populated correctly.
- No errors in the Streamlit server log or browser console.
- Saved a dashboard screenshot to `docs/screenshots/dashboard.jpg` and
  linked it from the README.

Next: Phase 3 — booking management (create/cancel bookings, add customers).
