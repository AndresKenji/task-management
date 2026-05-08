# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A portfolio project: a ticket and task management system for end-users and an engineering team. Backend is FastAPI in DDD layout deployed to AWS Lambda; frontend is Angular hosted on S3 + CloudFront; auth is AWS Cognito; infrastructure is Terraform; database is managed Postgres (Supabase by default, swappable via Terraform module).

This is a learning-mode collaboration: work in small milestones, explain non-obvious decisions, and pause at architectural choices for the user to weigh in.

## Stack and conventions

**Backend.** Python 3.13, FastAPI, SQLAlchemy 2 (async), Pydantic v2, Mangum (Lambda ASGI adapter), pytest. Dependencies managed by uv (`pyproject.toml` + `uv.lock`).

Layout follows Domain-Driven Design. Bounded contexts are top-level packages under `backend/src/` (`identity/`, `tickets/`, `shared/`). Each context has `domain/`, `application/`, `infrastructure/`, and `interface/` subpackages. The `interface/` layer holds FastAPI routers; `application/` holds use cases; `domain/` holds aggregates, value objects, and events with no framework imports.

Formatting is `black` (line length 100, configured in `pyproject.toml`). Linting is `flake8` (configured in `.flake8`, compatible with black). Tests are `pytest`: unit tests in `backend/tests/unit/` for domain and application (pure, no I/O); integration tests in `backend/tests/integration/` for repositories and routers.

**Frontend.** Angular 15 (TypeScript). Auth via `@aws-amplify/auth` v6. API base URL via `src/environments/environment*.ts` (introduced in milestone 8).

**Infrastructure.** Terraform 1.6+, AWS provider. Modules under `infrastructure/modules/`; per-env root modules under `infrastructure/envs/{dev,prod}/`.

**Auth.** AWS Cognito user pool. APIGW HTTP API uses a Cognito JWT authorizer. Lambda receives an already-validated JWT and reads `sub` (Cognito user ID) and groups from the request context.

**Compute.** Lambda container image (built from `backend/Dockerfile`, pushed to ECR). FastAPI is wrapped by Mangum.

**Database.** Postgres. Default provider is Supabase (cheap, free tier). The `infrastructure/modules/database/` module is a contract: it takes connection params as input and writes them to AWS Secrets Manager. Lambda reads the secret at startup. To swap to RDS or another provider, replace the module's implementation but keep the same input and output interface.

When connecting Lambda to Supabase, always use the pooler URL (PgBouncer transaction mode, port 6543), never the direct port. Lambdas do not share connections; direct connections exhaust the Postgres connection limit fast.

**Frontend hosting.** S3 (private bucket) + CloudFront with OAC, ACM cert, optional Route53. Built artifacts (`dist/task-manager/`) sync via GitHub Actions.

## Common commands

### Backend (local)

```bash
cd backend
uv sync
uv run black src tests
uv run flake8 src tests
uv run pytest
uv run pytest tests/unit
uv run pytest tests/integration
uv run uvicorn src.main:app --reload --port 8000
uv add <package>
uv add --dev <package>
uv remove <package>
```

`uv sync` installs runtime and dev dependencies into `.venv`. Run a single test with `uv run pytest tests/unit/tickets/test_ticket_aggregate.py::test_close`. Local Postgres for integration tests: `docker compose up -d postgres`.

### Frontend (local)

```bash
cd frontend/taskManager
npm install
npm start
npm run build
npm test
```

`npm start` serves at http://localhost:4200. `npm run build` outputs to `dist/task-manager/`. `npm test` runs Karma + Jasmine (test files to be added).

### Infrastructure

```bash
cd infrastructure/envs/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Always confirm `terraform apply` interactively. Never auto-apply.

After the first apply provides the ECR repo URL, build and push the Lambda image:

```bash
cd backend
docker build -t task-mgmt-api .
aws ecr get-login-password --region <region> | docker login --password-stdin <ecr-url>
docker tag task-mgmt-api:latest <ecr-url>:latest
docker push <ecr-url>:latest
aws lambda update-function-code --function-name task-mgmt-api-dev --image-uri <ecr-url>:latest
```

The Lambda Dockerfile uses uv to export pinned deps from `uv.lock` and pip-installs them into `${LAMBDA_TASK_ROOT}`. No `requirements.txt` is committed.

CI/CD (GitHub Actions) automates the build, push, and update step in `.github/workflows/ci.yml` (added in milestone 10).

## Architecture notes

### DDD layering (backend)

`<context>/domain/` holds aggregates, entities, value objects, and domain events. Pure Python: no FastAPI, no SQLAlchemy. Domain rules belong here.

`<context>/application/` holds use cases (one class per use case), DTOs, and ports (repository interfaces). Orchestrates domain objects, receives a Unit of Work, returns a result. No HTTP, no DB.

`<context>/infrastructure/` holds SQLAlchemy implementations of repository ports, Cognito client, external API clients. Framework code lives here.

`<context>/interface/` holds FastAPI routers and Pydantic request and response schemas. Translates HTTP into application use cases.

`shared/` holds cross-context base classes and infra (Entity, AggregateRoot, settings, db session, logging). Keep it small. Most things belong inside a context.

A use case looks like:

```python
class CreateTicket:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, cmd: CreateTicketCommand) -> TicketId:
        with self.uow:
            ticket = Ticket.create(title=cmd.title, reporter_id=cmd.reporter_id)
            self.uow.tickets.add(ticket)
            self.uow.commit()
        return ticket.id
