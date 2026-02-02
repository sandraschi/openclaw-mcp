import { NavLink } from "react-router-dom";
import { Home, Bot, MessageCircle, Route, GitBranch, BarChart3, Share2, Newspaper, Layers, Shield, Settings, Plug, Globe } from "lucide-react";
import { cn } from "../utils/cn";

const navItems = [
  { to: "/", icon: Home, label: "Startpage" },
  { to: "/ai", icon: Bot, label: "AI" },
  { to: "/channels", icon: MessageCircle, label: "Channels" },
  { to: "/routes", icon: Route, label: "Routes" },
  { to: "/diagram", icon: GitBranch, label: "Diagram" },
  { to: "/statistics", icon: BarChart3, label: "Statistics" },
  { to: "/moltbook", icon: Share2, label: "Moltbook" },
  { to: "/integrations", icon: Plug, label: "Integrations" },
  { to: "/clawnews", icon: Newspaper, label: "Clawnews" },
  { to: "/skills", icon: Layers, label: "Skills" },
  { to: "/security", icon: Shield, label: "Security" },
  { to: "/starter", icon: Globe, label: "Generate" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

interface SidebarProps {
  collapsed: boolean;
}

export default function Sidebar({ collapsed }: SidebarProps) {
  return (
    <aside
      className={cn(
        "flex shrink-0 flex-col border-r border-border bg-background-secondary transition-all duration-300",
        collapsed ? "w-16" : "w-56"
      )}
    >
      <nav className="flex flex-col gap-1 p-2">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                "hover:bg-muted hover:text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2 focus:ring-offset-background-secondary",
                collapsed ? "justify-center px-2" : "",
                isActive
                  ? "bg-primary/20 text-primary"
                  : "text-foreground-secondary"
              )
            }
          >
            <Icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
