# Design Direction

This is the design philosophy of the MTG Project — the visual language, the typographic voice, and the rules the interface follows when in doubt. The implementation lives in [`design/design-system.html`](../design/design-system.html); this document is the *why* behind it.

For the vision the design serves, see [`01-vision.md`](./01-vision.md). For the accessibility position the design takes as non-negotiable, that's woven through this document — there is no separate "accessibility chapter" because accessibility isn't a chapter.

---

## The metaphor

A wizard's library. Candlelit at night, sunlit in the morning. Same world, different hour.

The dark theme — **candlelit library** — is warm parchment ink on deep umber wood, lit by a single gold accent the way candlelight catches an illuminated initial. The light theme — **morning library** — is the same room when the shutters open: pale sun on linen pages, the gold accent now a quieter ochre.

The metaphor is load-bearing. It tells me when a design decision is correct (does this feel like an old library?) and when it isn't (does this feel like a SaaS dashboard?). It rules out an enormous space of plausible-but-wrong choices — bright primary colours, dense data tables, hard shadows, modern sans-serif headings — before I have to argue against them on case-by-case taste grounds.

---

## The first principle: one loud layer at a time

The interface has one loud thing at a time. The chrome stays quiet so the cards can breathe.

In practice:

- **Open a modal → background dims** to recede. The modal is the loud layer.
- **Focus a card → siblings desaturate slightly.** The focused card is the loud layer.
- **Apply filters → matching cards brighten, the rest become candidates for the next filter.** The result set is the loud layer.
- **Hover a button → the button gains presence**, but nothing else dims. Small interaction, small response.

This rule is what keeps the interface calm. Two loud things at once is a firehose. The MTG Project does not have firehoses.

---

## The second principle: filter-first, never search-first

The default state of any browsing surface is **empty**. The user adds constraints until the visible set is small enough to actually look at. The opposite of a search field with thousands of results paginated forever.

In practice:

- **Filter panels lead the layout.** They are not collapsed by default; they are the entry point.
- **The card grid is empty until at least one meaningful constraint is set.** A muted line of text sits in the void: *Choose a colour, type, or rarity to begin.*
- **As filters tighten, the visible count shrinks visibly.** That number going down is the feedback loop telling the user the filtering is working.

---

## Typography

Three faces, each with a specific job:

- **Cinzel** for display — headings, titles, navigation, button labels, card-name treatments. A monumental Roman-inscription serif. Carries the illuminated-manuscript feel; reads as voice, not as text to be scanned.
- **Andika** for body — paragraphs, descriptions, rules text, form labels, table content. A literacy-designed sans-serif with single-storey `a`, visually distinct `I` / `l` / `1`, open round shapes, generous spacing. Chosen specifically for accessibility, particularly dyslexic readers.
- **EB Garamond italic** for editorial moments — flavour text, quotations, section introductions, captions. A literary voice for paragraphs that earn it. Used sparingly.

Three faces is the right number. One is monotonous; two is fine but flat; four loses its grip on hierarchy. Three gives display, body, and editorial without anyone wearing two hats.

---

## Colour

Both palettes share the same role structure — only the values shift.

| Role | Candlelit (dark) | Morning library (light) |
|---|---|---|
| `--bg` | deep umber `#1a1410` | soft parchment `#f3e8d2` |
| `--bg-surface` | aged wood `#221a14` | linen `#ede0c4` |
| `--bg-elevated` | warmer wood `#2a2018` | warmer linen `#faf2e0` |
| `--ink` | parchment `#f0e3cd` | deep brown ink `#2c1810` |
| `--ink-muted` | aged ink `#b8a78a` | softer brown `#6a4d38` |
| `--accent-gold` | candleflame `#c4a059` | restrained ochre `#a8842a` |
| `--border` | wood grain `#3d2f23` | parchment edge `#d4be9b` |

