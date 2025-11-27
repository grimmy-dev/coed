"use client";

interface User {
  id: string;
  color: string;
}

interface UserSidebarProps {
  users: Map<string, User>;
  currentUserId: string | null;
}

// Map backend colors to Tailwind colors (matches cursor colors)
const getChartColor = (hexColor: string): string => {
  const colorMap: Record<string, string> = {
    "#C72626": "#ef4444", // red
    "#1C978F": "#14b8a6", // teal
    "#1E7D92": "#0ea5e9", // blue
    "#B3471D": "#f97316", // orange
    "#24B792": "#10b981", // green
    "#CBAA27": "#eab308", // yellow
    "#9A26CB": "#a855f7", // purple
    "#278BC1": "#3b82f6", // sky blue
  };
  return colorMap[hexColor] || "#6366f1"; // default indigo
};

/**
 * Sidebar showing all active users in the room
 * Highlights current user and shows color indicators
 */
export function UserSidebar({ users, currentUserId }: UserSidebarProps) {
  const userArray = Array.from(users.values());

  return (
    <div className="hidden md:flex w-64 border-l border-border bg-card p-4 flex-col">
      <div className="mb-4">
        <h2 className="text-sm font-semibold text-muted-foreground mb-2">
          Active Users ({userArray.length})
        </h2>
      </div>

      <div className="flex-1 space-y-2 overflow-y-auto">
        {userArray.map((user) => {
          const isCurrentUser = user.id === currentUserId;
          const chartColor = getChartColor(user.color);

          return (
            <div
              key={user.id}
              className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
            >
              {/* Color indicator (matches cursor color) */}
              <div
                className="w-3 h-3 rounded-full shrink-0"
                style={{
                  backgroundColor: chartColor,
                }}
              />

              {/* User info */}
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-foreground truncate">
                  {isCurrentUser ? "You" : user.id.slice(0, 8)}
                </div>
                {isCurrentUser && (
                  <div className="text-xs text-muted-foreground truncate">
                    {user.id}
                  </div>
                )}
              </div>

              {/* Online indicator */}
              <div
                className="w-2 h-2 rounded-full shrink-0 animate-pulse"
                style={{ backgroundColor: "#22c55e" }}
              />
            </div>
          );
        })}
      </div>

      {userArray.length === 0 && (
        <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
          No users connected
        </div>
      )}
    </div>
  );
}
