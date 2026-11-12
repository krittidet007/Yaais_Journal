#!/usr/bin/env python3
"""Render screenshots of the game so the art can be judged by eye.

    .venv/bin/python tools/shots.py [outdir]

Writes one PNG per region (the world at a stop in that region), plus the
title screen, scaled 2x for viewing.
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "shots")

import pygame  # noqa: E402

import main  # noqa: E402
from game import regions as RG  # noqa: E402
from game import settings as S  # noqa: E402
from game import story as ST  # noqa: E402


def shot(game, name, scale=2):
    surf = pygame.transform.scale(game.canvas, (S.INTERNAL_W * scale,
                                                S.INTERNAL_H * scale))
    path = os.path.join(OUT, name + ".png")
    pygame.image.save(surf, path)
    print("  ", path)


def main_run():
    os.makedirs(OUT, exist_ok=True)
    game = main.Game()
    game.state.reset()
    game.state.visited = ["prologue"]
    game.state.pos = None

    game.switch("cover")
    game.current.update(0.5)
    game.current.draw(game.canvas)
    shot(game, "00_title")

    game.switch("overworld")
    scene = game.current
    scene._modal = None
    game.box.hide()
    scene.fx = []
    n = 0
    for rid in RG.REGIONS:
        stop = ST.STOP_BY_ID.get(RG.REGIONS[rid]["stops"][-1])
        if stop is None:
            continue
        scene.player = pygame.Vector2(*scene._px(*stop["pos"]))
        scene.cam.snap_to(scene.player.x, scene.player.y)
        for _ in range(12):
            scene.update(1.0 / 30.0)
        scene._modal = None
        game.box.hide()
        scene.draw(game.canvas)
        shot(game, "%02d_%s" % (n, rid))
        n += 1

    # a night shot in the same place
    game.state.play_t = 260.0
    for _ in range(4):
        scene.update(1.0 / 30.0)
    scene._modal = None
    game.box.hide()
    scene.draw(game.canvas)
    shot(game, "90_night")


if __name__ == "__main__":
    pygame.display.init()
    main_run()
