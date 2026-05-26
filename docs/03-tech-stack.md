# Technical Stack

This document lists every tool committed to for the MTG Project, with the reasoning behind each choice. The stack is deliberately consistent with patterns from my Dev Academy bootcamp and my other ongoing project (Avalúne) — overlap means transferable patterns across projects and fewer context-switching costs in my own head.

For the timeline of when each piece comes into play, see [`02-roadmap.md`](./02-roadmap.md). For how the tools fit together at runtime, see [`04-architecture.md`](./04-architecture.md).

---

## Frontend framework

### Next.js (App Router)

A React framework that adds server-side rendering, file-based routing, API routes, and image optimisation on top of vanilla React. I'm using the App Router (Next 13+) rather than the older Pages Router, which gives access to React Server Components.

**Why:** The MTG Project has both data-heavy pages (filtered card browsing, collection views) and interactive components (deck builder, drag-and-drop). Server Components handle the data-heavy work without ballooning the client bundle; Client Components handle interactivity. API routes give me a backend without standing up a separate service. Built-in image optimisation matters more than it sounds — card images are everywhere in this app, and Next.js handles caching and responsive sizes automatically.

### TypeScript

Statically-typed superset of JavaScript that compiles to JavaScript. The type system catches mistakes at compile time that would otherwise become runtime errors.

**Why:** Scryfall returns JSON with a huge shape — many nested objects, optional fields, arrays, conditional shapes for different card layouts (normal, split, transform, etc.). TypeScript catches mismatches between my assumptions about that shape and what's actually there before code runs. Also valuable for Prisma, which generates fully-typed query clients from the schema.

### React

The component-based UI library Next.js is built on. Familiar from the bootcamp.

**Why:** Industry standard, well-documented, vast ecosystem, and the framework I'm strongest in. No reason to switch to Vue, Svelte, or Solid for a project this size when React handles it cleanly.

---

## Styling and UI primitives

### CSS Modules

Scoped CSS files (`Component.module.css`) where class names are local to the component rather than global. Composes cleanly with vanilla CSS without requiring a runtime CSS-in-JS library.

**Why:** The MTG Project's design direction (candlelit wizard's library / morning library) is custom, ornamental, and theme-token-driven. Tailwind's utility-first approach optimises for speed and consistency but works against the kind of bespoke styling this project needs. CSS Modules give me full control over the cascade while keeping styles co-located with their components.

### Radix UI

A library of unstyled, accessible UI primitives — dialogs, dropdowns, tabs, popovers, sliders, etc. Provides keyboard navigation, focus management, and ARIA semantics for free, while leaving all visual styling to the consumer.

**Why:** Building accessible UI primitives from scratch is genuinely hard — focus traps, escape key handling, ARIA roles, keyboard navigation patterns from the W3C ARIA Authoring Practices Guide, screen reader announcements. Radix handles all of that correctly. I supply the visual design; Radix supplies the accessibility. Given how non-negotiable accessibility is for this project, taking a shortcut on a11y primitives would undermine the whole design position.

### Motion (formerly Framer Motion)

Animation library for React. Provides declarative motion primitives that respect user motion preferences.

**Why:** Used sparingly, for the few animations that matter (theme transition, card hover lift, drawer open/close). The `prefers-reduced-motion` respect is built in. Lighter than pulling in a full animation framework when this covers what's actually used.

---

## Database

### PostgreSQL

Relational database with strong typing, JSONB columns, full-text search, array types, and a rich extension ecosystem.

**Why:** The data model is genuinely relational — cards relate to printings, printings to collection entries, decks contain cards. Postgres is built for this. Specific features that mattered to the choice:

- **JSONB columns** for nested Scryfall fields (`legalities`, `image_uris`, `prices`) that don't fit cleanly into separate columns
- **Full-text search** built into the database — no separate Elasticsearch needed for "search any card by name or rules text"
- **Text array types** with GIN indexes — used for `color_identity`, where Commander format legality requires "subset of" queries that arrays do efficiently
- **pgvector extension** available if Phase 3 ever needs semantic embeddings (deferred for now; see [`08-open-questions.md`](./08-open-questions.md))

