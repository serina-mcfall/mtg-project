# Open Questions

A working list of decisions deferred and unknowns acknowledged. The project is concept-stage; this document is honest about what hasn't been answered yet.

Each entry has the same shape: the question, what's known, what's deferred, the decision point (when an answer is actually needed), and the candidate options.

---

## Vector embeddings for AI card retrieval

**Question:** Should the AI's card-context retrieval use vector embeddings (semantic search) or stay with keyword and filter retrieval?

**Known:** Phase 3 ships with keyword and filter retrieval — a hand-crafted pre-filter that narrows the catalogue from ~30,000 cards to the ~500 most relevant for the AI's context, based on the user's commander and request. This is enough for most concept-to-deck and deck-doctor requests.

**Deferred:** Whether to layer `pgvector` embeddings on top later, for cases where semantic similarity ("cards that *feel* like X") matters more than keyword overlap.

**Decision point:** During Phase 3, once real usage shows where the keyword pre-filter is and isn't sufficient. Premature embedding adoption adds infrastructure (embedding generation, storage, query cost) for ambiguous benefit.

**Options:**

- **Keep keyword-only.** Simpler, no embedding maintenance, fast enough for most queries.
- **Layer `pgvector` on a small subset.** Compute embeddings only for card-text searches initiated explicitly by the user, not for every AI request.
- **Full embedding adoption.** Every card text embedded; AI retrieval becomes semantic-first with keyword fallback.

---

## OCR implementation (Phase 5)

**Question:** How is "scan a physical card to add to collection" implemented?

**Known:** It's a Phase 5 feature. Mobile-first; the user points a phone camera at a card and the app identifies it.

**Deferred:** Which OCR / image-recognition backend.

**Decision point:** Start of Phase 5. Choosing earlier means committing to operational assumptions (cost model, latency, accuracy) that may not hold by then.

**Options:**

- **Google Cloud Vision OCR + custom matching against the catalogue.** General-purpose, cheap per request, requires building the matching layer on top.
- **A commercial MTG-specific service.** Higher per-request cost but matching is solved. Reduces engineering work to integration only.
- **Self-hosted ML model.** Maximum control, zero per-request cost, large up-front model work and hosting decision.

Trade-off shape: cost vs. accuracy vs. control. The right answer depends on whether Phase 5 ever opens to other users.

---

## Multi-provider AI architecture (Phase 5)

**Question:** What does the OpenRouter integration look like in detail?

**Known:** OpenRouter is the committed architectural answer for multi-provider. It exposes a unified API across Anthropic, OpenAI, Google, Llama, Mistral and others.

**Deferred:** Integration shape (proxy via OpenRouter for *all* AI calls, or per-provider with OpenRouter as one of several?), model routing logic (does the user pick a model, or does the app pick based on the task?), key handling for the multi-provider case.

**Decision point:** Start of Phase 5.

**Options:**

- **OpenRouter for everything.** Single API surface, including Anthropic. Simplest architecture; small per-call markup.
- **Anthropic direct + OpenRouter for everyone else.** Preserves the existing Anthropic path; adds OpenRouter only for new providers. More code, no markup on Anthropic.
- **Per-provider integrations.** Custom integration for each. Most flexibility, most maintenance.

---

## Analytics

**Question:** Does the project use any analytics? If so, which?

**Known:** No analytics in Phase 1. Personal use; no traffic to analyse.

**Deferred:** Whether analytics are added at all, and which tool, depending on whether the project ever opens publicly.

**Decision point:** Whenever public-facing surfaces are seriously considered (Phase 5 territory).

**Options:**

- **No analytics.** Simplest. Honours the project's privacy-first instinct.
- **GoatCounter.** Privacy-respecting, no cookies, no personal data, generous free tier.
- **Plausible.** Similar position to GoatCounter; cleaner dashboards; small monthly cost.

Categorically excluded: Google Analytics, Mixpanel, Amplitude, or any analytics tool that fingerprints users or sells their data.

---

## Public surfaces — will the project ever open?

**Question:** Does this project ever become a public web app, or does it stay a personal tool?

