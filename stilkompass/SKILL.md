---
name: stilkompass
description: "Finds a clear visual direction for an app, game, website or landing page and turns it into a checked design brief: style, color tokens for light and dark mode, fonts, shapes, motion, plus domain rules and anti-patterns. Contrast is calculated with the WCAG formula and color-blind risks are estimated by simulation, not guessed. Use for «Stilkompass», «welcher Stil?», «Farben», «Design-Richtung», a new design system, or before designing screens."
---

# Stilkompass (Style Compass)

*Inspired by the product-to-style reasoning idea of "UI UX Pro Max" by Next Level Builder (github.com/nextlevelbuilder/ui-ux-pro-max-skill, MIT). Independently written as a decision method instead of a catalog; no data copied. See NOTICE.*

## What this does

AI-built screens tend to look alike: indigo gradient, glass cards, centered hero, three feature boxes. The Stilkompass picks a direction that fits the product and its users, explains why, and delivers tokens with a calculated contrast check and a color-blindness estimate. The result is saved in the project and feeds the design or code work that follows.

## Language

- Talk to the user in the language they write in. de-CH: "ss", never "ß".
- Token names stay English (`bg`, `text`, `primary`), so they work in code.

## 1. Context first

Answer from what is already known (the project, the spec, earlier chats); ask at most two short questions for what is missing.

- **Who and when:** Who uses it, where, in which moment? Outdoors in sun, at night in bed, mid-workout with sweaty hands, at a desk, glancing for two seconds?
- **Three mood words:** for example calm, precise, trustworthy, or loud, playful, fast.
- **What is on screen:** dense data, long text, media, controls under time pressure, a game world?
- **Existing brand:** logo, colors or fonts that must stay.
- **Platforms:** Android, iOS, web, watch. Platform habits beat style (Material on Android, Apple guidelines on iOS).
- **Sensitive domain:** health, money, children? These come with rules (section 3).

## 2. Pick one direction

Choose one main direction; at most one accent influence. When the user wants options, show two or three directions as short profiles, each with its trade-off, and recommend one.

| Direction | Feels | Good for | Watch out |
| --- | --- | --- | --- |
| Clear minimal (Swiss) | calm, precise | tools, dashboards, health, finance | turns bland without one strong accent and good type |
| Soft and calm | gentle, safe | wellness, meditation, care | low contrast is the classic failure; check every pair |
| Bold blocks | energetic, direct | fitness, timers, sports, events | can shout; keep one hierarchy |
| Editorial | serious, reading | articles, portfolios, long text | needs real typography and generous line length control |
| Dark high-contrast (OLED) | focused, technical | trading, night use, workout screens, media | pure white text on pure black glows and smears on OLED screens; use near-black and off-white |
| Data-dense pro | efficient | trading, analytics, admin | needs strict alignment, tabular numbers, quiet colors |
| Playful rounded | friendly | kids, learning, casual apps | can look childish for adults; keep text serious |
| Neo-brutalist | raw, confident | indie products, creative tools, landing pages | hard on accessibility if borders and colors fight |
| Glass and depth | modern, layered | small accents, media overlays | blur is slow on cheap phones and kills contrast; never for body text areas |
| Pixel / retro | nostalgic, game-like | pixel games, retro tools | integer scaling only, limited palette, pixel font only for short labels |
| Fantasy / illustrated | atmospheric | RPG, tower defense, story games | readability of UI over busy art; use solid panels behind text |

## 3. Domain rules

| Domain | Must | Avoid |
| --- | --- | --- |
| Health, medication | calm colors, large readable text, AAA contrast for doses and warnings, red only for real alerts, clear source of every number | neon, playful motion, dark patterns, guilt messages |
| Finance, trading | trust, tabular numbers, gains and losses shown with sign and arrow, not color alone; offer a color-blind palette (blue/orange) | casino effects, confetti on trades, hidden fees, urgency timers |
| Fitness, timers, sport | readable at arm's length and in sun, huge numbers, one main action, haptics, dark mode for night | small text, low contrast, too many controls during a workout |
| Kids, learning | big targets, simple words, friendly shapes, progress feedback | dark patterns, ads that look like content, tiny text |
| Productivity, tools | density options, keyboard support on desktop, quiet palette, clear states | decoration that competes with content |
| Games | style follows the game world; UI readable over art; consistent icon language | menu fonts that are hard to read, color-only status |
| Landing pages | one message above the fold, one call to action, honest proof | stock gradients, fake numbers, three generic feature cards |

## 4. Colors as tokens

Build a small token set instead of loose hex values:

`bg`, `surface`, `text`, `muted`, `border` (outlines of inputs and controls), `primary`, `on-primary`, `accent`, `on-accent`, `success`, `warning`, `danger`, `on-danger`, `focus`; for trading also `up` and `down`.

