# StoryBloom

A bedtime storytelling app for parents and children, ages 3–8. The child expresses how today felt through four soft, nonverbal picks (color, weather, shape, little friend), chooses a dreamland, and the app composes a short comforting bedtime story plus a goodnight ritual. Treat this as a real live product, not a concept — no "design exploration" language anywhere in the UI.

## Deployment

- GitHub: https://github.com/chang627627/StoryBloom (public, chang627627's account)
- Vercel: https://storybloom-psi.vercel.app (project `storybloom` under `changs-projects-4800cbf2`)
- Repo is connected to Vercel — `git push origin main` auto-deploys production.
- A GitHub Action (`.github/workflows/update-claude-md.yml` + `.github/scripts/update-claude-md.py`) auto-updates this file on every push to main. Requires `ANTHROPIC_API_KEY` as a repo secret. Bot commits are tagged `[skip-claudemd]` so the workflow does not loop.

## Files

- `index.html` — the app (single-file prototype, ~3300 lines)
- `site.html` — marketing landing page (hero + ritual + worlds + friends + reviews + CTA + footer)
- `slides.html` — 8-slide 1920×1080 deck for the NY Product Design Awards submission
- `assets/phone-frame.png`, `assets/status-bar.png`, `assets/home-indicator.png` — PNG chrome shared by the app and slides
- `CLAUDE.md` — this file (auto-synced on push)
- `.github/workflows/update-claude-md.yml` + `.github/scripts/update-claude-md.py` — the sync action
- `.claude/launch.json` — two static-server configs (`static-python`, `static-npx`). Both run `npx serve` under the hood (ports 4173 / 4174). macOS system Python 3.9's `http.server` fails with a sandbox `PermissionError` calling `os.getcwd()`, so the Python config was quietly swapped to `npx serve`.

## Stack

- Tailwind via CDN (`cdn.tailwindcss.com`) — no build step
- Fonts: **Fraunces** (serif display / story) + **Nunito** (UI)
- Vanilla JS for state + screen transitions. No framework, no bundler.
- Everything is a single HTML file per deliverable (app, site, slides)

## Layout constraint — do not change

- Fixed iOS viewport **393 × 852** inside a phone frame, centered on desktop
- Outer page scales the whole phone proportionally on short viewports via `.device-wrap` media queries — never reflow internal layout
- Soft pastel background around the phone; the phone is the only focus
- On mobile (`@media max-width: 560px`) the desktop chrome (STORYBLOOM brand, SITE link, RESET DEMO chip) is hidden so the phone is the only thing on screen

## Screen flow (7 screens)

0. **Splash** (`#scr-0`) — Centered brand-dot + "StoryBloom" wordmark + tagline "A bedtime ritual, shaped by today." Auto-advances to Welcome after **2.8s**; tap anywhere to skip.
1. **Welcome** (`#scr-1`) — "Let's make tonight's story." Lumo moon character asleep on a cloud. Saved stories appear as coral stars scattered around Lumo — tap one to re-open. Has a **Lily's shelf** profile pill top-left (opens the shelf drawer) and a **⚙ settings** gear top-right.
2. **Feeling** (`#scr-2`) — 4 sub-steps driven by `setStep(n)`: color → weather → shape → little friend. Progress dots at top. Step 3's prompt is *"What shape was the feeling?"* — it intentionally keeps the word "feeling" so steps 1–3 read as one conversation.
3. **World selection** (`#scr-3`) — 5 hero cards (Moon Garden, Sleepy Forest, Cloud Sea, Star Village, Dream Hill). CTA: *Write tonight's story*.
4. **Story** (`#scr-4`) — Illustrated scene + generated story (title + poetic paragraph). Brief "writing…" pulse animation sells the AI-generation feel. Meta reads *"written for tonight"* (or *"a kept story"* when reopening a saved one). *Another* button swaps between the two handwritten variants.
5. **Goodnight step** (`#scr-5`) — Breathing orb + one gentle action + passive alternate card. Buttons: *Tuck away* (back to Welcome) / *Goodnight* (→ Sleep Mode).
6. **Sleep Mode** (`#scr-6`) — Dim twilight screen with sleeping Lumo and "Sweet dreams." *Keep tonight's story* saves to `localStorage` with a rising-star animation. *Wake for a moment* returns to Welcome.

Navigation: `go(n)` swaps `.active` on `.screen` elements. Step engine: `setStep(n)`, `nextStep()`, `prevStep()`, `skipStep()`.

## Overlays (bottom-sheet modals)