**Known:** Personal use first. Multi-user support is in the data model from Phase 1, but no public-facing surfaces ship before Phase 5.

**Deferred:** Whether to take the project public at all. Doing so adds non-trivial surface area: account recovery, support, terms of service, privacy policy, abuse handling, cost-at-scale, more.

**Decision point:** During or after Phase 4. Not earlier — the decision depends on what the personal product feels like once it's polished.

**Options:**

- **Stay personal-only forever.** Honest acknowledgement that this is a personal tool. Saves a lot of work.
- **Open to a small circle.** Friends, playgroup, Discord. Low surface area, real users.
- **Open publicly with explicit BYOK gating.** Public sign-up but full AI features require the user's own Anthropic key. Scales without subsidising costs.
- **Open publicly with a freemium model.** Some features free, AI features behind subscription. Most engineering work; most ongoing cost.

---

## Deck versioning shape

**Question:** Does the deck-builder support versioning (snapshot a deck at a point in time), or overwrite-only?

**Known:** Phase 2 ships saves; whether they're versioned is "if scope allows" in the roadmap.

**Deferred:** The shape of versioning if it ships. Linear snapshots? Branched edits? Diffs between snapshots?

**Decision point:** During Phase 2 implementation.

**Options:**

- **No versioning.** Overwrite-only. Simplest. Easiest. Users sometimes regret edits.
- **Snapshot on demand.** User clicks "save version" when they want a checkpoint. Manual, predictable.
- **Auto-snapshot on every save.** Every save creates a new version automatically. Heavy on storage; great for "what did I have last week?".

---

## Mobile-specific UI

**Question:** Is there a mobile-specific layout, or does responsive design carry the whole load?

**Known:** Responsive design is implicit from Phase 1 — the design-system.html demonstrates both palettes at desktop sizes; mobile breakpoints are part of any web build.

**Deferred:** Whether mobile gets first-class native-feeling layouts (different navigation, gesture-first card flipping) or whether the responsive desktop layout simply collapses gracefully.

**Decision point:** During Phase 4 polish, or whenever OCR (Phase 5, mobile-first by definition) lands and forces the question.

**Options:**

- **Responsive only.** The desktop layout collapses to mobile via CSS breakpoints. Simplest.
- **Mobile-specific routes for high-value flows.** OCR scanning gets a mobile-native layout; everything else stays responsive.
- **Full mobile-first redesign.** Treat mobile as a first-class surface with its own layouts. Most work.

---

## Offline mode

**Question:** Should any part of the app work offline?

**Known:** Nothing in the current plan requires offline support.

**Deferred:** Whether the collection browser — the most useful offline-capable surface, at a tournament or in a deck-building session away from wifi — gets a service worker / IndexedDB cache.

**Decision point:** Post-Phase 5, if at all. Offline is a real engineering commitment and the project is not ready to make it.

**Options:**

- **Online-only, forever.** Honest about what the project is.
- **Offline read-only for the collection.** Cache the user's collection locally; allow browsing without network. Writes require connectivity.
- **Full offline mode.** Sync layer, conflict resolution, the whole thing. Major scope.

---

## Final project name

**Question:** What is this project called?

**Known:** "MTG Project" is a working title only. The README acknowledges this in its second line.

**Deferred:** The actual name. A name that fits the wizard's-library metaphor would carry the design language outward; a generic "MTGFoo" name would let the design language do all the work alone.

**Decision point:** Before public-facing surfaces ship, or before the project is presented to people outside the bootcamp circle — whichever comes first.

**Options:** Open. Candidate territory includes Latin / Old-English library words, names that evoke candlelight or quiet rooms, names that nod to the metaphor without being on-the-nose. No shortlist yet.

---

## How this document evolves

Open questions get added when they surface (during planning, during implementation, after user feedback). They get *removed* when answered — answered questions move into the document they actually affect (`04-architecture.md`, `03-tech-stack.md`, etc.).

The list is honest: if a question is here, it's because there isn't a decision yet, and pretending otherwise would weaken the planning.

---

*See [`02-roadmap.md`](./02-roadmap.md) for which phases these decisions land in, and [`04-architecture.md`](./04-architecture.md) for the architectural shapes affected.*