### Supabase

A managed Postgres host with built-in auth, storage, row-level security, and a generous free tier.

**Why:** Hosting Postgres yourself means managing backups, scaling, security patches, connection pooling. Supabase handles all that. Built-in auth means I don't need to write authentication from scratch or pull in a separate library (NextAuth, Clerk, etc.). The `pgsodium` extension comes built-in, which is needed for Phase 3 BYOK encryption of user-supplied API keys.

### Prisma

A type-safe ORM for Node.js. Generates a fully-typed query client from a declarative schema file; handles migrations as code.

**Why:** With TypeScript already in the stack, Prisma's generated types compose beautifully — autocomplete on every query, compile-time errors on schema mismatches. Migrations live in version control as `.sql` files. Drizzle is gaining traction as a newer alternative, but Prisma is what I'm most productive in coming out of bootcamp, and the maturity difference still matters for a project I'm presenting.

---

## Data source

### Scryfall

The community-standard Magic: The Gathering API. Free, comprehensive (every card ever printed), well-maintained, and explicitly licensed for use in Magic-related tools.

**Why:** Building a card catalogue from scratch is unnecessary — Scryfall already maintains the most accurate, complete, and up-to-date one. The "bulk data" endpoint provides the entire card database as a downloadable JSON file, which the app ingests on a schedule into its own Postgres tables. Direct API calls are reserved for things that change frequently, like current prices. Card image hot-linking from Scryfall's CDN is standard practice in Magic-related tools and explicitly permitted by their terms.

---

## AI layer

### Anthropic API (Claude)

The Anthropic API providing access to Claude models. Used for Phase 3 AI features (concept-to-deck building, deck doctor, card suggestion).

**Why:** Claude is strong at reasoning over structured data (cards) and producing structured output (deck lists with per-card rationale). I'm already familiar with the API surface from using Claude Code in my development workflow. The API has clean, well-documented streaming, structured output, and tool-use surfaces that fit how the AI Orchestrator needs to compose deck suggestions.

Phase 3 ships **Anthropic-only BYOK** (Bring Your Own Key). Each user provides their own API key, stored encrypted at rest via Postgres `pgsodium`, and the orchestrator uses their key on their behalf for AI requests. They pay Anthropic directly for their usage; the app absorbs no AI cost.

### OpenRouter (Phase 5)

A proxy service that exposes a unified API across many AI providers (Anthropic, OpenAI, Google, Llama, Mistral, etc.). Users get one API key that routes to any underlying model.

**Why:** Deferred to Phase 5. When multi-provider support becomes relevant, OpenRouter is the cleaner architectural answer than writing four separate provider integrations. Users get model choice without the app maintaining four API shapes. There's a small per-call markup, but the engineering simplification is worth it. Phase 3 stays Claude-only deliberately to keep the surface area focused and prompts tuned to Claude's strengths.

---

## Typography

### Cinzel — display

A monumental, Roman-inscription-style serif designed by Natanael Gama. Used for headings, titles, navigation, button labels, and card names.

**Why:** The design direction is illuminated-manuscript / wizard's-library, and Cinzel's hand-cut Roman feel fits that voice. It's also the closest free analogue to the kind of monumental titling typography used on Magic: The Gathering's own card names, which gives the project its MTG feel without using Wizards' proprietary Beleren typeface.

### Andika — body

A sans-serif designed for literacy and dyslexic readers. Single-storey lowercase `a`, visually distinct `I` / `l` / `1`, open round shapes, and generous spacing.

**Why:** Andika is designed specifically for accessibility, particularly for dyslexic readers. It's also the body font I use in my other project (Avalúne), keeping a consistent personal-practice line across projects. The accessibility position the MTG Project takes is meant to be genuine — and that starts with the font used for body text, which is where users spend the most reading time.

### EB Garamond — italic

An elegant, refined serif based on Claude Garamond's 16th-century types, digitised by Georg Duffner. Used in italic for quotations, flavour text, section introductions, and editorial moments.

**Why:** Provides a third voice on the page — different from monumental Cinzel headings and the working Andika body. Used sparingly, for moments that deserve a literary touch.

