# Backend - Collaborative Code Editor

Real-time collaborative editor backend with FastAPI, WebSockets, and Redis.

## Tech Stack

- **FastAPI** - Modern async web framework
- **Redis** - State management + pub/sub
- **WebSockets** - Real-time connections
- **Pydantic** - Data validation
- **Python 3.12+** - Async/await support

## Quick Start

### Prerequisites

- Python 3.12+
- Redis 7+
- uv (fast package manager)

### Install uv

```bash
pip install uv
```

### Install Dependencies

```bash
uv pip install -r pyproject.toml
```

### Start Redis

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### Run Backend

```bash
# Option 1: Direct uvicorn
uvicorn main:app --reload

# Option 2: With uv
uv run main.py
```

Server runs at `http://localhost:8000`

## Environment Variables

Create `.env`:

```bash
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=http://localhost:3000
ROOM_TTL_SECONDS=7200
```

## Project Structure

```
backend/
├── config/
│   ├── redis_client.py       # Singleton Redis connection
│   └── settings.py            # Environment config
│
├── models/
│   └── schemas.py             # Pydantic models
│
├── routers/
│   ├── rooms.py               # REST endpoints
│   └── websocket.py           # WebSocket endpoint
│
├── services/
│   ├── room_service.py        # Room management
│   ├── connection_manager.py  # WebSocket connections
│   ├── pubsub_service.py      # Redis pub/sub
│   └── autocomplete_service.py # Code suggestions
│
└── main.py                    # FastAPI app
```

## API Endpoints

### REST

**Create Room**

```bash
POST /rooms
Response: { "room_id": "a972ed", "join_url": "...", "ws_url": "..." }
```

**Check Room Exists**

```bash
GET /rooms/{room_id}/exists
Response: { "exists": true, "room_id": "a972ed" }
```

**Autocomplete**

```bash
POST /rooms/autocomplete
Body: { "code": "def ", "cursor_position": 4, "language": "python" }
Response: { "suggestion": "function_name():\n    pass", "insert_position": 4 }
```

**Health Check**

```bash
GET /health
Response: { "status": "ok" }
```

### WebSocket

**Connect to Room**

```
WS /ws/{room_id}
```

**Message Types**

Client → Server:

- `code_update` - User edited code
- `cursor_move` - User moved cursor

Server → Client:

- `init` - Initial room state
- `code_update` - Code changed
- `cursor_move` - Cursor moved
- `user_joined` - User entered room
- `user_left` - User left room

## Architecture

### Config Layer

- **redis_client.py** - Singleton connection pool
- **settings.py** - Environment variables

### Models Layer

- **schemas.py** - Request/response validation

### Routers Layer

- **rooms.py** - HTTP endpoints
- **websocket.py** - WebSocket endpoint

### Services Layer

- **room_service.py** - Room lifecycle (create, exists, TTL)
- **connection_manager.py** - In-memory WebSocket tracking
- **pubsub_service.py** - Redis pub/sub for multi-server scaling
- **autocomplete_service.py** - Pattern-based suggestions

## Redis Data Structure

```
room:{room_id}:code         # String - current code
room:{room_id}:users        # Set - user IDs
room:{room_id}:cursors      # Hash - user_id -> cursor JSON

room_channel:{room_id}      # Pub/Sub channel
```

All keys have TTL (default 2 hours) and refresh on activity.

## How It Works

### Room Creation

1. Generate random 6-char hex ID
2. Check for collisions (16M combinations = rare)
3. Create Redis key with TTL
4. Return room ID and URLs

### WebSocket Flow

1. Client connects to `/ws/{room_id}`
2. Validate room exists
3. Assign user ID and color
4. Subscribe to Redis pub/sub channel
5. Send initial state (code, users, cursors)
6. Broadcast "user joined" via pub/sub
7. Listen for messages (code, cursor)
8. On disconnect: cleanup, broadcast "user left"

### Multi-Server Scaling

Redis pub/sub enables horizontal scaling:

1. User A on Server 1 sends code update
2. Server 1 publishes to Redis channel
3. Server 2 receives from Redis
4. Server 2 broadcasts to its local clients
5. User B on Server 2 gets the update

### TTL Management

Rooms auto-expire after 2 hours of inactivity:

- TTL refreshes on code updates
- Prevents Redis memory leaks
- Inactive rooms cleaned up automatically

## Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Create Room

```bash
curl -X POST http://localhost:8000/rooms
```

### Check Room

```bash
curl http://localhost:8000/rooms/{room_id}/exists
```

### Autocomplete

```bash
curl -X POST http://localhost:8000/rooms/autocomplete \
  -H "Content-Type: application/json" \
  -d '{"code": "def ", "cursor_position": 4, "language": "python"}'
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

### Docker Compose

```bash
# Start everything
docker-compose up

# With rebuild
docker-compose up --build

# Stop
docker-compose down

# Logs
docker-compose logs -f backend
```

## Development

### API Docs

FastAPI auto-generates docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Hot Reload

```bash
uvicorn main:app --reload
```

Changes to `.py` files trigger automatic restart.

### Logging

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message")
```

## Autocomplete Implementation

Current implementation uses pattern matching:

```python
# Triggers
"def " → "function_name():\n    pass"
"for " → "item in items:\n    pass"
"import " → "numpy as np"
```

**Production Replacement:**

- Integrate OpenAI API
- Use language servers (pylsp, pyright)
- Connect to Copilot-style models

## Troubleshooting

**Redis connection failed:**

- Check Redis is running: `docker ps`
- Verify `REDIS_URL` in `.env`
- Test connection: `redis-cli ping`

**WebSocket won't connect:**

- Ensure room exists first
- Check CORS origins
- Verify WebSocket URL format

**Room not found:**

- Rooms expire after TTL (default 2 hours)
- Check room exists before connecting
- TTL refreshes on activity

**Autocomplete returns 404:**

- Normal behavior when no pattern matches
- Frontend should handle gracefully
- Not an error, just no suggestion

---

**Built with Python 3.12+ • FastAPI • Redis • WebSockets**