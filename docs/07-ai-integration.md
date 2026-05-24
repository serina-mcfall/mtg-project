# AI Integration

This document describes the AI layer in detail — what it does, how it's structured, where the user's key lives, what the validator gates, and why Phase 3 ships Anthropic-only despite a multi-provider future. Architectural shape lives in [`04-architecture.md`](./04-architecture.md); this is the why and the depth.

The AI layer is Phase 3 work. No part of it ships before Phases 1 and 2 are complete and stable.

---

## What the AI does (and doesn't)

The AI in this project has three jobs:

- **Concept-to-deck.** A user describes a deck in plain language ("aggressive Boros soldier tribal", "Simic ramp with a +1/+1 counter theme"). The AI proposes a 99-card list that fits the commander's colour identity and the format's rules.
- **Deck doctor.** A user selects an existing deck. The AI reads its shape and flags weak spots — insufficient ramp, missing removal, suspicious mana base, off-theme cards — and suggests specific replacements, preferring cards the user already owns.
- **Card suggestion.** While the user is building manually, "suggest five more cards that fit this theme" — a low-friction nudge, not a full handoff.

What the AI does *not* do:

- **Build decks autonomously.** The AI proposes; the user decides. There is no auto-save of an AI-built deck.
- **Bypass format rules.** The output is validated against the same rules as a human's input. The AI does not get a privileged code path.
- **Train on the user's data.** Anthropic's no-training-on-API-data terms apply to API requests by default; the app does not opt in to anything beyond that.
- **Hide its reasoning.** Every AI suggestion comes with a one-line rationale per card. The user can see why a card was picked.

---

## The Orchestrator

The AI Orchestrator is a backend module inside the Next.js app. It has five responsibilities:

1. **Compose the prompt** — system prompt with deck-building rules and format constraints, user prompt with the request and the relevant card context.
2. **Decrypt the user's BYOK key** — `pgsodium.crypto_secretbox_open` against the encrypted column in `users`, with the plaintext held only in memory for the duration of the request.
3. **Call Anthropic** — request structured output (JSON), enforce a maximum token budget, stream the response.
4. **Parse and validate the output** — JSON parse, schema check, then run the candidate deck list through the same format-legality validator the human deck-builder uses.
5. **Recover from failure** — if validation fails, attempt one repair pass (drop the offending card, re-prompt for a single replacement). If that also fails, return a structured error the UI can explain.

The Orchestrator is the only path between the user-facing AI features and the Anthropic API. There is no second route, no "internal" endpoint, no developer-only bypass.

---

## Prompt architecture

Two prompts per request:

**System prompt** — large, stable, mostly the same across requests. Includes:

- The role definition ("You are a Magic: The Gathering Commander deck-building assistant.")
- Format rules in plain language (colour identity, singleton, 99 cards plus commander, banned-list pointer).
- Output schema (JSON shape: array of card objects with `name`, `quantity`, `category`, `rationale`).
- Voice guidance — concise, neutral, explanatory. Not hyped, not hedged.

The system prompt is cached at the Anthropic API layer using `cache_control: { type: "ephemeral" }` markers. It changes rarely, so cache hits dominate cost across a session.

**User prompt** — small, per-request. Includes:

- The user's free-text description.
- The commander's full Oracle record.
- A pre-filtered candidate pool of cards — the user's collection plus high-relevance cards outside it — passed as a compact reference list. The pre-filter is the project's filter-first principle applied to the AI's context window: don't dump 30,000 cards into the prompt; dump the 500 most relevant.

---

## Structured output

Anthropic's tool-use schema constrains the response to a JSON shape:

```json
{
  "commander": { "name": "Isshin, Two Heavens as One", "rationale": "..." },
  "cards": [
    { "name": "Sol Ring", "quantity": 1, "category": "ramp", "rationale": "..." }
  ]
}
```

Why structured output: parsing free-form responses is unreliable, and the validator needs structured input. The schema is enforced by Anthropic's tool-use contract on the way out, and double-checked by the parser before validation runs.

---

## The validator

This is the load-bearing piece. The validator is the same code path used by the human deck-builder. The AI does not have its own validator.

Checks performed:

- **Colour identity.** Every card's `color_identity` must be a subset of the commander's `color_identity`.
- **Singleton rule.** No card appears more than once, except basic lands.
- **Card count.** Exactly 99 non-commander cards plus 1 commander (or 1 + 1 partner, where applicable).
- **Banned list.** No card on the Commander banned list appears.
- **Card existence.** Every card name resolves to a real card in the catalogue. A hallucinated card fails validation cleanly.

