# 0002. Mobile Responsive Strategy (RWD)

## Status
Accepted

## Context
The Logistics AI Control Tower requires a responsive layout for mobile and tablet devices. The application features complex B2B components, including a left navigation sidebar, a center data processing area (tables/chat), and a right panel for document OCR previews (`w-[500px]`). Initially, the layout used a rigid horizontal flex layout which caused severe horizontal overflow and un-usability on mobile screens.

## Decision
We decided to adopt the following mobile layout strategy:

1. **Left Sidebar (Navigation)**: 
   - Strategy: **Off-canvas Drawer**. 
   - Rationale: Horizontal space on mobile is too scarce for even a mini-sidebar. The sidebar is hidden by default and toggled via a Hamburger menu in the header on mobile/tablet. On desktop (`md:` breakpoint and above), it remains a fixed left column.

2. **Right Panel (Document Preview)**: 
   - Strategy: **Modal/Sheet Overlay**.
   - Rationale: Vertical stacking would force users to scroll endlessly past long data tables to view the document. Instead, the right panel becomes a full-screen overlay on mobile, toggled by a "View Document" button in the mobile header. On large desktops (`xl:` breakpoint and above), it remains a fixed right column.

## Consequences
- The layout structure uses responsive Vue bindings (`ref(false)`) and Tailwind breakpoint utilities (`md:`, `xl:`).
- Child views do not need to manage the layout's responsiveness, as the layout wrapper handles the drawer/modal state and CSS transitions.