The gold accent is the single non-neutral colour the chrome uses. It marks affordance: focus rings, active filter chips, primary buttons, the current filter count. Everything else is parchment, ink, or wood.

**MTG colour markers** (white, blue, black, red, green) are present but pulled back from their canonical brights — `#dccf9d` rather than the canonical pale cream, `#5e8fb8` rather than bright blue, and so on. The cards bring the saturation; the chrome doesn't compete.

---

## Light, depth, shadow

The candlelit theme uses warm, deep shadows (`rgba(0, 0, 0, 0.5)` for elevated surfaces, softer for resting ones). The morning theme uses pale brown shadows (`rgba(80, 56, 32, 0.18)`) — sun through window, not light-store fluorescent.

Surfaces are layered: `bg-deep < bg < bg-surface < bg-elevated`. The user's current focus rises through these layers. A modal sits on `bg-elevated`; the dimming wash sits between the modal and `bg`.

No hard edges. Borders are wood-grain warm; corners are gently rounded (≈8px on cards, ≈6px on inputs, ≈4px on buttons — small but present). Sharp 90° corners read as digital; a soft round reads as physical.

---

## Motion

Used sparingly. Specifically:

- **Theme transition** — the candlelit-to-sunlit swap. A 220ms cross-fade of background and ink, not all properties at once.
- **Modal / dialog open and close** — 180ms fade plus a slight scale (0.96 → 1.0), with focus moving in on open and restored on close.
- **Card hover** — a 120ms lift (`translateY(-2px)`, softened shadow). Subtle.
- **Drawer / panel open** — 200ms slide.

Every animation respects `prefers-reduced-motion`. When the OS asks for reduced motion, transitions shorten to near-instant cross-fades (≤50ms) but never disappear entirely — an instant flip can be more jarring than no animation at all.

---

## Component personality

Built on Radix UI primitives. Radix supplies the behaviour — focus trapping, keyboard navigation, ARIA semantics, escape handling. The MTG Project supplies the look. This is the right division: accessibility is solved upstream by people whose job it is to solve it; I focus on making the visual layer match the metaphor.

Each interactive widget meets its W3C ARIA Authoring Practices Guide pattern. Dialogs are real focus traps. Comboboxes announce as comboboxes to screen readers. Menus respect arrow-key navigation. None of that is bolted on. It comes for free with Radix and is preserved by the styling layer.

---

## What this design isn't

To make the design legible, here's what it explicitly is *not*:

- **A SaaS dashboard.** No status pills, no graphs cluttering the chrome, no "stats at a glance" bars at the top of every page.
- **A material-design Android app.** No bright primaries, no floating action buttons, no ripple effects.
- **A maximalist gaming UI.** No glowing borders, no animated backgrounds, no particle effects. Magic the game can be visually loud; Magic the *tool* should not be.
- **A neumorphism / glassmorphism / brutalism exercise.** No specific named style. The metaphor (wizard's library) is the style; trends come and go.

Naming what the design isn't is part of how it stays consistent.

---

## Accessibility is the design position

Saying "accessibility" as a feature is a sign it isn't one. In this project:

- Every interactive widget honours the W3C ARIA pattern for its widget type.
- Every interactive element has a visible `:focus-visible` ring (gold against either palette).
- All animation respects `prefers-reduced-motion`.
- Body text uses Andika, chosen for dyslexic legibility.
- Colour contrast hits WCAG AAA for body text and AA for muted text in both palettes.
- Every component is reachable and operable by keyboard alone — no mouse-only affordances.
- Card images carry meaningful alt text from Scryfall's data, not `alt="card"`.

Faking accessibility is worse than not claiming it. Anything in this project that says "accessible" actually is.

---

## The design philosophy in one line

*A wizard's library. Calm chrome, loud cards, one loud layer at a time.*

---

*See [`05-schema.md`](./05-schema.md) for the data the design renders, and [`design/design-system.html`](../design/design-system.html) for the working visual concept.*
