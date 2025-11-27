# Collaborative Code Editor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7+-DC382D?style=flat&logo=redis&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.122+-009688?style=flat&logo=fastapi&logoColor=white)

</div>

<img src="./public/hero.png" alt="hero">

Real-time collaborative code editor with WebSocket sync, live cursors, and autocomplete. Built for pair programming and team collaboration.

## Features

- **Real-time Sync** - Multiple users edit simultaneously with instant updates
- **Live Cursors** - See where teammates are typing in real-time
- **Autocomplete** - Context-aware code suggestions (Python)
- **No Sign-up** - Create room and start coding immediately
- **Fast** - Sub-50ms latency via WebSockets
- **Scalable** - Redis pub/sub for horizontal scaling

## Tech Stack

**Frontend:** Next.js 15 • React 19 • TypeScript • Monaco Editor • shadcn/ui • Tailwind

**Backend:** FastAPI • Python 3.12 • Redis • WebSockets • uv

**Infrastructure:** Docker • Docker Compose

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repo
git clone https://github.com/grimmy-dev/coed.git
cd coed

# Start all services
docker-compose up --build

# Access app
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000/docs
# Redis:    localhost:6379
```

### Option 2: Manual Setup

**1. Start Redis**

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**2. Backend**

```bash
cd backend
pip install uv
uv pip install -r pyproject.toml
uv run main.py
```

**3. Frontend**

```bash
cd frontend
pnpm install
pnpm dev
```

## Usage

1. **Create Room** → Click "Create New Room"
2. **Share Link** → Copy room URL to clipboard
3. **Join Room** → Teammates enter room code
4. **Code Together** → Edit with live sync
5. **See Cursors** → View teammate positions
6. **Autocomplete** → Pause typing for suggestions

## Overview Architecture

![Architecture Diagram](/public/architecture.png)

## Project Structure

```
.
├── backend/              # FastAPI server
│   ├── config/          # Redis & settings
│   ├── models/          # Pydantic schemas
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   └── BACKEND.md       # Backend docs
│
├── frontend/            # Next.js app
│   ├── app/            # Pages & routes
│   ├── components/     # React components
│   ├── hooks/          # WebSocket & autocomplete
│   ├── lib/            # API client & utils
│   └── FRONTEND.md     # Frontend docs
│
└── docker-compose.yml   # Orchestration
```

## API Reference

### REST Endpoints

```bash
POST   /rooms                  # Create new room
GET    /rooms/{id}/exists      # Check room exists
POST   /rooms/autocomplete     # Get code suggestions
GET    /health                 # Health check
```

### WebSocket

```
WS /ws/{room_id}
```

**Client → Server:**

- `code_update` - User edited code
- `cursor_move` - User moved cursor

**Server → Client:**

- `init` - Initial room state
- `code_update` - Code changed
- `cursor_move` - Cursor moved
- `user_joined` - User connected
- `user_left` - User disconnected

## Environment Variables

Create `.env` in root:

```bash
# Backend
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=http://localhost:3000
ROOM_TTL_SECONDS=7200

# Frontend
NEXT_PUBLIC_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Key Features

### Real-time Sync

- **Debounced updates** (300ms) reduce network traffic
- **Throttled cursors** (100ms) prevent spam
- **Auto-reconnect** with exponential backoff
- **Last-write-wins** conflict resolution

### Live Cursors

- Calculates positions from Monaco measurements
- Adapts to font size and zoom changes
- Color-coded per user (8 colors)
- Smooth CSS transitions

### Autocomplete

- Rule-based pattern matching (no ML)
- Triggers: `def`, `class`, `for`, `import`, etc.
- 600ms debounce to avoid spam
- Context-aware based on cursor position

### Scalability

- Redis pub/sub for horizontal scaling
- Multiple backend instances share state
- Stateless WebSocket connections
- Auto-expiring rooms (2-hour TTL)

## Performance

| Metric            | Target         |
| ----------------- | -------------- |
| Code sync latency | < 50ms (local) |
| Cursor updates    | 10/sec max     |
| Autocomplete      | < 100ms        |
| Room creation     | < 10ms         |
| WebSocket connect | < 500ms        |

## Limitations

- **No persistence** - Code lost when all users leave
- **No CRDT** - Simple last-write-wins
- **Python only** - Autocomplete limited (extensible)
- **Single room** - One room per user at a time

## Troubleshooting

**WebSocket won't connect:**

```bash
# Check backend is running
curl http://localhost:8000/health

# Check Redis
redis-cli ping

# Verify environment variables
echo $NEXT_PUBLIC_WS_URL
```

**Room not found:**

- Rooms expire after 2 hours (TTL)
- Create a new room

**Autocomplete not working:**

```bash
# Check backend logs
docker-compose logs backend

# Test endpoint
curl -X POST http://localhost:8000/rooms/autocomplete \
  -H "Content-Type: application/json" \
  -d '{"code": "def ", "cursor_position": 4, "language": "python"}'
```

**Cursors misaligned:**

- Monaco measurements calculated dynamically
- Check browser console for errors
- Refresh page to recalculate

## Docker Commands

```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Stop and remove
docker-compose down

# Clean everything
docker-compose down -v
```

## Development

**Backend:**

```bash
cd backend
uvicorn main:app --reload
# Docs: http://localhost:8000/docs
```

**Frontend:**

```bash
cd frontend
pnpm dev
# App: http://localhost:3000
```

**Redis CLI:**

```bash
docker exec -it redis redis-cli
> KEYS room:*
> GET room:abc123:code
```

## Documentation

- [Backend Documentation](./backend/BACKEND.md) - API, services, Redis structure
- [Frontend Documentation](./frontend/FRONTEND.md) - Components, hooks, WebSocket

## Demo Screenshot

![demo_screenshot](/public/demo.png)

---

**Built with Next.js • FastAPI • Redis • WebSockets**
