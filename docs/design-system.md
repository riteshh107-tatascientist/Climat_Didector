# ClimateGuard AI — Design System

Original design system — not copied from any product's branding, layout, or assets.
Usability patterns (navigation hierarchy, feed/history structure, search-first discovery)
are informed by familiar consumer products (YouTube, Facebook, Flipkart) as a usability
reference only.

## Color

Restrained palette. Risk colors are **reserved exclusively** for risk semantics — never used
decoratively elsewhere in the UI.

| Token | Hex | Use |
|---|---|---|
| `brand-700` | `#1f5c46` | Primary actions, active nav, logo mark |
| `teal-600` | `#1e7f82` | Secondary accents, charts |
| `risk-low` | `#2f9e5c` | LOW risk only |
| `risk-moderate` | `#d99a1f` | MODERATE risk only |
| `risk-high` | `#e2711d` | HIGH risk only |
| `risk-critical` | `#d1352b` | CRITICAL risk only |
| `surface` / `surface-subtle` / `surface-muted` | `#fff` / `#f7f8f7` / `#eef1ef` | Backgrounds, layered by elevation |
| `ink` / `ink-muted` / `ink-faint` | `#14201b` / `#4b5a53` / `#7c8b83` | Text hierarchy |

## Typography

Inter, system-ui fallback. Three weights of hierarchy: page title (`text-xl font-semibold`),
section heading (`text-sm font-semibold`), body (`text-sm`), meta/caption (`text-xs`).

## Layout principles

- Cards group related content — not applied to every element by default.
- Desktop: left sidebar navigation. Mobile: bottom nav (5 primary destinations) + slide-in
  menu for the rest — familiar, fast, no learning curve.
- Tables become stacked cards on mobile rather than horizontally scrolling illegibly.
- Whitespace is used deliberately; density is kept for tables/lists where it's earned data.

## Explicitly avoided

Per Phase 3 requirements: glassmorphism, large decorative gradients, glowing cards, excessive
rounded corners, walls of identical stat cards, unnecessary animation, generic "futuristic AI"
template aesthetics. Motion is limited to page-load skeletons, button loading states, and
toast entrance/exit — nothing decorative.
