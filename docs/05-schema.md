# Database Schema

This document describes the database tables, the relationships between them, and the design decisions behind the shape they take. The schema is implemented in Prisma, with PostgreSQL-specific features used where they earn their keep — `tsvector` for full-text search, GIN-indexed text arrays for colour-identity queries, JSONB for nested fields that don't decompose cleanly, and `pgsodium` for Phase 3 BYOK encryption.

For the architecture that uses this schema, see [`04-architecture.md`](./04-architecture.md). For the toolchain that defines it, see [`03-tech-stack.md`](./03-tech-stack.md).

---

## Overview

The schema has two halves:

- **Catalogue half** — `cards`, `printings`, `sets`. Owned by the Scryfall ingest. Read by every user. Mutated only by the scheduled ingest job; never by user-initiated requests.
- **User half** — `users`, `collection_entries`, `decks`, `deck_cards`. Owned by users. Reads and writes scoped per-user by Supabase row-level security.

An observability table (`ingest_runs`) sits alongside.

ER sketch:

```
            ┌─────────┐         ┌────────────┐         ┌──────┐
            │  cards  │◄────────│  printings │────────►│ sets │
            └─────────┘ 1   M   └────────────┘ M    1  └──────┘
                ▲                     ▲
              M │                   M │
                │                     │
                │                ┌────────────────────┐
                │                │ collection_entries │
                │                └────────────────────┘
                │                     ▲
                │                   M │ user_id
                │                     │
                │                ┌────────┐
                │                │ users  │
                │                └────────┘
                │                     ▲
                │                   1 │
                │                     ▼ M
            ┌─────────────┐     ┌─────────┐
            │ deck_cards  │────►│  decks  │
            └─────────────┘ M 1 └─────────┘
```

(`cards.id` rather than `printings.id` is the deck reference — Commander decks care about Oracle identity, not which printing.)

---

## Catalogue half

### `cards` — the Oracle card

The abstract card. One row per unique card (as Scryfall defines uniqueness via `oracle_id`). All reprints of *Lightning Bolt* across every set produce one `cards` row and many `printings` rows.

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` (PK) | Internal primary key. |
| `oracle_id` | `uuid` (UNIQUE) | Scryfall's `oracle_id`. Stable across reprints. |
| `name` | `text` | E.g. `Lightning Bolt`. |
| `mana_cost` | `text` | `{R}`. Nullable — lands and some special cards have none. |
| `cmc` | `numeric(4,1)` | Converted mana cost. Decimal because of `{X}` cards. |
| `colors` | `text[]` | `{W,U,B,R,G}` subset. The card's actual colours. |
| `color_identity` | `text[]` | Colour identity (mana symbols anywhere on the card). Used for Commander legality. **GIN-indexed.** |
| `type_line` | `text` | E.g. `Creature — Soldier`. |
| `oracle_text` | `text` | Rules text. Full-text indexed via `tsvector`. |
| `power` | `text` | Nullable. Text, not int — `*` exists. |
| `toughness` | `text` | Same as above. |
| `loyalty` | `text` | Nullable. Planeswalkers only. |
| `keywords` | `text[]` | E.g. `{Flying, Vigilance}`. |
| `layout` | `text` | `normal`, `split`, `transform`, `modal_dfc`, etc. |
| `legalities` | `jsonb` | `{ "commander": "legal", "modern": "banned", ... }`. JSONB because the set of formats grows and the structure is sparse. |
| `is_active` | `boolean` | Soft-delete. `false` if Scryfall removed it from a bulk file. |
| `updated_at` | `timestamptz` | Set by the ingest. |

**Indexes:** `oracle_id` (unique), `name` (btree), `color_identity` (GIN), `to_tsvector('english', oracle_text)` (GIN), `legalities` (GIN with `jsonb_path_ops`).

**Notes:**

- `color_identity` as a `text[]` plus GIN index lets Commander legality queries use the `<@` operator (`color_identity <@ ARRAY['R','W']`) to find every card whose identity is a subset of the commander's. Fast even with the full catalogue loaded.
- `legalities` as JSONB rather than separate columns because the set of formats changes over time and most cards are legal in most formats. Sparse data fits JSONB better than wide schemas.
- Multi-faced cards (transform, modal DFC, split) are stored as a single `cards` row; per-face data either lives on the row (where mana costs combine cleanly) or in a `card_faces` companion table if it grows. Deferred until the ingest actually hits a case where the single-row shape doesn't fit.

### `printings` — a specific printed version

A specific printing in a specific set. *Lightning Bolt* has dozens of printings; each is a row here.

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` (PK) | Internal. |
| `scryfall_id` | `uuid` (UNIQUE) | Scryfall's per-printing `id`. |
| `card_id` | `uuid` (FK → `cards.id`) | The Oracle card this printing is of. |
| `set_id` | `uuid` (FK → `sets.id`) | The set this was printed in. |
| `collector_number` | `text` | E.g. `42a`. Text because of variants. |
| `rarity` | `text` | `common`, `uncommon`, `rare`, `mythic`, `special`, `bonus`. |
| `image_uris` | `jsonb` | `{ "small": "...", "normal": "...", "large": "...", "art_crop": "..." }`. |
| `prices` | `jsonb` | `{ "usd": "0.50", "eur": "0.40", "tix": "0.10" }`. Updated more frequently than the rest. |
| `language` | `text` | `en`, `ja`, `de`, etc. Default `en`. |
| `frame` | `text` | `1993`, `1997`, `2003`, `2015`, `future`. |
| `released_at` | `date` | |
| `is_active` | `boolean` | Soft-delete. |

**Indexes:** `scryfall_id` (unique), `card_id`, `set_id`, `(set_id, collector_number)` (unique together).

