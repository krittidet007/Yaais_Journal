"""16x16 tile engine in the style of top-down SNES overworlds (LttP look).

Terrain types live on a coarse grid; each type is rendered lowest-priority
first so higher terrain (stone, water) carves into lower terrain (grass,
dirt). Every cell then gets a **blob edge mask** from its 8 neighbours and
applies the classic 1px dark rim + overhang detail at terrain transitions —
the thing that makes grass-to-dirt and water shores read as crisp, drawn
tiles instead of soft noise.

Autotile rule (Red Blob Games / Tiled blob): a diagonal neighbour only
matters if both adjacent cardinal neighbours are also of a higher type.
"""

import math
import random

import pygame

from . import artgen as A

# Palettes (SNES 15-bit approximations from ALttP parsing, 24-bit form).
GRASS = [(120, 184, 74), (78, 152, 56), (62, 120, 40), (51, 112, 31), (152, 208, 96)]
DIRT = [(200, 160, 90), (176, 136, 64), (154, 120, 64), (138, 106, 56), (216, 184, 120)]
SAND = [(230, 206, 140), (212, 184, 118), (186, 158, 100), (240, 224, 160)]
STONE = [(154, 160, 168), (110, 116, 124), (90, 96, 104), (198, 204, 210)]
WATER = [(52, 108, 196), (38, 84, 168), (82, 160, 236), (234, 246, 255), (24, 60, 132)]
CANOPY = [(78, 152, 56), (44, 100, 32), (28, 66, 20), (152, 208, 96)]
LIGHT_WARM = (255, 244, 214)
OUTLINE = (32, 24, 16)

PRIORITY = {"G": 0, "D": 1, "A": 2, "S": 3, "W": 4, "H": 5,
            "T": 2, "U": 3, "R": 1, "P": 2, "E": 2, "F": 1}

# how high each raised tile stands, in pixels
HEIGHTS = {"T": 4, "U": 9, "R": 2}
TILE = 16

_cache = {}


def _cached(key, build):
    if key not in _cache:
        _cache[key] = build()
    return _cache[key]