- **`#settingsBackdrop`** — parent-facing settings sheet. Sections: Little one (name, age), Story (narrator Mira/Onyx/Silent, reading speed, volume), Bedtime (dim, auto-sleep, gentle sounds), Content preferences (theme chips + skip-scary + multi-child). Opened from the gear button on Welcome.
- **`#cfBackdrop`** — Create-a-Friend sheet. Name + shape + color + trait chips + free-text description. Saved custom friends are stored in `localStorage` and appear in the little-friend grid on step 4.
- **`#shelfBackdrop`** — Lily's shelf drawer. Header with avatar + name + subtitle. Stat row (Stars kept / Nights / Friends met). Tabs (Kept stars / Recent / Friends). Opened from the shelf pill on Welcome.

## State model

```js
state = { step, color, weather, shape, sym, world, care, lastStory, variant, _writeTimer }
```

Feeling picks fill placeholders in the 10 handwritten story templates (2 per world × 5 worlds). `writeStory()` picks a random variant, runs the placeholder substitution, capitalizes sentence starts, and renders after an ~850ms "writing" pulse.

## Little friends (9 total, time-agnostic)

Paper Boat, Paper Crane, Lantern, Blanket, Nest, Owl, Little Bear, Bunny, Feather. Plus a **+ Create your own** tile that opens the Create-a-Friend sheet.

**Rule: no celestial friends (moon / star / sun).** These lock a scene to a time of day and clash with world backdrops (Cloud Sea has a sun, Moon Garden / Dream Hill have moons). The current 9 are all time-agnostic so any friend fits any world. Don't add moon/star back — it was deliberately dropped.

Only remaining backdrop duplicate: Cloud Sea contains a paper boat; picking Paper Boat as the friend renders a smaller paired boat (reads as "two paper boats drifting together," not a bug).

## Stories

- **10 handwritten templates**, 2 per world. Curated, not runtime-generated. The "AI" framing is for the shipped-product vision; the prototype shows 10 curated samples of what AI-generated stories would look like.
- Placeholders: `{friend}` (phrase from `symWords`), `{color}` (adj from `colorWords`), `{weather}` (phrase from `weatherWords`), `{shape}` (phrase from `shapeWords`).
- **Rule: `{friend}` appears exactly once per story.** Second mentions use pronouns or generic stand-ins (*its heart*, *the little one*). Don't add second `{friend}` placeholders.
- **Voice: child-friendly read-aloud.** Short sentences (6–14 words), concrete imagery (*pulled a soft blanket of moonlight*, *waved hello*), no adult philosophy (*time stopped asking questions* — killed). If you rewrite a story, keep it at picture-book vocabulary level.

## Scene images

Each of the 5 worlds is visually distinct — different time-of-day, no shared motifs:

- **Moon Garden** — deep-night lavender, crescent moon top-left, flower bed bottom, two subtle sparkles. No firefly glow.
- **Sleepy Forest** — mint + warm dusk wash, layered trees of varied sizes, fireflies. No moon, no stars.
- **Cloud Sea** — daylight sky-blue, warm-haloed sun top-right, wispy cloud bands, cloud-bank waves. No stars.
- **Star Village** — butter-gold sky, varied stars (4-point sparkles + dots + cross-glimmers), three houses. No moon.
- **Dream Hill** — sunset-to-twilight gradient, full moon right, warm horizon wash, layered rolling hills. No twinkling stars.

`renderStoryScene()` builds the backdrop inline per world, then places **one** floating friend instance at a per-world position that avoids the backdrop hero element (`worldFriendPos` map). One friend per scene — not two. That's deliberate; the user called the two-instance version too busy.

## Design language

Figma-inspired soft geometry, bedtime-warm:

