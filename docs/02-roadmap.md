# Roadmap

The MTG Project is built in five phases. Each one is a coherent slice of work that produces a meaningful product on its own — if the project stops at the end of any phase, what exists is still useful, not a half-finished feature stranded mid-build. Phase 1 is large enough that it ships in two deployable stages (1A and 1B); the other four phases each ship as a single unit.

The order is deliberately inward-out: build the core for one user (me) first, then make it teachable, then make it shareable. Features that touch the outside world — public access, OCR, multi-provider AI — sit at the end on purpose.

For the reasoning behind every tool used across these phases, see [`03-tech-stack.md`](./03-tech-stack.md). For how the pieces fit together at runtime, see [`04-architecture.md`](./04-architecture.md).

---

## Phase 1 — Foundation and collection

**Goal:** A working personal database of Magic cards with my collection loaded into it, browseable through a calm, filter-first interface.

Phase 1 ships in two deployable stages. **1A** is the lean MVP — bare-bones but genuinely *my* product, online and usable. **1B** is the polish and safety-net pass that turns 1A into a robust, tested product worth standing on for the rest of the build. Both stages produce a usable, deployed thing on their own; the 1A → 1B step is an upgrade in place, not a re-launch.

### Phase 1A — *"It's mine, and it's online."*

**Goal:** A deployed, authenticated browser of my Moxfield-imported collection, backed by Scryfall data, navigated through filters.

**Ships in this stage:**

- **Full database schema.** Cards, printings, sets, collection entries, users. Indexed for the queries the rest of the app will actually run.
- **Scryfall ingest pipeline.** A scheduled job that downloads Scryfall's bulk data file, parses it, and upserts into local Postgres tables. Designed to handle Scryfall's actual data shape — split cards, transform cards, modal double-faced cards — not just the happy path.
- **Collection management.** CSV import in Moxfield's export format, so I don't have to retype my collection. Manual add, remove, and quantity editing. Tags or notes per card if scope allows.
- **Filter-first card browsing.** The default state is empty. Filters add constraints. No infinite-scroll wall of every card ever printed.
- **Authentication.** Supabase auth. Single user to start (me); the data model already supports multiple users for later. In 1A this is non-negotiable — personal collection data on a live deployment without auth would be public to anyone with the URL.

**Definition of done:** I can log in to a live Vercel deployment, import my Moxfield CSV, and browse my collection through filters. The Scryfall ingest runs on a schedule.

### Phase 1B — *"It's polished, secured, and tested."*

**Goal:** The same product as 1A, with the testing safety net, theme scaffolding, and visual polish that the rest of the build will lean on.

**Ships in this stage:**

- **Theme architecture scaffolding.** CSS variables for both palettes, even though only dark ships in this stage. Light theme is a Phase 4 deliverable, but the architecture is in place from 1B on so Phase 4 becomes a palette swap, not a refactor.
- **Testing infrastructure.** Vitest + React Testing Library configured and in active use, with enough initial coverage that Phase 2 has somewhere to add tests rather than bolting testing on after the fact. CI runs the suite on every commit.
- **Polished dark theme + accessibility audit.** The candlelit palette tuned for contrast, hierarchy, and accessibility — not just "it works," but "it feels right and meets WCAG."

**Definition of done:** Test infrastructure runs in CI on every commit. The dark theme is polished and accessibility-audited. The 1A deployment is upgraded in place — same product, sturdier underneath.

**Explicitly not in Phase 1 (either stage):** Deck building. AI. Tutor mode. Light theme styling. OCR. Multi-user features beyond schema-level support.

**Why this phase boundary:** You can't build a deck-builder, an AI assistant, or a tutor mode without a database of cards underneath. Phase 1 is the foundation everything else stands on. It also produces something genuinely useful on its own: a calm, searchable view of my real collection. The 1A / 1B split keeps the first deploy moment as early and lean as possible — every shipped stage matters for motivation and feedback — while letting the safety net and polish layer arrive deliberately rather than being skipped in a rush to ship.

---

## Phase 2 — Deck building

**Goal:** A Commander deck-builder, fully manual, that knows the format's rules well enough to keep me inside them automatically.

**Ships in this phase:**

- **Commander deck-builder.** Pick a commander, the app derives the colour identity, every subsequent filter and pick respects it. No accidentally adding a Red card to a Mono-Blue deck.
- **Format-legal filtering.** Banned and restricted lists honoured. Singleton enforced (Commander is one-of-each-card except basic lands). Visual feedback when the user tries to violate a rule, not silent rejection.
- **Deck visualisations.** Mana curve, card-type breakdown, colour distribution, average mana value. Used sparingly — only the ones that actually help a deck-builder, not the firehose of statistics for its own sake.
- **Commander spotlight.** A browsing surface dedicated to legendary creatures (and other Commander-eligible cards), letting me research potential commanders without leaving the app.
- **Deck save / load / edit.** Multiple decks per user. Versioning if scope allows; otherwise overwrite-only.

**Explicitly not in this phase:** AI deck-building. Tutor mode. OCR. Other formats. Public deck sharing.

**Why this phase boundary:** Phase 2 produces a useful Commander tool *before* the AI lands. This matters for two reasons. First, the AI in Phase 3 needs to compose deck lists that pass the same constraints the human flow enforces — so the human flow has to exist and be correct first. Second, if Phase 3 never ships, Phase 2 is still a complete product.

**Definition of done:** I can pick a commander, build a full 99-card deck inside the colour identity, save it, reopen it, edit it. Deck visualisations render. All format rules enforced in the UI, not just in the database.

---

## Phase 3 — AI layer

**Goal:** An AI deck-building assistant that takes the cognitive load off "where do I even start" without taking the decisions away from the user.

**Ships in this phase:**

