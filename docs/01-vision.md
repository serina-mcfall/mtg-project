# Vision

The MTG Project is a personal Magic: The Gathering collection database and Commander deck-builder, designed around a single guiding principle: calm beats comprehensive. It starts narrow, lets the user add filters as they go, and never puts more on screen than the current decision actually needs.

The aim is a tool someone can sit down with after a long day and still enjoy using — not one that demands the user be at their sharpest before opening it.

---

## The user this is for

Magic players who want serious tools without the cognitive cost of serious tools. Specifically:

- **Collection-owning players** who want to actually *use* their collection when deck-building, not just browse infinite-scroll lists of every card ever printed.
- **Commander players**, because Commander is the format this project is shaped around — colour-identity constraints, singleton lists, ninety-nine card decks, format-legal cards only.
- **Players who find Moxfield, Archidekt, and EDHREC powerful but exhausting.** The features are there; the cost of finding the right one is the problem.
- **New players** who want to learn the format without being thrown into the deep end. Phase 4 territory, but the foundations are built with them in mind from the start.
- **Players with accessibility needs** — keyboard-only navigation, screen reader support, dyslexia-friendly typography, reduced motion. Not a Phase 9 retrofit. Baked into Phase 1.

The user this is **not** for: the EDHREC power user who lives in spreadsheets, runs decks through analytics suites, and wants every statistic on screen at once. Those tools exist and are excellent. This project does something different on purpose.

---

## The problem with existing tools

Existing Magic tools are built for the player who already knows what they're looking for. The interface assumes you can scan a dense table without losing your place, that you can tell which of fifteen filter dropdowns is the one you need, and that you can hold the rules of Commander in your head while doing it.

For an experienced player on a good day, that works fine. The cost is paid by everyone else:

- New players staring at a wall of options with no obvious starting point.
- Experienced players on tired days who just want to build something and stop having to fight the UI.
- Players with attention, sensory, or cognitive accessibility needs for whom "everything on screen at once" isn't a feature — it's a barrier.

The firehose isn't a design flaw. It's a deliberate choice optimised for the most engaged users. But it leaves a real gap underneath, and this project lives in that gap.

---

## What makes this different

**Filter-first, not search-first.** The default state is empty. You add constraints until the set of cards you're seeing is small enough to actually look at. The opposite of a search bar with thousands of results and pagination controls.

**One loud layer at a time.** The chrome stays quiet so the cards can breathe. A modal opens, the background dims. A card takes focus, its siblings recede. The interface never competes with itself.

**Commander as the first-class format.** Colour-identity rules baked into every filter and deck-builder constraint, not bolted on as a checkbox. The format defines the shape of the app, not the other way around.

**Accessibility as a design position, not a compliance checklist.** Radix UI primitives, semantic ARIA, full keyboard support, focus management on every state change, reduced-motion respect, dyslexia-friendly body type. Built in from Phase 1, not patched in later.

**AI that suggests, doesn't decide.** Phase 3 brings an AI assistant for deck-building — but on a BYOK (Bring Your Own Key) pattern so cost scales with use, and structured so the AI proposes and the user approves rather than the AI taking the wheel.

---

## What this is *not*

Clarity comes partly from being honest about constraints. The MTG Project is not:

- **A replacement for Moxfield, Archidekt, or EDHREC.** They are excellent at what they do. This project doesn't try to compete on feature parity.
- **A tournament-grade analytics suite.** No win-rate tracking, no metagame breakdowns, no statistical deck analysis.
- **A trading or marketplace app.** Prices surface from Scryfall for context, not for commerce.
- **A multi-format powerhouse.** Commander is the centre. Other formats may come later, but they don't shape the design.
- **A public platform — yet.** Personal use first. Public-facing surfaces are deferred to Phase 5 and remain explicitly optional.

Saying no to these is what makes saying yes to calm UX, accessibility, and Commander focus possible.

---

## The vision in one line

*A Magic tool you can use tired.*

---

*See [`02-roadmap.md`](./02-roadmap.md) for the phased build plan, and [`06-design-direction.md`](./06-design-direction.md) for the visual and tonal language that makes this vision tangible.*
