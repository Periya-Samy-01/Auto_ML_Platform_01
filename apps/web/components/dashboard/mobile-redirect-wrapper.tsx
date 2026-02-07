"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useIsMobile } from "@/hooks/use-mobile";

export function MobileRedirectWrapper({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const isMobile = useIsMobile();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        if (mounted && isMobile) {
            router.push("/dashboard/learn");
        }
    }, [mounted, isMobile, router]);

    // Prevent flash of content on mobile by not rendering children if mobile
    // However, during SSR/hydration, we might render until isMobile is determined
    if (mounted && isMobile) {
        return null;
    }

    return <>{children}</>;
}
