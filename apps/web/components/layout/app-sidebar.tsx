"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  GraduationCap,
  Database,
  Box,
  FlaskConical,
  Layers,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores";

const mainNavItems = [
  {
    title: "Home",
    url: "/dashboard",
    icon: Home,
  },
  {
    title: "Learn",
    url: "/dashboard/learn",
    icon: GraduationCap,
  },
  {
    title: "Datasets",
    url: "/dashboard/datasets",
    icon: Database,
  },
  {
    title: "Models",
    url: "/dashboard/models",
    icon: Box,
  },
  {
    title: "Playground",
    url: "/dashboard/playground",
    icon: FlaskConical,
  },
];



export function AppSidebar() {
  const pathname = usePathname();
  const { state, toggleSidebar } = useSidebar();
  const isCollapsed = state === "collapsed";
  const { user } = useAuthStore();

  const userInitials = user?.full_name
    ? user.full_name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
    : "U";

  return (
    <Sidebar
      collapsible="icon"
      className="border-r-0 bg-[#1a1a1f] overflow-x-hidden"
    >
      {/* Header with Logo */}
      <SidebarHeader
        className={cn(
          "overflow-hidden",
          isCollapsed ? "px-0 py-4" : "px-3 py-4"
        )}
      >
        <div
          className={cn(
            "flex items-center",
            isCollapsed ? "justify-center" : "justify-between"
          )}
        >
          <Link
            href="/dashboard"
            className={cn(
              "flex items-center gap-2 min-w-0",
              isCollapsed && "justify-center"
            )}
          >
            <div className="w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-lg bg-zinc-800">
              <Layers className="w-5 h-5 text-zinc-300" />
            </div>
            {!isCollapsed && (
              <div className="flex items-center gap-1.5 overflow-hidden">
                <span className="font-semibold text-base text-white whitespace-nowrap">
                  AutoML
                </span>
                <span className="text-[10px] text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded whitespace-nowrap">
                  v1.0
                </span>
              </div>
            )}
          </Link>

        </div>

        {/* Collapse Toggle Button - shown when expanded */}
        {!isCollapsed && (
          <button
            onClick={toggleSidebar}
            className="mt-3 w-full h-9 flex items-center justify-center gap-2 rounded-lg text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 transition-colors"
          >
            <div className="w-8 h-[18px] bg-zinc-800 rounded-full flex items-center justify-end px-0.5">
              <div className="w-3.5 h-3.5 bg-zinc-500 rounded-full" />
            </div>
            <span className="text-sm">Collapse</span>
          </button>
        )}

        {/* Toggle switch when collapsed */}
        {isCollapsed && (
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={toggleSidebar}
                className="mx-auto mt-3 w-8 h-[18px] bg-zinc-800 rounded-full flex items-center px-0.5 cursor-pointer hover:bg-zinc-700 transition-colors"
              >
                <div className="w-3.5 h-3.5 bg-white rounded-full" />
              </button>
            </TooltipTrigger>
            <TooltipContent side="right">Expand sidebar</TooltipContent>
          </Tooltip>
        )}
      </SidebarHeader>

      <SidebarContent
        className={cn(
          "overflow-x-hidden overflow-y-auto",
          isCollapsed ? "px-0" : "px-2"
        )}
      >
        {/* Main Navigation */}
        <SidebarGroup className={isCollapsed ? "px-0" : ""}>
          <SidebarGroupContent>
            <SidebarMenu className={isCollapsed ? "items-center gap-1" : ""}>
              {mainNavItems.map((item) => {
                const isActive =
                  pathname === item.url ||
                  (item.url !== "/dashboard" && pathname.startsWith(item.url));

                if (isCollapsed) {
                  return (
                    <SidebarMenuItem key={item.title} className="w-auto">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Link
                            href={item.url}
                            className={cn(
                              "w-8 h-8 flex items-center justify-center rounded-lg transition-colors",
                              isActive
                                ? "bg-zinc-800 text-white"
                                : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50"
                            )}
                          >
                            <item.icon className="w-[18px] h-[18px]" />
                          </Link>
                        </TooltipTrigger>
                        <TooltipContent side="right">{item.title}</TooltipContent>
                      </Tooltip>
                    </SidebarMenuItem>
                  );
                }

                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                      className={cn(
                        "h-10 gap-3 rounded-lg transition-all overflow-hidden",
                        isActive
                          ? "bg-zinc-800 text-white"
                          : "text-zinc-400 hover:text-white hover:bg-zinc-800/50"
                      )}
                    >
                      <Link href={item.url}>
                        <item.icon className="w-5 h-5 flex-shrink-0" />
                        <span className="text-sm font-medium truncate">
                          {item.title}
                        </span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>


      </SidebarContent>

      {/* Footer */}
      <SidebarFooter
        className={cn(
          "border-t border-zinc-800 overflow-hidden",
          isCollapsed ? "p-2" : "p-3"
        )}
      >
        {/* Collapsed: Avatar */}
        {isCollapsed ? (
          <div className="flex flex-col items-center gap-3">
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center cursor-pointer">
                  <span className="text-sm font-semibold text-white">
                    {userInitials}
                  </span>
                </div>
              </TooltipTrigger>
              <TooltipContent side="right">
                <div>
                  <p className="font-medium">{user?.full_name || "User"}</p>
                  <p className="text-xs text-zinc-400">
                    {user?.email || "user@example.com"}
                  </p>
                </div>
              </TooltipContent>
            </Tooltip>
          </div>
        ) : (
          <>
            {/* Expanded: User Profile */}
            <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-800/50 cursor-pointer">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center flex-shrink-0">
                <span className="text-sm font-semibold text-white">
                  {userInitials}
                </span>
              </div>
              <div className="flex-1 min-w-0 overflow-hidden">
                <p className="text-sm font-medium text-white truncate">
                  {user?.full_name || "User"}
                </p>
                <p className="text-xs text-zinc-500 truncate">
                  {user?.email || "user@example.com"}
                </p>
              </div>
            </div>
          </>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}
