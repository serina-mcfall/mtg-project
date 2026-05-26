# Architecture

This document describes how the major components of the MTG Project fit together at runtime — what runs where, how requests flow through the system, and which trust boundaries the architecture defends. Some pieces only appear in later phases; where a component is phase-specific, the doc says so explicitly.

For the *why* behind each tool, see [`03-tech-stack.md`](./03-tech-stack.md). For when each piece comes online, see [`02-roadmap.md`](./02-roadmap.md). For the database shape under it all, see [`05-schema.md`](./05-schema.md).

---

## The components

Five components form the backbone of the app, with one more added in Phase 3:

- **Next.js application.** The whole frontend plus its backend. Server Components render data-heavy pages without shipping the data to the client; Client Components handle interactivity; API routes serve mutations. Deployed to Vercel.
- **PostgreSQL database (Supabase).** Single source of truth for cards, collection, decks, users. Hosts the `pgsodium` extension for Phase 3 BYOK encryption, plus GIN indexes for array-subset queries and `tsvector` indexes for full-text search.
- **Supabase Auth.** User authentication and session management. The Next.js app calls Supabase for sign-in and sign-up; sessions are validated server-side on every request that touches user data.
- **Scryfall ingest worker.** A scheduled job that fetches Scryfall's bulk data file, parses it, and upserts into Postgres. Runs daily. Not a separate service in early phases — implemented as a Vercel Cron-triggered API route in Phase 1A.
- **Scryfall (external).** The source of truth for card data. Bulk endpoint for the catalogue, regular API for things that change frequently (prices, new releases between bulk drops).
- **AI Orchestrator (Phase 3+).** A backend module inside the Next.js app responsible for composing prompts, calling Anthropic, parsing structured output, and validating it against deck-building rules. Decrypts the user's BYOK Anthropic key per-request and never persists the plaintext.

---

## Where each component runs

