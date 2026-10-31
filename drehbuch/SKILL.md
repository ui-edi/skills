---
name: drehbuch
description: Builds scroll-driven landing pages where scrolling is the timeline, written like a screenplay with acts, one engineered peak and a real ending, delivered as one self-contained HTML file that works on phones. Use for "Drehbuch", "screenplay page", "scroll page", "scrollytelling", "Landingpage", "landing page that feels like an experience", "Apple-style page", "scroll animation", "make my app/game a website", or when a page looks like a template and should not.
---

# Drehbuch (Screenplay)

*Inspired by "scroll-craft" by Nate Herk (github.com/nateherkai/scroll-craft). Independently rewritten with its own engine, built for phones and single-file pages.*

## The idea

Everybody already knows how to scroll. Drehbuch treats scrolling as a timeline: the page is a short film with real, selectable text on top, written in acts like a screenplay. Each act behaves differently enough that the visitor keeps scrolling to see what the next one does, and one moment is built to be the one they remember.

What you deliver: a short **brief**, a **screenplay table** (acts, feelings, devices), one **self-contained HTML page** (engine inlined, works offline, publishable as a single file or artifact) and **proof** that it holds up: screenshots at every scroll position on desktop, phone and with reduced motion.

## Language

Talk to the user in their language. Write the page in the language(s) the user wants; if the product is bilingual, ask whether the page should be too.

## Files in this skill

- `engine/drehbuch.js` + `engine/drehbuch.css`: the mechanism. Never edit them per project; theme with tokens, add bespoke code in the page.
- `references/template.html`: starter page with the engine markers.
- `references/devices.md`: the device kit, with markup for each device. Read before scoring.
- `references/grammars.md`: page structures, the signature move, aesthetic range. Read before scoring.
- `references/design-floor.md`: spacing, type, colour, contrast, motion, mobile, refuse list. Read before writing markup.
- `scripts/inline.mjs`: puts the engine into the page, so the result is one file.
- `scripts/shoot.mjs`: walks the page and photographs every scroll position (needs Playwright).

If only this SKILL.md is available (no engine folder), get the files from `https://github.com/ui-edi/skills` (folder `drehbuch/`), or use the engine source in the appendix of this file if it has one.

## Step 1: Brief (one pass, short)

Reuse everything the user already said or attached (store texts, screenshots, logos, colours, earlier docs). Then ask only what is missing, in one message, maximum six questions:

1. **What is it, and who is it for?** One or two sentences in their words.
2. **What should the visitor believe at the end?** One sentence. If they give three, make them pick.
3. **What should the visitor do next?** One action with one label (for example "Play in browser"), used everywhere on the page.
4. **Vibe in three to five words**, plus up to three references from any medium (a film, an album cover, a game, a shop). Not other websites.
5. **The one moment they should remember.** The sentence a visitor would say to a friend: "It's the site where ___."
6. **What assets exist?** Screenshots, photos, footage, logo, colours, fonts. "Nothing" is a valid answer.

If the user says "you decide" or similar, write the brief yourself, mark it **Authored under creative delegation**, and continue without further check-ins. Never invent quotes, numbers, reviews or awards.

Write the brief as the first part of the build notes (`BRIEF.md` next to the page, or the top of the chat reply if there is no file system).

## Step 2: Screenplay

Four decisions, in this order. Details in `references/grammars.md` and `references/devices.md`.

1. **Feeling curve.** One line per act: the emotion, then what on screen causes it. Feelings first, devices second. Two neighbouring acts with the same feeling means one is filler: cut it.
2. **The peak.** One act is the memorable moment. It gets the biggest visual change, the most scroll room and the best asset, and the act before it is quieter.
3. **Grammar.** Pick the page structure that fits the brief (filmic, chapters, poster, gallery, split stage, one continuous world). Say in one line why.
4. **Signature move.** One bespoke interaction that exists only on this page, written as page code via `Drehbuch.on()`. A recoloured default effect is not one.

Then write the **screenplay table**:

| Act | Feeling | What happens | Device | Length |
| --- | --- | --- | --- | --- |
| 1 Opening | curiosity | … | parallax | 160vh |

Rules for the table:
- At least four different device families on the page, never the same device twice in a row.
- At most two `scrub` acts (video is heavy).
- Every act earns its length. A short, complete page beats a long, padded one. Typical total: 5 to 12 viewport heights.
- The last act resolves and holds: the action, said plainly, on a screen that feels finished. No fade into a footer.

Show the table to the user if they are around and the decisions are theirs. Under delegation, proceed.

