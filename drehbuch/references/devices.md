# The device kit

A device is how an act behaves while it scrolls. Every act uses one main device. A page uses at least four families and never the same one twice in a row.

All devices live inside an **act**:

```html
<section data-db="act" style="--len:250vh" aria-label="Short name of the act">
  <div class="db-stage">
    … content …
  </div>
</section>
```

- `--len` is how long the act scrolls. 100vh = one screen. The stage sticks while the act passes, so `--len:250vh` holds the frame for 1.5 extra screens.
- The engine sets `--p` on the act: 0 when its top hits the top of the screen, 1 when its bottom hits the bottom. Use `--p` in CSS (`calc()`) or in JS (`Drehbuch.on`).
- Acts without pinning are plain sections without `data-db="act"`.

---

## 1. `pin` + cues: the frame holds, the content advances

The stage stays still, text and objects appear one after another. Good for arguments, steps, a list of reasons.

```html
<section data-db="act" style="--len:300vh">
  <div class="db-stage pin-grid">
    <h2 data-db-cue="0.05-1" data-db-hold>Three things happen</h2>
    <p data-db-cue="0.25-1" data-db-hold>First …</p>
    <p data-db-cue="0.5-1" data-db-hold>Then …</p>
    <p data-db-cue="0.75-1" data-db-hold>Finally …</p>
  </div>
</section>
```

- `data-db-cue="a-b"`: visible while `--p` is between a and b; inside, `--c` runs 0..1.
- `data-db-hold`: stays visible after b (otherwise it leaves again).
- Every cue must be fully visible at some scroll position. Leave the last ~15% of the act for reading, not for new arrivals.

## 2. `parallax`: layers at different speeds

Depth from layers that move at different rates. The cheapest premium signal on a page, and the default for a hero.

```html
<section class="hero">
  <div class="layer sky"     data-db-speed="-0.15"></div>
  <div class="layer hills"   data-db-speed="-0.06"></div>
  <h1 class="hero-title">…</h1>
  <div class="layer front"   data-db-speed="0.12"></div>
</section>
```

- Negative = moves slower than the page (far away), positive = faster (close).
- Keep speeds small (−0.2 to 0.2). Large values look like a bug.
- Put the headline between layers (behind the foreground) for real depth, but keep it readable.
- Layers need overscan (be ~20% taller than the stage) so edges never show.

## 3. `reveal`: a wipe is a change of state

One state is replaced by another as you scroll: before/after, day/night, empty/full.

```html
<section data-db="act" style="--len:200vh">
  <div class="db-stage">
    <div class="state before">…</div>
    <div class="state after db-wipe">…</div>
  </div>
</section>
```

Classes: `db-wipe` (from bottom), `db-wipe-x` (from left), `db-wipe-circle` (from centre). Or write your own `clip-path` with `var(--p)`.

## 4. `pan`: vertical scroll, sideways travel

Scrolling down moves a row sideways. Reads as "options", "a range", "a timeline".

```html
<section data-db="act" style="--len:300vh">
  <div class="db-stage">
    <div class="pan-window">
      <div data-db-pan class="pan-row">
        <article class="card">…</article> …
      </div>
    </div>
  </div>
</section>
```

- `--len` should grow with the number of items (roughly 60–80vh per card).
- On phones, consider a vertical list instead: sideways travel on a narrow screen shows one card at a time.

## 5. `kinetic`: type that assembles

Words arrive one by one. Use for one strong line, not for paragraphs.

```html
<h2 data-db-words data-db-in>The whole sentence here</h2>
```

Works with `data-db-in` (on view) or inside a cue. Screen readers get the full sentence via `aria-label`.

## 6. `scrub`: the scroll wheel is the playhead

A video plays forward and backward with the scroll. The strongest device and the heaviest: at most two per page.

```html
<section data-db="act" style="--len:300vh">
  <div class="db-stage">
    <video data-db-scrub src="clip.mp4" muted playsinline preload="auto"></video>
    <h2 class="over" data-db-cue="0.6-1" data-db-hold>…</h2>
  </div>
</section>
```

- Encode without audio and with dense keyframes, or seeking stutters.
- Provide a poster image; on some phones the first frame appears late.
- Image sequences (frames on a `<canvas>`) are an alternative for short, small scenes.

## 7. `count`: numbers that land

```html
<strong data-db-count="34">34</strong> real ant species
```

Only real numbers that the user gave or that are verifiable. No number, no counter.

## 8. `in` + flow: ordinary sections, done well

Not every act needs to pin. Plain sections with `data-db-in` (fade up once) are the rest between bigger moments and keep the page from feeling like a theme park.

## 9. Pointer and touch: the page responds

Tilt on pointer move, drag to compare, tap to change a state. Always with a touch equivalent and never as the only way to see content.

## 10. Custom: `Drehbuch.on()`

The signature move lives here.

```html
<script>
  const act = document.querySelector("#dig");
  const path = act.querySelector("path.tunnel");
  const len = path.getTotalLength();
  path.style.strokeDasharray = len;
  Drehbuch.on(act, p => { path.style.strokeDashoffset = len * (1 - p); });
</script>
```

---

## Composing an act

- One main device per act; small `in` effects inside are fine.
- Text anchors vary across acts: left, right, centre, split.
- Check the act at `--p` = 0, 0.5 and 1. All three must look intended.
- Reduced motion: the engine shows all cues and stops movement. Make sure the static version still tells the story.
