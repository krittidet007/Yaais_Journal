"""Render key frames to PNGs without a display — for quick visual checks.

Usage:  .venv/bin/python tools/render_frames.py [outdir]
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from game import settings as S  # noqa: E402
from main import Game  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/opencode/shots"


def press(scene, key=pygame.K_SPACE):
    scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode=""))


def to_puzzle(g, limit=200):
    for _ in range(limit):
        if getattr(g.current, "stage", None) == "puzzle":
            return
        press(g.current)


def walk_to(g, x, y):
    """Teleport the hub player (Vector2) next to a target."""
    g.current.player = pygame.Vector2(x, y)


def shot(g, name):
    g.box.update(3.0)
    g.current.draw(g.canvas)
    os.makedirs(OUT, exist_ok=True)
    big = pygame.transform.scale(
        g.canvas, (S.INTERNAL_W * S.SCALE, S.INTERNAL_H * S.SCALE))
    pygame.image.save(big, os.path.join(OUT, name))
    print("saved", name, "| scene:", g.current.name)


def main():
    g = Game()
    press(g.current)
    shot(g, "1_washup.png")

    to = g.current
    for _ in range(200):
        if g.current is not to or g.ended:
            break
        press(g.current)
    shot(g, "2_hub.png")

    walk_to(g, g.current.ruen.x, g.current.ruen.y + 12)
    g.current._interact()
    to_puzzle(g)
    shot(g, "3_naming_panel.png")
    g.current._on_run(g.current.PREFILL)
    g.current.update(1.0)
    for _ in range(200):
        if g.current.name != "village_naming" or g.ended:
            break
        press(g.current)

    walk_to(g, g.current.shrine.x, g.current.shrine.y + 12)
    g.current._interact()
    to_puzzle(g)
    g.current._on_run('print("the shrine is warm")')
    g.current.update(1.5)
    shot(g, "4_shrine_lit.png")
    for _ in range(200):
        if g.current.name != "shrine" or g.ended:
            break
        press(g.current)

    walk_to(g, g.current.nok.x, g.current.nok.y + 12)
    g.current._interact()
    to_puzzle(g)
    g.current._on_run('print("draw")')
    shot(g, "5_well_panel.png")

    g.current._on_run('if bucket_lowered:\n    print("draw")\nelse:\n    print("hold")\n')
    g.current.update(2.0)
    for _ in range(200):
        if g.current.name != "well" or g.ended:
            break
        press(g.current)
    shot(g, "6_epilogue.png")


if __name__ == "__main__":
    main()