If validation passes, the deck is returned to the UI. If validation fails, the Orchestrator gets one repair attempt: identify the offending card, drop it, prompt Anthropic for a single replacement that satisfies the failed constraint. If repair also fails, the user sees a clear error explaining what went wrong, with the partial output preserved.

This validator design is the reason BYOK + AI is safe to ship. Without it, the AI could suggest illegal decks the user might unknowingly save. With it, the AI cannot.

---

## BYOK — Bring Your Own Key

The user supplies their own Anthropic API key. The app uses their key on their behalf. They pay Anthropic directly for their usage; the app absorbs no AI cost.

### Why BYOK

Three reasons, in order:

1. **Scalability.** The project has no path to subsidising AI calls at scale. BYOK removes the unit-cost problem entirely — usage scales with the user, paid by the user.
2. **User control.** The user can see, set, change, or delete their key at any time. They can also use Anthropic's usage dashboard to track their own spend.
3. **No middleman trust.** The app doesn't see the user's prompt history in any persistent way. Anthropic receives the request directly (via the user's key); the app processes and forgets.

### How the key is stored

- **Encrypted at rest** via Postgres `pgsodium` using `crypto_secretbox`. The encryption key is held server-side, separate from the database, injected via environment variable on deploy.
- **Stored as `bytea`** in `users.anthropic_key_encrypted`. The plaintext column does not exist.
- **Never read by the client.** The UI shows "configured" or "not configured" status, never the key itself. Even the user can't view their own stored key — they can only replace it (the standard pattern for credential storage; if you've lost it, you replace it).
- **Decrypted per-request** in the Orchestrator. The plaintext lives in memory for the duration of one Anthropic call. Not cached. Not logged. Not returned to the client.

### What the user can do

- **Set their key.** Input form in account settings. The key is encrypted before being written.
- **Replace their key.** Same input form overwrites the existing encrypted value.
- **Delete their key.** Removes the encrypted value; AI features become unavailable until a new key is set.
- **Verify their key is configured.** UI shows a configured-or-not state without revealing the key.

---

## Failure modes

The AI layer can fail in several ways. Each has a planned response:

- **Anthropic rate limit or outage.** Return a clear "Anthropic is currently unavailable" message. The deck-builder remains fully usable manually.
- **User's key is invalid (rejected by Anthropic).** Return "your API key was rejected" — prompt the user to update it in settings.
- **Validation fails after one repair attempt.** Return the partial output with the invalid cards flagged. The user can manually fix or discard.
- **Anthropic returns malformed JSON despite the tool schema.** Treat as a validation failure; one repair attempt; otherwise user-visible error.
- **Request times out.** Return a "the request took too long" message. No partial save.

Notably, none of these failure modes leak the user's key, the system prompt, or other users' data.

---

## Why Anthropic-only in Phase 3

The Phase 3 AI layer ships with Anthropic only — no other providers. This is deliberate.

- **Prompt tuning has provider-specific gravity.** Prompts optimised for Claude's strengths (structured reasoning, careful citation, neutral voice) don't always carry over to other models without retuning. Shipping with one provider lets the prompts be tight.
- **Token budgets, structured-output contracts, and caching behaviour vary by provider.** Targeting one means the cost and latency model is knowable; targeting four means four versions of every operational decision.
- **Familiarity matters for a one-person project.** I use the Anthropic API daily already. That fluency compounds.

Multi-provider support via OpenRouter is committed for Phase 5. The architectural answer is clean. But the engineering simplification only pays off once the basics are solid.

---

## What's outside the AI layer's reach

Worth naming explicitly:

- **The AI cannot save a deck on the user's behalf.** All saves are user-initiated.
- **The AI cannot modify a user's collection.** No suggestions about what to buy or sell from the AI surface; the collection is the user's domain.
- **The AI cannot read other users' data.** Even with the user's own key, the Orchestrator only ever passes the requesting user's collection and context. No cross-user information flow.
- **The AI does not generate flavour text, lore, or new card designs.** Out of scope. The project is about *playing* with existing Magic cards, not generating new ones.

---

*See [`04-architecture.md`](./04-architecture.md) for how this layer fits into the overall request flow, and [`08-open-questions.md`](./08-open-questions.md) for deferred multi-provider decisions.*
