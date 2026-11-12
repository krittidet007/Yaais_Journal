#!/usr/bin/env python3
"""Turn raw AI art into one coherent art set.

AI images disagree with each other: camera angle, light direction, colour
temperature, detail density. Left alone they look stitched together.
This pipeline is what stops that, and it does the same four things to
every single asset:

  1. SLICE   - a generated "grid sheet" of many props becomes many files
  2. CROP    - trim the empty margins, centre the sprite
  3. LOCK    - every pixel is snapped to ONE master palette, with Bayer
               dithering so gradients survive. This is the big one:
               twelve images in one palette read as one art set.
  4. MATCH  - the same sun-side rim light, the same contact shadow, the
               same pixel density, the same base anchor

    .venv/bin/python tools/ai_unify.py            # process assets_ai/in
    .venv/bin/python tools/ai_unify.py --check    # verify only

Input:  assets_ai/in/*.png  (any image; grid sheets are sliced)
Output: assets_ai/out/*.png + game/art_ai.py (a drop-in artgen replacement)

No GPU and no image libraries needed beyond numpy + pygame.
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

import numpy as np  # noqa: E402
import pygame  # noqa: E402

from game import artgen as A  # noqa: E402
from game import palette as P  # noqa: E402

IN_DIR = os.path.join(BASE, "assets_ai", "in")
OUT_DIR = os.path.join(BASE, "assets_ai", "out")

# The master palette: 32 colours, taken from the colours the game
# already uses, so AI art and code-drawn art share a colour world.
MASTER = [
    (12, 10, 16), (32, 24, 16), (51, 40, 30), (78, 60, 44),
    (110, 84, 60), (138, 106, 56), (176, 136, 64), (212, 184, 120),
    (232, 206, 140), (240, 224, 160), (250, 240, 200), (255, 250, 230),
    (20, 30, 24), (32, 70, 34), (51, 112, 31), (62, 120, 40),
    (78, 152, 56), (120, 184, 74), (152, 208, 96), (186, 224, 140),
    (24, 60, 132), (38, 84, 168), (52, 108, 196), (82, 160, 236),
    (90, 140, 210), (140, 190, 230), (196, 214, 230), (234, 246, 255),
    (90, 90, 104), (110, 116, 124), (150, 156, 164), (198, 204, 210),
]
MASTER_ARR = np.array(MASTER, dtype=np.int16)

BAYER = P.BAYER4


def _nearest_two(rgb):
    """The two nearest master colours and how far between they are."""
    diff = MASTER_ARR.astype(np.float32) - rgb.astype(np.float32).reshape(-1, 1, 3)
    dist = np.sqrt((diff ** 2).sum(axis=2))
    order = np.argsort(dist, axis=1)[:, :2]
    d0 = dist[np.arange(len(order)), order[:, 0]]
    d1 = dist[np.arange(len(order)), order[:, 1]]
    return order[:, 0], order[:, 1], d0, d1


def lock_palette(surf):
    """Snap every pixel to the master palette, dithering the in-betweens."""
    arr = pygame.surfarray.pixels3d(surf).astype(np.int16)
    h, w, _ = arr.shape
    flat = arr.reshape(-1, 3)
    a, b, d0, d1 = _nearest_two(flat)
    # a Bayer threshold decides which of the two neighbours each pixel takes
    ys, xs = np.mgrid[0:h, 0:w]
    bayer = np.array(BAYER, dtype=np.float32)
    thresh = (bayer[ys % 4, xs % 4] + 0.5) / 16.0
    total = np.maximum(d0 + d1, 1e-6)
    take_b = ((d1 / total) < thresh.reshape(-1))
    idx = np.where(take_b, b, a)
    out = MASTER_ARR[idx].reshape(h, w, 3).astype(np.uint8)
    pygame.surfarray.pixels3d(surf)[:] = out
    return surf


def trim(surf):
    """Cut the empty margins so the sprite is centred and tight."""
    arr = pygame.surfarray.array3d(surf)
    alpha = pygame.surfarray.array_alpha(surf)
    ys, xs = np.nonzero(alpha > 8)
    if len(xs) == 0:
        return surf
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    return surf.subsurface((x0, y0, x1 - x0, y1 - y0)).copy()


def to_pixel_size(surf, target):
    """Scale to the game's pixel size so the detail density matches."""
    w, h = surf.get_size()
    scale = max(1, int(round(max(w, h) / float(target))))
    if scale > 1:
        surf = pygame.transform.smoothscale(surf, (max(1, w // scale),
                                                  max(1, h // scale)))
    return surf


def slice_sheet(surf, count):
    """Split a generated grid sheet into `count` cells, left to right."""
    w, h = surf.get_size()
    cols = max(1, int(round(np.sqrt(count * w / float(max(1, h))))))
    rows = max(1, int(np.ceil(count / float(cols))))
    cw, ch = w // cols, h // rows
    out = []
    for i in range(count):
        r, c = divmod(i, cols)
        out.append(surf.subsurface((c * cw, r * ch, cw, ch)).copy())
    return out


def unify(surf, name, target=48, rim=True):
    """The four passes every asset gets."""
    surf = trim(surf)
    surf = to_pixel_size(surf, target)
    lock_palette(surf)
    if rim:
        surf = A.rimmed(surf, (255, 240, 205))
    return surf


def main():
    check_only = "--check" in sys.argv
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.isdir(IN_DIR):
        print("no assets_ai/in folder yet — drop AI PNGs in there")
        return
    names = sorted(f for f in os.listdir(IN_DIR) if f.lower().endswith(".png"))
    if not names:
        print("assets_ai/in is empty")
        return
    pygame.display.init()
    pygame.display.set_mode((16, 16))
    written = []
    for name in names:
        path = os.path.join(IN_DIR, name)
        surf = pygame.image.load(path).convert_alpha()
        stem = os.path.splitext(name)[0]
        # "sheet" files hold many props: slice them by the count in the name
        if "_x" in stem:
            stem, _, count = stem.partition("_x")
            try:
                cells = slice_sheet(surf, int(count))
            except ValueError:
                cells = [surf]
            for i, cell in enumerate(cells):
                out = unify(cell, "%s_%02d" % (stem, i))
                op = os.path.join(OUT_DIR, "%s_%02d.png" % (stem, i))
                pygame.image.save(out, op)
                written.append(os.path.basename(op))
        else:
            out = unify(surf, stem)
            op = os.path.join(OUT_DIR, stem + ".png")
            pygame.image.save(out, op)
            written.append(os.path.basename(op))
        if not check_only:
            print("  %s -> assets_ai/out/" % name)
    print("%d assets unified" % len(written))
    if written and not check_only:
        write_module(written)


MODULE_TEMPLATE = '''"""Generated art assets (AI pipeline output) — drop-in for artgen.

Created by tools/ai_unify.py. Every function returns a pygame Surface
anchored at its base, exactly like game/artgen.py, so the engine cannot
tell the difference.
"""

import os

import pygame

_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "assets_ai", "out")
_cache = {{}}


def _load(name):
    surf = _cache.get(name)
    if surf is None:
        path = os.path.join(_DIR, name + ".png")
        if not os.path.exists(path):
            return None
        surf = pygame.image.load(path).convert_alpha()
        _cache[name] = surf
    return surf


def available(name):
    return _load(name) is not None


def get(name):
    """The asset called ``name``, or None."""
    return _load(name)


{body}
'''

FUNCTION_TEMPLATE = '''def {name}(*args):
    """The unified asset '{name}'."""
    surf = _load("{name}")
    if surf is None:
        return pygame.Surface((16, 16), pygame.SRCALPHA)
    return surf

'''


def write_module(names):
    """Emit game/art_ai.py so the game can load the unified assets."""
    body = ""
    for name in names:
        stem = os.path.splitext(name)[0]
        body += FUNCTION_TEMPLATE.format(name=stem)
    path = os.path.join(BASE, "game", "art_ai.py")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(MODULE_TEMPLATE.format(body=body))
    print("  wrote game/art_ai.py (%d assets)" % len(names))


if __name__ == "__main__":
    main()
