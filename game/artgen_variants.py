"""Replacement prop art with real shape variety.

Every prop gets a family of distinct shapes instead of a near-copy: a
palm leans left or right, is tall or stunted, carries coconuts or does
not; a tree has a round crown, a flat one or a spire; a hut has a
different roof pitch, wall colour and door side.

The variant is chosen per cell from the cell's own hash, so the same
prop never clumps together in one place.
"""

import math
import random

from . import palette as P

ramp = P.ramp

LEAF = ramp((54, 122, 66), 5)
LEAF_DARK = ramp((36, 88, 52), 4)
WOOD = ramp((150, 104, 62), 5)
THATCH = ramp((178, 134, 78), 5)
ROOF = ramp((188, 104, 72), 5)
STONE = ramp((124, 128, 136), 5)
GOLD = ramp((214, 168, 78), 4)
STUCCO = ramp((206, 194, 166), 5)
BERRY = [(196, 70, 62), (224, 96, 80), (208, 84, 96), (236, 120, 72),
         (188, 76, 104), (226, 142, 78)]
PETAL = [(236, 112, 128), (244, 196, 96), (236, 236, 240), (216, 150, 214),
         (246, 156, 84)]


def _rnd(variant, salt=0):
    return random.Random(1000 + variant * 37 + salt)


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
        _rect(s, cx, cy, ex, ey, col)
        _px(s, ex, ey, LEAF[3])
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
    if shape == "round":
        pygame.draw.ellipse(s, LEAF_DARK[1], pygame.Rect(3, 3, 16, 12))
        pygame.draw.ellipse(s, LEAF[1], pygame.Rect(5, 4, 12, 9))
        pygame.draw.ellipse(s, LEAF[2], pygame.Rect(7, 5, 7, 5))
    elif shape == "spiky":
        for k in range(6):
            x = 4 + k * 3
            _rect(s, x, 12 - k % 3, x + 1, 15, LEAF[1])
            _px(s, x, 11 - k % 3, LEAF[2])
    elif shape == "wide":
        pygame.draw.ellipse(s, LEAF_DARK[1], pygame.Rect(1, 6, 20, 9))
        pygame.draw.ellipse(s, LEAF[1], pygame.Rect(3, 7, 16, 6))
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
