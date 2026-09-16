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

## 2026-09-16 — Phase 3: Booking management

Built:
- `pages/3_Bookings.py` — "New Booking" form (customer/flight pickers, seat,
  fare) that inserts a Confirmed booking; "Existing Bookings" list with
  status/search filters and row-select to cancel a Confirmed booking
  (status UPDATE, never a DELETE).
- Added an "Add New Customer" form to `pages/2_Customers.py`.
- Fixed a display bug found during testing: empty `phone`/`seat` values
  rendered as the literal text "None" in tables — fixed by calling
  `.fillna("")` on the query results before display (Customers and
  Bookings pages).

Tested (in a running browser session):
- Added a test customer ("Zephyr Testperson"), confirmed they appeared in
  Customers search.
- Booked them on flight AM936 (Seattle → Osaka), seat 9Z — confirmed the
  booking appeared in Existing Bookings, in AM936's passenger manifest
  (Flights page), and in the customer's booking history (Customers page).
- Cancelled the booking — confirmed status flipped to Cancelled, the
  passenger disappeared from the flight manifest (Confirmed-only), but the
  booking stayed visible as Cancelled in Existing Bookings and booking
  history.
- No errors in the Streamlit server log during the session.
- Removed the test customer/booking from the local `airline.db` afterward
  (not committed to git anyway — it's gitignored).

Next: Phase 4 — polish + documentation wrap-up.

## 2026-09-16 — Phase 4: Polish + documentation wrap-up (final)

Built:
- Added a "Bookings by Status" bar chart to the dashboard (`app.py`).
- Added empty-state messages ("No flights/customers/bookings match your
  search") on Flights, Customers, and Bookings when a search/filter returns
  zero rows, instead of just an empty table.
- Formatted `Fare` as currency (`$%.2f`) via `st.column_config.NumberColumn`
  in the flight manifest, customer booking history, and existing bookings
  tables.

Tested:
- Deleted `airline.db`, regenerated it with `generate_data.py`, and ran the
  app fresh (`streamlit run app.py`).
- Clicked through Dashboard → Flights → Customers → Bookings end to end:
  verified the new chart renders, currency formatting displays correctly
  (e.g. "$643.89"), and searching for a nonexistent flight/customer/booking
  shows the new empty-state message instead of an empty table.
- No errors in the Streamlit server log during the full smoke test.

This closes out all 4 phases. The app is feature-complete for its scope:
dashboard, flight search + manifest, customer search + history + add,
booking create/cancel. Documented non-goals (no auth, no overbooking/seat
checks, no multi-leg itineraries) remain intentional and unchanged.
