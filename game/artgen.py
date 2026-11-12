"""Procedurally generated pixel art.

The design doc calls for coded art rather than hand-drawn, so every tile and sprite
is built here from hue-shifted colour ramps (see `palette.py`) plus a deterministic
RNG. Each object gets a 1px dark outline, a warm-lit column on the left and a
cool-shadow column on the right, so it reads as a solid, lit form rather than a
flat rectangle.
"""

import math
import random

import pygame

from . import palette as P

ramp = P.ramp

# ------------------------------------------------------------------- palettes
SKY_NIGHT = [(7, 9, 20), (10, 13, 28), (15, 20, 40), (21, 29, 55), (29, 41, 71)]
SKY_DUSK = [(26, 24, 52), (50, 34, 62), (90, 50, 66), (144, 72, 68), (194, 106, 72), (226, 148, 94)]

GRASS = ramp((72, 138, 70), 5)
GRASS_DRY = ramp((132, 150, 76), 5)
DIRT = ramp((142, 106, 68), 5)
SAND = ramp((196, 176, 126), 5)
STONE = ramp((124, 128, 136), 5)
WOOD = ramp((150, 104, 62), 5)
THATCH = ramp((178, 134, 78), 5)
ROOF = ramp((188, 104, 72), 5)
LEAF = ramp((54, 122, 66), 5)
LEAF_DARK = ramp((36, 88, 52), 4)
WATER = ramp((58, 116, 150), 6)
GOLD = ramp((214, 168, 78), 4)
STUCCO = ramp((206, 194, 166), 5)

EYE = (26, 22, 30)
OUTLINE = (32, 24, 16)  # warm-black — SNES overworld outline colour

BAYER = P.BAYER4
_cache = {}


# -------------------------------------------------------------------- helpers
BERRY = [(196, 70, 62), (224, 96, 80), (208, 84, 96), (236, 120, 72),
         (188, 76, 104), (226, 142, 78)]
PETAL = [(236, 112, 128), (244, 196, 96), (236, 236, 240), (216, 150, 214),
         (246, 156, 84)]


def _rnd(variant, salt=0):
    """A seeded generator per prop variant, so shapes are stable."""
    return random.Random(1000 + variant * 37 + salt)


