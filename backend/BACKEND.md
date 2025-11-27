# Backend - Collaborative Code Editor

Real-time collaborative code editor built with FastAPI, WebSockets, and Redis.

## Features

- ✅ Room creation & joining
- ✅ Real-time code sync via WebSocket
- ✅ Cursor position tracking
- ✅ Redis pub/sub for horizontal scaling
- ✅ Autocomplete suggestions (rule-based)

## Quick Start

### Prerequisites

- Python 3.12+
- Redis 8+
- uv (install: `pip install uv`)

### Install

```bash
uv pip install -r pyproject.toml
```

### Run Redis

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### Run Backend

```bash
uvicorn main:app --reload
or
uv run main.py
```

Server runs at: http://localhost:8000

## Project Structure

```
backend/
├── config/          # Settings & Redis client
├── models/          # Pydantic schemas
├── routers/         # API endpoints
├── services/        # Business logic and connection manager
└── main.py          # FastAPI app
```

## API Endpoints

### REST

- `GET /health` - Health check
- `POST /rooms` - Create new room
- `GET /rooms/{room_id}/exists` - Check room exists
- `POST /rooms/autocomplete` - Get code suggestions

### WebSocket

- `WS /ws/{room_id}` - Real-time collaboration

## Environment Variables

Create `.env` file:

```
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=http://localhost:3000
ROOM_TTL_SECONDS=7200
```

## Docker

### Build

```bash
docker build -t collab-backend .
```

### Run

```bash
docker run -p 8000:8000 \
  -e REDIS_URL=redis://redis:6379 \
  collab-backend
```

### With Docker Compose

```bash
docker-compose up
```

## Test Autocomplete

```bash
curl -X POST http://localhost:8000/rooms/autocomplete \
  -H "Content-Type: application/json" \
  -d '{"code": "def ", "cursor_position": 4, "language": "python"}'
```

Response:

```json
{
  "suggestion": "def function_name():\n    pass",
  "insert_position": 4,
  "trigger_word": "def"
}
```

## Architecture

**Config** - Application settings  
**Models** - Request/response validation  
**Routers** - HTTP & WebSocket endpoints  
**Services** - Business logic and WebSocket lifecycle management (rooms, pub/sub, autocomplete)

## Tech Stack

- FastAPI - Web framework
- Redis - State management & pub/sub
- Pydantic - Data validation
- uvicorn - ASGI server
- uv - Fast dependency management

## Development

```bash
# Install dependencies
uv install -r pyproject.toml

# Run with auto-reload
uvicorn main:app --reload
or
# Run with uv
uv run main.py

# View API docs
open http://localhost:8000/docs
```

---

**Built with Python 3.12+ • FastAPI • Redis • WebSockets**
