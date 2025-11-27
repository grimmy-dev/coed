# Frontend - Collaborative Code Editor

Real-time collaborative editor with Monaco, WebSockets, and autocomplete.

## Tech Stack

- **Next.js 15+** - App router, React Server Components
- **TypeScript** - Type safety
- **Monaco Editor** - VS Code's editor
- **WebSockets** - Real-time sync
- **shadcn/ui** - Components
- **Tailwind CSS** - Styling

## Structure

```
frontend/
├── app/
│   ├── page.tsx                  # Home (create/join room)
│   └── [roomId]/page.tsx         # Room page with editor
│
├── components/
│   ├── editor/
│   │   ├── code-editor.tsx       # Monaco + autocomplete
│   │   └── cursor-overlay.tsx    # Live cursors
│   └── room/
│       ├── toolbar.tsx           # Top bar (room info, share)
│       ├── connection-status.tsx # WebSocket status
│       └── user-sidebar.tsx      # Active users list
│
├── hooks/
│   ├── use-websocket.ts          # WebSocket connection
│   └── use-autocomplete.ts       # Debounced suggestions
│
├── lib/
│   ├── api.ts                    # Backend API client
│   └── utils.ts                  # Debounce, throttle
│
└── types/
    └── index.ts                  # TypeScript types
```

## Quick Start

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Installation

```bash
# Install
pnpm install

# Dev server
pnpm dev

# Build
pnpm build

# Production
pnpm start
```

## Docker

### Build & Run

```bash
# Build image
docker build -t collab-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  -e NEXT_PUBLIC_WS_URL=ws://localhost:8000 \
  collab-frontend
```

### Docker Compose

```bash
# Start all services
docker-compose up

# With rebuild
docker-compose up --build

# Stop
docker-compose down

# Logs
docker-compose logs -f frontend
```

## Key Features

### Real-Time Collaboration

- **Code Sync**: Debounced (300ms) to reduce traffic
- **Live Cursors**: Throttled (100ms) for smooth updates
- **User Presence**: See who's in the room
- **Auto-Reconnect**: Handles connection drops

### Autocomplete

- **Trigger**: Backend suggests code completions
- **Debounce**: 600ms delay after typing stops
- **Accept**: Press Tab to insert suggestion
- **Display**: Floating tooltip shows preview

### Editor

- **Monaco**: Same editor as VS Code
- **Custom Tab**: Overrides indentation for autocomplete
- **Read-Only**: When disconnected
- **Cursor Sync**: Broadcasts position to others

## API Integration

### REST Endpoints

```typescript
// Create new room
const { room_id } = await ApiClient.createRoom();

// Check if room exists
const { exists } = await ApiClient.checkRoomExists(roomId);

// Get autocomplete
const { suggestion } = await ApiClient.getAutocomplete(
  code,
  cursorPosition,
  "python"
);
```

### WebSocket

```typescript
const {
  connectionState, // Status, userId, userColor
  code, // Current code
  users, // Active users
  cursors, // User cursors
  sendCodeUpdate, // Broadcast code
  sendCursorMove, // Broadcast cursor
} = useWebSocket(roomId);
```

#### Message Types

**Incoming:**

- `init` - Full state on connect
- `code_update` - Code changed
- `cursor_move` - User moved cursor
- `user_joined` - New user
- `user_left` - User disconnected

**Outgoing:**

- `code_update` - Send code changes
- `cursor_move` - Send cursor position

## File Guide

### Core Pages

**`app/page.tsx`** - Landing page with create/join UI

**`app/[roomId]/page.tsx`** - Main editor with WebSocket integration

### Hooks

**`use-websocket.ts`** - Manages WebSocket lifecycle, handles all message types, maintains room state

**`use-autocomplete.ts`** - Debounces autocomplete requests, fetches suggestions from backend

### Components

**`code-editor.tsx`** - Wraps Monaco, integrates autocomplete, overrides Tab key

**`cursor-overlay.tsx`** - Renders other users' cursors using Monaco measurements

**`toolbar.tsx`** - Room info, share button, leave button

**`connection-status.tsx`** - Visual WebSocket status (green/yellow/red)

**`user-sidebar.tsx`** - List of active users with color indicators

### Utilities

**`api.ts`** - Typed API methods for backend

**`utils.ts`** - Debounce (delays), throttle (limits)

## Performance Notes

- **Code sync**: 300ms debounce (reduces network spam)
- **Cursor updates**: 100ms throttle (smooth but not overwhelming)
- **Autocomplete**: 600ms debounce (waits for typing to pause)

## Color System

Backend assigns hex colors, we map them to Tailwind:

```typescript
const COLOR_MAP = {
  "#C72626": "#ef4444", // red
  "#1C978F": "#14b8a6", // teal
  "#1E7D92": "#0ea5e9", // blue
  "#B3471D": "#f97316", // orange
  // ... etc
};
```

Used in cursors and user sidebar for consistency.

## Troubleshooting

**WebSocket won't connect:**

- Check `NEXT_PUBLIC_WS_URL` in `.env.local`
- Ensure backend is running
- Check browser console for errors

**Autocomplete not working:**

- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend `/rooms/autocomplete` endpoint
- Check network tab for 404s

**Cursors misaligned:**

- Monaco measurements are calculated dynamically
- Check `cursor-overlay.tsx` console logs
- Verify `lineHeight` and `characterWidth` values

**Docker build fails:**

- Ensure `next.config.ts` has `output: "standalone"`
- Check Node version (20+)
- Verify all dependencies are in `package.json`

---

**Built with Next.js • Monaco • WebSockets • Tailwind**
