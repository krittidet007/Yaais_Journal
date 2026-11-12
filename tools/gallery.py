#!/usr/bin/env python3
"""A contact sheet of every sprite and prop the game draws.

Art problems are invisible in code — you cannot see that all your rocks
look identical until they sit side by side. This renders every generated
sprite, character pose and prop variant into one labelled PNG so the
weak ones are obvious at a glance.

    .venv/bin/python tools/gallery.py [out.png]
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

import pygame  # noqa: E402

from game import artgen as A  # noqa: E402
from game import pixel  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "shots", "gallery.png")

# props that take no argument
SIMPLE_PROPS = [
    "hut", "palm", "banana", "well", "shrine", "boat", "lamp", "fence",
    "fishtrap", "dryingrack", "flags", "stupa", "karst", "mosque",
    "lighthouse", "mountain", "rock", "bush", "stump", "tree", "bigrock",
    "flowers",
]
CHARACTERS = ["player", "nok", "ruen", "child", "spirit"]


def collect():
    """Every sprite we can draw, as (label, surface)."""
    items = []
    for who in CHARACTERS:
        for facing in ("up", "down", "side"):
            for frame in range(4):
                try:
                    items.append(("%s %s %d" % (who, facing, frame),
                                  A.character(who, facing, frame)))
                except Exception:
                    pass
    for name in SIMPLE_PROPS:
        fn = getattr(A, name, None)
        if fn is None:
            continue
        for variant in range(3):
            try:
                surf = fn(variant) if name in ("palm", "rock", "bush") else fn()
            except TypeError:
                try:
                    surf = fn()
                except Exception:
                    continue
            except Exception:
                continue
            items.append(("%s %d" % (name, variant), surf))
            if name not in ("palm", "rock", "bush"):
                break
    for kind in ("G", "D", "A", "S", "H"):
        try:
            items.append(("tile %s" % kind, A.tile(kind, 0)))
        except Exception:
            pass
    for frame in range(4):
        try:
            items.append(("spirit %d" % frame, A.spirit(frame)))
        except Exception:
            pass
    return items


def main():
    pygame.display.init()
    pygame.font.init()
    items = collect()
    if not items:
        print("nothing to draw")
        return
    cell = 44
    label_h = 9
    cols = 12
    rows = (len(items) + cols - 1) // cols
    width = cols * cell
    height = rows * (cell + label_h)
    sheet = pygame.Surface((width, height))
    sheet.fill((26, 24, 34))
    for i, (label, surf) in enumerate(items):
        cx = (i % cols) * cell
        cy = (i // cols) * (cell + label_h)
        pygame.draw.rect(sheet, (44, 40, 56), pygame.Rect(cx, cy, cell - 2, cell - 2))
        # checker so transparency is visible
        for yy in range(0, cell - 2, 8):
            for xx in range(0, cell - 2, 8):
                if (xx // 8 + yy // 8) % 2 == 0:
                    pygame.draw.rect(sheet, (34, 32, 44),
                                     pygame.Rect(cx + xx, cy + yy, 8, 8))
        if surf is not None:
            sheet.blit(surf, (cx + (cell - 2 - surf.get_width()) // 2,
                              cy + (cell - 2 - surf.get_height())))
        pixel.draw_text(sheet, label[:8], (cx + 2, cy + cell - 1), (170, 164, 150),
                        size=6, shadow=None)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(pygame.transform.scale(sheet, (width * 2, height * 2)), OUT)
    print("wrote %s  (%d sprites)" % (OUT, len(items)))


if __name__ == "__main__":
    main()
