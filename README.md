# Mini Agent Platform

A full-stack platform where users can create their own AI agents, chat with them, and connect custom HTTP tools to them. Built to learn, step by step, how a real backend project is actually put together.

## Features

- Registration / login (JWT-based authentication)
- Tenant-based data isolation (each user only accesses their own data)
- Agent CRUD (name, system prompt, model, temperature)
- Chat with an agent, with conversation history stored in the database
- User-defined HTTP tools that the LLM can call (function calling)
- Optional Redis cache for agent configuration (PostgreSQL stays the source of truth)
- React-based web interface

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis (optional cache), LangChain
**Frontend:** React, Vite
**LLM access:** OpenRouter (access to different models through an OpenAI-compatible API)
**Packaging:** Docker, Docker Compose

## Architecture

```
Frontend (React)
    |  HTTP + JWT
    v
api/      -> route definitions, request/response validation
core/     -> business logic (auth, agent, chat, tool services)
models/   -> SQLAlchemy tables
schemas/  -> Pydantic request/response schemas
    v
PostgreSQL  (+ optional Redis cache, used from core/)
```

Rule: the `api/` layer contains no business logic; database queries only happen in the `core/` layer's services.

## Project Structure

```
backend/
  app/
    api/        auth.py, agents.py, tools.py, deps.py
    core/       auth_service.py, agent_service.py, chat_service.py,
                tool_service.py, tool_builder.py, security.py, llm.py,
                cache.py, snapshots.py
    models/     tenant.py, user.py, agent.py, conversation.py,
                message.py, tool.py
    schemas/    auth.py, agent.py, chat.py, tool.py
    config.py
    main.py
  alembic/      database migrations
  Dockerfile    backend image
frontend/
  src/
    AuthView.jsx        login / register screen
    DashboardView.jsx   agent listing / creation
    ChatView.jsx         chat screen with an agent
    ToolsView.jsx        tool management screen
    api.js               backend communication layer
  Dockerfile    frontend image (build with Node, serve with nginx)
docker-compose.yml      postgres, redis, backend, frontend
```

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env` from `.env.example` and fill it in:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | JWT signing key |
| `JWT_ALGORITHM` | JWT algorithm (default: HS256) |
| `JWT_EXPIRE_MINUTES` | Token validity period (minutes) |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `OPENROUTER_BASE_URL` | OpenRouter API base URL |
| `REDIS_URL` | Redis connection string, e.g. `redis://127.0.0.1:6379/0`. Leave empty to disable the cache |
| `AGENT_CACHE_TTL_SECONDS` | Lifetime of a cached agent in seconds (default: 300) |
| `CORS_ORIGINS` | Comma-separated frontend origins allowed by CORS (default: `http://localhost:5173`) |

Run the database migrations:

```bash
alembic upgrade head
```

Start the server:

```bash
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

## Running with Docker

Requires Docker with Compose. One command starts the whole stack: PostgreSQL, Redis, the backend and the frontend.

```bash
cp .env.example .env
```

Open `.env` and set `POSTGRES_PASSWORD`, `JWT_SECRET` and `OPENROUTER_API_KEY`, then:

```bash
docker compose up -d --build
```

- App: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`

Stop it with `docker compose down`. The database lives in the `postgres_data` volume, so your data survives `down`; `docker compose down -v` deletes it.

| Service | Image | Notes |
|---|---|---|
| `postgres` | `postgres:17-alpine` | Data in the `postgres_data` volume, not exposed to the host |
| `redis` | `redis:7-alpine` | Persistence disabled, not exposed to the host |
| `backend` | built from `backend/Dockerfile` | Runs `alembic upgrade head` on start, then the API on port 8000 |
| `frontend` | built from `frontend/Dockerfile` | Static build served by nginx on port 80 |

Variables read from the root `.env`:

| Variable | Description |
|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Database credentials and name (required) |
| `JWT_SECRET` | JWT signing key (required) |
| `OPENROUTER_API_KEY` | OpenRouter API key (required) |
| `POSTGRES_VERSION` | PostgreSQL image tag (default: `17-alpine`) |
| `BACKEND_PORT` | Host port of the API (default: `8000`) |
| `FRONTEND_PORT` | Host port of the web app (default: `5173`) |

Things to know:

- The database starts empty; it is separate from any PostgreSQL you run locally.
- `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` are only applied the first time the volume is created. Changing them later does not change the existing database; run `docker compose down -v` to start over. Use a password without `@`, `:` or `/`, because it is placed inside the connection URL.
- A volume created by one PostgreSQL major version cannot be opened by another one. Pick `POSTGRES_VERSION` before the first start.
- The frontend bakes the API address in at build time (`VITE_API_URL`, derived from `BACKEND_PORT`). After changing `BACKEND_PORT` or `FRONTEND_PORT`, run `docker compose up -d --build`.
- A tool URL that uses `localhost` points to the backend container itself, not to your computer. Use `host.docker.internal` to reach a service on your machine.

## Redis Cache (optional)

Agent configuration (system prompt, model, temperature and the agent's tools) is read on every chat message. When `REDIS_URL` is set, it is cached in Redis. PostgreSQL always remains the source of truth.

Start a local Redis (requires Docker):

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine redis-server --save "" --appendonly no
```

Persistence is turned off on purpose: the cache is disposable, and a Redis that reloads old data after a restart could bring back entries that were stale when it went down.

Then set `REDIS_URL=redis://127.0.0.1:6379/0` in `backend/.env`. Leave it empty to run without a cache.

How it works:

- Cache-aside: chat reads `agent:v1:{tenant_id}:{agent_id}` from Redis. On a miss it loads the agent and its tools from PostgreSQL and stores a JSON snapshot with a TTL (`AGENT_CACHE_TTL_SECONDS`).
- Keys contain the tenant id, so tenants never share cache entries.
- Invalidation: updating or deleting an agent, and creating, updating or deleting one of its tools, deletes the key right after the database commit.
- Failure behavior: Redis is only an accelerator. If it is unreachable the app keeps working from PostgreSQL, and after a failure Redis is skipped for 30 seconds so requests are not slowed down.

Things to know:

- Changes made outside the app (manual SQL, migrations) do not invalidate the cache. Stale entries expire after the TTL.
- If an agent is updated while Redis is unreachable, the invalidation cannot be delivered. An old entry that is still stored in Redis can be served again once Redis is back, until its TTL runs out.
- The cached snapshot contains tool URLs and headers, which can hold API keys, as plain text. Do not expose the Redis port, and set a password if the instance is reachable by others.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Log in, returns a JWT token |
| GET | `/auth/me` | Info about the currently logged-in user |
| GET/POST | `/agents/` | List / create agents |
| GET/PATCH/DELETE | `/agents/{agent_id}` | Operate on a single agent |
| POST | `/agents/{agent_id}/chat` | Send a message to an agent |
| GET/POST | `/agents/{agent_id}/tools/` | List / create tools |
| GET/PATCH/DELETE | `/agents/{agent_id}/tools/{tool_id}` | Operate on a single tool |