- **Concept-to-deck.** User describes a deck in plain language ("aggressive Red-White soldier tribal", "Simic ramp with a +1/+1 counter theme"). The AI proposes a deck list that respects the commander's colour identity and the rest of Phase 2's constraints. The user accepts, rejects, or edits individual cards.
- **Deck doctor.** User selects an existing deck. The AI flags weak spots (insufficient ramp, missing removal, mana base issues) and suggests specific replacements, preferring cards already in the user's collection.
- **Card suggestion.** While building manually, "suggest five more cards that fit this theme" — a low-friction nudge rather than a full handoff.
- **Anthropic-only BYOK.** Each user provides their own Anthropic API key, encrypted at rest via Postgres `pgsodium`. The orchestrator uses their key for their requests; the app absorbs no AI cost.
- **AI Orchestrator.** A backend component that composes prompts, calls Claude, parses structured output, validates it against the deck-building rules, and returns suggestions to the UI. The AI's output is always run through the same format-legality checks as a human's input — the AI doesn't get to bypass the rules.

**Explicitly not in this phase:** Multi-provider AI. AI without a user-supplied key. Fully autonomous deck-building (the AI proposes; the user always decides). Tutor mode (Phase 4 owns the teaching layer).

**Why this phase boundary:** The AI is a layer on top of working deck-building, not a replacement for it. Phase 2's constraints exist as a moat the AI must respect. Building AI first would mean an assistant that can suggest illegal decks; building it third means an assistant that can't.

**Definition of done:** A user (with their own Anthropic API key) can describe a deck in plain language and get a colour-identity-legal, format-legal deck list back. The deck doctor can analyse a saved deck and suggest specific improvements. All AI output passes the same rule checks as a human's. BYOK encryption verified end-to-end.

---

## Phase 4 — Onboarding and teaching

**Goal:** A version of the app a brand-new Magic player can sit down with and learn from, without needing a friend already in the hobby to explain things.

**Ships in this phase:**

- **Tutor mode.** A guided introduction to Magic: the colour pie, card types, the stack, combat, common mechanics. Designed for someone who has never played, not a refresher for lapsed players.
- **Beginner-friendly deck recommender.** Rather than "describe a deck and AI builds it" (which assumes vocabulary the newcomer doesn't have yet), this is a short series of friendly questions — *do you like attacking? do you prefer one big creature or lots of small ones? are you OK with reading lots of text?* — that recommends a starting commander and a deck shape.
- **Power-level estimation.** A rough 1-to-10 read on a deck's competitive power, with plain-language explanation of where it sits and why. Useful for finding the right pod to play with.
- **Light theme — "morning library."** The light counterpart to the dark "candlelit library." Already scaffolded in Phase 1; this is where the palette tuning and visual polish happen.

**Explicitly not in this phase:** OCR. Multi-provider AI. Public-facing surfaces.

**Why this phase boundary:** The teaching layer makes sense only once the product it's teaching actually works. Phases 1–3 build the tool; Phase 4 makes it learnable. The light theme lands here, not earlier, because it's polish-and-finishing work and this is the polish-and-finishing phase.

**Definition of done:** A friend with zero Magic experience can complete the tutor mode, pick a starting commander through the recommender, and end up with a deck they understand and can play. Light theme is visually complete, accessibility-audited, and toggleable.

---

## Phase 5 — Integrations

**Goal:** Outward-facing features. The things that matter only if the project opens beyond personal use.

**Ships in this phase:**

- **OCR card scanning.** Point a phone camera at a physical card; the app identifies it and offers to add it to the collection. Implementation approach is deferred — three viable options (Google Cloud Vision, a commercial MTG-specific service, a self-hosted ML model) each carry different cost and accuracy trade-offs. Choice made when Phase 5 begins.
- **Multi-provider AI via OpenRouter.** A single API surface that routes to any major AI provider. Users get model choice; the app stays simple. Architecture committed (OpenRouter), implementation deferred to this phase.
- **Public-facing surfaces, if relevant.** If the project ever opens to other users, the work required for that lives here — onboarding for unfamiliar users, account management beyond the personal-use baseline, privacy and ToS surfaces, analytics if any.

**Explicitly not in this phase:** Anything that doesn't make sense before Phases 1–4 are stable.

**Why this phase boundary:** Outward-facing features carry overhead — public account management, support, terms of service, hosting costs at scale, multi-provider maintenance. None of that overhead is worth taking on until the inward-facing product is genuinely good.

**Definition of done:** Deliberately loose. Phase 5 is the phase where the project decides what kind of public-facing thing it wants to be, or decides not to be one at all. The shape of "done" depends on that decision.

---

## Beyond the phases

A few things sit deliberately outside the roadmap, either because they're permanent non-goals or because they're decisions to defer. The full list lives in [`08-open-questions.md`](./08-open-questions.md). The headline non-goals:

- Tournament-grade competitive analytics.
- A trading or marketplace surface.
- Deep multi-format support beyond Commander.
- Anything that requires hosting costs the project can't sustain on a free tier.

---

## A note on timelines

There are deliberately no dates on the phases above. This project starts towards the end of bootcamp and is, realistically, a long-running thing — possibly across years, possibly never reaching completion. That's fine. The phases are scope groupings, not calendar commitments.

What matters more than a delivery date is that each phase, on its own, is a complete and useful thing. After Phase 1A, my collection is online and browseable. After Phase 1B, it's polished, secured, and tested. After Phase 2, a Commander deck-builder. After Phase 3, an AI-assisted deck-builder. Each step is real, ship-ready, and worth the work even if no further step ever happens.

---

*Linked next: [`03-tech-stack.md`](./03-tech-stack.md) for the toolchain that supports every phase, and [`04-architecture.md`](./04-architecture.md) for how the system fits together.*
