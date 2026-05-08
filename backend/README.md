# TODO
1. backend/src/tickets/interface/router.py:42 — implement list_tickets.
2. Unskip tests/integration/tickets/test_tickets_router.py:33 and write the body.
3. backend/src/tickets/interface/router.py:53 — implement get_ticket (404 on KeyError — you'll need from fastapi import HTTPException).
4. Unskip the two TestGetTicket tests and fill them in.
5. backend/src/tickets/interface/router.py:67 — implement assign_ticket (404 on KeyError, 409 on ValueError; you'll also need AssignTicketCommand in the imports).
6. Unskip the two TestAssignTicket tests and fill them in.

## How to run:

docker compose up -d postgres
uv run pytest tests/integration -v

You should see 1 passed, 5 skipped initially. As you implement and unskip, watch the count flip.

Optional Alembic sanity check:

uv run alembic upgrade head    # creates tickets table
uv run alembic downgrade base  # drops it
uv run alembic upgrade head    # back up

Run those against the docker-compose Postgres if you want to verify the migration works end-to-end. Tests bypass Alembic and use Base.metadata.create_all directly for speed.

When everything's green, milestone 3 is yours.