def _new(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _rect(surf, x0, y0, x1, y1, color):
    pygame.draw.rect(surf, color, pygame.Rect(x0, y0, x1 - x0 + 1, y1 - y0 + 1))


def _px(surf, x, y, color):
    if 0 <= x < surf.get_width() and 0 <= y < surf.get_height():
        surf.set_at((x, y), color)


def _rng(x, y, salt=0):
    n = (int(x) * 73856093) ^ (int(y) * 19349663) ^ (int(salt) * 83492791)
    n &= 0x7FFFFFFF
    return ((n >> 7) % 1000) / 1000.0


def add_outline(surf, color=OUTLINE):
    w, h = surf.get_size()
    out = surf.copy()
    opaque = [[surf.get_at((x, y))[3] > 0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if opaque[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and opaque[ny][nx]:
                    out.set_at((x, y), color)
                    break
    return out


def _finish(key, surf):
    out = add_outline(surf)
    _cache[key] = out
    return out


_rim_cache = {}


def rimmed(surf, color=(255, 238, 205)):
    """Add a 1px highlight along the sun-side edge of a sprite.

    Flat fills are what make code-drawn art look like stickers. A rim
    light on the upper-left edge gives every object a light source, and
    because the scene's ambient multiply tints the frame afterwards, a
    neutral rim reads correctly in every region.
    """
    key = (id(surf), color)
    out = _rim_cache.get(key)
    if out is not None:
        return out
    w, h = surf.get_size()
    out = surf.copy()
    for y in range(h):
        for x in range(w):
            if out.get_at((x, y))[3] < 200:
                continue
            nx, ny = x - 1, y - 1          # the light sits up and to the left
            if nx < 0 or ny < 0:
                continue
            if out.get_at((nx, ny))[3] > 80:
                continue
            c = out.get_at((x, y))
            out.set_at((x, y), (
                min(255, int(c[0] * 0.78 + color[0] * 0.22)),
                min(255, int(c[1] * 0.78 + color[1] * 0.22)),
                min(255, int(c[2] * 0.78 + color[2] * 0.22)),
                c[3]))
    _rim_cache[key] = out
    return out


def _dither(surf, rect, a, b, ratio, offset=0):
    for y in range(rect.top, rect.bottom):
        for x in range(rect.left, rect.right):
            th = (BAYER[(y - rect.top + offset) % 4][(x - rect.left) % 4] + 0.5) / 16.0
            surf.set_at((x, y), b if ratio > th else a)


# ---------------------------------------------------------------------- tiles
def tile(kind, variant=0):
    key = ("tile", kind, variant)
    if key in _cache:
        return _cache[key]
    surf = _new(16, 16)

    if kind == "water":
        surf.fill(WATER[2])
        for x in range(16):
            wave = int(round(math.sin(x * 0.5 + variant * 1.3) * 1.7))
            for y in range(16):
                v = (y + wave) % 7
                if v == 0:
                    surf.set_at((x, y), WATER[1])
                elif v == 3:
                    surf.set_at((x, y), WATER[3])
                elif v == 4 and _rng(x, y, variant) > 0.7:
                    surf.set_at((x, y), WATER[4])
        for i in range(3):
            surf.set_at((int(_rng(i, variant, 11) * 15), int(_rng(variant, i, 12) * 15)), WATER[5])
        _cache[key] = surf
        return surf

    colors = {
        "grass": GRASS, "grass_dry": GRASS_DRY, "dirt": DIRT,
        "sand": SAND, "stone": STONE, "wood": WOOD,
    }[kind]
    surf.fill(colors[1])
    for i in range(6):
        x = int(_rng(i, variant, 31) * 15)
        y = int(_rng(variant, i, 32) * 15)
        w = 1 + int(_rng(i, i + 1, 33) * 2)
        _rect(surf, x, y, min(15, x + w), min(15, y + 1), colors[0] if i % 2 else colors[2])
    for i in range(4):
        x = 2 + int(_rng(i, variant, 41) * 12)
        y = 5 + int(_rng(variant, i, 42) * 8)
        surf.set_at((x, y), colors[3])
        surf.set_at((x, y + 1), colors[2])
    if kind == "stone":
        for yy in (0, 8):
            for xx in (0, 8):
                pygame.draw.rect(surf, colors[0], pygame.Rect(xx, yy, 8, 8), 1)
                _rect(surf, xx + 1, yy + 1, xx + 3, yy + 2, colors[3])
    _cache[key] = surf
    return surf


# -------------------------------------------------------------------- scenery
def well(water=0.0):
    key = ("well", round(water, 1))
    if key in _cache:
        return _cache[key]
    s = _new(48, 54)
    # stone rim from individual stones
    pygame.draw.ellipse(s, STONE[3], pygame.Rect(6, 28, 36, 14))
    pygame.draw.ellipse(s, STONE[2], pygame.Rect(7, 29, 34, 12))
    for i in range(12):
        a = i / 12 * math.tau
        x = int(24 + math.cos(a) * 15)
        y = int(34 + math.sin(a) * 5.5)
        _px(s, x, y, STONE[1])
        _px(s, x, y + 1, STONE[0])
    _rect(s, 7, 34, 40, 46, STONE[2])
    _rect(s, 7, 34, 8, 46, STONE[3])
    _rect(s, 39, 34, 40, 46, STONE[0])
    for y in range(36, 46, 4):
        pygame.draw.line(s, STONE[0], (9, y), (39, y))
    pygame.draw.ellipse(s, (10, 14, 22), pygame.Rect(11, 30, 26, 9))
    if water > 0.02:
        pygame.draw.ellipse(s, WATER[2], pygame.Rect(13, 31, 22, 6))
        pygame.draw.ellipse(s, WATER[3], pygame.Rect(16, 32, 12, 3))
        _px(s, 20, 33, WATER[5])
        _px(s, 27, 34, WATER[5])
    # posts, beam, roof, windlass
    for x in (10, 35):
        _rect(s, x, 8, x + 2, 31, WOOD[2])
        _px(s, x, 8, WOOD[3])
    _rect(s, 8, 8, 39, 10, WOOD[1])
    pygame.draw.polygon(s, WOOD[0], [(3, 9), (24, 0), (44, 9)])
    pygame.draw.polygon(s, THATCH[1], [(5, 9), (24, 2), (41, 9)])
    pygame.draw.polygon(s, THATCH[3], [(9, 8), (24, 4), (37, 8)])
    for x in range(8, 41, 3):
        _px(s, x, 7, THATCH[0])
    _rect(s, 21, 11, 26, 14, WOOD[3])          # windlass drum
    _px(s, 26, 12, WOOD[1])
    pygame.draw.line(s, WOOD[1], (27, 12), (31, 9))  # crank handle
    length = 15 if water <= 0.02 else 10
    pygame.draw.line(s, (196, 178, 132), (24, 14), (24, 14 + length))
    _rect(s, 21, 14 + length, 26, 17 + length, WOOD[3])
    for i in range(0, 44, 7):                   # moss
        _px(s, 9 + i % 30, 35 + (i % 9), STONE[0] if i % 2 else LEAF_DARK[1])
    return _finish(key, s)


def shrine(lit=False):
    """Thai spirit house: a post, a small gold-tiered roof and offerings."""
    key = ("shrine", lit)
    if key in _cache:
        return _cache[key]
    s = _new(34, 52)
    # ornate carved post
    _rect(s, 15, 26, 18, 48, WOOD[1])
    _rect(s, 15, 26, 15, 48, WOOD[2])
    _rect(s, 13, 30, 20, 34, WOOD[2])
    for y in (31, 33):
        pygame.draw.line(s, WOOD[0], (14, y), (19, y))
    _rect(s, 12, 46, 21, 49, WOOD[1])
    # platform
    _rect(s, 7, 24, 26, 27, WOOD[3])
    _rect(s, 7, 24, 26, 24, WOOD[3])
    _rect(s, 7, 27, 26, 27, WOOD[0])
    # body
    _rect(s, 8, 14, 25, 24, WOOD[3])
    _rect(s, 8, 14, 9, 24, (236, 214, 168))
    _rect(s, 24, 14, 25, 24, WOOD[1])
    for y in range(16, 24, 3):
        pygame.draw.line(s, WOOD[2], (10, y), (23, y))
    # tiered gold roof
    pygame.draw.polygon(s, ROOF[1], [(3, 15), (17, 5), (30, 15)])
    pygame.draw.polygon(s, ROOF[2], [(5, 14), (17, 7), (28, 14)])
    pygame.draw.polygon(s, ROOF[1], [(6, 10), (17, 2), (27, 10)])
    pygame.draw.polygon(s, ROOF[3], [(8, 9), (17, 4), (25, 9)])
    pygame.draw.line(s, GOLD[2], (4, 14), (29, 14))
    pygame.draw.line(s, GOLD[3], (7, 9), (26, 9))
    _rect(s, 16, 0, 17, 3, GOLD[2])
    _px(s, 16, 0, GOLD[3])
    _px(s, 17, 1, GOLD[0])
    # garland along the eaves
    for x in range(6, 29, 3):
        _px(s, x, 16, (238, 176, 72) if (x // 3) % 2 else (226, 108, 70))
    # candle glow / shrine window
    win = (255, 214, 128) if lit else (54, 58, 74)
    _rect(s, 13, 17, 18, 21, win)
    pygame.draw.rect(s, WOOD[1], pygame.Rect(13, 17, 6, 5), 1)
    if lit:
        _px(s, 15, 19, (255, 246, 210))
    # offering tray
    _rect(s, 20, 40, 30, 42, WOOD[2])
    _rect(s, 21, 39, 23, 40, (238, 176, 72))
    _rect(s, 25, 39, 27, 40, (226, 108, 70))
    _px(s, 24, 38, GOLD[3])
    return _finish(key, s)


def boat():
    key = ("boat",)
    if key in _cache:
        return _cache[key]
    s = _new(46, 18)
    pygame.draw.polygon(s, WOOD[2], [(1, 8), (5, 14), (40, 14), (44, 8), (40, 10), (5, 10)])
    pygame.draw.polygon(s, WOOD[1], [(3, 9), (6, 13), (39, 13), (42, 9)])
    pygame.draw.polygon(s, WOOD[3], [(2, 7), (6, 9), (40, 9), (43, 7), (40, 8), (6, 8)])
    for x in range(8, 40, 6):
        pygame.draw.line(s, WOOD[0], (x, 10), (x, 13))
    _rect(s, 32, 2, 34, 10, WOOD[2])      # prow post
    _px(s, 32, 2, WOOD[3])
    pygame.draw.line(s, WOOD[0], (10, 4), (36, 6))   # oar
    return _finish(key, s)


def lamp():
    key = ("lamp",)
    if key in _cache:
        return _cache[key]
    s = _new(12, 40)
    _rect(s, 5, 12, 6, 39, WOOD[1])
    _px(s, 5, 12, WOOD[3])
    pygame.draw.line(s, WOOD[1], (5, 12), (2, 10))
    pygame.draw.line(s, WOOD[1], (6, 12), (9, 10))
    pygame.draw.circle(s, (250, 206, 120), (5, 8), 4)
    pygame.draw.circle(s, (255, 240, 190), (5, 8), 2)
    pygame.draw.arc(s, WOOD[0], pygame.Rect(1, 3, 8, 8), 0.4, 2.7, 1)
    return _finish(key, s)


def fence():
    key = ("fence",)
    if key in _cache:
        return _cache[key]
    s = _new(34, 14)
    for x in range(2, 33, 8):
        _rect(s, x, 2, x + 1, 13, WOOD[2])
        _px(s, x, 2, WOOD[3])
    pygame.draw.line(s, WOOD[1], (1, 5), (32, 5))
    pygame.draw.line(s, WOOD[0], (1, 9), (32, 9))
    return _finish(key, s)


def fishtrap():
    key = ("fishtrap",)
    if key in _cache:
        return _cache[key]
    s = _new(24, 18)
    pygame.draw.ellipse(s, WOOD[2], pygame.Rect(1, 5, 22, 12))
    pygame.draw.ellipse(s, WOOD[1], pygame.Rect(3, 6, 18, 10))
    for x in range(4, 20, 3):
        pygame.draw.line(s, WOOD[0], (x, 7), (x, 15))
    for y in range(8, 15, 3):
        pygame.draw.line(s, WOOD[0], (4, y), (19, y))
    pygame.draw.circle(s, WOOD[0], (12, 7), 2)
    return _finish(key, s)


def dryingrack():
    key = ("dryingrack",)
    if key in _cache:
        return _cache[key]
    s = _new(32, 22)
    _rect(s, 2, 6, 3, 21, WOOD[1])
    _rect(s, 28, 6, 29, 21, WOOD[1])
    pygame.draw.line(s, WOOD[1], (2, 7), (29, 7))
    for x in (8, 15, 22):
        pygame.draw.circle(s, (150, 158, 168), (x, 10), 3)
        pygame.draw.ellipse(s, (176, 186, 196), pygame.Rect(x - 3, 9, 6, 3))
        _px(s, x + 2, 9, (60, 62, 72))
    return _finish(key, s)


def flags(frame=0):
    key = ("flags", frame)
    if key in _cache:
        return _cache[key]
    s = _new(14, 30)
    _rect(s, 3, 4, 4, 29, WOOD[1])
    _px(s, 3, 4, WOOD[3])
    for i, y in enumerate((5, 12, 19)):
        sway = int(math.sin(frame * 1.3 + i) * 1)
        color = (226, 108, 70) if i % 2 == 0 else (238, 196, 96)
        pygame.draw.polygon(s, color, [(5, y), (13 + sway, y + 3), (5, y + 6)])
        pygame.draw.polygon(s, (255, 236, 200), [(5, y), (9 + sway, y + 1), (5, y + 2)])
    return _finish(key, s)


def stupa():
    """A Srivijaya bell chedi: stepped base, bell, ringed spire."""
    key = ("stupa",)
    if key in _cache:
        return _cache[key]
    s = _new(26, 46)
    _rect(s, 3, 38, 22, 45, STONE[1])
    _rect(s, 5, 34, 20, 37, STONE[2])
    _rect(s, 7, 30, 18, 33, STONE[3])
    pygame.draw.ellipse(s, GOLD[1], pygame.Rect(6, 16, 14, 15))
    pygame.draw.ellipse(s, GOLD[2], pygame.Rect(8, 14, 10, 12))
    pygame.draw.ellipse(s, GOLD[3], pygame.Rect(10, 15, 5, 6))
    for y, w in ((12, 10), (9, 8), (6, 6), (3, 4)):
        _rect(s, 13 - w // 2, y, 13 + w // 2, y + 1, GOLD[1])
    _px(s, 13, 1, GOLD[3])
    _px(s, 9, 20, GOLD[3])
    return _finish(key, s)


def karst():
    """A Phang Nga limestone cliff: grey teeth with a green crown."""
    key = ("karst",)
    if key in _cache:
        return _cache[key]
    s = _new(28, 54)
    pygame.draw.polygon(s, STONE[1],
                        [(2, 53), (4, 20), (8, 10), (12, 16), (16, 6),
                         (20, 14), (24, 22), (26, 53)])
    pygame.draw.polygon(s, STONE[2],
                        [(6, 53), (8, 22), (11, 14), (14, 20), (17, 12),
                         (20, 20), (22, 53)])
    pygame.draw.polygon(s, STONE[3], [(11, 14), (14, 20), (15, 15), (12, 12)])
    for x, y in ((8, 9), (14, 5), (19, 13), (23, 21)):
        pygame.draw.ellipse(s, LEAF[1], pygame.Rect(x - 3, y - 2, 7, 4))
        _px(s, x - 1, y - 1, LEAF[3])
    _px(s, 10, 30, STONE[3])
    _px(s, 18, 40, STONE[0])
    return _finish(key, s)


def mosque():
    """Krue Se in miniature: white dome, one minaret, arched door."""
    key = ("mosque",)
    if key in _cache:
        return _cache[key]
    s = _new(34, 48)
    WHITE = (236, 240, 244)
    SHADE = (170, 182, 198)
    _rect(s, 2, 30, 24, 47, WHITE)
    _rect(s, 2, 30, 24, 32, SHADE)
    pygame.draw.ellipse(s, WHITE, pygame.Rect(2, 14, 23, 18))
    pygame.draw.ellipse(s, SHADE, pygame.Rect(2, 22, 23, 10))
    _rect(s, 12, 6, 14, 16, SHADE)
    _px(s, 13, 4, GOLD[2])
    pygame.draw.arc(s, GOLD[2], pygame.Rect(10, 0, 7, 7), 0.6, 5.6, 1)
    _rect(s, 27, 10, 30, 47, WHITE)
    _rect(s, 26, 8, 31, 10, SHADE)
    _rect(s, 28, 12, 29, 16, SHADE)
    _rect(s, 28, 20, 29, 24, SHADE)
    _rect(s, 10, 36, 16, 47, WOOD[2])
    pygame.draw.arc(s, WOOD[3], pygame.Rect(10, 34, 7, 6), 3.2, 6.2, 1)
    return _finish(key, s)


def lighthouse():
    """The Trang seal in miniature: white tower, red bands, lit crown."""
    key = ("lighthouse",)
    if key in _cache:
        return _cache[key]
    s = _new(16, 52)
    _rect(s, 4, 10, 11, 51, (236, 240, 244))
    _rect(s, 4, 18, 11, 23, (200, 84, 76))
    _rect(s, 4, 32, 11, 37, (200, 84, 76))
    _rect(s, 3, 6, 12, 10, (60, 62, 72))
    pygame.draw.circle(s, (250, 206, 120), (7, 8), 4)
    pygame.draw.circle(s, (255, 240, 190), (7, 8), 2)
    _rect(s, 6, 44, 8, 51, WOOD[2])
    return _finish(key, s)


def mountain():
    """A southern massif: grey teeth over green shoulders."""
    key = ("mountain",)
    if key in _cache:
        return _cache[key]
    s = _new(44, 60)
    pygame.draw.ellipse(s, LEAF_DARK[1], pygame.Rect(2, 44, 40, 14))
    pygame.draw.ellipse(s, LEAF[1], pygame.Rect(5, 42, 34, 10))
    pygame.draw.polygon(s, STONE[1],
                        [(4, 48), (10, 20), (16, 10), (22, 18), (28, 6),
                         (34, 16), (40, 28), (42, 48)])
    pygame.draw.polygon(s, STONE[2],
                        [(12, 48), (16, 24), (21, 14), (26, 22), (31, 14),
                         (35, 24), (37, 48)])
    pygame.draw.polygon(s, STONE[3], [(21, 14), (26, 22), (24, 16), (22, 15)])
    pygame.draw.polygon(s, (236, 240, 244), [(25, 8), (28, 6), (29, 9), (26, 10)])
    _px(s, 18, 30, STONE[3])
    _px(s, 32, 34, STONE[0])
    return _finish(key, s)


def stump():
    key = ("stump",)
    if key in _cache:
        return _cache[key]
    s = _new(14, 12)
    _rect(s, 3, 5, 11, 11, WOOD[1])
    pygame.draw.ellipse(s, WOOD[2], pygame.Rect(2, 2, 10, 6))
    pygame.draw.ellipse(s, WOOD[3], pygame.Rect(4, 3, 6, 3))
    pygame.draw.ellipse(s, WOOD[0], pygame.Rect(6, 4, 2, 1))
    return _finish(key, s)


CHARS = {
    "player": dict(skin=(238, 198, 158), hair=(128, 76, 36), style="cap",
                   shirt=(28, 186, 54), pants=(96, 74, 58), accent=(212, 178, 92),
                   shoes=(104, 68, 40), build="normal"),
    "ruen": dict(skin=(226, 180, 140), hair=(206, 206, 212), style="bun",
                 shirt=(168, 92, 72), pants=(112, 72, 52), accent=(226, 182, 96),
                 shoes=(60, 48, 42), build="normal"),
    "nok": dict(skin=(216, 168, 120), hair=(46, 38, 32), style="bandana",
                shirt=(86, 128, 96), pants=(70, 74, 90), accent=(196, 96, 72),
                shoes=(48, 44, 42), build="normal"),
    "child": dict(skin=(238, 198, 158), hair=(40, 34, 30), style="tuft",
                  shirt=(226, 196, 110), pants=(120, 96, 70), accent=(180, 120, 90),
                  shoes=(72, 58, 44), build="small"),
}


def character(who, facing="down", frame=0):
    key = ("char", who, facing, frame)
    if key in _cache:
        return _cache[key]
    c = CHARS[who]
    skin = ramp(c["skin"], 4)
    hair = ramp(c["hair"], 4)
    shirt = ramp(c["shirt"], 4)
    pants = ramp(c["pants"], 4)
    shoe = ramp(c["shoes"], 3)
    small = c["build"] == "small"
    s = _new(18, 22)

    bob = 1 if frame in (1, 3) else 0
    dy = 2 if small else 0            # small body starts slightly lower / shorter
    head_y0 = 2 + dy
    head_y1 = 9 + dy
    torso_y0 = 10 + dy
    torso_y1 = 15 + dy
    hip_y = torso_y1
    foot_y = 21

    # ---- legs (four-frame cycle)
    if frame in (1, 3):
        legs = [(6, 7), (9, 10)]
        offs = (0, 0)
    elif frame == 0:
        legs = [(4, 6), (10, 12)]
        offs = (0, -1)
    else:
        legs = [(5, 7), (9, 11)]
        offs = (-1, 0)
    for (lx0, lx1), off in zip(legs, offs):
        _rect(s, lx0, hip_y + 1 + off, lx1, foot_y - 1 + off, pants[1])
        _rect(s, lx0, hip_y + 1 + off, lx0, foot_y - 1 + off, pants[2])
        _rect(s, lx0, foot_y - 1 + off, lx1, foot_y + off, shoe[1])
        _px(s, lx0, foot_y - 1 + off, shoe[2])

    # ---- torso
    _rect(s, 5, torso_y0 - bob, 12, torso_y1 - bob, shirt[1])
    _rect(s, 5, torso_y0 - bob, 5, torso_y1 - bob, shirt[2])
    _rect(s, 12, torso_y0 - bob, 12, torso_y1 - bob, shirt[0])
    _rect(s, 5, torso_y1 - bob, 12, torso_y1 - bob, shirt[0])      # hem
    pygame.draw.line(s, c["accent"], (11, torso_y0 + 1 - bob), (8, torso_y1 - 1 - bob))  # sash
    _rect(s, 5, hip_y - bob, 12, hip_y - bob, c["accent"])

    # ---- arms (swing on contact frames)
    arm_y = torso_y0 + 1 - bob
    if frame == 0:
        arms = [(3, arm_y + 1), (13, arm_y - 1)]
    elif frame == 2:
        arms = [(3, arm_y - 1), (13, arm_y + 1)]
    else:
        arms = [(4, arm_y), (13, arm_y)]
    for ax, ay in arms:
        _rect(s, ax, ay, ax + 1, ay + 4, shirt[1])
        _px(s, ax, ay, shirt[2])
        _rect(s, ax, ay + 5, ax + 1, ay + 6, skin[2])              # hand

    # ---- head
    _rect(s, 5, head_y0, 12, head_y1, skin[2])
    _rect(s, 5, head_y0, 5, head_y1, skin[3])
    _rect(s, 12, head_y0, 12, head_y1, skin[1])
    _rect(s, 7, head_y1 + 1, 10, torso_y0, skin[1])                # neck

    style = c["style"]
    hair_top = head_y0 - 1
    if facing == "up":
        _rect(s, 4, hair_top, 13, head_y1, hair[1])
        _rect(s, 4, hair_top, 13, hair_top + 1, hair[2])
        _px(s, 5, hair_top, hair[3])
    else:
        _rect(s, 4, hair_top, 13, head_y0 + 1, hair[1])
        _rect(s, 4, hair_top, 13, hair_top, hair[2])
        _px(s, 5, hair_top, hair[3])
        _rect(s, 4, hair_top, 4, head_y1 - 1, hair[1])
        _rect(s, 13, hair_top, 13, head_y1 - 1, hair[1])
        _px(s, 4, hair_top, hair[2])
    if style == "bun":
        pygame.draw.circle(s, hair[1], (9, max(0, hair_top - 1)), 2)
        _px(s, 8, max(0, hair_top - 2), hair[2])
    elif style == "tuft":
        _rect(s, 8, max(0, hair_top - 1), 9, hair_top, hair[1])
        _px(s, 8, max(0, hair_top - 2), hair[2])
    elif style == "bandana":
        _rect(s, 4, hair_top + 1, 13, hair_top + 1, c["accent"])
        _rect(s, 4, hair_top, 13, hair_top, hair[0])
        _px(s, 13, hair_top + 1, c["accent"])
    elif style == "cap":
        # pointed hero cap (Link-style): band + dome + tip
        pygame.draw.circle(s, shirt[1], (9, hair_top), 3)
        _px(s, 9, hair_top - 2, shirt[3])
        _px(s, 8, hair_top - 1, shirt[3])
        _rect(s, 4, hair_top + 1, 13, hair_top + 1, shirt[2])
        _px(s, 9, hair_top + 1, shirt[2])

    if facing == "down":
        _px(s, 7, head_y0 + 4, EYE)
        _px(s, 10, head_y0 + 4, EYE)
        _px(s, 7, head_y0 + 3, skin[3])
        _px(s, 10, head_y0 + 3, skin[3])
        if style == "tuft":
            _px(s, 6, head_y0 + 5, (222, 128, 110))
            _px(s, 11, head_y0 + 5, (222, 128, 110))
    elif facing == "side":
        _px(s, 10, head_y0 + 4, EYE)
        _px(s, 10, head_y0 + 3, skin[3])
        _rect(s, 4, head_y0, 4, head_y1 - 1, hair[1])              # side hair mass
    return _finish(key, s)


def lying_player():
    key = ("lying",)
    if key in _cache:
        return _cache[key]
    c = CHARS["player"]
    skin = ramp(c["skin"], 4)
    shirt = ramp(c["shirt"], 4)
    pants = ramp(c["pants"], 4)
    hair = ramp(c["hair"], 4)
    s = _new(30, 18)
    _rect(s, 4, 8, 18, 14, pants[1])                 # legs
    _rect(s, 4, 8, 18, 8, pants[2])
    _rect(s, 10, 6, 20, 14, shirt[1])                # torso
    _rect(s, 10, 6, 20, 6, shirt[2])
    _rect(s, 10, 14, 20, 14, shirt[0])
    pygame.draw.circle(s, skin[2], (24, 10), 5)      # head
    pygame.draw.circle(s, hair[1], (24, 8), 5)
    pygame.draw.circle(s, skin[2], (24, 10), 4)
    _px(s, 26, 10, skin[3])
    _px(s, 23, 10, EYE)
    _px(s, 26, 10, EYE)
    return _finish(key, s)


def portrait(who):
    key = ("portrait", who)
    if key in _cache:
        return _cache[key]
    c = CHARS[who]
    skin = ramp(c["skin"], 4)
    hair = ramp(c["hair"], 4)
    shirt = ramp(c["shirt"], 4)
    s = _new(30, 30)
    _rect(s, 1, 1, 28, 28, (30, 26, 40))             # frame
    _rect(s, 2, 2, 27, 27, (46, 42, 62))
    _rect(s, 5, 20, 25, 28, shirt[1])                # shoulders
    _rect(s, 5, 20, 25, 20, shirt[2])
    pygame.draw.ellipse(s, skin[2], pygame.Rect(6, 5, 18, 19))   # face
    pygame.draw.ellipse(s, skin[3], pygame.Rect(7, 5, 8, 8))
    _rect(s, 5, 3, 24, 9, hair[1])                   # hair
    _rect(s, 5, 3, 24, 4, hair[2])
    _rect(s, 4, 3, 5, 18, hair[1])
    _rect(s, 24, 3, 25, 18, hair[1])
    if c["style"] == "bun":
        pygame.draw.circle(s, hair[1], (15, 2), 4)
        _px(s, 12, 1, hair[2])
    elif c["style"] == "tuft":
        _rect(s, 13, 1, 17, 4, hair[1])
        _px(s, 14, 0, hair[2])
    elif c["style"] == "bandana":
        _rect(s, 4, 8, 25, 9, c["accent"])
    elif c["style"] == "cap":
        pygame.draw.circle(s, shirt[1], (15, 2), 3)
        _px(s, 15, 2, shirt[3])
        _px(s, 13, 3, shirt[2])
        _px(s, 17, 3, shirt[2])
    # eyes
    for ex in (10, 18):
        _rect(s, ex, 13, ex + 1, 14, (250, 250, 252))
        _px(s, ex + (0 if ex < 14 else 1), 13, EYE)
        _px(s, ex, 14, EYE)
        pygame.draw.line(s, hair[0], (ex - 1, 11), (ex + 2, 11))
    _px(s, 15, 18, (196, 128, 112))                  # mouth
    _px(s, 14, 18, (196, 128, 112))
    if c["style"] == "tuft":
        _rect(s, 7, 17, 9, 17, (224, 132, 116))
        _rect(s, 20, 17, 22, 17, (224, 132, 116))
    return _cache.setdefault(key, add_outline(s, (18, 14, 22)))


def spirit(frame=0):
    key = ("spirit", frame)
    if key in _cache:
        return _cache[key]
    s = _new(18, 20)
    breathe = [0, 1, 2, 1][frame % 4]
    cy = 12 - breathe
    pygame.draw.polygon(s, (46, 150, 152),
                        [(9, cy - 8), (13, cy - 1), (13, cy + 3), (5, cy + 3), (5, cy - 1)])
    pygame.draw.polygon(s, (92, 226, 214),
                        [(9, cy - 7), (12, cy - 1), (12, cy + 3), (6, cy + 3), (6, cy - 1)])
    pygame.draw.polygon(s, (170, 252, 240),
                        [(9, cy - 5), (11, cy), (11, cy + 2), (7, cy + 2), (7, cy)])
    _px(s, 9, cy - 3, (240, 255, 252))
    # trailing wisps
    for i, (dx, dy) in enumerate(((-3, 3), (3, 3), (0, 5))):
        a = 200 - i * 50
        _px(s, 9 + dx, cy + dy + breathe, (120, 230, 220))
    _cache[key] = s
    return s

def palm(variant=0):
    """A coconut palm: it leans, it varies, some carry fruit."""
    key = ("palm", variant)
    if key in _cache:
        return _cache[key]
    rnd = _rnd(variant, 5)
    s = _new(38, 60)
    lean = rnd.choice((-1.0, -0.6, -0.25, 0.3, 0.7, 1.0))
    height = rnd.choice((22, 25, 28, 31))
    base_x = 17 + rnd.randrange(-2, 3)
    top_x = base_x + int(lean * rnd.choice((6, 9, 12)))
    pts = []
    for i in range(height):
        f = i / float(height - 1)
        x = int(base_x + (top_x - base_x) * (f ** 1.7))
        pts.append((x, 56 - i))
    for i, (x, y) in enumerate(pts):
        c = WOOD[2] if i % 4 else WOOD[1]
        _rect(s, x, y, x + 2, y, c)
        _px(s, x, y, WOOD[3])
        _px(s, x + 2, y, WOOD[0])
    cx, cy = pts[-1][0] + 1, 56 - height
    # the crown: a blob of fronds, shaped differently each time
    spread = rnd.choice((9, 10, 12))
    pygame.draw.ellipse(s, LEAF[1], pygame.Rect(cx - spread, cy - 6, spread * 2, 12))
    pygame.draw.ellipse(s, LEAF[2], pygame.Rect(cx - spread + 3, cy - 4,
                                                spread * 2 - 6, 8))
    pygame.draw.ellipse(s, LEAF[3], pygame.Rect(cx - 4, cy - 3, 8, 5))
    blades = rnd.choice((6, 7, 8))
    for k in range(blades):
        ang = -176 + k * (352 // blades)
        rad = math.radians(ang)
        ex = int(cx + math.cos(rad) * spread)
        ey = int(cy + math.sin(rad) * 6)
        col = LEAF[2] if k % 2 else LEAF[1]
        # each frond is a tapered blade, not a wire
        steps = max(abs(ex - cx), abs(ey - cy), 1)
        for t in range(steps + 1):
            fx = cx + (ex - cx) * t / steps
            fy = cy + (ey - cy) * t / steps
            wdt = 2 if t > steps * 0.5 else 1
            _rect(s, int(fx), int(fy), int(fx) + wdt, int(fy) + 1, col)
            if t > steps * 0.6:
                _px(s, int(fx), int(fy), LEAF[3])
    if rnd.random() < 0.45:                    # a cluster of coconuts
        for _ in range(rnd.randrange(2, 5)):
            _px(s, cx + rnd.randrange(-3, 4), cy + 2 + rnd.randrange(0, 3),
                (92, 68, 44))
    return _finish(key, s)


def tree(variant=0):
    """A broad-leafed valley tree — the crown shape differs each time."""
    key = ("tree", variant)
    if key in _cache:
        return _cache[key]
    rnd = _rnd(variant, 9)
    s = _new(50, 56)
    bx = 24 + rnd.randrange(-2, 3)
    lean = rnd.choice((-3, -1, 0, 1, 3))
    top = 34 + rnd.randrange(-2, 3)
    _rect(s, bx - 3, top, bx, 52, WOOD[2])
    _rect(s, bx - 1, top, bx + 1, 52, WOOD[1])
    _px(s, bx - 2, top + 8, WOOD[3])
    _px(s, bx, top + 16, WOOD[3])
    shape = rnd.choice(("round", "flat", "spire", "wide"))
    if shape == "round":
        blobs = ((0, 12, 11, 9), (-9, 18, 8, 7), (9, 17, 8, 7),
                 (-5, 8, 7, 6), (6, 7, 7, 6))
    elif shape == "flat":
        blobs = ((0, 14, 15, 7), (-11, 17, 8, 6), (11, 16, 8, 6),
                 (-7, 10, 6, 5), (7, 10, 6, 5))
    elif shape == "spire":
        blobs = ((0, 8, 7, 8), (-5, 15, 6, 6), (5, 14, 6, 6),
                 (-8, 20, 5, 5), (8, 19, 5, 5))
    else:
        blobs = ((0, 16, 13, 8), (-13, 20, 8, 6), (13, 19, 8, 6),
                 (-8, 10, 8, 6), (8, 9, 8, 6))
    shade = rnd.choice((LEAF, LEAF, LEAF_DARK))
    for dx, dy, rw, rh in blobs:
        cx, cy = bx + dx, 12 + dy
        pygame.draw.ellipse(s, LEAF_DARK[1],
                            pygame.Rect(cx - rw, cy - rh, rw * 2, rh * 2))
    for dx, dy, rw, rh in blobs:
        cx, cy = bx + dx, 12 + dy
        pygame.draw.ellipse(s, shade[1],
                            pygame.Rect(cx - rw + 1, cy - rh + 1, rw * 2 - 2, rh * 2 - 2))
    for dx, dy, rw, rh in blobs[:3]:
        cx, cy = bx + dx, 12 + dy
        pygame.draw.ellipse(s, shade[2],
                            pygame.Rect(cx - rw + 3, cy - rh + 3, rw - 1, rh - 1))
    for _ in range(rnd.randrange(2, 6)):
        _px(s, bx + rnd.randrange(-12, 13), rnd.randrange(6, 26), LEAF[3])
    return _finish(key, s)


def bush(variant=0):
    """A roadside bush — round, spiky, low or bushy."""
    key = ("bush", variant)
    if key in _cache:
        return _cache[key]
    rnd = _rnd(variant, 13)
    s = _new(22, 16)
    base = 11
    shape = rnd.choice(("round", "spiky", "wide", "small"))
    jx = rnd.randrange(-1, 2)
    jy = rnd.randrange(-1, 2)
    if shape == "round":
        pygame.draw.ellipse(s, LEAF_DARK[1],
                            pygame.Rect(3 + jx, 3 + jy, 16, 12))
        pygame.draw.ellipse(s, LEAF[1],
                            pygame.Rect(5 + jx, 4 + jy, 12, 9))
        pygame.draw.ellipse(s, LEAF[2],
                            pygame.Rect(7 + jx, 5 + jy, 7, 5))
    elif shape == "spiky":
        for k in range(6):
            x = 4 + k * 3
            _rect(s, x, 12 - k % 3, x + 1, 15, LEAF[1])
            _px(s, x, 11 - k % 3, LEAF[2])
    elif shape == "wide":
        pygame.draw.ellipse(s, LEAF_DARK[1],
                            pygame.Rect(1 + jx, 6 + jy, 20, 9))
        pygame.draw.ellipse(s, LEAF[1],
                            pygame.Rect(3 + jx, 7 + jy, 16, 6))
    else:
        pygame.draw.ellipse(s, LEAF_DARK[1], pygame.Rect(6, 7, 10, 8))
        pygame.draw.ellipse(s, LEAF[1], pygame.Rect(8, 8, 6, 5))
    if rnd.random() < 0.5:
        _px(s, base + rnd.randrange(-4, 5), 8 + rnd.randrange(-2, 3), BERRY[0])
    return _finish(key, s)


def flowers(variant=0):
    """A clump of wild flowers — the colour changes with the variant."""
    key = ("flowers", variant)
    if key in _cache:
        return _cache[key]
    rnd = _rnd(variant, 17)
    s = _new(18, 14)
    colour = PETAL[variant % len(PETAL)]
    for _ in range(rnd.randrange(3, 7)):
        x = rnd.randrange(2, 15)
        y = rnd.randrange(4, 12)
        _px(s, x, y, LEAF[1])
        _px(s, x, y - 1, colour)
        if rnd.random() < 0.4:
            _px(s, x + 1, y - 1, colour)
    return _finish(key, s)


def rock(variant=0):
    """A stone — every one a different shape."""
    key = ("rock", variant)
    if key in _cache:
        return _cache[key]
    rnd = _rnd(variant, 19)
    s = _new(20, 16)
    style = rnd.choice(("point", "flat", "slab", "pebble"))
    if style == "point":
        pygame.draw.polygon(s, STONE[1],
                            [(1, 15), (4, 5), (9, 2), (15, 7), (18, 15)])
        pygame.draw.polygon(s, STONE[2], [(4, 14), (6, 7), (9, 5), (12, 9), (10, 14)])
        pygame.draw.polygon(s, STONE[3], [(6, 7), (9, 5), (10, 7), (7, 9)])
    elif style == "flat":
        pygame.draw.polygon(s, STONE[1], [(1, 12), (3, 8), (10, 6), (18, 10), (17, 14)])
        pygame.draw.polygon(s, STONE[2], [(3, 12), (5, 9), (11, 8), (16, 11)])
        pygame.draw.polygon(s, STONE[3], [(5, 9), (11, 8), (12, 10)])
    elif style == "slab":
        pygame.draw.polygon(s, STONE[1], [(2, 15), (3, 4), (16, 3), (18, 15)])
        pygame.draw.polygon(s, STONE[2], [(4, 14), (5, 6), (15, 5), (16, 14)])
        pygame.draw.polygon(s, STONE[3], [(5, 6), (15, 5), (13, 7), (7, 8)])
    else:
        pygame.draw.ellipse(s, STONE[1], pygame.Rect(2, 7, 16, 8))
        pygame.draw.ellipse(s, STONE[2], pygame.Rect(4, 8, 11, 5))
        pygame.draw.ellipse(s, STONE[3], pygame.Rect(6, 9, 5, 2))
    # weathering: no two stones are the same stone
    for _ in range(rnd.randrange(2, 6)):
        _px(s, rnd.randrange(0, 18), rnd.randrange(0, 15),
            STONE[rnd.randrange(0, 4)])
    return _finish(key, s)


def bigrock(variant=0):
    """A house-sized mossy boulder."""
    key = ("bigrock", variant)
    if key in _cache:
        return _cache[key]
    rnd = _rnd(variant, 23)
    s = _new(40, 34)
    lean = rnd.choice((0, -3, 3))
    pygame.draw.polygon(s, STONE[1],
                        [(2, 33), (6, 12 + lean), (16, 4), (30, 9),
                         (38, 33)])
    pygame.draw.polygon(s, STONE[2],
                        [(5, 32), (9, 14 + lean), (17, 8), (28, 12), (33, 32)])
    pygame.draw.polygon(s, STONE[3],
                        [(9, 14 + lean), (17, 8), (21, 11), (13, 16)])
    for _ in range(rnd.randrange(3, 8)):
        _px(s, rnd.randrange(6, 34), rnd.randrange(20, 32), (108, 132, 96))
    return _finish(key, s)


def hut(lit=False, variant=0):
    """A wooden house on stilts — roof pitch, colour and door vary."""
    key = ("hut", lit, variant)
    if key in _cache:
        return _cache[key]
    rnd = _rnd(variant, 29)
    s = _new(40, 40)
    base = 5 + rnd.randrange(-1, 3)
    wall = rnd.choice(((186, 150, 104), (166, 132, 92), (198, 168, 120),
                       (150, 118, 84)))
    roof = rnd.choice(((188, 104, 72), (150, 92, 66), (206, 128, 78)))
    pitch = rnd.choice((6, 8, 10))
    width = rnd.choice((18, 20, 22))
    # stilts
    for x in (base + 2, base + width - 4):
        _rect(s, x, 26, x + 1, 38, WOOD[1])
    # the walls
    _rect(s, base, 20, base + width, 27, wall)
    _rect(s, base, 20, base + width, 21, (wall[0] - 18, wall[1] - 16, wall[2] - 12))
    # the roof
    pygame.draw.polygon(s, roof, [(base - 2, 20), (base + width // 2, 20 - pitch),
                                   (base + width + 2, 20)])
    pygame.draw.polygon(s, (roof[0] - 20, roof[1] - 16, roof[2] - 12),
                        [(base + 1, 19), (base + width // 2, 20 - pitch + 1),
                         (base + width, 19)])
    # the door, and sometimes a window
    dx = base + rnd.randrange(3, max(4, width - 8))
    _rect(s, dx, 22, dx + 4, 27, (108, 78, 52))
    if rnd.random() < 0.6:
        wx = base + rnd.choice((1, width - 7))
        _rect(s, wx, 22, wx + 4, 24, (96, 120, 132))
    if lit:
        _rect(s, dx, 22, dx + 4, 24, (250, 210, 130))
    return _finish(key, s)


def banana(variant=0):
    """A banana clump."""
    key = ("banana", variant)
    if key in _cache:
        return _cache[key]
    rnd = _rnd(variant, 31)
    s = _new(24, 26)
    for k in range(rnd.randrange(3, 6)):
        x = 8 + k * 2
        top = 24 - rnd.randrange(8, 18)
        _rect(s, x, top, x + 1, 25, LEAF[1])
        _px(s, x, top - 1, LEAF[2])
        _px(s, x + 1, top + 1, LEAF_DARK[1])
    return _finish(key, s)


# ------------------------------------------------- region-specific props
def mangrove(variant=0):
    """A mangrove: stilt roots over mud, a dense green crown."""
    key = ("mangrove", variant)
    if key in _cache:
        return _cache[key]
    s = _new(30, 40)
    rnd = _rnd(variant, 61)
    base = 12 + rnd.randrange(-2, 4)
    roots = rnd.randrange(4, 8)
    spread = rnd.choice((3, 4, 5))
    # the stilt roots: the whole point of a mangrove
    for i in range(roots):
        x = base + int((i - roots / 2.0) * spread) + rnd.randrange(-1, 2)
        root = WOOD[0] if i % 2 else WOOD[1]
        _rect(s, x, 26, x + 1, 39, root)
        _px(s, x, 39, WOOD[0])
        _px(s, x + 1, 30, WOOD[2])
    # trunk
    _rect(s, base + 1, 12, base + 3, 28, WOOD[2])
    _rect(s, base + 1, 12, base + 2, 28, WOOD[3])
    # crown
    cw = rnd.choice((17, 19, 21))
    pygame.draw.ellipse(s, LEAF_DARK[1], pygame.Rect(base - cw // 2, 4, cw, 13))
    pygame.draw.ellipse(s, LEAF[1], pygame.Rect(base - cw // 2 + 2, 6, cw - 4, 9))
    pygame.draw.ellipse(s, LEAF[2], pygame.Rect(base - 4, 7, 8, 5))
    for _ in range(6):
        _px(s, base + rnd.randrange(-6, 8), 6 + rnd.randrange(0, 8), LEAF[3])
    for _ in range(rnd.randrange(2, 6)):                    # leaf litter
        _px(s, base + rnd.randrange(-8, 9), rnd.randrange(8, 20), LEAF[2])
    return _finish(key, s)


def rubber(variant=0):
    """A rubber tree: straight pale trunk, high flat crown."""
    key = ("rubber", variant)
    if key in _cache:
        return _cache[key]
    s = _new(26, 46)
    rnd = _rnd(variant, 67)
    base = 11 + rnd.randrange(-1, 3)
    top = rnd.choice((10, 12, 14))
    _rect(s, base, top, base + 2, 45, WOOD[3])
    _rect(s, base + 2, top, base + 3, 45, WOOD[1])
    for y in range(top + 2, 44, rnd.choice((4, 5, 6))):   # the tapping scars
        _px(s, base, y, WOOD[0])
        _px(s, base + 3, y, WOOD[0])
    cw = rnd.choice((17, 19, 21))
    pygame.draw.ellipse(s, LEAF_DARK[1], pygame.Rect(base - cw // 2, top - 8, cw, 11))
    pygame.draw.ellipse(s, LEAF[1], pygame.Rect(base - cw // 2 + 2, top - 7, cw - 4, 8))
    pygame.draw.ellipse(s, LEAF[2], pygame.Rect(base - 4, top - 6, 9, 5))
    for _ in range(rnd.randrange(2, 6)):
        _px(s, base + rnd.randrange(-cw // 2, cw // 2),
            top + rnd.randrange(-6, 4), LEAF[3])
    return _finish(key, s)


def spirit_house(variant=0):
    """A pha: the little house on a post that holds the guardian."""
    key = ("spirit_house", variant)
    if key in _cache:
        return _cache[key]
    s = _new(20, 34)
    rnd = _rnd(variant, 73)
    base = 7 + rnd.randrange(-1, 3)
    roof_col = rnd.choice(((188, 104, 72), (150, 92, 66), (206, 150, 78),
                           (120, 96, 84)))
    _rect(s, base + 1, 16, base + 3, 33, WOOD[2])          # the post
    _rect(s, base, 8, base + 8, 17, (188, 176, 150))      # the house
    _rect(s, base, 8, base + 8, 10, GOLD[2])               # the gold trim
    pygame.draw.polygon(s, roof_col, [(base - 2, 8), (base + 4, 2),
                                      (base + 10, 8)])
    pygame.draw.polygon(s, (min(255, roof_col[0] + 18),
                            min(255, roof_col[1] + 14),
                            min(255, roof_col[2] + 10)),
                        [(base - 1, 8), (base + 4, 3), (base + 9, 8)])
    _rect(s, base + 3, 12, base + 5, 16, (96, 84, 72))     # the door
    _px(s, base + 4, 11, GOLD[3])
    for _ in range(rnd.randrange(1, 4)):                    # age and moss
        _px(s, rnd.randrange(base, base + 8), rnd.randrange(9, 17),
            (120, 140, 104))
    return _finish(key, s)


def shophouse(variant=0):
    """A Sino-Portuguese shophouse: two storeys, shuttered windows."""
    key = ("shophouse", variant)
    if key in _cache:
        return _cache[key]
    s = _new(30, 40)
    rnd = _rnd(variant, 71)
    base = 3 + rnd.randrange(-1, 3)
    wall = rnd.choice(((222, 206, 186), (206, 186, 168), (196, 206, 200),
                       (226, 196, 176), (186, 200, 186)))
    _rect(s, base, 10, base + 23, 39, wall)
    _rect(s, base, 10, base + 23, 12, (186, 166, 146))
    _rect(s, base, 20, base + 23, 22, (186, 166, 146))
    _rect(s, base + 9, 26, base + 14, 39, (140, 110, 84))   # the door
    shutter = rnd.choice(((118, 96, 78), (86, 96, 110), (140, 90, 76)))
    for wx in (base + 2, base + 16):                        # shuttered windows
        _rect(s, wx, 13, wx + 5, 18, shutter)
        _rect(s, wx, 15, wx + 5, 16, (shutter[0] - 30, shutter[1] - 26, shutter[2] - 20))
    _rect(s, base, 8, base + 23, 10, (168, 84, 72))        # tiled eave
    for i in range(0, 24, 4):
        _px(s, base + i, 9, (140, 66, 58))
    # weathering, so no two houses are quite alike
    for _ in range(rnd.randrange(2, 6)):
        _px(s, rnd.randrange(base, base + 23), rnd.randrange(11, 38),
            (rnd.choice(((150, 130, 110), (210, 196, 176), (120, 110, 100)))))
    return _finish(key, s)


def fern(variant=0):
    """A jungle fern: a fan of fronds."""
    key = ("fern", variant)
    if key in _cache:
        return _cache[key]
    s = _new(20, 18)
    rnd = _rnd(variant, 79)
    base = 10 + rnd.randrange(-1, 3)
    fronds = rnd.randrange(4, 8)
    for i in range(fronds):
        ang = -1.2 + i * (2.4 / max(1, fronds - 1))
        dx = int(9 * math.cos(ang))
        dy = int(7 * math.sin(ang))
        col = LEAF[2] if i % 2 else LEAF[1]
        for t in range(1, 8):
            _px(s, base + dx * t // 8, 16 + dy * t // 8, col)
    _px(s, base, 16, LEAF_DARK[1])
    _px(s, base - 1, 15, LEAF_DARK[0])
    _px(s, base + 1, 15, LEAF_DARK[0])
    for _ in range(rnd.randrange(1, 5)):
        _px(s, base + rnd.randrange(-6, 7), rnd.randrange(8, 17), LEAF[1])
    return _finish(key, s)


def stilt(variant=0):
    """A stilt house over the mud: legs, deck, thatched roof."""
    key = ("stilt", variant)
    if key in _cache:
        return _cache[key]
    s = _new(26, 32)
    base = 4 + variant
    for x in (base + 2, base + 9, base + 17):
        _rect(s, x, 20, x + 1, 31, WOOD[1])
    _rect(s, base, 12, base + 21, 20, WOOD[3])          # the deck
    _rect(s, base + 2, 6, base + 18, 12, (196, 176, 132))   # the wall
    pygame.draw.polygon(s, (150, 122, 78),
                        [(base - 1, 6), (base + 10, 0), (base + 21, 6)])
    pygame.draw.polygon(s, (176, 146, 96),
                        [(base + 1, 5), (base + 10, 1), (base + 19, 5)])
    _rect(s, base + 8, 8, base + 12, 12, (120, 96, 72))
    return _finish(key, s)

# ------------------------------------------------------- the heritage
def wat(variant=0):
    """A wat: tiered roof, gold finial, a chedi beside the hall."""
    key = ("wat", variant)
    if key in _cache:
        return _cache[key]
    s = _new(46, 48)
    base = 6 + variant * 2
    # the hall
    _rect(s, base, 20, base + 27, 44, (226, 214, 190))
    _rect(s, base, 20, base + 27, 22, (196, 180, 156))
    _rect(s, base + 10, 30, base + 17, 44, (150, 118, 88))    # the door
    for i in range(3):                                          # tiered roof
        w = 30 - i * 4
        y = 20 - i * 4
        _rect(s, base + 13 - w // 2, y - 3, base + 13 + w // 2, y, ROOF[3 - i % 3])
        _rect(s, base + 13 - w // 2 + 1, y - 4, base + 13 + w // 2 - 1, y - 3,
              ROOF[2 - i % 2])
    _rect(s, base + 12, 6, base + 14, 12, GOLD[1])              # the finial
    _px(s, base + 13, 4, GOLD[3])
    _px(s, base + 11, 8, GOLD[2])
    _px(s, base + 15, 8, GOLD[2])
    # a chedi standing beside the hall
    cx = base + 30
    _rect(s, cx - 5, 36, cx + 5, 45, STUCCO[1])
    _rect(s, cx - 4, 30, cx + 4, 36, STUCCO[2])
    pygame.draw.ellipse(s, GOLD[1], pygame.Rect(cx - 4, 24, 9, 8))
    _rect(s, cx - 1, 19, cx + 1, 24, GOLD[2])
    _px(s, cx, 18, GOLD[3])
    return _finish(key, s)


def buddha(variant=0):
    """A seated Buddha under a naga hood, on a plinth."""
    key = ("buddha", variant)
    if key in _cache:
        return _cache[key]
    s = _new(26, 34)
    base = 10 + variant
    _rect(s, base - 5, 27, base + 5, 33, STUCCO[1])      # the plinth
    _rect(s, base - 4, 27, base + 4, 28, STUCCO[3])
    # the body: seated, robe over one shoulder
    pygame.draw.ellipse(s, GOLD[1], pygame.Rect(base - 4, 16, 9, 12))
    pygame.draw.ellipse(s, GOLD[2], pygame.Rect(base - 3, 15, 7, 8))
    pygame.draw.ellipse(s, (226, 190, 140), pygame.Rect(base - 3, 8, 7, 8))
    _px(s, base - 1, 11, (90, 70, 50))                   # the eyes
    _px(s, base + 1, 11, (90, 70, 50))
    _px(s, base, 9, (214, 168, 78))                     # the urna
    # the naga hood behind the head
    for i in range(7):
        pygame.draw.arc(s, (150, 118, 78),
                        pygame.Rect(base - 6 + i, 6 - i // 2, 14, 12), 0.2, 2.9, 2)
    _px(s, base - 6, 18, GOLD[2])
    _px(s, base + 6, 18, GOLD[2])
    return _finish(key, s)


def ruin(variant=0):
    """A Srivijaya brick ruin: a broken wall and a fallen doorframe."""
    key = ("ruin", variant)
    if key in _cache:
        return _cache[key]
    s = _new(34, 30)
    base = 3 + variant
    brick = (168, 96, 74)
    _rect(s, base, 12, base + 11, 28, brick)
    _rect(s, base, 12, base + 11, 13, (196, 124, 96))
    for y in range(14, 28, 3):                          # the courses
        _rect(s, base, y, base + 11, y, (146, 80, 62))
    _rect(s, base + 12, 18, base + 22, 28, brick)       # the broken half
    _rect(s, base + 12, 18, base + 22, 19, (196, 124, 96))
    for y in range(20, 28, 3):
        _rect(s, base + 12, y, base + 22, y, (146, 80, 62))
    _rect(s, base + 4, 8, base + 8, 12, (150, 84, 64))  # the fallen lintel
    _px(s, base + 2, 26, (120, 150, 110))               # moss
    _px(s, base + 19, 26, (120, 150, 110))
    _px(s, base + 6, 27, (108, 140, 100))
    return _finish(key, s)


def puppet_stage(variant=0):
    """A Nang Talung shadow-puppet stage: a lamp behind a white sheet."""
    key = ("puppet_stage", variant)
    if key in _cache:
        return _cache[key]
    s = _new(30, 30)
    base = 3 + variant
    for x in (base, base + 21):                        # the frame posts
        _rect(s, x, 6, x + 1, 28, WOOD[1])
    _rect(s, base, 4, base + 22, 6, WOOD[2])           # the top beam
    _rect(s, base + 1, 7, base + 20, 25, (238, 232, 216))   # the white sheet
    _rect(s, base + 1, 7, base + 20, 8, (214, 206, 190))
    pygame.draw.circle(s, (250, 214, 140), (base + 10, 17), 3)   # the lamp
    # the puppets' shadows on the sheet
    for i, (dx, dy) in enumerate(((3, 5), (9, 7), (14, 4))):
        pygame.draw.circle(s, (150, 130, 120), (base + 4 + dx, 18 - dy), 2)
    _rect(s, base + 3, 26, base + 18, 28, WOOD[2])     # the bench
    return _finish(key, s)


def carving(variant=0):
    """A rock relief: a Srivijaya carving worn by the weather."""
    key = ("carving", variant)
    if key in _cache:
        return _cache[key]
    s = _new(30, 24)
    base = 2 + variant
    _rect(s, base, 4, base + 25, 22, STONE[2])
    _rect(s, base, 4, base + 25, 5, STONE[3])
    _rect(s, base, 4, base + 1, 22, STONE[3])
    # a seated figure and a naga, worn nearly flat
    pygame.draw.arc(s, STONE[1], pygame.Rect(base + 5, 8, 10, 11), 0.3, 2.8, 1)
    pygame.draw.arc(s, STONE[1], pygame.Rect(base + 14, 6, 9, 14), 0.4, 2.7, 1)
    for i in range(6):
        _px(s, base + 4 + i * 3, 19, STONE[1])
    _px(s, base + 8, 6, (128, 150, 120))                # moss in the groove
    return _finish(key, s)


def kiln(variant=0):
    """An old tin smelter: a stone chimney and a collapsed furnace."""
    key = ("kiln", variant)
    if key in _cache:
        return _cache[key]
    s = _new(30, 36)
    base = 5 + variant
    _rect(s, base + 6, 6, base + 13, 34, STONE[1])       # the flue
    _rect(s, base + 6, 6, base + 8, 34, STONE[3])
    for y in range(8, 34, 4):
        _rect(s, base + 6, y, base + 13, y, STONE[0])
    _rect(s, base, 26, base + 24, 34, STONE[2])          # the furnace base
    _rect(s, base + 3, 28, base + 12, 33, (40, 34, 32))  # the cold mouth
    _px(s, base + 20, 30, (150, 84, 62))                # rust
    _px(s, base + 21, 31, (150, 84, 62))
    return _finish(key, s)


def market_stall(variant=0):
    """A market stall: a striped awning over a table of produce."""
    key = ("market_stall", variant)
    if key in _cache:
        return _cache[key]
    rnd = _rnd(variant, 83)
    s = _new(26, 24)
    base = 3 + rnd.randrange(-1, 3)
    awning = rnd.choice(((196, 78, 68), (70, 110, 160), (214, 176, 76),
                         (110, 150, 96)))
    for x in range(base, base + 20):
        _px(s, x, 8, awning if (x // 2) % 2 else (240, 236, 220))
    _px(s, base, 7, (80, 70, 60))
    _px(s, base + 19, 7, (80, 70, 60))
    _rect(s, base + 1, 8, base + 2, 23, WOOD[1])        # the legs
    _rect(s, base + 17, 8, base + 18, 23, WOOD[1])
    _rect(s, base, 17, base + 19, 19, WOOD[3])          # the table
    for _ in range(rnd.randrange(3, 7)):                # the produce
        x = base + 2 + rnd.randrange(0, 15)
        _px(s, x, 16, rnd.choice(BERRY))
        _px(s, x, 15, rnd.choice(BERRY))
    return _finish(key, s)


def windmill(variant=0):
    """A water pump: a bamboo frame with a small wheel."""
    key = ("windmill", variant)
    if key in _cache:
        return _cache[key]
    rnd = _rnd(variant, 89)
    s = _new(22, 30)
    base = 9 + rnd.randrange(-1, 3)
    _rect(s, base, 14, base + 1, 29, WOOD[2])
    _rect(s, base + 4, 18, base + 5, 29, WOOD[2])
    _rect(s, base - 1, 13, base + 7, 14, WOOD[3])
    cx, cy = base + 3, 10
    pygame.draw.circle(s, WOOD[1], (cx, cy), 6)
    pygame.draw.circle(s, WOOD[3], (cx, cy), 4)
    pygame.draw.circle(s, WOOD[0], (cx, cy), 1)
    for k in range(4):
        a = k * 1.57 + rnd.random()
        _px(s, int(cx + 5 * math.cos(a)), int(cy + 5 * math.sin(a)), WOOD[3])
    return _finish(key, s)
