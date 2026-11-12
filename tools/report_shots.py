#!/usr/bin/env python3
"""Render the screenshots used by the project report and the competition board.

    .venv/bin/python tools/report_shots.py [outdir]

Every frame is rendered from the real game (same scenes, same HUD) at the
internal 640x320 canvas, then scaled 3x with nearest neighbour and centred
on a 1920x1080 black field - exactly how the game appears full-screen on a
1080p laptop.  Also writes the raw 640x320 canvases into ``raw/``.
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "shots", "report")

import pygame  # noqa: E402

import main  # noqa: E402
from game import settings as S  # noqa: E402
from game import story as ST  # noqa: E402

W, H = S.INTERNAL_W, S.INTERNAL_H
SCALE = 3
FULL_W, FULL_H = W * SCALE, H * SCALE

# The stops the report frames are taken at.
HERO = "nakhon"          # Nakhon Si Thammarat: wat, chedi, plaza
ROUTE = ["prologue", "chumphon", "ko_tao", "ko_pha_ngan", "ko_samui",
         "surat_thani", "ranong", "surin_islands", "khao_lak", "similan",
         "phang_nga", "phuket", "promthep", "ko_phi_phi", "krabi"]


def _frame(canvas):
    """640x320 canvas -> 1920x1080 PNG-ready surface."""
    big = pygame.transform.scale(canvas, (FULL_W, FULL_H))
    full = pygame.Surface((1920, 1080))
    full.fill((8, 9, 12))
    full.blit(big, (0, (1080 - FULL_H) // 2))
    return full


def _save(game, name):
    pygame.image.save(_frame(game.canvas), os.path.join(OUT, name + ".png"))
    pygame.image.save(game.canvas, os.path.join(OUT, "raw", name + ".png"))
    print("  ", name)


def _prep_overworld(game, stop_id, visited, beats=3):
    st = game.state
    st.reset()
    st.visited = list(visited)
    st.pos = None
    game.switch("overworld")
    scene = game.current
    stop = ST.STOP_BY_ID[stop_id]
    # stand a few tiles below the stop beacon so the beacon and the HUD show
    px, py = scene._px(*stop["pos"])
    scene.player = pygame.Vector2(px, py + 26)
    scene.cam.snap_to(scene.player.x, scene.player.y)
    st.quests[stop_id] = beats
    for _ in range(14):
        scene.update(1.0 / 30.0)
    scene._modal = None
    game.box.hide()
    return scene


def main_run():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "raw"), exist_ok=True)

    pygame.display.init()
    pygame.display.set_mode((W, H))
    game = main.Game()
    game.state.reset()
    game.state.visited = []
    game.state.pos = None

    # --- Figure 1: cover -------------------------------------------------
    game.switch("cover")
    game.current.update(0.15)
    game.current.draw(game.canvas)
    _save(game, "fig4_1_cover")

    # --- Figure 2: overworld with HUD and beacon -------------------------
    scene = _prep_overworld(game, HERO, ROUTE)
    scene.draw(game.canvas)
    _save(game, "fig4_2_overworld")

    # --- Figure 3: dialogue with Noi -------------------------------------
    stop = ST.STOP_BY_ID[HERO]
    line = ("NOI", "NOI", "This is the town of the great chedi. "
            "Read the rule on the tablet, then write the spell in Python.")
    for cand in stop.get("lines", []):
        if cand[0].upper() in ("NOI", "YAAI"):
            line = cand
            break
    game.box.show(line[0], line[1], line[2])
    game.box.skip()
    scene.draw(game.canvas)
    game.box.draw(game.canvas)
    _save(game, "fig4_3_dialogue")

    # --- Figure 4: rune tablet with its prefill --------------------------
    scene = _prep_overworld(game, HERO, ROUTE)
    spec = ST.code_of(HERO)
    scene.panel.open(spec["title"], spec.get("prefill", ""),
                     spec.get("status", ""), spec.get("teach", ""))
    scene.panel.update(0.3)
    scene.draw(game.canvas)
    _save(game, "fig4_4_tablet")

    # --- Figure 5: journal ----------------------------------------------
    scene = _prep_overworld(game, HERO, ROUTE)
    st = game.state
    seen = ST.STOPS[:13]
    st.pages = [s["id"] for s in seen]
    st.visited = [s["id"] for s in ST.STOPS[:16]]
    st.words = [s["word"] for s in seen if s.get("word")]
    st.cards = [c for s in seen for c in s.get("cards", [])]
    scene.draw(game.canvas)
    game.journal.open()
    game.journal.update(0.3)
    game.journal.draw(game.canvas)
    _save(game, "fig4_5_journal")

    # --- Figure 6: sailing map ------------------------------------------
    scene = _prep_overworld(game, HERO, ROUTE)
    scene.draw(game.canvas)
    game.map_view.open()
    game.map_view.update(0.3)
    game.map_view.draw(game.canvas)
    _save(game, "fig4_6_map")

    # --- extra scenery for the board (not in the report) -----------------
    for rid in ("gulf_shore", "mangrove", "deep_south"):
        from game import regions as RG
        stops = RG.REGIONS[rid]["stops"]
        scene = _prep_overworld(game, stops[-1], ROUTE)
        scene.draw(game.canvas)
        _save(game, "board_" + rid)

    print("done ->", OUT)


if __name__ == "__main__":
    main_run()
