"""Dump sprites and scene frames as ASCII so shape/layout can be checked in a terminal.

Usage:  .venv/bin/python tools/ascii_preview.py [sprite|scene]
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from game import artgen  # noqa: E402

RAMP = " .:-=+*xX#@"


def ascii_sprite(surf):
    w, h = surf.get_size()
    rows = []
    for y in range(h):
        line = ""
        for x in range(w):
            r, g, b, a = surf.get_at((x, y))
            if a < 40:
                line += " "
                continue
            if (r, g, b) == artgen.OUTLINE:
                line += "#"
                continue
            lum = (r * 0.3 + g * 0.55 + b * 0.15) / 255.0
            line += RAMP[min(len(RAMP) - 1, 1 + int(lum * (len(RAMP) - 2)))]
        rows.append(line)
    return rows


def show(name, surf):
    print("==", name, surf.get_size())
    for row in ascii_sprite(surf):
        print("  " + row)
    print()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "sprite"
    if mode == "sprite":
        for who in ("player", "ruen", "nok", "child"):
            show("char " + who, artgen.character(who, "down", 0))
        show("char player up", artgen.character("player", "up", 0))
        show("char player side f1", artgen.character("player", "side", 1))
        show("hut lit", artgen.hut(lit=True))
        show("shrine lit", artgen.shrine(lit=True))
        show("well", artgen.well(0.9))
        show("palm", artgen.palm())
        show("bush", artgen.bush())
        show("rock", artgen.rock())
        return

    from game import settings as S
    from game import views
    canvas = pygame.Surface((S.INTERNAL_W, S.INTERNAL_H))
    cols, rows = 100, int(100 * S.INTERNAL_H / S.INTERNAL_W)
    for name, fn in (("washup", views.draw_washup), ("village", views.draw_village)):
        fn(canvas, 0.0)
        small = pygame.transform.smoothscale(canvas, (cols, rows))
        print("== scene", name)
        for y in range(rows):
            line = ""
            for x in range(cols):
                r, g, b, a = small.get_at((x, y))
                lum = (r * 0.3 + g * 0.55 + b * 0.15) / 255.0
                line += RAMP[min(len(RAMP) - 1, int(lum * (len(RAMP) - 1)))]
            print("  " + line)
        print()


if __name__ == "__main__":
    main()