---

## Testing

### Vitest

A fast unit-testing framework built on top of Vite. Compatible with Jest's API but significantly faster in this stack.

**Why:** Native ESM support, well-integrated with TypeScript, and the modern Next.js / TypeScript ecosystem has largely consolidated around it. No reason to use the older, slower Jest when Vitest is the same API with better ergonomics.

### React Testing Library

A companion library for testing React components by their accessibility tree rather than their implementation details.

**Why:** Tests written against what the user sees (and what assistive technology sees) are more durable than tests written against implementation. The library's approach reinforces the accessibility-first principle baked into the rest of the architecture — if a test passes, the feature is reachable by keyboard and screen reader.

Testing infrastructure lands as **Phase 1B scaffolding**, not a later addition. The Phase 1A MVP can ship without an automated test suite, but 1B's polish pass is where Vitest and React Testing Library come in — early enough that Phase 2 and beyond have somewhere to add tests as features arrive, rather than bolting testing on after the fact.

---

## Hosting and deployment

### Vercel

Hosting platform for Next.js applications. Free tier sufficient for personal-scale traffic.

**Why:** Built by the same company as Next.js, so deployment is zero-config: push to GitHub, Vercel deploys. Automatic preview environments per pull request, edge runtime for fast responses, generous free tier. Self-hosting on a VPS would trade simplicity for control I don't need at this stage.

### Supabase (database + auth)

Already covered under Database. Worth noting here that Supabase + Vercel together cover the entire production hosting footprint of the application — both free at the scale this project operates.

---

## Development environment

### Operating system: WSL (Ubuntu) on Windows

Windows Subsystem for Linux. Lets me use a Linux toolchain (Node, Postgres, build tools) on my Windows desktop without dual-booting or running a full virtual machine.

### Editor: VS Code

With extensions: ESLint, Prettier, the official Prisma extension, and GitLens.

### Version control: Git and GitHub

GitHub Education account, which provides GitHub Pro features, Codespaces hours, and full Copilot access (though I primarily use Claude Code for AI-assisted development).

### Optional: GitHub Codespaces

Cloud-hosted development environments. 180 core-hours per month via the Education plan. Used when working across machines or when I need a fresh, isolated environment quickly.

---

## Deferred technical decisions

Several Phase 3+ technical choices are deliberately deferred and tracked in [`08-open-questions.md`](./08-open-questions.md):

- **Vector embeddings** — Phase 3 starts with simple keyword/filter retrieval. If that proves insufficient for the AI deck-builder's needs, `pgvector` embeddings get layered on later. No decision required before then.
- **OCR scanning** — Phase 5 feature. Three possible implementations exist (Google Cloud Vision API, a commercial MTG-specific service, or self-hosted ML model), each with different cost and accuracy trade-offs. Decision deferred until Phase 5 begins.
- **Multi-provider AI** — Phase 5 feature. Architectural answer (OpenRouter) is committed; implementation deferred until Phase 5.
- **Analytics** — Only relevant if the project ever opens publicly. GoatCounter or Plausible (matching the privacy-first stance) are the leading candidates.

---

## Why this stack reads as a coherent whole

Every choice above either reinforces an explicit design principle of the project or matches my existing toolchain. The MTG Project's stated values — calm UX, accessibility-first, filter-first navigation, "lower cognitive load than Moxfield" — show up in the toolchain decisions:

- **Radix UI** for accessibility primitives, because faking accessibility is worse than no accessibility
- **Andika** for body text, because the body font is where accessibility is felt most
- **CSS Modules** rather than utility-first frameworks, because the design voice is bespoke
- **CSS variables** for the eventual light/dark theme swap, baked in from Phase 1B so Phase 4 is a swap not a rewrite
- **Postgres text arrays** for `color_identity`, because Commander's legality rule needs subset queries to be fast
- **Anthropic-only Phase 3 / OpenRouter Phase 5** for AI, because shipping focused beats shipping generic
- **TypeScript + Prisma + Supabase** as the data spine, because end-to-end types make the schema knowable to the rest of the system

No tool is in this stack because it's trendy. Each one is justified by a specific need the project has.
