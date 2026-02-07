# Mobile Learn Mode

> **Note**: This documentation describes the specialized mobile experience for the AutoML Platform.

## Overview

The **Mobile Learn Mode** is a dedicated experience for users accessing the platform on mobile devices (screens narrower than 768px). To optimize for small screens and focus on educational content, the complex dashboard features (Datasets, Models, Playground) are disabled, and the interface transforms into a focused **Learning Center**.

## Key Features

### 1. Focused Navigation
- **Sidebar Hidden**: The main navigation sidebar is completely removed to maximize screen real estate.
- **Navbar Hidden**: The top dashboard navbar is removed to reduce distraction.
- **Simplified Layout**: Content padding is adjusted for better density on small screens.

### 2. Automatic Redirection
- Users attempting to access the main Dashboard (`/dashboard`) on a mobile device are **automatically redirected** to the Learning Center (`/dashboard/learn`).
- This ensures mobile users land directly on content that is optimized for their device.

### 3. Responsive Learning Components
- **Topic List**: Adapts to a single-column card view.
- **Lesson View**: Typography and spacing are optimized for readability on mobile.
- **Quiz Interface**: Touch-friendly buttons and layout.

## Implementation Details

### Hook: `useIsMobile`
Located in `apps/web/hooks/use-mobile.ts`. Uses `window.matchMedia` to detect if the viewport is less than 768px.

### Wrapper: `MobileRedirectWrapper`
Located in `apps/web/components/dashboard/mobile-redirect-wrapper.tsx`. Wraps the dashboard home page to enforce redirection logic on the client side.

### Layout Logic
In `apps/web/components/layout/dashboard-layout.tsx`, the sidebar and navbar are conditionally rendered based on the `useIsMobile` hook.

## How to Test

To verify the Mobile Learn Mode on a desktop browser:

1.  Open Developer Tools (F12).
2.  Toggle the **Device Toolbar** (Ctrl+Shift+M or Cmd+Shift+M).
3.  Select a mobile device (e.g., iPhone, Pixel) or resize the viewport width to be less than **768px**.
4.  Navigate to `/dashboard`.
5.  Confirm that you are redirected to `/dashboard/learn` and the navigation elements are hidden.