## Step 3: Assets

Order of preference:
1. **The user's own material:** screenshots, photos, footage, logo. Real beats generated.
2. **Drawn in code:** SVG and CSS scenes, shapes, gradients, illustrations. Perfect for games, apps and illustrated brands, weighs almost nothing and stays sharp on every phone.
3. **Generated images,** only if an image tool is available and the user agrees. Write one style preamble and reuse it word for word in every prompt so the images look like one shoot. Look at every image before using it.
4. **Free stock,** only with a licence that allows it, and say which.

Never put text into images; text is always real markup. Never use photos of real public figures. Video for scrubbing must have no audio track and dense keyframes (for example `ffmpeg -i in.mp4 -an -c:v libx264 -g 6 -crf 23 -movflags +faststart out.mp4`).

## Step 4: Build

1. Start from `references/template.html`. Read `references/design-floor.md` first.
2. Write real HTML: one `<h1>`, real `<p>`, real links and buttons, sensible reading order. The engine reads `data-db-*` attributes; it never builds the page for you.
3. Theme with the six colour tokens and two font tokens. Fonts only from Google Fonts or system stacks.
4. Phone first: design the 390px composition on purpose (different crop, stacked layout, bigger tap targets), not as a squeezed desktop.
5. Write the signature move as page code with `Drehbuch.on(actElement, p => …)`.
6. Make it one file: `node scripts/inline.mjs page.html` writes `page.single.html` with engine, styles and small assets inline. Keep it under a few MB; large videos stay separate files.

## Step 5: Verify by scrolling

Not optional. Every scroll position is a different frame, and the bugs live between the two you happened to look at.

```bash
node scripts/shoot.mjs page.single.html --out shots/desktop
node scripts/shoot.mjs page.single.html --out shots/mobile --mobile
node scripts/shoot.mjs page.single.html --out shots/reduced --mobile --reduced
```

The script reports dead scroll, horizontal overflow, text cut off at the edge, console errors and images that did not load, and writes `sheet.png`. Then do what the script cannot: **look at every sheet.** Check that text is readable over every frame, that the peak is the biggest change, that the phone layout is composed rather than squeezed, and that reduced motion shows everything without pinning. Fix, shoot again.

**Feel check:** scroll the page cold and write one word per act for what you felt. Compare with the feeling curve. Where they differ, the page is wrong, not the brief.

Say plainly what you could not verify. A headless browser is not a real phone: video autoplay rules, low-power mode and touch scrolling can differ. If the user reports a phone problem, ask for a screen recording before guessing.

## Step 6: Deliver

Publish the single HTML file the way the environment allows (an artifact, a file, or a folder for hosting such as itch.io, GitHub Pages or Netlify).

- **Artifact hosts that add their own page skeleton** (for example claude.ai artifacts): build with `node scripts/inline.mjs page.html out.html --fragment`, which drops the `<!doctype>`, `<html>`, `<head>` and `<body>` wrappers. Follow the host's rules: short `<title>` (the product name), fonts only from Google Fonts, everything else inline, and for a dark-only design `color-scheme: dark` on `:root`.
- **Real hosting:** use the full `page.single.html` and add an Open Graph image if the user has one. Then report briefly: grammar and why, the screenplay table, the peak, the signature move, what was verified (attach or show the sheets) and what was not.

## Hard rules

| Never | Instead |
| --- | --- |
| Building before the brief and the screenplay exist | Steps 1 and 2 first, even if short |
| A "scroll down" arrow, mouse icon or "scroll to explore" | Nothing. The hero makes people scroll |
| Section counters like `01 / 06` | Delete them |
| The same device in two neighbouring acts | Re-score the screenplay |
| Centred text in every act | Vary: left, right, centre, split |
| No peak, or three competing peaks | One peak with the most room and the biggest change |
| An ending that fades into a footer | A closing screen that resolves and holds |
| Invented numbers, reviews, awards, quotes | Real facts only. No number, no counter |
| Text baked into images | Real markup |
| Dark overlay over the whole image to fix contrast | A scrim only where the text sits |
| Gradient text, neon glow, rainbow everything | Weight, size and one accent |
| Animating width, height, top, left, or `transition: all` | `transform`, `opacity`, `clip-path` |
| Em dash (—) in visible text | Period, comma, colon or parentheses |
| Audio on a scroll page | Silence. Strip audio from scrub videos |
| Editing the engine for one project | Bespoke code in the page via `Drehbuch.on()` |
| Shipping without Step 5 | Run Step 5 |
