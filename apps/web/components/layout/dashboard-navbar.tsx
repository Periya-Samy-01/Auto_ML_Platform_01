"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { LogOut, User, Settings } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { useAuthStore } from "@/stores/auth-store";

const pageTitles: Record<string, string> = {
  "/dashboard": "Home",
  "/dashboard/learn": "Learn",
  "/dashboard/datasets": "Datasets",
  "/dashboard/models": "Models",
};

export function DashboardNavbar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch with Radix UI
  useEffect(() => {
    setMounted(true);
  }, []);

  // Get page title from pathname
  const getPageTitle = () => {
    if (pageTitles[pathname]) {
      return pageTitles[pathname];
    }
    for (const [path, title] of Object.entries(pageTitles)) {
      if (path !== "/dashboard" && pathname.startsWith(path)) {
        return title;
      }
    }
    return "Dashboard";
  };

  const handleLogout = () => {
    logout();
  };

  // Get user initials for avatar
  const getInitials = () => {
    if (user?.full_name) {
      return user.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    }
    if (user?.email) {
      return user.email[0].toUpperCase();
    }
    return "U";
  };

  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-border bg-background/50 backdrop-blur-sm relative z-10">
      <div className="flex items-center gap-4">
        <SidebarTrigger className="md:hidden" />
        <h1 className="text-xl font-semibold">{getPageTitle()}</h1>
      </div>

      <div className="flex items-center gap-4">
        {/* User menu - only render after mount to prevent hydration mismatch */}
        {mounted ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="relative h-9 w-9 rounded-full bg-primary/10 hover:bg-primary/20"
              >
                <span className="text-sm font-medium">{getInitials()}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <div className="flex items-center gap-2 p-2">
                <div className="flex flex-col space-y-1">
                  {user?.full_name && (
                    <p className="text-sm font-medium">{user.full_name}</p>
                  )}
                  <p className="text-xs text-muted-foreground">{user?.email}</p>
                </div>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <div className="h-9 w-9 rounded-full bg-primary/10 animate-pulse" />
        )}
      </div>
    </header>
  );
}