### `sets` — Magic sets

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` (PK) | |
| `code` | `text` (UNIQUE) | Three- or four-letter set code, e.g. `MOM`. |
| `name` | `text` | `March of the Machine`. |
| `released_at` | `date` | |
| `set_type` | `text` | `expansion`, `core`, `commander`, `masters`, `promo`, etc. |
| `icon_svg_uri` | `text` | Set symbol. |

**Indexes:** `code` (unique).

---

## User half

### `users` — user accounts

Extends Supabase Auth. Supabase manages email/password, sessions, recovery. This table holds app-level user data.

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` (PK, FK → `auth.users.id`) | Same UUID as the Supabase auth row. |
| `display_name` | `text` | Optional. |
| `theme_preference` | `text` | `dark`, `light`, or `system`. Defaults to `dark`. |
| `anthropic_key_encrypted` | `bytea` | Nullable. `pgsodium`-encrypted Anthropic API key. **Phase 3.** Never read by the client. |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**RLS:** every policy on `users` checks `id = auth.uid()` — users can only read or update their own row.

### `collection_entries` — what the user owns

A row per (user, printing) combination with a quantity. Modelled per-printing rather than per-card because a player might own multiple printings of the same card (different sets, foils, conditions) and care about distinguishing them.

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` (PK) | |
| `user_id` | `uuid` (FK → `users.id`) | |
| `printing_id` | `uuid` (FK → `printings.id`) | |
| `quantity` | `integer` | Non-negative. |
| `notes` | `text` | Free-form, optional. |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Indexes:** `(user_id, printing_id)` (unique together), `user_id`.

**RLS:** every policy checks `user_id = auth.uid()`.

### `decks` — saved decks

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` (PK) | |
| `user_id` | `uuid` (FK → `users.id`) | |
| `name` | `text` | |
| `description` | `text` | Optional. |
| `format` | `text` | `commander` initially. Other formats may follow. |
| `commander_card_id` | `uuid` (FK → `cards.id`) | Nullable for non-commander formats. |
| `partner_card_id` | `uuid` (FK → `cards.id`) | Nullable. For commanders with the Partner mechanic. |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Indexes:** `user_id`, `(user_id, name)`.

**RLS:** policies scope per `user_id`.

### `deck_cards` — deck contents

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` (PK) | |
| `deck_id` | `uuid` (FK → `decks.id`, ON DELETE CASCADE) | |
| `card_id` | `uuid` (FK → `cards.id`) | Oracle card, not printing — Commander cares about the abstract card. |
| `quantity` | `integer` | Always 1 outside of basic lands. |
| `is_commander` | `boolean` | True for the commander (and partner if any). |
| `category` | `text` | Optional grouping in the UI: `ramp`, `removal`, `card_draw`, etc. |

**Indexes:** `deck_id`, partial unique index on `(deck_id, card_id)` excluding basic lands.

---

## Observability

### `ingest_runs`

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` (PK) | |
| `started_at` | `timestamptz` | |
| `finished_at` | `timestamptz` | Nullable until done. |
| `cards_upserted` | `integer` | |
| `printings_upserted` | `integer` | |
| `scryfall_data_version` | `text` | From Scryfall's bulk-data manifest. |
| `status` | `text` | `running`, `succeeded`, `failed`. |
| `error_message` | `text` | Nullable. |

Server-only table. Not exposed to users.

---

## Design decisions

A few choices worth calling out:

**UUIDs as primary keys, not auto-incremented integers.** UUIDs make merging data across environments safer (dev / staging / prod) and avoid leaking record counts via sequential IDs. The cost (more storage, slightly slower indexes) is negligible at this scale.

**Soft-deletes on catalogue tables.** `cards.is_active` and `printings.is_active` rather than hard deletes. A user's collection or deck may reference cards that Scryfall later drops from its bulk file; preserving the row keeps those references valid. The UI shows a clear "no longer current" hint when an inactive card surfaces.

**Per-printing collection, per-card decks.** Collections distinguish printings because players care about which version they own. Decks reference Oracle cards because Commander legality is defined at the Oracle level — which set you choose to print your *Sol Ring* with doesn't affect deck legality.

**`color_identity` as a `text[]` with GIN index.** The `<@` containment operator on GIN-indexed arrays is the right primitive for Commander's "subset of the commander's colour identity" rule. A relational design (a `card_colors` junction table) would be cleaner academically but slower in practice for this specific query.

**JSONB for `legalities`, `image_uris`, and `prices`.** Sparse data with shapes that change as Scryfall evolves. JSONB with GIN indexes covers query needs without paying for schema changes every time a new format launches.

**Row-level security as a defence in depth.** Application code is already careful about user-scoped queries, but RLS catches the case where a bug slips one through. Two locks on the door beat one.

**`pgsodium` for BYOK, not application-layer encryption.** Encryption inside Postgres means the key never crosses an unnecessary boundary; decryption happens in the same transaction as the request. Application-layer encryption would also work but is more code to get right.

---

## Migrations

Migrations are managed by Prisma Migrate. Each migration is a versioned `.sql` file checked into the repository under `prisma/migrations/`. The `prisma migrate deploy` command runs all unapplied migrations against an environment.

Principles:

- **Forward-only.** No rollback scripts. If a migration is wrong, the next migration fixes it.
- **Schema and data migrations are separate.** Data migrations live in their own SQL files, executed by a deploy script, not by Prisma's migration runner.
- **Production migrations run on deploy.** No manual schema changes on production.

---

*See [`04-architecture.md`](./04-architecture.md) for how this schema is queried at runtime, and [`07-ai-integration.md`](./07-ai-integration.md) for the BYOK encryption flow that depends on `users.anthropic_key_encrypted`.*
