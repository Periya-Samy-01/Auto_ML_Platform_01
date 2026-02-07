"use client";

import { usePathname } from "next/navigation";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppSidebar } from "./app-sidebar";
import { DashboardNavbar } from "./dashboard-navbar";
import { cn } from "@/lib/utils";
import { useIsMobile } from "@/hooks/use-mobile";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname();
  const isPlayground = pathname === "/dashboard/playground";
  const isMobile = useIsMobile();

  return (
    <TooltipProvider delayDuration={0}>
      <SidebarProvider defaultOpen={true}>
        {!isMobile && <AppSidebar />}
        <SidebarInset className="flex flex-col min-h-screen dashboard-bg dashboard-mesh">
          {!isPlayground && !isMobile && <DashboardNavbar />}
          <main className={cn("flex-1 overflow-auto relative z-10", !isPlayground && !isMobile && "p-6", isMobile && "p-4")}>
            {children}
          </main>
        </SidebarInset>
      </SidebarProvider>
    </TooltipProvider>
  );
}