class TileMap:
    def __init__(self, cols, rows, fill="G"):
        self.cols = cols
        self.rows = rows
        self.grid = [[fill] * cols for _ in range(rows)]

    def _inside(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def cell(self, r, c):
        return self.grid[r][c] if self._inside(r, c) else None

    def rect(self, r0, r1, c0, c1, kind):
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if self._inside(r, c):
                    self.grid[r][c] = kind

    def line(self, c0, r0, c1, r1, kind, width=1):
        """Rough Bresenham corridor of the given width."""
        dc = abs(c1 - c0)
        dr = -abs(r1 - r0)
        sc = 1 if c0 < c1 else -1
        sr = 1 if r0 < r1 else -1
        err = dc + dr
        c, r = c0, r0
        while True:
            self.rect(r - width // 2, r + width // 2, c - width // 2, c + width // 2, kind)
            if c == c1 and r == r1:
                break
            e2 = 2 * err
            if e2 >= dr:
                err += dr
                c += sc
            if e2 <= dc:
                err += dc
                r += sr


# ------------------------------------------------------------------ masks
def mask_of(tm, r, c):
    """Return (side_mask, corners) blob bits for a land cell.

    side_mask: N=1 E=2 S=4 W=8. corners: (NE, SE, SW, NW) — a diagonal only
    counts if both adjacent cardinals AND the diagonal are higher type.

    The answer never changes, so it is remembered per cell: the camera
    asks for the same tiles every frame and recomputing eight neighbour
    lookups each time was costing half the frame budget.
    """
    cache = tm.__dict__.get("_mask_cache")
    if cache is None:
        cache = {}
        tm.__dict__["_mask_cache"] = cache
    key = (r, c)
    hit = cache.get(key)
    if hit is not None:
        return hit[0], hit[1]
    me = tm.cell(r, c)
    pr = PRIORITY[me]

    def higher(dr, dc):
        other = tm.cell(r + dr, c + dc)
        return other is not None and PRIORITY[other] > pr

    n, e, s, w = higher(-1, 0), higher(0, 1), higher(1, 0), higher(0, -1)
    ne, se, sw, nw = (higher(-1, 1), higher(1, 1), higher(1, -1), higher(-1, -1))
    corners = (e and s and se, s and w and sw, w and n and nw, n and e and ne)
    mask = (1 if n else 0) | (2 if e else 0) | (4 if s else 0) | (8 if w else 0)
    out = (mask, corners)
    cache[key] = (mask, corners, (tm.cell(r - 1, c), tm.cell(r, c + 1),
                                  tm.cell(r + 1, c), tm.cell(r, c - 1)))
    return out


def neighbours_of(tm, r, c):
    """The four neighbours' materials (N, E, S, W), remembered per cell."""
    cache = tm.__dict__.get("_mask_cache")
    if cache is None:
        cache = {}
        tm.__dict__["_mask_cache"] = cache
    key = (r, c)
    hit = cache.get(key)
    if hit is not None and len(hit) == 3:
        return hit[2]
    n = tm.cell(r - 1, c)
    e = tm.cell(r, c + 1)
    s = tm.cell(r + 1, c)
    w = tm.cell(r, c - 1)
    kinds = (n, e, s, w)
    if hit is None:
        # keep mask + corners in step with the neighbour cache
        mask, corners = mask_of(tm, r, c)
        cache[key] = (mask, corners, kinds)
    else:
        cache[key] = (hit[0], hit[1], kinds)
    return kinds


def water_mask_of(tm, r, c):
    """Water cells foam wherever any non-water neighbour touches them."""
    mask = 0
    if tm.cell(r - 1, c) not in (None, "W"):
        mask |= 1
    if tm.cell(r, c + 1) not in (None, "W"):
        mask |= 2
    if tm.cell(r + 1, c) not in (None, "W"):
        mask |= 4
    if tm.cell(r, c - 1) not in (None, "W"):
        mask |= 8
    return mask


def _px(surface, x, y, color):
    if 0 <= x < 16 and 0 <= y < 16:
        surface.set_at((x, y), color)


def _rim(surface, mask, corners, dark, overhang=None):
    """1px dark rim where the cell borders higher terrain + corner niceties."""
    n = mask & 1
    e = mask & 2
    s = mask & 4
    w = mask & 8
    ne, se, sw, nw = corners

    if n:
        for x in range(16):
            _px(surface, x, 0, dark)
        for x in range(0, 16, 4):
            _px(surface, x, 1, dark)
    if s:
        for x in range(16):
            _px(surface, x, 15, dark)
        for x in range(0, 16, 4):
            _px(surface, x, 14, dark)
    if w:
        for y in range(16):
            _px(surface, 0, y, dark)
        for y in range(0, 16, 4):
            _px(surface, 1, y, dark)
    if e:
        for y in range(16):
            _px(surface, 15, y, dark)
        for y in range(0, 16, 4):
            _px(surface, 14, y, dark)

    # inner (concave) corners — higher terrain wraps my corner
    if n and w and not nw:
        for pt in ((0, 0), (1, 0), (0, 1)):
            _px(surface, *pt, dark)
    if n and e and not ne:
        for pt in ((15, 0), (14, 0), (15, 1)):
            _px(surface, *pt, dark)
    if s and w and not sw:
        for pt in ((0, 15), (0, 14), (1, 15)):
            _px(surface, *pt, dark)
    if s and e and not se:
        for pt in ((15, 15), (14, 15), (15, 14)):
            _px(surface, *pt, dark)

    if overhang:
        light, count, seed = overhang
        rnd = random.Random(seed)
        picks = []
        if n:
            picks += [(rnd.randrange(0, 16), 0) for _ in range(count)]
        if s:
            picks += [(rnd.randrange(0, 16), 15) for _ in range(count)]
        if w:
            picks += [(0, rnd.randrange(0, 16)) for _ in range(count)]
        if e:
            picks += [(15, rnd.randrange(0, 16)) for _ in range(count)]
        for x, y in picks:
            _px(surface, x, y, light)


def _foam(surface, mask, seed):
    """2px foam band on the water side of a land edge."""
    n, e, s, w = mask & 1, mask & 2, mask & 4, mask & 8
    rnd = random.Random(seed)
    foam, shal = WATER[3], WATER[2]
    if n:
        for x in range(16):
            _px(surface, x, 0, foam)
            _px(surface, x, 1, shal if (x + seed) % 3 else foam)
    if s:
        for x in range(16):
            _px(surface, x, 15, foam)
            _px(surface, x, 14, shal)
    if w:
        for y in range(16):
            _px(surface, 0, y, foam)
            _px(surface, 1, y, shal)
    if e:
        for y in range(16):
            _px(surface, 15, y, foam)
            _px(surface, 14, y, shal)
    for _ in range(max(0, 4 - (n + e + s + w) * 2)):   # interior sparkles
        _px(surface, rnd.randrange(0, 16), rnd.randrange(0, 16), foam)
    if n and w:
        _px(surface, 0, 0, foam)
    if n and e:
        _px(surface, 15, 0, foam)
    if s and w:
        _px(surface, 0, 15, foam)
    if s and e:
        _px(surface, 15, 15, foam)


# ------------------------------------------------------------- tile bodies
def _seed(r, c, salt):
    return int(A._rng(r, c, salt) * 1000000)


def _hash_cell(r, c):
    return _seed(r, c, 3)


def _make_grass(r, c):
    s = pygame.Surface((TILE, TILE))
    s.fill(GRASS[0])
    rnd = random.Random(_hash_cell(r, c) + 7)
    for _ in range(6):                        # calm tuft clusters
        x, y = rnd.randrange(1, 14), rnd.randrange(1, 14)
        _px(s, x, y, GRASS[1])
        if rnd.random() < 0.6:
            _px(s, x + 1, y, GRASS[1])
        if rnd.random() < 0.35:
            _px(s, x, y + 1, GRASS[2])
    for _ in range(4):                        # light blades
        x, y = rnd.randrange(1, 15), rnd.randrange(1, 15)
        _px(s, x, y, GRASS[4])
        _px(s, x, y + 1, GRASS[1])
    if rnd.random() < 0.12:                   # flowers sit on grass
        x = rnd.randrange(2, 14)
        _px(s, x, 13, GRASS[1])
        _px(s, x, 12, LIGHT_WARM if rnd.random() < 0.5 else (232, 140, 170))
    return s


def _make_dirt(r, c):
    s = pygame.Surface((TILE, TILE))
    s.fill(DIRT[0])
    rnd = random.Random(_hash_cell(r, c) + 11)
    for _ in range(7):
        x, y = rnd.randrange(0, 16), rnd.randrange(0, 16)
        _px(s, x, y, DIRT[1])
    for _ in range(5):
        x, y = rnd.randrange(0, 16), rnd.randrange(0, 16)
        _px(s, x, y, DIRT[4])
        if rnd.random() < 0.5:
            _px(s, x, (y + 1) % 16, DIRT[1])
    for _ in range(2):
        x, y = rnd.randrange(1, 15), rnd.randrange(1, 15)
        _px(s, x, y, DIRT[2])
        _px(s, x + 1, y, DIRT[2])
    return s


def _make_sand(r, c):
    s = pygame.Surface((TILE, TILE))
    s.fill(SAND[0])
    rnd = random.Random(_hash_cell(r, c) + 15)
    for _ in range(8):
        x, y = rnd.randrange(0, 16), rnd.randrange(0, 16)
        _px(s, x, y, SAND[1])
    for _ in range(5):
        x, y = rnd.randrange(0, 16), rnd.randrange(0, 16)
        _px(s, x, y, SAND[3])
    for _ in range(3):                        # dry grass stalks
        x = rnd.randrange(1, 15)
        _px(s, x, 14, (208, 218, 140))
        _px(s, x, 13, (188, 196, 120))
    return s


def _make_stone(r, c):
    # limestone is pale: the karst of Phang Nga is white rock in the sun
    s = pygame.Surface((TILE, TILE))
    s.fill(STONE[2])
    rnd = random.Random(_hash_cell(r, c) + 13)
    for i in (3, 7, 11):                      # grout seams, slightly off-line
        yoff = rnd.randrange(-1, 2)
        for x in range(16):
            _px(s, x, (i + yoff) % 16, STONE[1])
    for i in (3, 7, 11):
        xoff = rnd.randrange(-1, 2)
        for y in range(16):
            _px(s, (i + xoff) % 16, y, STONE[1])
    for _ in range(10):                       # sunlit faces of the rock
        _px(s, rnd.randrange(0, 16), rnd.randrange(0, 16), STONE[3])
    for _ in range(6):
        _px(s, rnd.randrange(0, 16), rnd.randrange(0, 16), STONE[3])
    for _ in range(3):
        x, y = rnd.randrange(0, 14), rnd.randrange(0, 14)
        _px(s, x, y, STONE[2])
        _px(s, x + 1, y, STONE[2])
    return s


def _make_water(phase, r, c):
    s = pygame.Surface((TILE, TILE))
    s.fill(WATER[0])
    rnd = random.Random(_hash_cell(r, c) + 17)
    for _ in range(3):                        # deep patches
        x, y = rnd.randrange(0, 15), rnd.randrange(0, 16)
        _px(s, x, y, WATER[1])
        _px(s, x + 1, y, WATER[1])
    # two wave trains, half a cycle apart, so the water never pulses
    for x in range(16):
        y = int(6 + math.sin(x * 0.7 + phase * 1.5) * 2)
        _px(s, x, y, WATER[2])
        y2 = int(11 + math.sin(x * 0.5 - phase * 1.1) * 2)
        _px(s, x, y2, WATER[1])
        _px(s, x, (y + 4) % 16, WATER[2] if (x + phase) % 3 else WATER[0])
    # sparkles toggle with the phase and sit on the crests
    for _ in range(3):
        x, y = rnd.randrange(1, 15), rnd.randrange(4, 12)
        if (x + y + phase) % 3 == 0:
            _px(s, x, y, WATER[3])
            _px(s, x + 1, y, WATER[3])
    return s


def _make_hedge(r, c, side_mask=0):
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    rnd = random.Random(_hash_cell(r, c) + 19)
    for x in range(16):
        hgt = 7 + rnd.randrange(0, 3) + int(math.sin(x * 1.7 + r) * 2)
        for y in range(hgt, 16):
            _px(s, x, y, CANOPY[1])
    # base contact shadow + side shading where the hedge meets other terrain
    for x in range(16):
        _px(s, x, 15, CANOPY[2])
    if side_mask & 8:
        for y in range(16):
            _px(s, 0, y, CANOPY[2])
    if side_mask & 2:
        for y in range(16):
            _px(s, 15, y, CANOPY[2])
    # silhouette: warm outline + highlight along the top of the canopy
    for x in range(16):
        top = 16
        for y in range(16):
            if s.get_at((x, y))[3] > 0:
                top = y
                break
        if top < 16:
            if top > 0:
                _px(s, x, top - 1, OUTLINE)
            _px(s, x, top, CANOPY[3] if rnd.random() < 0.45 else CANOPY[0])
    return s


# ----------------------------------------------------------------- render
def tile_for(kind, mask, corners, r, c, phase=0):
    key = (kind, mask, corners, r % 4, c % 4, phase)
    if key in _cache:
        return _cache[key]
    if kind == "G":
        s = _make_grass(r, c)
        _rim(s, mask, corners, GRASS[3], overhang=(GRASS[4], 3, _seed(r, c, 21)))
    elif kind == "D":
        s = _make_dirt(r, c)
        _rim(s, mask, corners, DIRT[3], overhang=(DIRT[4], 2, _seed(r, c, 23)))
    elif kind == "A":
        s = _make_sand(r, c)
        _rim(s, mask, corners, SAND[2], overhang=(SAND[3], 2, _seed(r, c, 25)))
    elif kind == "S":
        s = _make_stone(r, c)
        _rim(s, mask, corners, STONE[2])
    elif kind == "P":
        s = _make_plaza(r, c)
    elif kind == "F":
        s = _make_paddy(r, c)
    elif kind == "T":
        s = _make_terrace(r, c, 0)
    elif kind == "E":
        s = _make_terrace(r, c, 5)
    elif kind == "U":
        s = _make_terrace(r, c, 9)
    elif kind == "R":
        s = _make_stairs(r, c)
    elif kind == "H":
        s = _make_hedge(r, c, mask)
    else:                                     # water base (animated below)
        s = pygame.Surface((TILE, TILE))
        s.fill(WATER[0])
    _cache[key] = s
    return s


_SOLID_KINDS = ("G", "D", "A", "S", "H", "T", "U", "R", "P", "E", "F")

# the mid tone of each material — used when one material dithers into
# another so the ground blends instead of snapping between hard squares
_MAT_COLOR = {
    "G": GRASS[1],
    "D": DIRT[1],
    "A": SAND[1],
    "S": STONE[1],
}

_EDGE_BAND = 4
_BAYER = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)


def _edge_overlay(side, other_kind):
    """A dithered band of one material bleeding into its neighbour."""
    key = ("edge", side, other_kind)
    surf = _cache.get(key)
    if surf is not None:
        return surf
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    col = _MAT_COLOR.get(other_kind)
    if col is not None:
        for y in range(TILE):
            for x in range(TILE):
                if side == "up":
                    depth, along = y, x
                elif side == "down":
                    depth, along = TILE - 1 - y, x
                elif side == "left":
                    depth, along = x, y
                else:
                    depth, along = TILE - 1 - x, y
                if depth >= _EDGE_BAND:
                    continue
                p = (1.0 - depth / float(_EDGE_BAND)) * 0.85
                th = (_BAYER[y % 4][x % 4] + 0.5) / 16.0
                if th < p:
                    surf.set_at((x, y), (col[0], col[1], col[2], 255))
    _cache[key] = surf
    return surf


def render_static(tm):
    """All terrain with static art; water cells get their deep base."""
    surf = pygame.Surface((tm.cols * TILE, tm.rows * TILE), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    for kind in _SOLID_KINDS:
        for r in range(tm.rows):
            for c in range(tm.cols):
                if tm.grid[r][c] != kind:
                    continue
                mask, corners = mask_of(tm, r, c)
                if kind == "H":               # hedge edges where it meets open ground
                    mask = 0
                    for bit, (dr, dc) in ((1, (-1, 0)), (2, (0, 1)), (4, (1, 0)), (8, (0, -1))):
                        other = tm.cell(r + dr, c + dc)
                        if other is not None and other != "H":
                            mask |= bit
                surf.blit(tile_for(kind, mask, corners, r, c), (c * TILE, r * TILE))
    for r in range(tm.rows):
        for c in range(tm.cols):
            if tm.grid[r][c] == "W":
                surf.blit(_cached("water_base", lambda: (lambda s: (s.fill(WATER[0]), s)[1])(pygame.Surface((TILE, TILE)))), (c * TILE, r * TILE))
    return surf


def draw_water(surface, tm, phase, offset=(0, 0)):
    for r in range(tm.rows):
        for c in range(tm.cols):
            if tm.grid[r][c] != "W":
                continue
            mask = water_mask_of(tm, r, c)
            key = ("wm", mask, phase)
            if key not in _cache:
                s = _make_water(phase, r, c)
                _foam(s, mask, _seed(r, c, 29))
                _cache[key] = s
            surface.blit(_cache[key], (offset[0] + c * TILE, offset[1] + r * TILE))


def draw_view(surface, tm, cam, phase=0, pad=2, fill=(16, 18, 30)):
    """Draw only the tiles the camera can see.

    The world is far larger than the screen, so a full-bake surface would
    cost tens of megabytes and minutes of construction. Tile variants are
    cached by (kind, mask, corners, r%4, c%4), so culling to the viewport
    keeps a whole open world as cheap as one screen.
    """
    ox, oy = int(cam[0]), int(cam[1])
    w, h = surface.get_size()
    surface.fill(fill)
    c0 = max(0, ox // TILE - pad)
    c1 = min(tm.cols - 1, (ox + w + TILE) // TILE + pad)
    r0 = max(0, oy // TILE - pad)
    r1 = min(tm.rows - 1, (oy + h + TILE) // TILE + pad)
    for kind in _SOLID_KINDS:
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if tm.grid[r][c] != kind:
                    continue
                mask, corners = mask_of(tm, r, c)
                if kind == "H":               # hedge edges where it meets open ground
                    mask = 0
                    for bit, (dr, dc) in ((1, (-1, 0)), (2, (0, 1)), (4, (1, 0)), (8, (0, -1))):
                        other = tm.cell(r + dr, c + dc)
                        if other is not None and other != "H":
                            mask |= bit
                surface.blit(tile_for(kind, mask, corners, r, c),
                             (c * TILE - ox, r * TILE - oy))
                # dithered transitions: one material bleeding into the next
                # instead of a hard square edge between them
                if kind != "H":
                    n, e, s, w = neighbours_of(tm, r, c)
                    for side, other in (("up", n), ("down", s),
                                        ("left", w), ("right", e)):
                        if other is None or other == kind or other in ("W", "H"):
                            continue
                        surface.blit(_edge_overlay(side, other),
                                     (c * TILE - ox, r * TILE - oy))
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            if tm.grid[r][c] != "W":
                continue
            mask = water_mask_of(tm, r, c)
            key = ("wm", mask, phase)
            if key not in _cache:
                s = _make_water(phase, r, c)
                _foam(s, mask, _seed(r, c, 29))
                _cache[key] = s
            surface.blit(_cache[key], (c * TILE - ox, r * TILE - oy))
    return (c0, r0, c1, r1)


def phase_for(t):
    return int(t * 6) % 3


# ------------------------------------------------------------------ maps
def village_map():
    tm = TileMap(20, 10)
    # enclosing hedge with a village entrance gap (middle of row 0)
    tm.rect(0, 0, 0, 19, "H")
    tm.rect(1, 4, 0, 0, "H")
    tm.rect(1, 5, 19, 19, "H")
    # entry path down the middle, a westward plaza, a branch to the well
    tm.line(9, 0, 9, 2, "D", 2)
    tm.line(9, 2, 6, 3, "D", 2)
    tm.line(6, 3, 5, 5, "D", 2)
    tm.rect(4, 6, 3, 6, "D")                  # front-left hut yard
    tm.line(9, 2, 12, 4, "D", 2)              # branch to the well
    # stone platforms: shrine (rows 2-5, cols 14-16) and well (rows 5-6, 11-13)
    tm.rect(2, 5, 14, 16, "S")
    tm.rect(5, 6, 11, 13, "S")
    tm.rect(6, 7, 12, 12, "A")                # sandy patch under the well
    # pond rimmed in stone at the bottom-right
    tm.rect(6, 7, 18, 19, "W")
    tm.rect(5, 5, 18, 19, "S")
    tm.rect(6, 7, 17, 17, "S")
    return tm


def washup_map():
    tm = TileMap(20, 10)
    tm.rect(0, 4, 0, 19, "W")                 # the river
    tm.rect(5, 9, 0, 19, "A")                 # sandy bank
    return tm


# ------------------------------------------------------------------ big world
# The walkable hub world: a tall (30x30 tile) valley. North holds the shrine
# terrace under a mountaintop lake; the village sits mid-valley; a river runs
# across the south toward a big lake — so travel is mostly along Y.
BIG_COLS, BIG_ROWS = 30, 30


def big_map():
    tm = TileMap(BIG_COLS, BIG_ROWS)

    # forest frame along every edge
    tm.rect(0, 0, 0, 29, "H")
    tm.rect(29, 29, 0, 29, "H")
    tm.rect(1, 28, 0, 0, "H")
    tm.rect(1, 28, 29, 29, "H")

    # ---- north: mountain lake, shrine terrace, then a path down the woods
    tm.rect(1, 5, 1, 28, "H")                 # north woods
    tm.rect(2, 3, 12, 17, "W")                # mountain lake
    tm.rect(4, 5, 13, 16, "S")                # shrine terrace
    tm.rect(4, 4, 14, 15, "S")                # terrace upper step
    tm.rect(5, 6, 14, 15, "D")                # stairs down through the woods

    # ---- mid-valley: open meadow band, then the village plaza
    tm.rect(7, 9, 8, 20, "D")                 # village plaza
    tm.rect(7, 7, 10, 18, "D")                # plaza upper lip
    tm.rect(8, 8, 6, 7, "D")                  # west lane (Grandma Ruen)
    tm.rect(10, 11, 6, 7, "D")                # south-west lane

    # well on a stone platform east of the plaza
    tm.rect(10, 11, 21, 23, "S")
    tm.rect(11, 11, 22, 22, "A")

    # pond at the south-east corner of the village
    tm.rect(11, 13, 25, 28, "W")
    tm.rect(10, 10, 25, 28, "S")
    tm.rect(11, 13, 24, 24, "S")
    tm.rect(11, 13, 29, 29, "S")

    # ---- a river crosses the south, bridged mid-valley
    tm.rect(16, 18, 1, 28, "W")               # the river
    tm.rect(16, 18, 13, 16, "S")              # stone bridge
    tm.rect(15, 15, 1, 28, "A")               # north bank
    tm.rect(19, 19, 1, 28, "A")               # south bank

    # ---- south: meadow, a big lake, then the far shore
    tm.rect(23, 25, 17, 22, "W")              # south lake
    tm.rect(22, 22, 17, 22, "A")              # lake north shore
    tm.rect(26, 26, 17, 22, "A")              # lake south shore
    tm.rect(26, 28, 6, 12, "D")               # far-shore lane (to the river)

    # south lane from the bridge into the wilds
    tm.rect(14, 15, 14, 15, "D")
    tm.rect(20, 27, 14, 15, "D")

    _scatter_nature(tm)
    return tm


def _scatter_nature(tm):
    """Deterministic clumps of trees, rocks and puddles on open grass,
    kept away from paths, platforms and water edges."""
    rng = random.Random(2026)
    keep = set()
    for r in range(tm.rows):
        for c in range(tm.cols):
            if tm.grid[r][c] not in ("G",):
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        keep.add((r + dr, c + dc))
    for r in range(2, tm.rows - 2):
        for c in range(2, tm.cols - 2):
            if (r, c) in keep or tm.grid[r][c] != "G":
                continue
            roll = rng.random()
            if roll < 0.05:
                tm.grid[r][c] = "H"           # tree grove
                for dr, dc in ((0, 1), (1, 0), (1, 1), (2, 1), (1, 2)):
                    rr, cc = r + dr, c + dc
                    if tm.grid[rr][cc] == "G" and (rr, cc) not in keep \
                            and rng.random() < 0.65:
                        tm.grid[rr][cc] = "H"
            elif roll < 0.065:
                tm.grid[r][c] = "S"           # rocks
            elif roll < 0.08:
                tm.grid[r][c] = "W"           # little rain puddle w/ sand lip
                for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    rr, cc = r + dr, c + dc
                    if tm.grid[rr][cc] == "G":
                        tm.grid[rr][cc] = "A"


def grid_ascii(tm):
    kinds = {"G": ".", "D": ":", "A": "~", "S": "+", "W": "=", "H": "#"}
    return "\n".join("".join(kinds[tm.grid[r][c]] for c in range(tm.cols))
                     for r in range(tm.rows))


def walkable_at(tm, x, y, ground_y=62):
    """True when the world point (x, y) — ground px, incl. the ground offset —
    sits on a walkable tile (water and forest walls are impassable)."""
    c = int(x) // TILE
    r = int(y - ground_y) // TILE
    cell = tm.cell(r, c)
    return cell is not None and cell not in ("W", "H")


def solid_base(tm, x, y, ground_y=62):
    """The walkable 'next row down' from a position, for depth-sorting."""
    c = int(x) // TILE
    r = int(y - ground_y) // TILE
    return max(r, 0)

def _make_terrace(r, c, rise):
    """A raised stone platform: paving on top, a cut face at the front."""
    s = pygame.Surface((TILE, TILE))
    rnd = random.Random(_hash_cell(r, c) + 31)
    top = TILE - rise
    # the paving on top
    for y in range(top):
        for x in range(16):
            _px(s, x, y, STONE[2])
    off = (r * 7 + c * 13) % 5                 # the slabs do not line up
    for i in range(0, 16, 5):                  # the joints between slabs
        for x in range(16):
            _px(s, x, (i + off) % max(1, top), STONE[1])
    for _ in range(6):
        _px(s, rnd.randrange(0, 16), rnd.randrange(0, max(1, top)),
            STONE[3])
    # the cut face at the front, in shadow
    for y in range(top, TILE):
        for x in range(16):
            _px(s, x, y, STONE[0])
    for x in range(16):
        _px(s, x, top, STONE[3])
        _px(s, x, TILE - 1, STONE[0])
    if rise > 5:
        for x in range(16):
            _px(s, x, top + 1, STONE[1])
    for _ in range(2):                        # moss in the joints
        _px(s, rnd.randrange(0, 16), rnd.randrange(0, max(1, top)),
            (108, 132, 96))
    return s


def _make_stairs(r, c):
    """A flight of steps: you climb it without jumping."""
    s = pygame.Surface((TILE, TILE))
    rnd = random.Random(_hash_cell(r, c) + 37)
    s.fill((58, 60, 66))
    steps = 4
    for i in range(steps):
        y = TILE - 2 - i * 4
        for x in range(16):
            _px(s, x, y, STONE[3])
            _px(s, x, y + 1, STONE[1])
    for _ in range(4):
        _px(s, rnd.randrange(0, 16), rnd.randrange(0, 10), STONE[2])
    return s


def _make_plaza(r, c):
    """A paved village square: pale stone slabs with neat joints."""
    s = pygame.Surface((TILE, TILE))
    rnd = random.Random(_hash_cell(r, c) + 41)
    s.fill((168, 166, 158))
    for i in range(0, 16, 8):
        for x in range(16):
            _px(s, x, i, (140, 138, 132))
        for y in range(16):
            _px(s, i, y, (140, 138, 132))
    for i in range(0, 16, 8):
        for j in range(0, 16, 8):
            if (i // 8 + j // 8 + r + c) % 2 == 0:
                for y in range(j, j + 8):
                    for x in range(i, i + 8):
                        _px(s, x, y, (176, 174, 166))
    for _ in range(6):
        _px(s, rnd.randrange(0, 16), rnd.randrange(0, 16), (188, 186, 178))
    return s


def _make_paddy(r, c):
    """A flooded rice paddy: young plants in standing water, mud edges."""
    s = pygame.Surface((TILE, TILE))
    rnd = random.Random(_hash_cell(r, c) + 43)
    s.fill((74, 106, 92))                 # the water
    for y in range(TILE):
        for x in range(TILE):
            if (x * 3 + y * 5 + r + c) % 7 == 0:
                _px(s, x, y, (86, 122, 104))
    # rows of rice, planted in lines
    for i in range(4):
        y = 2 + i * 4
        for x in range(0, 16, 2):
            _px(s, x, y, (128, 168, 84))
            _px(s, x, y + 1, (74, 120, 60))
            if rnd.random() < 0.4:
                _px(s, x + 1, y, (150, 186, 96))
    for _ in range(3):
        _px(s, rnd.randrange(0, 16), rnd.randrange(0, 16), (198, 214, 190))
    return s