- Rounded cards, 20–28px radii, soft shadows, floating pastel blobs.
- Palette vars at `:root`: `--lavender`, `--sky`, `--butter`, `--peach`, `--mint`, `--coral`, plus `--ink` (#3b2d5a), `--ink-dim`, `--ink-mute`, `--bedtime` (#8f9eff).
- **Primary accent: periwinkle blue (#8f9eff / #b8c2ff)** — not coral. Coral is activating; blue is sleepy, which is on-brief for bedtime. Buttons, selection rings, progress dots all use blue. Yellow pills and saved-star glyphs stay warm as secondary accents.
- **Brand dot** (corner mark + splash + marketing site) — 12–26px radial gradient `circle at 35% 35%, #fff 0%, #b8c2ff 45%, #8f9eff 100%` with a soft periwinkle glow and inset bottom shadow. App and site use the same recipe so they read as one product.
- Selection ring affordance: **`::after { border: 3px solid #8f9eff }`** on `.world-card.selected`, NOT `box-shadow: 0 0 0 X inset`. Inset shadows render below absolutely-positioned SVG children inside cards (Cloud Sea's white wave covered the bottom of an inset ring).
- Animations: `floaty` / `floaty-2` / `floaty-3`, `twinkle`, `breathe`, `writing-dot` (writing-pulse), `splash-dot-breath`. Keep them slow (5–8s).
- Writing-pulse: three dots, ~850ms, before the story fades in. Don't shorten below 600ms or it stops reading as "composing."

## CTA alignment

All primary blue CTAs across screens 2–5 sit at the **same 43px from the phone bottom** as the *Goodnight step* button on screen 4. This is enforced by `.screen { padding-bottom: 40px }` as the default, matching the override on screen 4. The Welcome screen's button sits slightly higher because the "Takes about 3 minutes" micro-copy hangs below it — explicit exception.

## Save-as-constellation

- `localStorage` key: `storybloom:stars`, shape `[{id, date, world, sym, title, text}, …]`.
- `saveStarFromSleep()` pushes the current story to the array on tap of *Keep tonight's story*. Plays rising-star animation + "Tucked into the sky" toast.
- `renderConstellation()` paints saved stars onto the Welcome screen at positions derived from a deterministic FNV-1a hash of the star id (so the same story always lands in the same spot). Avoids the central text column.
- `openSavedStar(id)` restores state and jumps to the story screen with the saved title + text verbatim; meta reads "a kept story" instead of "written for tonight." Does NOT re-trigger the writing pulse — saved stories appear instantly.

## Copy voice

Simple, warm, magical, for child + parent ears. Avoid adult-wellness phrasing ("a quiet place for a feeling", "private studio", "time stopped asking questions"). Use "tonight's story", "little friend", "dreamland", "goodnight step", "keep tonight's story".

## Non-obvious decisions (read before changing)

- **Treat this as a real product.** No "concept prototype", "design exploration", or "2026 edition" language anywhere in user-facing copy. The site and app both read as a live commercial product.
- **World selection is a separate phase, not step 5 of a 5-step progress.** Feeling picks are inward (reflective); world pick is outward (imaginative). Splitting them preserves the two-act ritual feel. If this comes up again, suggest a "Part 2 of 2 · Your dreamland" eyebrow instead of merging.
- **Sleep Mode is the intended final screen after Goodnight** — not a bounce-back to Welcome. Bedtime apps shouldn't invite another session at bedtime. The dim screen is also the strongest "final frame" for presentation slides.
- **One friend instance per scene, placed per-world.** Two instances felt busy; the user pushed back. Position map lives in `renderStoryScene`.
- **AI framing is kept but proven subtly.** No chat UI, no model picker (deliberate — the brief says invisible AI). The writing-pulse + *written for tonight* + *Write tonight's story* CTA sell the claim without category-typical visual clichés.
- **The `{friend}` appears once** per story. Rewrites must respect this — second references use pronouns.
- **Don't bring back moon / star / cloud / tree / hill / window as friends.** They're either time-bound (celestial) or places, not companions. The current 9 are all portable, time-agnostic, and friend-shaped.
- **Splash auto-advances at 2.8s**, not faster. Gives the tagline a full second of settled visibility after it fades in at 1.6s, and lets the brand-dot complete one breathing pulse. Shorter felt rushed against the bedtime tone.
- **Mobile hides chrome, not the phone frame.** On mobile viewports the desktop-only decorations (STORYBLOOM brand corner, SITE link, RESET DEMO) are hidden via the `@media max-width: 560px` rule — but the phone mockup + internal content stay. The user rejected a proposal to strip the phone frame entirely on mobile.
- **Transition overlap when navigating programmatically via `preview_eval`** (both screens briefly `.active` mid-fade). That's a verification artifact, not a real-flow bug.

## slides.html (NY Product Design Awards deck)

- 8 slides at **1920 × 1080** each, scaled-to-fit in the viewport with `translate(-50%, -50%) scale(--deck-scale)` centering.
- Layout rule: every slide has at least one phone mockup. No tags, no page-number footer, no brand mark on the slide chrome (just the nav bar at the bottom for presenter navigation).
- Multi-phone slides explain progression:
  - **Slide 02 (The ritual)** — 4 phones showing the 4 feeling steps (color, weather, shape, friend)
  - **Slide 04 (Tonight's story)** — 2 phones: first telling + after-Another telling, showing the story regenerates without losing picks
  - **Slide 05 (Little friends)** — 2 phones: picker grid + Create-a-Friend sheet
  - **Slide 07 (Dim, keep, return)** — 3 phones: Sleep Mode + Welcome with constellation + Lily's Shelf
- **Slide 08 is Settings** ("For grown-ups") showing the parent-side controls.
- Navigation: ←/→ / Space / Page Up/Down / Home / End. Deep-link via `#s3` etc.
- Em-dashes stripped from slide copy (user preference).
- Phone scale varies per slide: 0.62 default, 0.68 for 3-up slide 7, 0.78 for 2-up slides 4 & 5.

## Running locally

```
npx serve . -l 4174
```

Or via the Claude Code preview tool: `preview_start` with name `static-npx` (or `static-python` — same underlying command).
