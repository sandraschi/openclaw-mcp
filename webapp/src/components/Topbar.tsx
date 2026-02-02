import { HelpCircle, ScrollText, LogIn, Menu } from "lucide-react";
import { cn } from "../utils/cn";

interface TopbarProps {
  onToggleSidebar: () => void;
  sidebarCollapsed: boolean;
  onOpenHelp: () => void;
  onOpenLogger: () => void;
  onOpenAuth: () => void;
}

export default function Topbar({
  onToggleSidebar,
  sidebarCollapsed,
  onOpenHelp,
  onOpenLogger,
  onOpenAuth,
}: TopbarProps) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-background-secondary px-4">
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onToggleSidebar}
          className={cn(
            "rounded-md p-2 text-foreground-secondary transition-colors",
            "hover:bg-muted hover:text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
          )}
          aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <Menu className="h-5 w-5" />
        </button>
        <span className="font-mono text-lg font-semibold text-primary">
          openclaw-mcp
        </span>
        <span className="hidden text-sm text-foreground-secondary sm:inline">
          OpenClaw + Moltbook
        </span>
      </div>

      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={onOpenHelp}
          className={cn(
            "rounded-md p-2 text-foreground-secondary transition-colors",
            "hover:bg-muted hover:text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
          )}
          aria-label="Help"
          title="Help"
        >
          <HelpCircle className="h-5 w-5" />
        </button>
        <button
          type="button"
          onClick={onOpenLogger}
          className={cn(
            "rounded-md p-2 text-foreground-secondary transition-colors",
            "hover:bg-muted hover:text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
          )}
          aria-label="Logger"
          title="Logger"
        >
          <ScrollText className="h-5 w-5" />
        </button>
        <button
          type="button"
          onClick={onOpenAuth}
          className={cn(
            "rounded-md p-2 text-foreground-secondary transition-colors",
            "hover:bg-muted hover:text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
          )}
          aria-label="Auth"
          title="Auth"
        >
          <LogIn className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}

