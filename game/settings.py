"""Screen, palette and timing constants.

The internal canvas is pixel-locked: draw at 640x320 and scale up with
integer nearest-neighbour so every pixel stays crisp. The art target is
a fluid, atmospheric southern Thai pixel adventure.
"""

import pygame

INTERNAL_W = 640
INTERNAL_H = 320
SCALE = 4
WINDOW_W = INTERNAL_W * SCALE
WINDOW_H = INTERNAL_H * SCALE

WIDTH = INTERNAL_W
HEIGHT = INTERNAL_H

FPS = 60

# Palette
BLACK = (12, 10, 16)
BG = (16, 14, 22)
PANEL_BG = (20, 18, 28)
PANEL_BG_ALT = (26, 24, 36)
PANEL_BORDER = (72, 64, 52)
PANEL_EDGE = (118, 106, 88)
TEXT = (232, 224, 200)
MUTED = (150, 140, 116)
SPIRIT = (196, 214, 230)
RUEN = (210, 178, 140)
NOK = (188, 198, 214)
CHILD = (214, 200, 166)
WARN = (238, 176, 74)
DANGER = (232, 96, 96)
RED = (232, 96, 96)
GOOD = (142, 214, 142)
GOLD = (232, 198, 110)

TITLE = "YAAI'S JOURNAL: A SOUTHERN THAILAND ADVENTURE"

AMBER = (232, 198, 110)

# Time of day
DAY_LEN = 900.0
DAWN = 0.22
DUSK = 0.72


# Accents and colors for dialogue
ACCENTS = {
    "YAAI": RUEN,
    "RUEN": RUEN,
    "NOI": SPIRIT,
    "SPIRIT": SPIRIT,
    "NOK": NOK,
    "CHILD": CHILD,
    "PLAYER": TEXT,
    "NARRATOR": MUTED,
    "TEXT": MUTED,
    "LOM": DANGER,
    "DANGER": DANGER,
    "WARN": WARN,
    "KEEPER": RUEN,
    "MONK": RUEN,
    "ELDER": RUEN,
    "VOLUNTEER": NOK,
    "FISHER": NOK,
    "BOY": CHILD,
    "GIRL": CHILD,
    "AUNTIE": RUEN,
    "VILLAGER": NOK,
    "GUIDE": NOK,
    "FAMILY": NOK,
    "PAINTER": RUEN,
    "SINGER": NOK,
    "DANCER": RUEN,
    "PUPPETEER": RUEN,
    "TAPPER": NOK,
    "COLLECTOR": NOK,
}


def accent_for(name):
    if name is None:
        return TEXT
    if isinstance(name, tuple) or isinstance(name, list):
        # sometimes passed as (name, color)
        if len(name) == 0:
            return TEXT
        name = name[0]
    s = str(name).upper()
    if s in ACCENTS:
        return ACCENTS[s]
    # direct color
    if isinstance(name, (tuple, list)) and len(name) == 3:
        return tuple(name)
    return TEXT
