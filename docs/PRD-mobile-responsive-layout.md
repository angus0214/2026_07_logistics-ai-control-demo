## Problem Statement

The Logistics AI Control Tower currently lacks proper responsive web design (RWD) for mobile devices. The horizontal flex layout (`flex-row`) works well on desktop but forces horizontal overflow on smaller screens. Consequently, mobile users (such as managers checking the dashboard on their phones) experience a broken layout where they cannot effectively use the left navigation sidebar or view the right document panel. 

## Solution

Implement a mobile-specific layout strategy that preserves all existing functionality without degrading features. We will replace the rigid horizontal layout with a responsive wrapper. The left sidebar will become an Off-canvas Drawer toggled by a hamburger menu, and the right document preview panel will be converted into a Modal/Sheet overlay that opens when the user clicks a "View Document" button. On desktop/tablet (from `md:` and `xl:` breakpoints up), the layout will remain as-is.

## User Stories

1. As a mobile user, I want the left navigation sidebar to be hidden by default, so that the main content area occupies the full width of my small screen.
2. As a mobile user, I want a hamburger menu icon in the top header, so that I can open the navigation menu when needed.
3. As a mobile user, I want the left sidebar to slide in as an overlay (Off-canvas Drawer) when I click the hamburger menu, so that I can switch views easily.
4. As a mobile user, I want to click outside the drawer to close the sidebar, so that I can quickly return to my task.
5. As a mobile user, I want the right document preview panel to be completely hidden by default, so that I don't have to scroll past my main data tables.
6. As a mobile user, I want a "View Document" button in the header, so that I can request to see the original Bill of Lading image.
7. As a mobile user, I want the document preview to appear as a full-screen Modal overlay when I click "View Document", so that I can inspect the image clearly.
8. As a desktop user, I want the left sidebar and right panel to remain fixed and visible side-by-side, so that my existing workflow is not disrupted.

## Implementation Decisions

- **Layout Structure**: We will modify `frontend/src/components/layout/DashboardLayout.vue`.
- **Left Sidebar**: We will add Tailwind classes to the left `<aside>` to handle responsive sliding (`fixed inset-y-0 left-0 z-50 -translate-x-full md:relative md:translate-x-0`).
- **Right Panel**: We will add Tailwind classes to the right `<aside>` to handle modal behavior (`fixed inset-0 z-50 xl:relative xl:w-[500px]`). 
- **State Management**: We will introduce two reactive variables (`isSidebarOpen` and `isRightPanelOpen`) via Vue's `ref` to manage the overlay states.
- **Toggle Controls**: A hamburger menu will be added to the mobile header to toggle `isSidebarOpen`. A "View Document" button will be added to toggle `isRightPanelOpen`.
- **References**: Documented in ADR `0004-mobile-responsive-strategy.md` and added to `CONTEXT.md`.

## Testing Decisions

- **Testing Approach**: Tests should focus on the external layout behavior and state toggling (DOM visibility) across different viewport sizes, rather than internal Vue implementation details.
- **Seams**: We will test at the component level targeting `DashboardLayout.vue` using Vue Test Utils.
- **Test Scenarios**: Ensure the sidebar overlays properly when `isSidebarOpen` is toggled. Ensure the right panel acts as a modal overlay when `isRightPanelOpen` is toggled. Verify that desktop layout ignores the toggle state and displays panels statically.

## Out of Scope

- Changing the internal content or styling of the individual Views (`DashboardView.vue`, `OpIngestionView.vue`).
- Implementing complex swipe gestures for the drawer (standard click-to-close overlay is sufficient for this iteration).

## Further Notes
- This is a critical enabler for the "Boss Dashboard" use case, where managers are highly likely to check the Text-to-SQL dashboard on their mobile devices while away from their desks.
