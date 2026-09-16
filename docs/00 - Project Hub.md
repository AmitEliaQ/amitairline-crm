# AmitAirline CRM — Project Hub

**Status**: Phase 1 complete (scaffolding, schema, synthetic data)

## Goal

A simple internal CRM for a fictional airline, "AmitAirline," so a single travel
agent can:
- Track existing flight bookings
- Manage customer registrations for flights (create/cancel bookings)

Deliberately simple — no auth, no multi-user accounts, no production-grade
guardrails (overbooking, seat collisions, etc. are explicitly out of scope).

## Stack

- Python 3.14
- Streamlit (UI)
- SQLite (`airline.db`, via the stdlib `sqlite3`)
- pandas (for `st.dataframe(pd.read_sql_query(...))` tables)

## Constraints / decisions

- No login screen — opens straight into the app.
- No Faker dependency — synthetic data is hand-rolled with plain `random` +
  small hardcoded name/city lists.
- Cancelling a booking is a status update (`Confirmed` → `Cancelled`), never a
  row delete, so history is preserved.
- Documentation lives in this `docs/` folder inside the project, not a
  separate notes vault.

## Notes

- [[01 - Architecture]] — schema, file layout, key decisions
- [[02 - Dev Log]] — phase-by-phase build log

## Phases

1. Scaffolding, schema, synthetic data generator — **done**
2. Read-only Streamlit skeleton (dashboard, flights, customers)
3. Booking management (create/cancel bookings, add customers)
4. Polish + documentation wrap-up
