#!/usr/bin/env python3
"""Stilkompass contrast and color-vision check. Standard library only, no network, no file writes.

Usage:
  python3 kontrast.py "#FFFFFF" "#767676"            one pair (foreground, background)
  python3 kontrast.py --palette tokens.json          a whole palette, optionally light and dark mode

Palette file (one of):
  {"colors": {...}}                                  one mode
  {"light": {"colors": {...}}, "dark": {"colors": {...}}}
  {"colors": {...}, "dark": {"colors": {...}}}       top-level colors count as the light mode
Per mode, optional:
  "checks":   [[foreground, background, kind], ...]   kind: "text" 4.5:1, "large" 3:1, "ui" 3:1, "aaa" 7:1
  "distinct": [[colorA, colorB], ...]                 pairs that must stay apart with color-vision deficiency
Without "checks"/"distinct", common token names are checked automatically.

Exit code 0 when all checks pass, 1 when any fails, 2 on usage or file errors.
"""
import json
import math
import sys

THRESHOLDS = {"text": 4.5, "large": 3.0, "ui": 3.0, "aaa": 7.0}
# Simulation matrices for full dichromacy (Machado, Oliveira, Fernandes 2009), applied in linear RGB.
CVD = {
    "Protanopie (rot-blind)": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "Deuteranopie (gruen-blind)": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "Tritanopie (blau-blind)": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}
DISTINCT_MIN_DELTA_E = 20.0   # heuristic: CIE76 distance below this is hard to tell apart at a glance
# Status colors are often used as text (error messages, gains/losses), so they are checked as text by default.
DEFAULT_CHECKS = [
    ("text", "bg", "text"), ("text", "surface", "text"), ("muted", "bg", "text"), ("muted", "surface", "text"),
    ("on-primary", "primary", "text"), ("on-accent", "accent", "text"), ("on-danger", "danger", "text"),
    ("primary", "bg", "ui"), ("border", "bg", "ui"), ("focus", "bg", "ui"),
    ("success", "bg", "text"), ("danger", "bg", "text"), ("warning", "bg", "text"),
    ("up", "bg", "text"), ("down", "bg", "text"),
]
DEFAULT_DISTINCT = [("success", "danger"), ("up", "down"), ("primary", "danger"), ("warning", "danger")]


class UsageError(Exception):
    pass


def parse(value):
    if not isinstance(value, str):
        raise UsageError("color must be a string like \"#RRGGBB\", got %r" % (value,))
    h = value.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6 or any(c not in "0123456789abcdefABCDEF" for c in h):
        raise UsageError("not a #RRGGBB color: %r" % value)
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def to_srgb(c):
    c = min(1.0, max(0.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def luminance(rgb):
    r, g, b = (to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def simulate(rgb, matrix):
    lin = [to_linear(c) for c in rgb]
    return tuple(to_srgb(sum(m * v for m, v in zip(row, lin))) for row in matrix)


def lab(rgb):
    r, g, b = (to_linear(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    return math.dist(lab(a), lab(b))


def grade(r):
    if r >= 7:
        return "AAA"
    if r >= 4.5:
        return "AA"
    if r >= 3:
        return "AA nur grosser Text / UI"
    return "durchgefallen"


def pairs(value, size, field):
    if not isinstance(value, list) or not all(isinstance(p, list) and len(p) == size for p in value):
        raise UsageError("'%s' must be a list of %d-element lists" % (field, size))
    return value


def check_mode(name, spec):
    if not isinstance(spec, dict) or not isinstance(spec.get("colors"), dict) or not spec["colors"]:
        raise UsageError("mode '%s' needs a non-empty \"colors\" object" % name)
    colors = {k: parse(v) for k, v in spec["colors"].items()}
    checks = pairs(spec["checks"], 3, "checks") if "checks" in spec else \
        [c for c in DEFAULT_CHECKS if c[0] in colors and c[1] in colors]
    distinct = pairs(spec["distinct"], 2, "distinct") if "distinct" in spec else \
        [d for d in DEFAULT_DISTINCT if d[0] in colors and d[1] in colors]
    failed = 0
    print("== %s" % name)
    if not checks and not distinct:
        print("  XX  Keine bekannten Token-Paare gefunden; 'checks' angeben.")
        return 1
    for fg, bg, kind in checks:
        if kind not in THRESHOLDS:
            raise UsageError("unknown kind %r (use text, large, ui or aaa)" % kind)
        if fg not in colors or bg not in colors:
            print("  XX  %s auf %s: Token fehlt" % (fg, bg))
            failed += 1
            continue
        need = THRESHOLDS[kind]
        r = ratio(colors[fg], colors[bg])
        ok = r >= need
        failed += not ok
        print("  %s  %-12s auf %-10s %5.2f:1  (braucht %.1f, %s)  %s" % (
            "OK " if ok else "XX ", fg, bg, r, need, kind, grade(r)))
    for a, b in distinct:
        if a not in colors or b not in colors:
            print("  XX  %s vs %s: Token fehlt" % (a, b))
            failed += 1
            continue
        worst = min((delta_e(simulate(colors[a], m), simulate(colors[b], m)), label) for label, m in CVD.items())
        ok = worst[0] >= DISTINCT_MIN_DELTA_E
        failed += not ok
        print("  %s  %s vs %s: Abstand normal %.0f, schlechtester Fall %.0f bei %s%s" % (
            "OK " if ok else "XX ", a, b, delta_e(colors[a], colors[b]), worst[0], worst[1],
            "" if ok else " -> zusaetzlich Symbol, Text oder Muster noetig"))
    return failed


def load_modes(data):
    if not isinstance(data, dict):
        raise UsageError("the palette file must contain a JSON object")
    modes = {}
    if "colors" in data:
        modes["light" if any(isinstance(v, dict) and "colors" in v for v in data.values()) else "palette"] = data
    for key, value in data.items():
        if isinstance(value, dict) and "colors" in value:
            if key in modes:
                raise UsageError("mode '%s' is defined twice" % key)
            modes[key] = value
    if not modes:
        raise UsageError("no \"colors\" found (see --help for the file format)")
    return modes


def main(argv):
    if len(argv) == 3 and not argv[1].startswith("--"):
        r = ratio(parse(argv[1]), parse(argv[2]))
        print("%s auf %s: %.2f:1  -> %s" % (argv[1], argv[2], r, grade(r)))
        print("Normaler Text braucht 4.5:1 (AA) bzw. 7:1 (AAA); grosser Text und UI-Elemente 3:1.")
        return 0 if r >= 4.5 else 1
    if len(argv) == 3 and argv[1] == "--palette":
        with open(argv[2], encoding="utf-8") as fh:
            data = json.load(fh)
        modes = load_modes(data)
        failed = sum(check_mode(name, spec) for name, spec in modes.items())
        print("\nErgebnis: %s" % ("alles bestanden" if not failed else "%d Pruefung(en) durchgefallen" % failed))
        print("Hinweis: Kontrast nach WCAG-Formel. Der Farbabstand bei Farbsehschwaeche ist eine Faustregel "
              "(Simulation plus CIE76, Schwelle %d), kein Ersatz fuer echte Bildschirme und echte Menschen." % DISTINCT_MIN_DELTA_E)
        return 1 if failed else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except (UsageError, OSError, json.JSONDecodeError) as e:
        print("Fehler: %s" % e)
        sys.exit(2)