Rules:
- Start from one brand hue; derive neutrals with a light tint of it. Roughly 60 % background and surfaces (`bg`, `surface`), 30 % text and supporting elements (`text`, `muted`, `border`), 10 % `primary` and `accent`.
- One accent color. Two accents compete; three look random.
- **Dark mode is designed, not inverted:** near-black background, surfaces get lighter with elevation, accents slightly lighter and less saturated, text off-white.
- Status never by color alone: always an icon, a sign (+/−), a word or a pattern as well.
- Decorative dividers may be faint; outlines that identify inputs and controls need 3:1.

**Check with numbers.** Write the tokens as JSON and run the bundled script (in this skill's `scripts` folder):

```
python3 -I <skill-folder>/scripts/kontrast.py --palette tokens.json
python3 -I <skill-folder>/scripts/kontrast.py "#6B7280" "#FFFFFF"
```

It checks text 4.5:1, large text and UI 3:1, and `aaa` 7:1 where a domain demands it (WCAG). Status colors (`success`, `danger`, `warning`, `up`, `down`) are checked as text by default, because they often are text (error messages, gains and losses). It also simulates protanopia, deuteranopia and tritanopia for pairs that must stay apart (`success`/`danger`, `up`/`down`); that part is a rule of thumb, not a guarantee. Missing tokens and typos count as failures. Fix every failing pair before handing the palette over. Without a code environment, say that the contrast is unchecked and list the pairs to verify (for example in a browser contrast checker).

## 5. Type

- One family is usually enough; two at most (one for headings, one for text). Fonts must be free to use; prefer the SIL Open Font License.
- Body text 16 px / 16 sp or larger on phones, line height 1.4–1.6, lines of about 45–75 characters on wide screens.
- A size scale with few steps (for example 12, 14, 16, 20, 24, 32), few weights (regular, medium, bold).
- Numbers that change (timers, prices, scores) use tabular figures so they don't jump.
- **Self-host web fonts** instead of loading them from a font CDN. That is faster, works offline in a PWA, and avoids sending visitors' IP addresses to a third party; a German court ruled in 2022 that embedding fonts from Google's servers without consent broke data protection law.

Safe starting points (all under the SIL Open Font License):

| Use | Fonts |
| --- | --- |
| Neutral UI | Inter, Manrope, IBM Plex Sans, DM Sans |
| Friendly, rounded | Nunito, Outfit |
| Strong display | Space Grotesk, Barlow Condensed (headings only) |
| Editorial | Fraunces or Source Serif 4 for headings, Inter for text |
| Maximum readability (health, low vision) | Atkinson Hyperlegible, Lexend |
| Numbers and code | JetBrains Mono, IBM Plex Mono |
| Pixel games | Press Start 2P or Silkscreen for short labels, a readable sans for longer text |

## 6. Shape, icons, motion

- Spacing on an 8-point grid; corner radius from one small scale (for example 4, 8, 16) used consistently.
- One icon set with one stroke weight, for example Lucide (ISC), Phosphor (MIT), Material Symbols (Apache 2.0). Emojis are not icons.
- Elevation: a few defined shadow or surface levels, not a new shadow per card.
- Motion 150–300 ms with easing; it explains a change (where did this come from, what happened), it does not decorate. Respect "reduce motion".
- Touch targets at least 48 dp on Android and 44 pt on iOS.

## 7. The AI-default look: avoid unless asked

- Purple-to-pink or indigo gradients as the main color
- Glass cards everywhere, blurred blobs in the background
- Centered hero, three equal feature cards, testimonials with invented people
- Gradient text in headings, glowing borders, random sparkles
- Emojis as icons, five different shadow styles, every corner fully rounded
- Light gray text on white "for elegance"

Choose these only when they truly fit the product and the user asked for them.

## Output: the style profile

Keep it short enough to read on a phone, then deliver the tokens:

```
Stil-Steckbrief: <product>
Richtung: <direction> (+ <accent influence>), because <one sentence on users and moment>
Stimmung: <three words>
Farben: primary <hex>, accent <hex>, bg/text light <hex>/<hex>, dark <hex>/<hex>
Schrift: <heading> / <body>, base <size>
Form: radius <scale>, icons <set>, motion <duration>
Domain-Regeln: <the 2–3 that apply>
Kontrast-Check: <result of kontrast.py, or "nicht gerechnet" with the pairs to check>
Bewusst nicht: <2–3 anti-patterns ruled out>
```

Then the tokens as CSS variables (light and dark) and as the JSON used for the check.

**Save it in the project** so the next chat keeps the same look: `docs/STIL.md` (the profile and the reasons) and `docs/tokens.json` (the checked palette). When working from a phone with a project ZIP, deliver both files inside the new ZIP. Later changes update these files instead of starting over. The next step is the design or the build (for example with the skill app-studio or game-studio, or a design artifact).

## Final check

- [ ] The direction follows from users, moment and domain, not from trends.
- [ ] One direction, one accent, a small token set for light and dark mode.
- [ ] Every text and control pair passes, calculated with the script or marked as not calculated.
- [ ] `docs/STIL.md` and `docs/tokens.json` are saved in the project.
- [ ] Status and gains/losses are never shown by color alone.
- [ ] Fonts and icons are free to use and self-hosted on the web.
- [ ] Domain rules applied; AI-default look avoided unless requested.
