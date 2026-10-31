# Design floor

The minimum quality every page meets, whatever its style. Read before writing markup; check again before shipping.

## Spacing

- Use a scale, not random values: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128 px.
- Generous outer space: at least 24px side padding on phones, 48–96px on desktop.
- Related things sit close, unrelated things far apart. Space shows structure before any line or box does.

## Typography

- Two fonts at most: one display, one text. System stacks are fine.
- Size with `clamp()`: body 16–19px, headlines that really scale (for example `clamp(2.4rem, 7vw, 6rem)`).
- Line length 45–75 characters for paragraphs (`max-width: 60ch`).
- Line height 1.5–1.7 for text, 0.95–1.15 for big headlines.
- Emphasis through weight and size, not through colour tricks, underlines everywhere or ALL CAPS paragraphs.
- No orphaned single words in big headlines (`text-wrap: balance`).

## Colour

- Six tokens: canvas, surface, ink, ink-soft, accent, accent-ink. Everything else derives from them.
- One accent, used for the action and a few highlights. If everything is accent, nothing is.
- Contrast: body text at least 4.5:1, large text at least 3:1, measured against what is actually behind it (including images and video frames).
- Dark pages: avoid pure black and pure white; use warm or cool near-blacks and off-whites.

## Text over images and video

- Check the brightest frame behind the text, not the average.
- Use a local scrim (a soft gradient only where the text sits), a text panel, or move the text to a calm area of the image.
- Never a full-screen dark overlay to rescue contrast; it kills the image.

## Depth

- Layers with different speeds, occlusion (things in front of other things), soft real shadows (offset + blur), atmospheric haze for distance.
- No zero-offset coloured glows, no neon halos, no gradient text.

## Motion

- Animate only `transform`, `opacity`, `clip-path`, `filter` (sparingly).
- Durations 300–900 ms, ease-out curves. Nothing bounces unless the brand is playful.
- Motion explains something (arrival, change, depth). Decoration-only motion goes.
- Reduced motion: the page must be complete and readable with all motion off.

## Phone first

- Compose the 390×844 view on purpose: crop images differently, stack instead of squeeze, fewer layers.
- Tap targets at least 44×44 px with space between them.
- Use `100svh` for full-screen stages so mobile browser bars don't cut content.
- No horizontal scrolling of the page itself, ever.
- Test with the system font set larger: labels must wrap, not overflow.

## Content

- Real text from the user or their existing material. Never lorem ipsum in a delivered page.
- One action, one label, repeated wherever the action appears.
- Links say where they go ("Play in browser", not "Click here").
- `<html lang>` set, images with meaningful `alt` (empty `alt=""` for decoration), one `<h1>`.
- Meta: `<title>`, description, and an Open Graph image if the user has one.

## Refuse list

Patterns that make a page look generated. Don't ship them:

- "Scroll down" arrows, bouncing mouse icons, "scroll to explore"
- `01 / 06` counters and eyebrows above every heading
- Identical three-card feature grids
- Fake dashboards, fake testimonials, invented stats, "trusted by" logos that aren't real
- Purple-to-blue AI gradients, glassmorphism everywhere, neon glows
- Every act centred, every act the same height
- Stock phrases: "Unlock", "Elevate", "Seamless", "Next level", «nahtlos», «auf das nächste Level»
- An ending that is just a footer

## Squint test

Squint at each screenshot. You should still see: where to look first, what the action is, and that this act differs from the one before. If not, simplify.
