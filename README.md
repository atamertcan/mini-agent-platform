# Mini Agent Platform

A full-stack platform where users can create their own AI agents, chat with them, and connect custom HTTP tools to them. Built to learn, step by step, how a real backend project is actually put together.

## Features

- Registration / login (JWT-based authentication)
- Tenant-based data isolation (each user only accesses their own data)
- Agent CRUD (name, system prompt, model, temperature)
- Chat with an agent, with conversation history stored in the database
- User-defined HTTP tools that the LLM can call (function calling)
- React-based web interface

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, LangChain
**Frontend:** React, Vite
**LLM access:** OpenRouter (access to different models through an OpenAI-compatible API)

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
PostgreSQL
```

Rule: the `api/` layer contains no business logic; database queries only happen in the `core/` layer's services.

## Project Structure

```
backend/
  app/
    api/        auth.py, agents.py, tools.py, deps.py
    core/       auth_service.py, agent_service.py, chat_service.py,
                tool_service.py, tool_builder.py, security.py, llm.py
    models/     tenant.py, user.py, agent.py, conversation.py,
                message.py, tool.py
    schemas/    auth.py, agent.py, chat.py, tool.py
    config.py
    main.py
  alembic/      database migrations
frontend/
  src/
    AuthView.jsx        login / register screen
    DashboardView.jsx   agent listing / creation
    ChatView.jsx         chat screen with an agent
    ToolsView.jsx        tool management screen
    api.js               backend communication layer
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