![Runtime architecture topology. The user's browser communicates over HTTPS with the Next.js application running on Vercel. The Next.js application contains React Server Components, hydrated Client Components, API routes for mutations, a Scryfall ingest cron, and the Phase 3+ AI Orchestrator. The Scryfall ingest pulls card data from Scryfall's bulk-data endpoint. Vercel reads from and writes to Supabase Postgres via Prisma; Supabase hosts pgsodium for BYOK encryption, GIN indexes, and Supabase Auth. In Phase 3 and beyond, the AI Orchestrator calls the Anthropic API using the user's BYOK Anthropic key.](./assets/architecture-topology.svg)

The whole production footprint is two managed services: Vercel and Supabase. Both are free at the scale this project operates at, and neither requires me to run servers myself.

---

## Data flow — card browsing (Phase 1A)

The most common interaction. A user opens a card-browsing page with some filters applied.

1. **Browser issues a GET** to `/cards?colors=UB&type=instant&owned=true`.
2. **Vercel routes the request** to the Next.js App Router. The matching page is a React Server Component.
3. **The Server Component reads the user's session** from the Supabase Auth cookie (needed for collection-scoped filters like `owned=true`).
4. **The Server Component constructs a Prisma query** from the filter parameters. Filter composition is type-checked at compile time — invalid filter combinations don't compile.
5. **Prisma issues a single Postgres query.** Queries on `color_identity` use the GIN index on the text array column; full-text searches use the `tsvector` index. Result set capped at a sensible page size.
6. **The Server Component renders the card grid as HTML on the server.** Only the rendered HTML and a small client-side JS payload (for filter interactivity) cross the wire. The card data itself does not get serialised to the client.
7. **The browser receives HTML and hydrates the interactive bits.** The user sees cards immediately; the filter controls work as soon as the JS hydrates.

Why this matters: card-browsing pages would be expensive if every card object were JSON-serialised and shipped to the client. Server Components let the data stay on the server and only the rendered output travel.

---

## Data flow — Scryfall ingest (Phase 1A)

Periodic, server-only, no user involvement.

1. **Vercel Cron fires the ingest endpoint** on a schedule (daily, off-peak hours).
2. **The endpoint fetches Scryfall's bulk-data manifest** and downloads the latest bulk file (default-cards JSON, on the order of 150 MB).
3. **The parser streams the JSON** rather than holding it all in memory, normalising each card into the project's schema (one row per card, additional rows per printing).
4. **Prisma upserts each card.** New cards inserted; existing cards updated where Scryfall data has changed. Cards no longer in the bulk file are marked `is_active = false` rather than deleted — preserving referential integrity with collection entries that reference them.
5. **The endpoint records the ingest run** (start time, end time, card count, Scryfall data version) for observability.

Why this matters: rebuilding the catalogue from scratch each time would be slow and would risk dropping cards mid-update. Upsert plus soft-delete preserves user collections even if Scryfall removes a card from the bulk file.

---

## Data flow — collection mutation (Phase 1A)

User adds a card to their collection from the browser.

1. **User clicks "Add to collection"** on a card. The Client Component issues a POST to `/api/collection`.
2. **The API route validates the request** — session is real, card ID exists, quantity is within range.
3. **Prisma writes the new collection entry** or increments the quantity on an existing entry (Postgres `ON CONFLICT` upsert).
4. **The API route returns the updated collection state for that card.** The Client Component reconciles its optimistic update against the response.
5. **A revalidation tag invalidates any cached views** that show this user's collection counts.

Why this matters: separating reads (Server Components, direct Prisma) from writes (API routes, validated) is the canonical Next.js App Router shape. Mutations always pass through a single validated layer that also handles revalidation; reads stay fast.

---

## Data flow — AI deck-building request (Phase 3)

The most interesting flow architecturally, because of the BYOK constraint. User asks the AI to draft a deck.

1. **User submits a prompt** ("aggressive Boros soldier tribal") from the deck-builder, with a commander already chosen.
2. **The Client Component POSTs to `/api/ai/concept-to-deck`** with the prompt and the commander.
3. **The API route validates the request** and resolves the commander's full record (including colour identity).
4. **The API route fetches the user's encrypted Anthropic key** from `users.anthropic_key_encrypted` and decrypts it via `pgsodium.crypto_secretbox_open` using a server-held master key. **The plaintext key lives only in memory for this request.** It is never logged, never returned to the client, never written back.
5. **The AI Orchestrator composes the prompt** — a system prompt with deck-building rules and format constraints, a user prompt with the concept and the commander record.
6. **The Orchestrator calls Anthropic** with the user's key, requesting structured output (a JSON deck list with per-card rationale).
7. **The Orchestrator parses the response** and runs it through the same format-legality validator the human deck-builder uses (colour identity, singleton rule, banned list, total card count). If validation fails, the Orchestrator either repairs (drops the offending card and re-prompts for a replacement) or rejects with a clear error.
8. **The validated deck list is returned to the client.** The user reviews, accepts, or edits individual cards before saving.

Three properties this design enforces:

- The user's plaintext API key never leaves the server's memory boundary.
- The AI cannot produce a deck that bypasses format rules — the same validator the human flow uses gates the response.
- The app pays no AI cost; usage bills directly to the user's Anthropic account.

---

## Trust boundaries

Three boundaries matter:

**Client / server.** The client is untrusted. Anything coming from the browser is validated server-side — filter parameters, mutation payloads, AI prompts. Cards and deck data are sent from the server in already-validated form.

**Server / database.** The Next.js server holds the database connection string and the `pgsodium` master key. Prisma's parameterised queries prevent SQL injection. Supabase row-level security policies add a second layer: a user can only read or modify their own collection and decks, even if a server-side bug somehow constructed a query for the wrong user.

**Server / external services.** Calls to Scryfall and Anthropic originate from Vercel functions, not from the browser. The Anthropic call carries the *user's* key (decrypted in-memory just before the request). Scryfall calls carry no auth — bulk and card data are public.

---

## Key architectural decisions

A few choices in here are deliberate and worth calling out:

**Server Components for data-heavy reads, API routes for mutations.** The canonical Next.js App Router shape. Reads benefit from rendering on the server (less data crossing the wire); writes benefit from passing through a single validated layer that can also handle cache revalidation.

**Single Next.js app, not a separate backend service.** API routes give me a backend without standing up a second service. Phase 5 may eventually warrant splitting the AI Orchestrator out, but not before then — premature service-splitting costs more than it earns at this scale.

**BYOK key decrypted per-request, never cached.** The simplest secure approach. Caching decrypted keys would save a few milliseconds per request at the cost of holding plaintext credentials in memory longer than necessary. Not a worthwhile trade.

**AI output validated against the same rules as human input.** The AI Orchestrator does not get a privileged code path. If the human deck-builder can't add an off-colour card, neither can the AI. This is the only design that makes the BYOK + AI combination safe to ship.

**Scryfall ingest as a cron'd API route, not a separate worker.** True for Phases 1 and 2. If the ingest grows past what a Vercel function comfortably handles (execution time limits, payload size), it moves to a dedicated worker. For now, simpler is better.

**Soft-delete cards from ingest, not hard-delete.** Foreign key integrity with collection entries matters more than perfect catalogue freshness. A card removed from Scryfall's bulk file is marked `is_active = false` rather than dropped; collection rows referencing it remain valid and surface a clear "this printing is no longer current" hint in the UI.

---

## What's not designed yet

Honest list of things this doc deliberately doesn't decide:

- **OCR (Phase 5).** Implementation choice deferred until Phase 5 begins — see [`02-roadmap.md`](./02-roadmap.md). Whichever path is chosen will add a new component to this architecture (mobile capture surface, image-processing pipeline, card-identification backend).
- **Multi-provider AI (Phase 5).** OpenRouter is committed architecturally, but the integration shape (proxy vs. direct calls, key handling for non-Anthropic providers, model routing logic) is deferred.
- **Public-facing surfaces.** If the project opens up to other users, this architecture grows surfaces this doc doesn't currently describe — rate-limiting, abuse prevention, account recovery flows, support tooling.
- **Vector embeddings.** Phase 3 starts with keyword and filter retrieval for the AI's card context. If that proves insufficient, `pgvector` gets layered on later. Tracked in [`08-open-questions.md`](./08-open-questions.md).

Naming what isn't decided is part of the design. Pretending these were already solved would be worse than leaving them visibly open.

---

*See [`05-schema.md`](./05-schema.md) for the database tables that sit underneath all of this, and [`07-ai-integration.md`](./07-ai-integration.md) for the AI Orchestrator design in detail.*
