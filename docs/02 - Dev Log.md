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
