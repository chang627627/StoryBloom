# StoryBloom

Concept prototype for a bedtime-story iOS app for parents + children. The child expresses how the day felt via visual picks (color, weather, shape, symbol), chooses a dreamland, and the app generates a short comforting bedtime story plus a goodnight ritual.

Not a mood tracker, not a wellness app. Child-first, parent-assisted.

## Stack & structure

Single-file prototype. Everything lives in `index.html`.

- Tailwind via CDN (`cdn.tailwindcss.com`) — no build step.
- Fonts: **Fraunces** (serif display / story) and **Nunito** (UI).
- Vanilla JS for state + screen transitions. No framework, no bundler.
- `.claude/launch.json` defines two static-server configs; `static-npx` (port 4174) is the one that works (macOS system Python 3.9's `http.server` hits a sandbox permission error).

## Layout constraint — do not change

- Fixed iOS viewport **393 × 852** inside a phone frame, centered on desktop.
- Outer page scales the whole phone proportionally on short viewports via `.device-wrap` media queries — never reflow internal layout.
- Neutral background around the phone; the phone is the only focus.

## Screen flow

1. **Welcome** (`#scr-1`) — Lumo moon character, "Let's make tonight's story."
2. **Feeling** (`#scr-2`) — 4 sub-steps driven by `setStep(n)`: color → weather → shape → symbol. Step dots at top.
3. **World selection** (`#scr-3`) — 5 hero cards (Moon Garden, Sleepy Forest, Cloud Sea, Tiny Star Village, Dream Hill).
4. **Story** (`#scr-4`) — Illustrated scene + generated story (title + poetic paragraph).
5. **Goodnight step** (`#scr-5`) — Breathing orb + one gentle action + alternate card.

Navigation: `go(n)` swaps `.active` on `.screen` elements. Step engine: `setStep(n)`, `nextStep()`, `prevStep()`, `skipStep()`.

## State model

```js
state = { step, color, weather, shape, sym, world, care }
```

Selections populate dictionaries (`colorWords`, `weatherWords`, `shapeWords`, `symWords`, `worlds`) that `writeStory()` composes into 1 of 4 random variants. Story scene is rendered by `renderStoryScene()` using a per-world inline SVG backdrop plus two floating symbol instances.

## Design language

Figma-inspired soft geometry, adapted for bedtime:
- Rounded cards, generous radii (20–28px), soft shadows, floating pastel blobs.
- Palette CSS vars at `:root`: `--lavender`, `--sky`, `--butter`, `--peach`, `--mint`, `--coral`, plus `--ink` (#3b2d5a) and `--ink-dim`.
- Selection affordance: coral ring. **Use `::after { border: 3px solid #ff9e87 }`**, NOT `box-shadow: 0 0 0 X inset` — inset shadows render below absolutely-positioned SVG children inside cards (e.g., Cloud Sea's white wave covered the bottom of the ring).
- Animations: `floaty` / `floaty-2` / `floaty-3`, `twinkle`, `breathe`. Keep them slow (5–8s).

## Copy voice

Simple, warm, magical, for child + parent ears. Avoid adult-wellness phrasing ("a quiet place for a feeling", "private studio"). Use "tonight's story", "little friend", "dreamland", "goodnight step".

## Non-obvious product decisions

- **World selection is intentionally a separate phase, not step 5 of a 5-step progress.** Feeling picks are inward (reflective); world pick is outward (imaginative). Keeping them split preserves the two-act ritual feel and keeps the child from feeling homework-like. If this comes up again, suggest a "Part 2 of 2 · Your dreamland" eyebrow instead of merging.
- World-card height is 96px — the previous 128px pushed the "Build my world" CTA off-screen at 393×852.
- The flex scroll area on screen 3 needs `min-h-0` so `overflow-y-auto` actually scrolls inside the flex column.
- Transition overlaps when navigating programmatically via `preview_eval` (both screens briefly `.active` mid-fade). That's a verification artifact, not a real-flow bug.

## Running locally

```
npx serve . -l 4174
```

Or via the Claude Code preview tool: `preview_start` with name `static-npx`.
