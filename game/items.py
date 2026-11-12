"""Collectible items: catalogue + procedural 16x16 pixel icons."""

import pygame

from . import palette as P

SIZE = 16

# Ordered catalogue — inventory shows them in the order collected instead,
# but this drives the "known item" descriptions.
ITEMS = {
    "river_stone": {
        "name": "River Stone",
        "desc": "Smooth and river-cold. You woke up already holding it.",
    },
    "spirit_charm": {
        "name": "Spirit Charm",
        "desc": "A knotted cord from Grandma Ruen. Keeps your spirit from drifting.",
    },
    "rune_tablet": {
        "name": "Rune Tablet",
        "desc": "Reads the old words. Whatever the village forgot, this remembers.",
    },
    "shrine_ember": {
        "name": "Shrine Ember",
        "desc": "Still warm. The little shrine answered when you spoke to it.",
    },
    "well_water": {
        "name": "Well Water",
        "desc": "Clean at last. A small promise, kept for the whole village.",
    },
    "gift_flower": {
        "name": "Village Flower",
        "desc": "Picked for you by the child. She insists it is lucky.",
    },
}

_ORDER = list(ITEMS)
_cache = {}


def name(item_id):
    return ITEMS.get(item_id, {}).get("name", item_id)


def description(item_id):
    return ITEMS.get(item_id, {}).get("desc", "")


# ------------------------------------------------------------------- icon art
def _blob(surf, rect, ramp, seed=0):
    pygame.draw.ellipse(surf, ramp[1], rect)
    pygame.draw.ellipse(surf, ramp[2], rect.inflate(-4, -4).move(1, -1))
    pygame.draw.ellipse(surf, ramp[3], rect.inflate(-8, -8).move(1, -1))


def _charm(s):
    cord = P.ramp((180, 150, 90), 3)
    bead = P.ramp((108, 240, 222), 4)
    pygame.draw.line(s, cord[1], (5, 1), (8, 5))
    pygame.draw.line(s, cord[1], (11, 1), (8, 5))
    pygame.draw.circle(s, bead[1], (8, 9), 5)
    pygame.draw.circle(s, bead[2], (8, 9), 4)
    pygame.draw.circle(s, bead[3], (7, 8), 1)
    s.set_at((6, 7), (200, 255, 250))


def _tablet(s):
    stone = P.ramp((150, 156, 168), 4)
    rune = (96, 230, 210)
    pygame.draw.rect(s, stone[0], pygame.Rect(3, 1, 10, 14))
    pygame.draw.rect(s, stone[1], pygame.Rect(4, 2, 8, 12))
    pygame.draw.rect(s, stone[2], pygame.Rect(4, 2, 2, 12))
    for y in (4, 6, 8, 10):
        s.set_at((6, y), rune)
        s.set_at((7, y), rune)
        if y % 4 == 0:
            s.set_at((9, y), rune)


def _ember(s):
    dark = (40, 24, 20)
    outer = P.ramp((214, 96, 40), 4)
    inner = P.ramp((250, 214, 120), 4)
    pygame.draw.circle(s, dark, (8, 9), 6)
    pygame.draw.polygon(s, outer[1], [(8, 2), (12, 9), (8, 13), (4, 9)])
    pygame.draw.polygon(s, outer[2], [(8, 4), (10, 9), (8, 12), (6, 9)])
    pygame.draw.polygon(s, inner[2], [(8, 6), (9, 9), (8, 11), (7, 9)])
    s.set_at((8, 8), (255, 250, 220))


def _water(s):
    deep = P.ramp((58, 138, 216), 4)
    pygame.draw.circle(s, deep[1], (8, 10), 5)
    pygame.draw.polygon(s, deep[1], [(8, 1), (4, 8), (12, 8)])
    pygame.draw.circle(s, deep[2], (8, 10), 4)
    pygame.draw.polygon(s, deep[2], [(8, 3), (6, 8), (10, 8)])
    s.set_at((6, 8), (200, 236, 255))
    s.set_at((7, 11), (200, 236, 255))


def _stone(s):
    grey = P.ramp((140, 146, 156), 4)
    pygame.draw.ellipse(s, grey[1], pygame.Rect(2, 5, 12, 9))
    pygame.draw.ellipse(s, grey[2], pygame.Rect(3, 5, 10, 7))
    pygame.draw.ellipse(s, grey[3], pygame.Rect(4, 6, 4, 3))


def _flower(s):
    petal = P.ramp((232, 140, 178), 4)
    heart = P.ramp((250, 220, 120), 3)
    pygame.draw.line(s, (78, 152, 56), (8, 14), (8, 9))
    s.set_at((6, 12), (78, 152, 56))
    for dx, dy in ((0, -3), (3, 0), (0, 3), (-3, 0), (2, -2), (-2, -2), (2, 2), (-2, 2)):
        s.set_at((8 + dx, 5 + dy), petal[2])
    pygame.draw.circle(s, heart[2], (8, 5), 2)


_ICONS = {
    "river_stone": _stone,
    "spirit_charm": _charm,
    "rune_tablet": _tablet,
    "shrine_ember": _ember,
    "well_water": _water,
    "gift_flower": _flower,
}


def icon(item_id):
    if item_id not in _cache:
        s = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
        drawer = _ICONS.get(item_id, _stone)
        drawer(s)
        _cache[item_id] = s
    return _cache[item_id]


def known(item_id):
    return item_id in ITEMS
