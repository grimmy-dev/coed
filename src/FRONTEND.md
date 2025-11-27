# Frontend - Collaborative Code Editor

Real-time collaborative code editor built with Next.js, TypeScript, and Monaco Editor.

## Structure

```
frontend/
├── app/
│   ├── page.tsx                    # Home page (create/join)
│   └── [roomId]/page.tsx           # Room page (editor)
├── components/
│   ├── editor/
│   │   ├── code-editor.tsx         # Monaco editor + autocomplete
│   │   └── cursor-overlay.tsx
│   └── room/
│       ├── connection-status.tsx   # WebSocket status
│       ├── toolbar.tsx             # Room toolbar
│       └── user-sidebar.tsx        # Active users list
├── hooks/
│   ├── use-autocomplete.ts         # Autocomplete hook
│   └── use-websocket.ts            # WebSocket connection
├── lib/
│   ├── api.ts                      # API client
│   └── utils.ts                    # Utility functions
└── types/
    └── index.ts                    # TypeScript types
```

## Features

### Core

- ✅ Room creation & joining
- ✅ Real-time code sync (WebSocket)
- ✅ Live cursor positions (Monaco-based)
- ✅ User presence (sidebar + cursors)
- ✅ Connection status indicator

### Enhanced

- ✅ Autocomplete (600ms debounce)
- ✅ Monaco editor integration
- ✅ shadcn/ui components
- ✅ Responsive design
- ✅ Docker support (pnpm + standalone)

## Environment Variables

Create `.env`:

```
NEXT_PUBLIC_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Installation

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

## Docker

### Prerequisites

Make sure `next.config.ts` has standalone output:

```typescript
const nextConfig: NextConfig = {
  output: "standalone", // Required for Docker
};
export default nextConfig;
```

### Build

```bash
docker build -t collab-frontend .
```

### Run

```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  -e NEXT_PUBLIC_WS_URL=ws://localhost:8000 \
  collab-frontend
```

### With Docker Compose

```bash
# Start all services
docker-compose up

# Build and start
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f frontend
```

## API Integration

### REST Endpoints

```typescript
ApiClient.createRoom(); // Create new room
ApiClient.checkRoomExists(roomId); // Check if room exists
ApiClient.getAutocomplete(code, pos, lang); // Get suggestions
```

### WebSocket

```typescript
const { connectionState, code, users, sendCodeUpdate, sendCursorMove } =
  useWebSocket(roomId);
```

## Autocomplete

### Usage

```typescript
const { suggestion, isLoading } = useAutocomplete(
  code,
  cursorPosition,
  "python",
  { debounceMs: 600 }
);
```

### Supported Triggers

- `def ` → Function template
- `class ` → Class template
- `for ` → Loop template
- `import ` → Common imports
- `try` → Try/except template
- And more...

## File Descriptions

### Core Files

**`app/page.tsx`**

- Home page with create/join UI
- Fixed routing consistency
- Error handling

**`app/[roomId]/page.tsx`**

- Main editor page
- WebSocket integration
- Connection overlays

**`hooks/use-websocket.ts`**

- WebSocket connection manager
- Message handling
- State management

**`hooks/use-autocomplete.ts`**

- Debounced autocomplete
- API integration
- Loading states

**`lib/api.ts`**

- API client methods
- Typed responses
- Error handling

**`types/index.ts`**

- TypeScript definitions
- Message types
- State types

### Components

**`components/editor/code-editor.tsx`**

- Monaco editor wrapper
- Autocomplete integration
- Cursor tracking

**`components/editor/cursor-overlay.tsx`**

- Live cursor positions
- Monaco measurement-based
- shadcn colors
- Smooth animations

**`components/room/connection-status.tsx`**

- Visual connection state
- shadcn colors

**`components/room/toolbar.tsx`**

- Room info display
- Share functionality
- Leave room button

**`components/room/user-sidebar.tsx`**

- Active users list
- Color indicators
- Current user highlight

## Dependencies

Core:

- Next.js 16
- React 19+
- TypeScript 5+

UI:

- @monaco-editor/react
- shadcn/ui
- Tailwind CSS

**WebSocket required for collaboration.**

## Performance

- Code sync debounced (300ms)
- Cursor updates throttled (100ms)
- Autocomplete debounced (600ms)

---

**Built with Next.js • Monaco • shadcn/ui • WebSockets**
