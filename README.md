# MTG Project
*(working title — final project name pending)*

> A personal Magic: The Gathering collection database and Commander-focused deck builder, built around calm filter-first navigation rather than the firehose of existing tools.

---

## Status

**Concept stage.** Design and architecture decisions are documented in [`docs/`](./docs/), and a working visual concept plan lives at [`design/design-system.html`](./design/design-system.html). Implementation has not yet started — Phase 1A begins once the planning artefacts are complete.

See [`docs/02-roadmap.md`](./docs/02-roadmap.md) for the full phased build plan.

---

## Why this exists

Existing MTG tools — Moxfield, Archidekt, EDHREC — are powerful, but they're firehose-style: every option on screen at once, dense data tables, infinite scrolling. Brilliant for power users. Hostile to anyone who needs lower cognitive load.

The MTG Project is the calmer alternative. A personal collection database and Commander deck-builder, designed around filter-first navigation: start narrow, add filters as you go, let the AI assist you in building without making you wade through thousands of cards.

The same principle applies across the whole interface — **only one layer is loud at a time.** The chrome stays quiet so the cards can breathe.

---

## Planned features by phase

**Phase 1 — Foundation and collection**
Ships in two deployable stages. **1A** — Scryfall ingest pipeline, full database schema, collection management with CSV import from Moxfield, filter-first card browsing, and authentication. The lean MVP, deployed and usable. **1B** — Theme architecture scaffolding (dark mode default; light theme deferred to Phase 4), testing infrastructure, polished dark theme with accessibility audit.

**Phase 2 — Deck building**
Commander-first deck builder with automatic colour-identity constraints, format-legal filtering, deck visualisations (mana curve, type breakdown, colour distribution), commander spotlight for browsing and researching legendary creatures.

**Phase 3 — AI layer**
AI deck-building assistant powered by the Anthropic API. Concept-to-deck, deck doctor, card suggestion. Bring-your-own-key (BYOK) pattern — users provide their own API key for sustainable, scalable use.

**Phase 4 — Onboarding and teaching**
MTG-for-newcomers tutor mode, beginner-friendly deck recommender, power-level estimation. Light theme palette ("morning library") also lands in this phase.

**Phase 5 — Integrations**
OCR card scanning for physical-collection ingest, multi-provider AI support (via OpenRouter), and any public-facing surfaces if the project opens up to others.

---

## Tech stack at a glance

- **Frontend** — Next.js (App Router), TypeScript, React
- **Styling** — CSS Modules, Radix UI primitives, Motion
- **Database** — PostgreSQL via Supabase, Prisma ORM
- **Data source** — Scryfall (community-standard MTG API)
- **AI** — Anthropic API (Phase 3), OpenRouter (Phase 5)
- **Typography** — Cinzel, Andika, EB Garamond
- **Testing** — Vitest, React Testing Library
- **Hosting** — Vercel + Supabase

Full reasoning for each choice in [`docs/03-tech-stack.md`](./docs/03-tech-stack.md).

---

## Documentation

| Doc | What it covers |
|-----|----------------|
| [`01-vision.md`](./docs/01-vision.md) | Vision, target user, problem statement, differentiator |
| [`02-roadmap.md`](./docs/02-roadmap.md) | Five-phase build plan |
| [`03-tech-stack.md`](./docs/03-tech-stack.md) | Every tool, what it is, why chosen |
| [`04-architecture.md`](./docs/04-architecture.md) | System architecture and data flow |
| [`05-schema.md`](./docs/05-schema.md) | Database schema and design decisions |
| [`06-design-direction.md`](./docs/06-design-direction.md) | Design philosophy and visual identity |
| [`07-ai-integration.md`](./docs/07-ai-integration.md) | AI layer architecture and the BYOK pattern |
| [`08-open-questions.md`](./docs/08-open-questions.md) | Deferred decisions and known unknowns |

---

## Design

The visual concept plan is in [`design/design-system.html`](./design/design-system.html) — open it in a browser to see both palettes in action. The default is the candlelit dark theme; toggle in the top-right to preview the morning library light theme.

---

## Design philosophy in one line

A wizard's library. Candlelit at night, sunlit in the morning. Same world, different hour.

---

## Acknowledgements

- [**Scryfall**](https://scryfall.com) — for maintaining the community's most complete and accurate MTG card database, and making it freely available
- [**Wizards of the Coast**](https://magic.wizards.com) — for the game itself, and for the Fan Content Policy that makes projects like this possible
- [**Andrew Gioia**](https://github.com/andrewgioia/mana) — for the Mana font, the unsung backbone of every MTG tool on the web
- The Magic: The Gathering community — for thirty years of strategy, art, and stories

---

## License

[MIT](./LICENSE) — see the license file for full terms.

---

*This README is a living document. It will evolve as the project moves from concept into Phase 1 and beyond.*