```

### Auth flow

1. Frontend signs in via Amplify v6 (`signIn({ username, password })`) and receives Cognito ID and access tokens.
2. Frontend attaches `Authorization: Bearer <id_token>` to API calls via an interceptor.
3. APIGW Cognito JWT authorizer validates the token. On success, the request reaches Lambda with `requestContext.authorizer.jwt.claims` populated.
4. A FastAPI dependency reads `sub` and `cognito:groups` from the Lambda event (Mangum exposes it). No password handling, no JWT verification in Python at runtime. The bundled `pyjwt` is for local-dev token validation when no APIGW is in front.
5. Cognito groups (`admin`, `user`) drive authorization in use-case dependencies.

### Database module contract

`infrastructure/modules/database/` does not provision the database (Supabase is configured manually). It accepts `var.host`, `var.port`, `var.database`, `var.username`, and `var.password` (sensitive), and writes them to a single AWS Secrets Manager secret as JSON. It outputs `secret_arn`. The `lambda_api` module attaches the secret to the Lambda IAM role and exposes its ARN via env var; the FastAPI app reads the secret on cold start.

To swap to RDS later, replace this module with one that provisions `aws_db_instance` but keep the same outputs (`secret_arn`). No other module changes needed.

### Lambda packaging

Base image is `public.ecr.aws/lambda/python:3.13`. Deps are installed via `uv export --frozen --no-dev` piped into `pip install --target ${LAMBDA_TASK_ROOT}` so packages land at the runtime import root. `CMD ["src.main.handler"]` where `handler` is `Mangum(app)`. The image is pushed to a private ECR repo created by Terraform.

Cold start is roughly 1 to 1.5 seconds for FastAPI + SQLAlchemy + asyncpg. Acceptable for a portfolio. Skip provisioned concurrency unless the user opts in.

## Milestone roadmap

Each milestone is independently shippable, ends with something working, and pauses for the user.

1. Skeleton and tooling (done). Restructure to target layout. uv-managed `pyproject.toml`, `.flake8`, `uv.lock`. Local-dev `docker-compose.yml` runs only postgres.
2. Tickets domain (offline). Implement `Ticket` aggregate, `TicketStatus` value object, in-memory `TicketRepository`, `CreateTicket` and `AssignTicket` use cases. Pytest suite for domain and application. No FastAPI yet.
3. Tickets HTTP layer + SQLAlchemy. Add FastAPI router, Pydantic schemas, SQLAlchemy `Ticket` table, SQLAlchemy `TicketRepository` impl, Unit of Work. Integration tests against local postgres. Introduce Alembic.
4. Identity context skeleton. `User` aggregate (Cognito `sub` as ID), `UserRepository`, profile endpoint. No Cognito wiring yet; use a fake `current_user` dependency.
5. Terraform: cognito and database modules. Cognito user pool, app client, groups. Database contract module wired to Supabase secret. Apply in `dev/`. Manually verify Cognito hosted UI sign-up works.
6. Terraform: lambda_api module. ECR repo, Lambda fn, APIGW HTTP API with Cognito JWT authorizer, IAM. Wire env vars (secret ARN, Cognito pool ID). First deploy: build image, push, invoke `/health`.
7. Wire FastAPI to Cognito. Replace the fake `current_user` with a dependency that reads claims from the Lambda event. Confirm an authenticated request from a real Cognito-issued token reaches a protected endpoint.
8. Frontend Cognito and env config. Install `@aws-amplify/auth` v6. Replace JWT-based `AuthService` with Amplify. Move API URL to `environment.ts`. Refactor `TodoComponent` to call the new `/tickets` API contract.
9. Terraform: frontend_hosting module. S3 + CloudFront + OAC + ACM. Manual sync to verify; GitHub Action comes later.
10. CI/CD. GitHub Actions: lint and test on PR; build, push image, run `lambda update-function-code`, sync frontend on merge to `main`.
11. Polish. README rewrite (English), dev setup doc, screenshots refreshed.

## Repo-wide gotchas

- No Alembic and no migrations yet. Schema work begins in milestone 3.
- Do not connect Lambda to Postgres directly. Always use the pooler URL.
- Domain layer must stay framework-free. No `from sqlalchemy ...` or `from fastapi ...` inside `<context>/domain/`. Enforce by code review.
- CORS origins will be a Terraform variable on the APIGW, not hardcoded in Python.
- `.env` is for local dev only. Production Lambda reads from Secrets Manager. Never commit a real `.env`.
- No `requirements.txt` in git. uv generates it on the fly during the Docker build from `uv.lock`.
- The existing frontend hardcodes `http://localhost:8000/api/...` in service files. Milestone 8 cleans this up.
