"""The open world of the South, traced from the real Southern Thailand.

The landmass is not invented: it is the GADM boundary set for the 14
southern provinces (Chumphon, Ranong, Surat Thani, Phangnga, Phuket,
Krabi, Nakhon Si Thammarat, Phatthalung, Trang, Satun, Songkhla,
Pattani, Yala, Narathiwat), rasterized to 240x320 and embedded below
(zlib + base64; grid spans lon 97.5-102.1, lat 5.6-11.05). Stop pins
are projected from real latitude/longitude, so Chumphon sits on the
Gulf side of the Kra Isthmus, Ranong on the Andaman side, Phuket is a
real island, and Narathiwat is the easternmost pin.

Terrain is the SNES-style top-down engine from ``tiles`` (G grass,
D dirt/road, A sand, S stone, W water, H forest/hedge), drawn with
viewport culling. Water is impassable on foot — but **gliding floats
over it**, which is how you reach the islands.
"""

import base64
import math
import os
import random
import zlib

from . import tiles as T

# The GADM mask is 240x320 (one cell ~2 km). The playable world is
# MAP_SCALE times finer so the South reads as a *country*, not an
# island: ~720x960 tiles, a full traverse on foot takes minutes.
BASE_COLS = 240
BASE_ROWS = 320
MAP_SCALE = 10

# BUMP THIS whenever the world generation changes, so the cached world on
# disk is rebuilt instead of being reused
WORLD_VERSION = 2
WORLD_COLS = BASE_COLS * MAP_SCALE
WORLD_ROWS = BASE_ROWS * MAP_SCALE

# Offsets in the art data (town radius, prop placement, spark rings) were
# tuned against a 3x world. TUNE keeps their proportions as the grid grows,
# so a province keeps the same look while taking three times as long to
# cross.
TUNE = MAP_SCALE / 3.0


def sc(value):
    """Scale a tile offset from the old tuning to the current world."""
    return int(round(value * TUNE))

# lon 97.5-102.1, lat 5.6 (south) - 11.05 (north); 1 = land.
# Rebuild from GADM with /tmp/opencode/build_mask.py if pins ever move.
_MASK_B64 = (
    "eNrtneuWozAMg6X3f+m9cqa0QIE4rW2J37N75hs5jnOxAvgb/iiGS4rhShGTD8TsLfhvMD5/YGf"
    "enU8MV47XAnfmbVuCKGl7JG/Pollq7IqlKq2piFq8pJi8tLzGVcAV4/XMa14Xkt60Mq95vw+sxQ"
    "uY17zG9a6keT39erlgXq/24yajP/cYZHghNvma18Wkl74urszrasPyeqvd8t7GhbOzJ6MePR1D2"
    "apgEJi3dTy7tvI1JC8VHM3mdTxb30zJ2dNRc3nZrDd/3dvbm5cn5FXj7eY1QWjxIlJfSqXn3PH"
    "AaN7c8c9To/e6vkzNGzp+ayS4o1rj4q9fBTcwQYvxZp+RqFRPnuOlhA9D1wWDlsCncNkmX/1FCe"
    "JdfpAiCatI9DMauDprJ17o8PIKL69aNyZd60fydornCwJXyc3jy/5SuAECp597GQzcoXRutGQwb"
    "2teMXVDeCnF+zN1S4zeWvE+wvtSjxXCxU3eSgmNg8VVxQTO69/RP02/y34PePeGS/1ThVarCSn"
    "ee8Fs3iK8p2fdJsD/S14Z4GVmEeKFmL7x6qbmhRTv1aOFFuNXK19pVdCKBYdYvaE1H5m3/wpJL"
    "V+Z17zmrQhM85rXvFV5aV7Hs3nzAtMBrcxL8xq4Ei+/pm9GhQkxXjHgybwUC2imuxdNfkBfyvA"
    "urjxSvBTiXQ7TEwPDAg8SJ+dtfWX2VYw5miNp2++sGM/JO/HOXT5ejRPwdShj2h3DrPqyeU/D+"
    "Taq1sDsz7tauPW9crfNi768O94vXQN6mX0gw/uvY+N5y1qF96x1buGEtc7MArx8bmjoXnD8mH5"
    "dsM4tCfy8dcp7Pf31eJ+31rrz4gl4CVg0G8Avfguv3VhozDtxzza/vrHAKeWdyJsJ+KFsPtrjq"
    "s/7bFu1+VsFJepM89HhmwlEG95TTq9BXbPIKPCoZ9RWgktkn3vqjz8kLzIO4M/YKNXg5aHZVcE"
    "B/O7KUNiBElK99TSfl1kcVj5lgpbHvv0zdy2RGJhNK8pzf4aYEguo5KgbsNdRiTdi27KUwAGL/"
    "1oO0ePbHRV5JYDleIPOHqrlZx3emA3akrwCwLTAOrwiFYdWQEONF1oD2Lzm7Q8MBV6OnflX5H0"
    "EhkJAq/GObM3Wi+ZHr2yIZOjlSXdoTEkju3c189VA5VGdFxcdG4qO3ZuPF1YAZshJOOoAx5z8l"
    "3xedeA62oVrMpkrrWv3DdHgIeHrpjq1ge8c/heuKjclRs86+n6lJfPEewNgMV6pzcoBYjF99YA"
    "tcP8jFmrtz1bd4KESMcWAx60rdt827ep9f/S/tXX7h/3v80pMPWBo+d+LPekg+CjLzJAWee89o"
    "a/y4zY05nnC5+2uXLuGE/1sLPdCup/r0Ko56cA3nI1MHvZnJTFeKPByGm8aV5pdS4fouuv7dh0"
    "8dBiuLPDaHOxoAG84L0Ut/j9uvso3/XYrX5YJK4nvW9Bw/x58fatD4rRpCecYHhbpK92YrPo9q"
    "Bzd35Jc4EmOHvV4B6UGfPfDVwN8NcDNpuZ1RFvhrx3BqPFSqVm8bMf4cjvlntqAVnkJMWDzOp4"
    "7TU5w34d5PX6rAsO8xu3Ci/KfcTvjyvFCDBeW17j9eTcdINqKW6cLKxC3HfD7MdpeX2jxHv1Et"
    "2y1ddulN+/bF9Y7AR87T6Fd6Tz2amI94ohnBNvw9vnUeCGGCzHczJ4b33qi15/Y9wuVmUYE"
)

_mask = None


def _upscale_mask(raw):
    """Bilinear-grow the 240x320 mask to WORLD_COLS x WORLD_ROWS.

    Smoothing (then a 0.5 threshold) keeps the coastline organic
    instead of staircases, while staying true to the GADM shape.
    Vectorised with numpy: the world is millions of cells, so a Python
    loop per cell would cost tens of seconds at every start-up.
    """
    try:
        import numpy as np
    except ImportError:
        return _upscale_mask_slow(raw)
    src = np.frombuffer(raw, dtype=np.uint8).reshape(BASE_ROWS, BASE_COLS)
    src = src.astype(np.float32)
    ys = (np.arange(WORLD_ROWS, dtype=np.float32) + 0.5) * \
        (BASE_ROWS / float(WORLD_ROWS)) - 0.5
    xs = (np.arange(WORLD_COLS, dtype=np.float32) + 0.5) * \
        (BASE_COLS / float(WORLD_COLS)) - 0.5
    ys = np.clip(ys, 0.0, BASE_ROWS - 1.0)
    xs = np.clip(xs, 0.0, BASE_COLS - 1.0)
    y0 = np.floor(ys).astype(np.int32)
    x0 = np.floor(xs).astype(np.int32)
    y1 = np.minimum(y0 + 1, BASE_ROWS - 1)
    x1 = np.minimum(x0 + 1, BASE_COLS - 1)
    fy = (ys - y0)[:, None]
    fx = (xs - x0)[None, :]
    top = src[y0][:, x0] * (1 - fx) + src[y0][:, x1] * fx
    bot = src[y1][:, x0] * (1 - fx) + src[y1][:, x1] * fx
    out = top * (1 - fy) + bot * fy
    land = out >= 0.5
    # clean the noise the bilinear upscale leaves. An opening (erode then
    # dilate) drops every blob smaller than a few cells, so the coast has
    # no freckles of sand in the middle of the fields.
    for _ in range(3):
        pad = np.pad(land, 1, constant_values=False)
        neighbours = (pad[:-2, 1:-1] & pad[2:, 1:-1] &
                      pad[1:-1, :-2] & pad[1:-1, 2:])
        eroded = land & neighbours              # shrink
        pad = np.pad(eroded, 1, constant_values=False)
        grown = eroded | (pad[:-2, 1:-1] | pad[2:, 1:-1] |
                          pad[1:-1, :-2] | pad[1:-1, 2:])
        land = grown                          # and grow back
    # and fill the small holes of water inside the land: they used to
    # leave a ring of sand around a puddle in the middle of a field
    for _ in range(2):
        pad = np.pad(land, 1, constant_values=True)
        enclosed = (~land) & (pad[:-2, 1:-1] & pad[2:, 1:-1] &
                              pad[1:-1, :-2] & pad[1:-1, 2:])
        land = land | enclosed
    return land.astype(np.uint8).tobytes()


def _upscale_mask_slow(raw):
    """Pure-python fallback for machines without numpy."""
    out = bytearray(WORLD_COLS * WORLD_ROWS)
    inv = 1.0 / MAP_SCALE
    for R in range(WORLD_ROWS):
        sy = R * inv
        y0 = int(sy)
        y1 = y0 + 1 if y0 + 1 < BASE_ROWS else y0
        fy = sy - y0
        b0 = y0 * BASE_COLS
        b1 = y1 * BASE_COLS
        ob = R * WORLD_COLS
        for C in range(WORLD_COLS):
            sx = C * inv
            x0 = int(sx)
            x1 = x0 + 1 if x0 + 1 < BASE_COLS else x0
            fx = sx - x0
            top = raw[b0 + x0] + (raw[b0 + x1] - raw[b0 + x0]) * fx
            bot = raw[b1 + x0] + (raw[b1 + x1] - raw[b1 + x0]) * fx
            out[ob + C] = 1 if (top + (bot - top) * fy) >= 0.5 else 0
    return bytes(out)


def land_mask():
    """The real-provinces landmask as bytes (1 = land), decoded once."""
    global _mask
    if _mask is None:
        raw = zlib.decompress(base64.b64decode(_MASK_B64))
        _mask = _upscale_mask(raw) if MAP_SCALE != 1 else raw
    return _mask


def _in_land(row, col):
    if not (0 <= row < WORLD_ROWS and 0 <= col < WORLD_COLS):
        return False
    return land_mask()[row * WORLD_COLS + col] == 1


_spans = None


def _row_spans():
    """First and last land column of every row, computed once.

    The mountain and forest passes ask for this thousands of times; at
    2400 columns a row-by-row Python scan would cost seconds.
    """
    global _spans
    if _spans is None:
        try:
            import numpy as np
            m = np.frombuffer(land_mask(), dtype=np.uint8).reshape(
                WORLD_ROWS, WORLD_COLS)
            land = m == 1
            any_land = land.any(axis=1)
            first = np.where(any_land, land.argmax(axis=1), -1)
            last = np.where(any_land, WORLD_COLS - 1 - land[:, ::-1].argmax(axis=1), -1)
            _spans = list(zip(first.tolist(), last.tolist()))
        except ImportError:
            _spans = []
            for r in range(WORLD_ROWS):
                lo, hi = None, None
                base = r * WORLD_COLS
                for c in range(WORLD_COLS):
                    if land_mask()[base + c]:
                        if lo is None:
                            lo = c
                        hi = c
                _spans.append((lo if lo is not None else -1,
                               hi if hi is not None else -1))
    return _spans


def _row_span(r):
    """(west, east) land columns on row ``r``, or None when all water."""
    if not (0 <= r < WORLD_ROWS):
        return None
    lo, hi = _row_spans()[r]
    if lo < 0:
        return None
    return lo, hi


def _fill_base(tm, mask):
    """Land as grass, the coastline as sand — vectorised.

    Every land cell is tested against its four neighbours, which at
    2400x3200 cells is ten million reads if done in Python.
    """
    try:
        import numpy as np
        m = np.frombuffer(mask, dtype=np.uint8).reshape(WORLD_ROWS, WORLD_COLS)
        land = m == 1
        sea = ~land
        pad = np.pad(sea, 1, constant_values=True)
        coast = land & (pad[:-2, 1:-1] | pad[2:, 1:-1] |
                        pad[1:-1, :-2] | pad[1:-1, 2:])
        raw = np.full((WORLD_ROWS, WORLD_COLS), ord("W"), dtype=np.uint8)
        raw[land] = ord("G")
        raw[coast] = ord("A")
        tm.grid = [list(raw[r].tobytes().decode("ascii"))
                   for r in range(WORLD_ROWS)]
        return
    except ImportError:
        pass
    for r in range(WORLD_ROWS):
        base = r * WORLD_COLS
        for c in range(WORLD_COLS):
            if not mask[base + c]:
                continue
            coast = any(
                0 <= r + dr < WORLD_ROWS and 0 <= c + dc < WORLD_COLS
                and not mask[(r + dr) * WORLD_COLS + (c + dc)]
                for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            tm.grid[r][c] = "A" if coast else "G"


def _build_world():
    tm = T.TileMap(WORLD_COLS, WORLD_ROWS, fill="W")
    mask = land_mask()
    _fill_base(tm, mask)

    # Real ranges — the Phuket Range, the Nakhon/Banthat wall and the
    # Sankalakhiri — drawn as NARROW ridges with natural passes, not a
    # grey smear over the whole interior. You cross them at the gaps.
    # Rows are given on the 240x320 base map and scaled up, so the ranges
    # stay where the real ones are at any world size.
    MOUNTAIN_RANGES = (
        (40, 110, 0.36, 0.05, 6),      # Phuket Range (west-central)
        (100, 193, 0.52, 0.05, 7),     # Nakhon / Banthat wall
        (187, 300, 0.44, 0.06, 8),     # Sankalakhiri (deep south spine)
    )
    rng = random.Random(7)
    passes = set()
    for rlo, rhi, _cf, _w, _t in MOUNTAIN_RANGES:
        lo_r, hi_r = rlo * MAP_SCALE, rhi * MAP_SCALE
        for _ in range(5):
            pr = rng.randrange(lo_r + 8, hi_r - 8)
            for k in range(-7 * MAP_SCALE // 3, 8 * MAP_SCALE // 3):
                passes.add(pr + k)
    for rlo, rhi, cfrac, wiggle, thick in MOUNTAIN_RANGES:
        for r in range(rlo * MAP_SCALE, rhi * MAP_SCALE):
            if r in passes:
                continue
            span = _row_span(r)
            if span is None:
                continue
            lo, hi = span
            width = hi - lo
            if width < 14 * MAP_SCALE // 3:
                continue
            centre = lo + width * cfrac + \
                math.sin(r * 0.028 * 3.0 / MAP_SCALE) * wiggle * width
            half = (thick * MAP_SCALE // 3) // 2 + \
                (1 if rng.random() < 0.16 else 0)
            for c in range(int(centre - half), int(centre + half) + 1):
                if not (0 <= c < tm.cols):
                    continue
                if tm.grid[r][c] not in ("G", "H"):
                    continue
                tm.grid[r][c] = "S" if abs(c - centre) <= half - 1 else "H"

    # rainforest crowding the western (Andaman) flank
    for r in range(13 * MAP_SCALE, WORLD_ROWS - 7 * MAP_SCALE):
        span = _row_span(r)
        if span is None:
            continue
        lo, hi = span
        for _ in range(max(1, int((hi - lo) * 0.035))):
            c = rng.randrange(lo, lo + max(2, (hi - lo) // 3))
            if tm.grid[r][c] != "G":
                continue
            size = rng.randrange(1, 5)
            for _k in range(size):
                rr, cc = r + rng.randrange(-2, 3), c + rng.randrange(-2, 3)
                if _in_land(rr, cc) and tm.grid[rr][cc] == "G":
                    tm.grid[rr][cc] = "H"

    # the real lakes: Thale Sap (Songkhla lake) and Cheow Lan reservoir
    _carve_lake(tm, rows=range(184 * MAP_SCALE, 219 * MAP_SCALE),
                centre=152 * MAP_SCALE,
                half=(2 * MAP_SCALE // 3, 4 * MAP_SCALE // 3), seed=11)
    _carve_lake(tm, rows=range(117 * MAP_SCALE, 127 * MAP_SCALE),
                centre=63 * MAP_SCALE,
                half=(2 * MAP_SCALE // 3, 4 * MAP_SCALE // 3), seed=23)

    from . import story as ST
    mainland, islands = [], []
    for stop in ST.STOPS:
        (c, r) = stop["pos"]
        if stop["kind"] == "secret" and _is_island(stop):
            islands.append((stop["id"], c, r))
        else:
            mainland.append((stop["id"], c, r))
        _town(tm, r, c)

    # the village of the prologue
    pc, pr = ST.PROLOGUE["pos"]
    _town(tm, pr, pc, radius=4)

    # roads linking the mainland stops in travel order, plus the prologue
    route = [(pc, pr)] + [(c, r) for _, c, r in mainland]
    for i in range(len(route) - 1):
        c0, r0 = route[i]
        c1, r1 = route[i + 1]
        _road(tm, r0, c0, r1, c1)

    # islands: stamp land (and a sand ford so they are reachable by glide)
    for _id, c, r in islands:
        stamp_island(tm, r, c)

    # real islets with no stops: Ang Thong, Ko Yao, Ko Lanta, Ko Adang
    # (Ko Lanta is the same island as the ko_lipe stop, so this runs before
    # the terraces, not after)
    for r, c in ((82 * MAP_SCALE, 113 * MAP_SCALE),
                 (173 * MAP_SCALE, 57 * MAP_SCALE),
                 (205 * MAP_SCALE, 80 * MAP_SCALE),
                 (265 * MAP_SCALE, 92 * MAP_SCALE)):
        stamp_island(tm, r, c)

    # the rice paddies: the flat lowland is not empty grass, it is
    # flooded fields in rectangular blocks, with mud dikes between them
    _paddies(tm)

    # and now the ground the temples and stupas stand on is raised: the
    # towns are built on terraces, with steps down at the edge
    for stop in ST.STOPS:
        _terrace(tm, stop["pos"][1], stop["pos"][0], radius=6)
    _terrace(tm, pr, pc, radius=6)

    _smooth_speckles(tm)
    return tm


def _smooth_speckles(tm):
    """Remove single-tile noise at material boundaries.

    A lone grass square in the sand, or a lone sand square in the grass,
    reads as a bug rather than as terrain. Any land tile whose four
    neighbours are all the *same* other material becomes that material.
    Water, granite and forest are never touched, so paths, passes and
    the coastline keep working exactly as before.
    """
    try:
        import numpy as np
        arr = np.array([[ord(ch) for ch in row] for row in tm.grid],
                        dtype=np.uint8)
    except Exception:
        arr = None
    if arr is not None:
        padded = np.pad(arr, 1, mode="edge")
        up = padded[:-2, 1:-1]
        down = padded[2:, 1:-1]
        left = padded[1:-1, :-2]
        right = padded[1:-1, 2:]
        same = (up == down) & (down == left) & (left == right)
        others = (up == ord("G")) | (up == ord("A")) | (up == ord("D"))
        for kind in ("G", "A", "D"):
            cell = arr == ord(kind)
            change = cell & same & others & (up != arr)
            arr[change] = up[change]
        tm.grid = [list(row.tobytes().decode("ascii")) for row in arr]
        return
    grid = tm.grid
    rows, cols = tm.rows, tm.cols
    changes = []
    for r in range(1, rows - 1):
        row = grid[r]
        up, down = grid[r - 1], grid[r + 1]
        for c in range(1, cols - 1):
            kind = row[c]
            if kind not in ("G", "A", "D"):
                continue
            around = (up[c], down[c], row[c - 1], row[c + 1])
            if kind in around:
                continue                      # touches its own kind: real patch
            other = around[0]
            if any(o != other for o in around):
                continue                      # not a lone speck
            if other in ("G", "A", "D"):
                changes.append((r, c, other))
    for r, c, kind in changes:
        grid[r][c] = kind


_WORLD_CACHE = None


def _cache_path():
    """Where the built world is kept between runs (it never changes)."""
    try:
        from . import options as O
        os.makedirs(O.CONFIG_DIR, exist_ok=True)
        return os.path.join(O.CONFIG_DIR,
                            "world_%dx%d_v%d.bin" % (WORLD_COLS, WORLD_ROWS,
                                                     WORLD_VERSION))
    except Exception:
        return None


def south_map():
    """The South. Built once, then copied (cheap) for each scene."""
    global _WORLD_CACHE
    if _WORLD_CACHE is None:
        _WORLD_CACHE = _load_or_build_world()
    tm = T.TileMap(WORLD_COLS, WORLD_ROWS, fill="W")
    tm.grid = [row[:] for row in _WORLD_CACHE.grid]
    return tm


def _load_or_build_world():
    """Load the world from disk if we have built it before, else build it.

    The world is deterministic, so there is no reason to rebuild seven
    million cells every time the game starts.
    """
    path = _cache_path()
    if path and os.path.exists(path):
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
            if len(raw) == WORLD_COLS * WORLD_ROWS:
                tm = T.TileMap(WORLD_COLS, WORLD_ROWS, fill="W")
                tm.grid = [list(raw[r * WORLD_COLS:(r + 1) * WORLD_COLS]
                                .decode("ascii"))
                           for r in range(WORLD_ROWS)]
                return tm
        except Exception:
            pass
    tm = _build_world()
    if path:
        try:
            raw = bytearray(WORLD_COLS * WORLD_ROWS)
            for r in range(WORLD_ROWS):
                raw[r * WORLD_COLS:(r + 1) * WORLD_COLS] = \
                    "".join(tm.grid[r]).encode("ascii")
            with open(path, "wb") as fh:
                fh.write(raw)
        except Exception:
            pass
    return tm


def _is_island(stop):
    """Secret stops that are genuinely offshore islands."""
    return stop["id"] in (
        "ko_tao", "ko_pha_ngan", "ko_samui", "surin_islands",
        "similan", "ko_phi_phi", "ko_kradan", "ko_lipe",
    )


def _paddies(tm, count=520, seed=21):
    """Flooded rice fields in the flat lowland, with dikes between."""
    import random as _rnd_mod
    rng = _rnd_mod.Random(seed)
    from . import regions as RG
    lowland = ("gulf_shore", "samui_sea", "sweet_islands", "deep_south")
    placed = 0
    tries = 0
    while placed < count and tries < count * 40:
        tries += 1
        r = rng.randrange(20, tm.rows - 20)
        c = rng.randrange(20, tm.cols - 20)
        w = rng.randrange(7, 16)
        h = rng.randrange(6, 14)
        if c + w >= tm.cols or r + h >= tm.rows:
            continue
        # it must be flat open ground, and in a region that farms
        flat = True
        for rr in range(r, r + h):
            row = tm.grid[rr]
            for cc in range(c, c + w):
                if row[cc] != "G":
                    flat = False
                    break
            if not flat:
                break
        if not flat:
            continue
        # dikes around the block
        for rr in range(max(0, r - 1), min(tm.rows, r + h + 1)):
            for cc in range(max(0, c - 1), min(tm.cols, c + w + 1)):
                if rr in (r - 1, r + h) or cc in (c - 1, c + w):
                    if tm.grid[rr][cc] == "G":
                        tm.grid[rr][cc] = "D"
        for rr in range(r, r + h):
            for cc in range(c, c + w):
                if tm.grid[rr][cc] == "G":
                    tm.grid[rr][cc] = "F"
        placed += 1


def _terrace(tm, r, c, radius=3):
    """Raise the ground around a place into a stone terrace, with steps.

    Temples, stupas and shrines do not stand on flat grass. The terrace
    gives the country its levels: you walk up onto a plinth, and down
    the steps at the edge.
    """
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            if abs(dr) + abs(dc) > radius:
                continue
            rr, cc = r + dr, c + dc
            if not (0 <= rr < tm.rows and 0 <= cc < tm.cols):
                continue
            if tm.grid[rr][cc] in ("G", "A"):
                tm.grid[rr][cc] = "T"
    # the front edge of the platform, where the cut face shows
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            if abs(dr) + abs(dc) > radius:
                continue
            rr, cc = r + dr + 1, c + dc
            if not (0 <= rr < tm.rows and 0 <= cc < tm.cols):
                continue
            if tm.grid[rr][cc] == "T":
                tm.grid[rr][cc] = "E"
    # the steps down, on the south side — they may cross a road, which is
    # exactly what a staircase in a village does
    for i in range(radius + 1, radius + 4):
        rr = r + i
        if 0 <= rr < tm.rows and tm.grid[rr][c] in ("G", "A", "D"):
            tm.grid[rr][c] = "R"


def _town(tm, r, c, radius=2):
    """A built-up town district with a stone plaza and dirt streets."""
    radius = sc(radius)
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            if abs(dr) + abs(dc) <= radius:
                rr, cc = r + dr, c + dc
                if 0 <= rr < tm.rows and 0 <= cc < tm.cols:
                    tm.grid[rr][cc] = "P" if (dr == 0 and dc == 0) else "D"


def _road(tm, r0, c0, r1, c1):
    """A 2-wide dirt road, nudged around granite so towns stay connected.

    Never paves the sea: water is skirted, and a leg that cannot cross
    a bay on foot simply ends at the shore.
    """
    c, r = c0, r0
    guard = 0
    while (c != c1 or r != r1) and guard < 40000:
        guard += 1
        dc = (c1 > c) - (c1 < c)
        dr = (r1 > r) - (r1 < r)
        if abs(c1 - c) > abs(r1 - r):
            c += dc
        else:
            r += dr
        # walk around stone: step sideways if the way ahead is granite
        if 0 <= r < tm.rows and 0 <= c < tm.cols and tm.grid[r][c] in ("S", "H"):
            for sidestep in (1, -1, 2, -2):
                cc = c + sidestep
                if (0 <= cc < tm.cols and tm.grid[r][cc] not in ("S", "H", "W")
                        and abs(cc - c) < abs(c - c1) + 6):
                    c = cc
                    break
            else:
                c += dc
        if not (0 <= r < tm.rows and 0 <= c < tm.cols):
            continue
        if tm.grid[r][c] == "W":
            # skirt the shore: feel for land along the beach
            for wr, wc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1),
                           (r + 1, c + 1), (r - 1, c - 1)):
                if (0 <= wr < tm.rows and 0 <= wc < tm.cols
                        and tm.grid[wr][wc] not in ("W", "S", "H")
                        and abs(wc - c1) + abs(wr - r1) < abs(c - c1) + abs(r - r1) + 2):
                    r, c = wr, wc
                    break
            else:
                # a strait too wide to skirt: bridge it if the far shore
                # is close (a ferry run), else end the road at the beach
                if not _bridge(tm, r, c, r1, c1, dc, dr):
                    return
        tm.grid[r][c] = "D"
        for off in range(1, max(1, sc(1))):
            if tm.cell(r, c - off) in ("G", "A"):
                tm.grid[r][c - off] = "D"
            if tm.cell(r + off, c) in ("G", "A"):
                tm.grid[r + off][c] = "D"


def _bridge(tm, r, c, r1, c1, dc, dr):
    """Pave a short ferry crossing (<=4 water tiles) toward the goal.

    Returns True and moves (r, c) onto the far shore when the gap is
    small; otherwise returns False and the road ends at the beach.
    """
    for span in range(1, sc(5) + 1):
        nr, nc = r + dr * span, c + dc * span
        if not (0 <= nr < tm.rows and 0 <= nc < tm.cols):
            return False
        if tm.grid[nr][nc] != "W":
            if span > sc(4) or tm.grid[nr][nc] in ("S", "H"):
                return False
            for i in range(1, span):
                tm.grid[r + dr * i][c + dc * i] = "D"
            tm.grid[nr][nc] = "D"
            return True
    return False


def _carve_lake(tm, rows, centre, half, seed):
    """Carve a wobbling real lake where the mask has land."""
    rr = random.Random(seed)
    wobble = {r: rr.randrange(-half[0], half[1] + 1) for r in rows}
    for r in rows:
        if not (0 <= r < tm.rows):
            continue
        for c in range(centre + wobble[r] - half[1], centre + wobble[r] + half[1] + 1):
            if 0 <= c < tm.cols and _in_land(r, c) and tm.grid[r][c] in ("G", "S", "H"):
                tm.grid[r][c] = "W"


def _pass(tm, r):
    """A dirt cut east-west through rock and forest: a mountain pass."""
    if not (0 <= r < tm.rows):
        return
    span = _row_span(r)
    if span is None:
        return
    lo, hi = span
    for c in range(lo, hi + 1):
        if _in_land(r, c) and tm.grid[r][c] in ("S", "H"):
            tm.grid[r][c] = "D"


def hidden_spot(tm, stop):
    """Where a stop's hidden page-spark waits: a walkable tile on a ring
    5..12 tiles out, found by deterministic spiral search. Prefers tiles
    reachable on foot; on specks of island with no room, any island tile
    (glide in, walk around) will do."""
    c0, r0 = stop["pos"]
    rng = random.Random("spark-" + stop["id"])

    def cell_ok(c, r):
        return (0 <= r < tm.rows and 0 <= c < tm.cols
                and tm.grid[r][c] not in ("W", "H"))

    # walkable-on-foot from the pin, so the spark is always earnable
    # without flight (decorative islets next door do not count)
    seen = set()
    queue = [(c0, r0)]
    while queue and len(seen) < 4000:
        c, r = queue.pop()
        if (c, r) in seen or not cell_ok(c, r):
            continue
        seen.add((c, r))
        queue.extend(((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)))

    # walk outwards ring by ring and take the first tile that is both
    # walkable and on the ring — no shuffling of thousands of
    # candidates, which used to cost half a second per stop
    lo_r, hi_r = sc(5), sc(13)
    for radius in range(lo_r, hi_r):
        ring = []
        for dc in range(-radius, radius + 1):
            ring.append((c0 + dc, r0 - radius))
            ring.append((c0 + dc, r0 + radius))
        for dr in range(-radius + 1, radius):
            ring.append((c0 - radius, r0 + dr))
            ring.append((c0 + radius, r0 + dr))
        rng.shuffle(ring)          # only this ring, so it still varies
        for c, r in ring:
            if (c, r) in seen:
                return (c, r)

    # specks of island smaller than the ring: hide it on the island
    # itself, just off the pin so arrival doesn't trip it instantly
    inner = []
    for radius in range(1, 5):
        for dc in range(-radius, radius + 1):
            for dr in (-radius, radius):
                inner.append((c0 + dc, r0 + dr))
    rng.shuffle(inner)
    for c, r in inner:
        if (c, r) != (c0, r0) and (c, r) in seen:
            return (c, r)
    return stop["pos"]


def dock_spots(tm):
    """One boat dock per stop near open water: the closest water tile
    within 6 of the town, paired with the beach tile beside it."""
    from . import story as ST
    docks = []
    for stop in ST.STOPS:
        c0, r0 = stop["pos"]
        best = None
        reach = sc(10)
        for r in range(r0 - reach, r0 + reach + 1):
            for c in range(c0 - reach, c0 + reach + 1):
                if not (0 <= r < tm.rows and 0 <= c < tm.cols):
                    continue
                if tm.grid[r][c] != "W":
                    continue
                # a landing needs walkable shore next to it
                shore = any(
                    0 <= r + dr < tm.rows and 0 <= c + dc < tm.cols
                    and tm.grid[r + dr][c + dc] not in ("W", "H")
                    for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if not shore:
                    continue
                d = abs(c - c0) + abs(r - r0)
                if best is None or d < best[0]:
                    best = (d, c, r)
        if best is not None:
            docks.append({"stop": stop["id"], "pos": (best[1], best[2])})
    return docks


def stamp_island(tm, r, c):
    """A blob of island beach/grass where an offshore stop sits."""
    rng = random.Random(r * 97 + c * 13)
    rad = 4 * MAP_SCALE
    for dr in range(-rad, rad + 1):
        for dc in range(-rad, rad + 1):
            if dr * dr + dc * dc > rad * rad * 0.75:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < tm.rows and 0 <= cc < tm.cols:
                edge = math.hypot(dr, dc)
                # sand only at the water's edge; the island inside is green
                if edge > rad * 0.82:
                    tm.grid[rr][cc] = "A"
                elif edge > rad * 0.62:
                    tm.grid[rr][cc] = "A" if rng.random() < 0.45 else "G"
                else:
                    tm.grid[rr][cc] = "G" if rng.random() < 0.94 else "A"
    return tm


def region_crop(tm, stop, w=46, h=34):
    from . import tiles as T
    c0, r0 = stop["pos"]
    ox = max(0, min(tm.cols - w, c0 - w // 2))
    oy = max(0, min(tm.rows - h, r0 - h // 2))
    crop = T.TileMap(w, h, fill="W")
    for r in range(h):
        for c in range(w):
            crop.grid[r][c] = tm.grid[oy + r][ox + c]
    return crop, ox, oy


def stop_pos(stop_id):
    for stop in _STOPS_WITH_PROLOGUE():
        if stop["id"] == stop_id:
            return stop["pos"]
    return None


# ------------------------------------------------------------------ scenery
# Signatures of life, scattered deterministically: palms on the sand,
# trees in the rainforest, huts and lamps where people live, fishing
# gear on working shores, plus one hand-placed set per stop.
# What grows where. One generic prop set everywhere makes the whole
# peninsula look like a park; each region gets the plants and buildings
# that actually stand there.
#   (terrain, chance, [(kind, variants)])
REGION_SCATTER = {
    "gulf_shore": (
        ("F", 0.010, [("windmill", 1)]),
        ("A", 0.028, [("palm", 3), ("rock", 2), ("boat", 1)]),
        ("G", 0.030, [("palm", 2), ("bush", 2), ("flowers", 2), ("banana", 1)]),
        ("H", 0.105, [("palm", 2), ("tree", 2), ("bigrock", 1)]),
        ("S", 0.035, [("rock", 2), ("mountain", 1)]),
        ("D", 0.026, [("lamp", 1), ("fence", 2), ("dryingrack", 1), ("market_stall", 1)]),
    ),
    "samui_sea": (
        ("F", 0.010, [("windmill", 1)]),
        ("A", 0.038, [("palm", 3), ("rock", 2), ("boat", 1)]),
        ("G", 0.034, [("palm", 2), ("banana", 2), ("bush", 2), ("flowers", 1)]),
        ("H", 0.110, [("tree", 2), ("bigrock", 1), ("palm", 1)]),
        ("S", 0.035, [("rock", 2), ("bigrock", 1)]),
        ("D", 0.028, [("lamp", 1), ("fence", 1), ("flowers", 1), ("market_stall", 1)]),
    ),
    "mangrove": (
        ("A", 0.034, [("mangrove", 3), ("rock", 1), ("boat", 1)]),
        ("G", 0.030, [("mangrove", 3), ("tree", 2), ("bush", 2)]),
        ("H", 0.125, [("mangrove", 2), ("tree", 2), ("bigrock", 1)]),
        ("S", 0.04, [("rock", 2), ("bigrock", 1)]),
        ("D", 0.032, [("stilt", 1), ("fence", 1), ("lamp", 1), ("market_stall", 1)]),
    ),
    "karst": (
        ("A", 0.022, [("palm", 2), ("rock", 2)]),
        ("G", 0.026, [("tree", 2), ("fern", 3), ("bush", 2), ("flowers", 1)]),
        ("H", 0.135, [("tree", 3), ("bigrock", 2), ("fern", 1)]),
        ("S", 0.055, [("karst", 1), ("rock", 2), ("mountain", 1)]),
        ("D", 0.026, [("lamp", 1), ("fence", 1), ("market_stall", 1)]),
    ),
    "pearl_coast": (
        ("A", 0.034, [("palm", 2), ("rock", 2), ("boat", 1)]),
        ("G", 0.030, [("shophouse", 2), ("palm", 1), ("bush", 2), ("flowers", 1)]),
        ("H", 0.110, [("tree", 2), ("bigrock", 1)]),
        ("S", 0.040, [("rock", 2), ("mountain", 1)]),
        ("D", 0.030, [("shophouse", 2), ("lamp", 2), ("fence", 1), ("flags", 1), ("market_stall", 1)]),
    ),
    "green_deep": (
        ("A", 0.022, [("rock", 2), ("fern", 2)]),
        ("G", 0.034, [("tree", 3), ("fern", 3), ("banana", 2), ("bush", 2)]),
        ("H", 0.145, [("tree", 3), ("fern", 2), ("bigrock", 2)]),
        ("S", 0.048, [("rock", 2), ("bigrock", 1), ("mountain", 1)]),
        ("D", 0.026, [("fence", 1), ("lamp", 1), ("flowers", 1), ("market_stall", 1)]),
    ),
    "sweet_islands": (
        ("F", 0.010, [("windmill", 1)]),
        ("A", 0.036, [("palm", 3), ("rock", 2), ("boat", 1)]),
        ("G", 0.038, [("rubber", 4), ("palm", 1), ("bush", 1)]),
        ("H", 0.115, [("tree", 2), ("rubber", 2), ("bigrock", 1)]),
        ("S", 0.035, [("rock", 2), ("mountain", 1)]),
        ("D", 0.038, [("hut", 1), ("lamp", 1), ("dryingrack", 1), ("fence", 1), ("market_stall", 1)]),
    ),
    "deep_south": (
        ("F", 0.010, [("windmill", 1)]),
        ("A", 0.028, [("palm", 2), ("rock", 1), ("boat", 1)]),
        ("G", 0.038, [("rubber", 3), ("spirit_house", 1), ("bush", 2)]),
        ("H", 0.12, [("tree", 2), ("rubber", 2), ("bigrock", 1)]),
        ("S", 0.040, [("rock", 2), ("mountain", 1)]),
        ("D", 0.028, [("mosque", 1), ("stupa", 1), ("hut", 1), ("lamp", 1), ("market_stall", 1)]),
    ),
}

# The heritage: what a southern Thai countryside is actually full of.
# Temples and chedis in the towns, spirit houses at the roads, Srivijaya
# ruins in the jungle, tin kilns in the old mining country, shadow-puppet
# stages at the festivals.
HERITAGE = {
    "gulf_shore": (
        ("A", 0.005, [("wat", 1), ("buddha", 1), ("shrine", 1)]),
        ("G", 0.0012, [("shrine", 1), ("buddha", 1)]),
        ("D", 0.0025, [("shrine", 1), ("flags", 1)]),
    ),
    "samui_sea": (
        ("A", 0.0045, [("wat", 1), ("buddha", 1), ("shrine", 1)]),
        ("G", 0.0012, [("shrine", 1), ("buddha", 1)]),
        ("D", 0.003, [("puppet_stage", 1), ("flags", 1)]),
    ),
    "mangrove": (
        ("A", 0.0035, [("shrine", 1), ("buddha", 1)]),
        ("G", 0.0012, [("shrine", 1), ("spirit_house", 1)]),
        ("H", 0.0018, [("carving", 1), ("ruin", 1)]),
        ("D", 0.002, [("shrine", 1)]),
    ),
    "karst": (
        ("A", 0.0035, [("buddha", 1), ("shrine", 1)]),
        ("G", 0.0008, [("shrine", 1)]),
        ("H", 0.003, [("carving", 1), ("ruin", 1), ("buddha", 1)]),
        ("S", 0.003, [("buddha", 1), ("carving", 1)]),
    ),
    "pearl_coast": (
        ("A", 0.004, [("wat", 1), ("shrine", 1)]),
        ("G", 0.0012, [("shrine", 1), ("spirit_house", 1)]),
        ("D", 0.004, [("shrine", 1), ("puppet_stage", 1)]),
    ),
    "green_deep": (
        ("A", 0.002, [("buddha", 1)]),
        ("G", 0.0012, [("shrine", 1), ("buddha", 1)]),
        ("H", 0.0035, [("ruin", 1), ("carving", 1), ("buddha", 1)]),
        ("D", 0.0015, [("shrine", 1)]),
    ),
    "sweet_islands": (
        ("A", 0.003, [("wat", 1), ("shrine", 1)]),
        ("G", 0.0012, [("shrine", 1), ("spirit_house", 1)]),
        ("H", 0.003, [("kiln", 1), ("ruin", 1), ("carving", 1)]),
        ("D", 0.002, [("shrine", 1), ("kiln", 1)]),
    ),
    "deep_south": (
        ("A", 0.0025, [("mosque", 1), ("buddha", 1)]),
        ("G", 0.0014, [("stupa", 1), ("spirit_house", 1), ("buddha", 1)]),
        ("H", 0.0024, [("ruin", 1), ("carving", 1)]),
        ("D", 0.0035, [("mosque", 1), ("stupa", 1), ("puppet_stage", 1)]),
    ),
}

# Homes and shrines belong to a village. Scattered along every road in
# the country they turn the whole map into a suburb; clustered around the
# towns they read as villages in a landscape.
SETTLEMENT_KINDS = {"hut", "shophouse", "spirit_house", "stilt", "wat",
                     "well", "lamp", "fence", "flags", "dryingrack",
                     "market_stall", "puppet_stage", "stupa", "mosque",
                     "kiln", "buddha", "ruin", "shrine", "carving",
                     "lighthouse"}

# the old flat set, used where a region is unknown
SCATTER = (
    ("A", 0.022, [("palm", 2), ("rock", 2)]),
    ("G", 0.026, [("bush", 2), ("flowers", 2), ("banana", 1), ("tree", 2)]),
    ("H", 0.110, [("tree", 2), ("bigrock", 1), ("bush", 1)]),
    ("S", 0.035, [("rock", 2), ("bigrock", 1), ("mountain", 1)]),
    ("D", 0.028, [("lamp", 1), ("fence", 1), ("flowers", 1), ("market_stall", 1)]),
)

# solid things you walk around, not through (never on roads or pins)
SOLID_KINDS = {"hut", "tree", "bigrock", "well", "stupa", "karst",
               "mosque", "lighthouse", "mountain", "wat", "mangrove",
               "rubber", "spirit_house", "shophouse", "stilt", "kiln",
               "puppet_stage", "ruin"}

# hand-placed dressing per stop: (kind, variant, tile-dx, tile-dy).
# Every stop gets its own face: stupas where the chedis stand, karsts
# where the cliffs rise, a mosque in Pattani, rubber rows in Trang.
DRESSING = {
    "chumphon": [("wat", 0, 0, -5), ("dryingrack", 0, -3, 1), ("hut", 0, 3, 2), ("lamp", 0, -2, -2)],
    "ko_tao": [("shrine", 0, 0, -4), ("fishtrap", 0, -2, 0), ("palm", 1, 2, 1), ("flowers", 0, 1, -2)],
    "ko_pha_ngan": [("shrine", 0, 0, -4), ("rock", 0, -2, -2), ("rock", 1, 2, -1), ("bush", 0, 0, 3)],
    "ko_samui": [("wat", 0, 0, -5), ("banana", 0, -3, 0), ("hut", 0, 3, 1), ("bigrock", 0, -1, -3)],
    "surat_thani": [("stupa", 0, 0, -5), ("stupa", 0, 0, -3), ("flags", 0, -3, 0), ("hut", 0, 3, 2)],
    "ranong": [("wat", 0, 0, -5), ("well", 0, 2, -2), ("hut", 0, -3, 1), ("flowers", 0, 1, 2)],
    "surin_islands": [("shrine", 0, 0, -4), ("hut", 0, -2, 1), ("fishtrap", 0, 2, 0)],
    "khao_lak": [("wat", 0, 0, -5), ("lamp", 0, -1, -2), ("flowers", 0, 2, 1), ("flowers", 0, -3, 0)],
    "similan": [("shrine", 0, 0, -4), ("bigrock", 0, -3, -1), ("bigrock", 0, 3, 0)],
    "phang_nga": [("wat", 0, 0, -5), ("karst", 0, -3, -2), ("karst", 0, 3, -1), ("hut", 0, 0, 3)],
    "phuket": [("shophouse", 1, 0, -5), ("shrine", 0, 2, -4), ("hut", 0, -3, -1), ("hut", 0, 3, -1), ("lamp", 0, 0, -3)],
    "promthep": [("lighthouse", 0, 0, -5), ("lamp", 0, -2, 0), ("rock", 0, 2, 1), ("flags", 0, 0, 3)],
    "ko_phi_phi": [("shrine", 0, 0, -4), ("karst", 0, -2, -1), ("rock", 1, 3, -1)],
    "krabi": [("wat", 0, 0, -5), ("karst", 0, -4, -1), ("shrine", 0, -2, -2), ("flags", 0, 2, -2), ("lamp", 0, 0, 2)],
    "nakhon": [("wat", 0, 0, -5), ("stupa", 0, 0, -3), ("flags", 0, -3, 0), ("hut", 0, 3, 2)],
    "phatthalung": [("puppet_stage", 0, 0, -5), ("hut", 0, -2, 2), ("fence", 0, 2, -1), ("lamp", 0, -1, -3)],
    "trang": [("mosque", 0, 0, -5), ("lighthouse", 0, -4, -2), ("tree", 0, -4, 0), ("tree", 1, -4, 2), ("tree", 0, 4, 0), ("stump", 0, -2, 1), ("hut", 0, 2, -3)],
    "ko_kradan": [("shrine", 0, 0, -4), ("boat", 0, 3, 0), ("palm", 0, -2, 0), ("palm", 1, 2, 1), ("flowers", 0, 0, -2)],
    "satun": [("shrine", 0, 0, -4), ("bigrock", 0, -3, 0), ("boat", 0, 3, 1), ("hut", 0, 1, 3)],
    "ko_lipe": [("shrine", 0, 0, -4), ("boat", 0, 3, 0), ("hut", 0, -3, 1)],
    "songkhla": [("wat", 0, 0, -5), ("lighthouse", 0, 3, -2), ("dryingrack", 0, 2, 1), ("hut", 0, -3, -1), ("lamp", 0, 1, -2)],
    "pattani": [("mosque", 0, 0, -5), ("mosque", 0, 0, 3), ("flags", 0, 2, -2), ("boat", 0, -3, 1)],
    "yala": [("shrine", 0, 0, -4), ("bigrock", 0, 0, -3), ("flowers", 0, -2, -1), ("hut", 0, 2, 2)],
    "narathiwat": [("wat", 0, 0, -5), ("flags", 0, -2, 0), ("hut", 0, 3, 1), ("lamp", 0, 0, -2)],
}


def grid_array(tm):
    """The tile grid as a numpy uint8 array, remembered per map.

    The grid is a list of lists of one-character strings, so this is the
    one place that has to pay for converting 7 million cells.
    """
    arr = tm.__dict__.get("_np_grid")
    if arr is None:
        import numpy as np
        arr = np.frombuffer(
            "".join("".join(row) for row in tm.grid).encode("ascii"),
            dtype=np.uint8).reshape(tm.rows, tm.cols)
        tm.__dict__["_np_grid"] = arr
    return arr


def region_ids(tm, cell=16):
    """A numpy array of the region id for every cell (index into REGIONS)."""
    arr = tm.__dict__.get("_np_region")
    if arr is not None:
        return arr
    import numpy as np
    from . import regions as RG
    grid = region_grid(tm, cell)
    ids = {rid: i for i, rid in enumerate(RG.REGIONS)}
    small = np.zeros((len(grid), len(grid[0])), dtype=np.uint8)
    for r, row in enumerate(grid):
        for c, rid in enumerate(row):
            small[r][c] = ids.get(rid, 0)
    big = np.repeat(np.repeat(small, cell, axis=0), cell, axis=1)
    big = big[:tm.rows, :tm.cols]
    tm.__dict__["_np_region"] = big
    return big


def _scatter_vectorised(tm, scatter, props, rng):
    """Scatter by terrain kind without walking every cell in Python.

    At 2400x3200 cells a cell-by-cell loop costs seconds at every
    start-up; picking the cells with numpy is instant. Each region has
    its own plants, so the peninsula is not one long lawn.
    """
    try:
        import numpy as np
        arr = grid_array(tm)
        rid_arr = region_ids(tm)
        gen = np.random.default_rng(1234)
        from . import regions as RG
        rids = list(RG.REGIONS)

        flat = arr.ravel()
        rflat = rid_arr.ravel()

        town_mask = settlement_mask(tm)

        def place(table, heritage=False):
            for i, rid in enumerate(rids):
                # the cells of this region, once
                rcells = np.flatnonzero(rflat == i)
                if rcells.size == 0:
                    continue
                for kind, chance, kinds in table:
                    sub = rcells[flat[rcells] == ord(kind)]
                    if sub.size == 0:
                        continue
                    picked = sub[gen.random(sub.size) < chance]
                    n = picked.size
                    if n == 0:
                        continue
                    rows = picked // tm.cols
                    cols = picked - rows * tm.cols
                    xs = (cols * 16 + 8).tolist()
                    ys = (rows * 16 + 8).tolist()
                    # the kind and the variant come from the CELL's own
                    # hash, so the same prop never clumps and no two
                    # neighbours look alike
                    hashes = ((rows * 73856093) ^ (cols * 19349663))
                    hashes = (hashes & 0x7FFFFFFF) % 100000
                    pick_idx = (hashes % len(kinds)).tolist()
                    var_idx = ((hashes // len(kinds)) % 6).tolist()
                    picks = [kinds[v][0] for v in pick_idx]
                    # rubber trees are planted in rows, so they are snapped
                    # onto a grid: the plantations read as plantations
                    for k, kind in enumerate(picks):
                        if kind == "rubber":
                            nx = (xs[k] // 48) * 48 + 24
                            ny = (ys[k] // 32) * 32 + 16
                            if tm.cell(ny // 16, nx // 16) not in ("W", "H"):
                                xs[k], ys[k] = nx, ny
                    variants = ([0] * n if heritage else var_idx)
                    # homes only stand in a village: a prop that belongs to
                    # a settlement is dropped if its cell is out in the
                    # country, so the map is villages in farmland
                    town_flat = town_mask.ravel()
                    keep = []
                    for k in range(n):
                        if picks[k] in SETTLEMENT_KINDS:
                            if not town_flat[picked[k]]:
                                continue
                        keep.append(k)
                    if not keep:
                        continue
                    props.extend(zip([xs[k] for k in keep], [ys[k] for k in keep],
                                     [picks[k] for k in keep],
                                     [variants[k] for k in keep]))

        for rid, table in REGION_SCATTER.items():
            place(table)
        # and the heritage on top: temples, chedis, ruins, spirit houses
        for rid, table in HERITAGE.items():
            place(table, heritage=True)
        return
    except Exception:
        pass
    for r in range(tm.rows):
        for c in range(tm.cols):
            entry = scatter.get(tm.grid[r][c])
            if entry is None:
                continue
            chance, kinds = entry
            if rng.random() >= chance:
                continue
            pick, variants = kinds[rng.randrange(len(kinds))]
            props.append((c * 16 + 8, r * 16 + 8, pick, rng.randrange(variants)))


def landmark_spots(tm):
    """Where every landmark stands, in tile coordinates.

    A landmark is pinned to a town and an offset from it; if the sea has
    moved since the map was drawn the marker is nudged onto the nearest
    walkable tile so it is always reachable on foot.
    """
    from . import landmarks as LM
    from . import story as ST
    out = []
    for region, marks in LM.LANDMARKS.items():
        for mark in marks:
            stop = ST.STOP_BY_ID.get(mark["stop"])
            if stop is None:
                continue
            c0, r0 = stop["pos"]
            dx, dy = mark["at"]
            c, r = c0 + dx, r0 + dy
            c, r = _nearest_walkable(tm, c, r)
            out.append({
                "id": mark["id"],
                "name": mark["name"],
                "region": region,
                "stop": mark["stop"],
                "pos": (c, r),
                "story": mark["story"],
                "card": mark.get("card", mark["name"]),
            })
    return out


def _nearest_walkable(tm, c, r, reach=40):
    """The closest tile you can actually stand on."""
    if 0 <= r < tm.rows and 0 <= c < tm.cols and tm.grid[r][c] in ("G", "A", "D", "S"):
        return c, r
    for radius in range(1, reach):
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if max(abs(dr), abs(dc)) != radius:
                    continue
                cc, rr = c + dc, r + dr
                if 0 <= rr < tm.rows and 0 <= cc < tm.cols \
                        and tm.grid[rr][cc] in ("G", "A", "D", "S"):
                    return cc, rr
    return c, r


def chunk_props(props, chunk=16):
    """Group props into chunks of ``chunk`` tiles.

    The world holds tens of thousands of props; walking all of them each
    frame is what made the game stutter. The scene asks only for the
    chunks under the camera.
    """
    size = chunk * 16
    out = {}
    for x, y, kind, variant in props:
        key = (int(x) // size, int(y) // size)
        bucket = out.get(key)
        if bucket is None:
            out[key] = [(x, y, kind, variant)]
        else:
            bucket.append((x, y, kind, variant))
    return out


_region_grid = None


def region_grid(tm, cell=16):
    """A coarse grid of which region each part of the world is in.

    Regions are decided by the nearest town, so the grid is built once
    at a low resolution (16x16 tiles a cell) and the scatter looks it up.
    """
    global _region_grid
    if _region_grid is not None:
        return _region_grid
    from . import regions as RG
    from . import story as ST
    cols = (tm.cols + cell - 1) // cell
    rows = (tm.rows + cell - 1) // cell
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            wx = c * cell * 16 + cell * 8
            wy = r * cell * 16 + cell * 8
            row.append(RG.region_for_position(wx, wy, ST.STOPS, 16))
        grid.append(row)
    _region_grid = grid
    return grid


SCENERY_VERSION = 2


def _scenery_cache_path():
    try:
        from . import options as O
        os.makedirs(O.CONFIG_DIR, exist_ok=True)
        return os.path.join(O.CONFIG_DIR,
                            "scenery_%dx%d_v%d.bin" % (WORLD_COLS, WORLD_ROWS,
                                                      SCENERY_VERSION))
    except Exception:
        return None


def settlement_mask(tm, radius=8):
    """True for the tiles that belong to a town (and its outskirts)."""
    mask = tm.__dict__.get("_settlement_mask")
    if mask is not None:
        return mask
    import numpy as np
    from . import story as ST
    out = np.zeros((tm.rows, tm.cols), dtype=bool)
    for stop in ST.STOPS + [ST.PROLOGUE]:
        c0, r0 = stop["pos"]
        r_lo = max(0, r0 - radius)
        r_hi = min(tm.rows - 1, r0 + radius)
        c_lo = max(0, c0 - radius)
        c_hi = min(tm.cols - 1, c0 + radius)
        for rr in range(r_lo, r_hi + 1):
            dr = rr - r0
            for cc in range(c_lo, c_hi + 1):
                if abs(rr - r0) + abs(cc - c0) <= radius:
                    out[rr][cc] = True
    tm.__dict__["_settlement_mask"] = out
    return out


def scenery(tm):
    """Scatter props over the world.

    Returns ``(props, blocked)``: ``props`` is a list of
    ``(x_px, y_px, kind, variant)`` (x/y = base of the prop) and
    ``blocked`` is a set of ``(col, row)`` tiles solid things stand on.
    Deterministic — the same seed, the same South — so it is built once
    and kept on disk, because it is a lot of props to make every time.
    """
    global _SCENERY_CACHE
    if _SCENERY_CACHE is not None:
        return _SCENERY_CACHE
    path = _scenery_cache_path()
    if path and os.path.exists(path):
        try:
            import struct
            with open(path, "rb") as fh:
                blob = fh.read()
            count = struct.unpack_from("<I", blob, 0)[0]
            props = []
            off = 4
            names = _PROP_NAMES
            index = {n: i for i, n in enumerate(names)}
            for _ in range(count):
                x, y, k, v = struct.unpack_from("<HHBB", blob, off)
                off += 6
                props.append((x, y, names[k], v))
            blocked = _blocked_from(tm, props)
            _SCENERY_CACHE = (props, blocked)
            return _SCENERY_CACHE
        except Exception:
            pass
    _SCENERY_CACHE = _build_scenery(tm)
    if path:
        try:
            import struct
            index = {n: i for i, n in enumerate(_PROP_NAMES)}
            out = bytearray()
            for x, y, kind, variant in _SCENERY_CACHE[0]:
                out += struct.pack("<HHBB", int(x), int(y),
                                   index.get(kind, 0), int(variant) % 256)
            with open(path, "wb") as fh:
                fh.write(struct.pack("<I", len(_SCENERY_CACHE[0])))
                fh.write(bytes(out))
        except Exception:
            pass
    return _SCENERY_CACHE


_PROP_NAMES = ["palm", "rock", "boat", "bush", "flowers", "banana", "tree",
               "bigrock", "mountain", "lamp", "fence", "dryingrack", "hut",
               "market_stall", "windmill",
               "mangrove", "rubber", "spirit_house", "shophouse", "fern",
               "stilt", "wat", "buddha", "ruin", "puppet_stage", "carving",
               "kiln", "stupa", "mosque", "shrine", "karst", "well",
               "fishtrap", "flags", "boat"]


def _blocked_from(tm, props):
    """The tiles that solid things stand on."""
    blocked = set()
    for x, y, kind, _variant in props:
        if kind in SOLID_KINDS:
            c, r = int(x) // 16, int(y) // 16
            if tm.grid[r][c] == "D":
                continue                # buildings face the road, not on it
            blocked.add((c, r))
    return blocked


_SCENERY_CACHE = None


def _build_scenery(tm):
    from . import story as ST
    rng = random.Random(1234)
    props = []
    scatter = {kind: (chance, kinds) for kind, chance, kinds in SCATTER}
    _scatter_vectorised(tm, scatter, props, rng)
    for stop in ST.STOPS:
        c0, r0 = stop["pos"]
        for kind, variant, dx, dy in DRESSING.get(stop["id"], []):
            c, r = c0 + sc(dx), r0 + sc(dy)
            if not (0 <= r < tm.rows and 0 <= c < tm.cols):
                continue
            if tm.grid[r][c] == "W":
                continue
            props.append((c * 16 + 8, r * 16 + 8, kind, variant))

    blocked = set()
    for x, y, kind, _variant in props:
        if kind in SOLID_KINDS:
            c, r = int(x) // 16, int(y) // 16
            if tm.grid[r][c] == "D":
                continue                # buildings face the road, not on it
            blocked.add((c, r))

    # never wall off a pin, a host, or Yaai's doorstep
    for stop in ST.STOPS + [ST.PROLOGUE]:
        c0, r0 = stop["pos"]
        for dc in range(-2, 3):
            for dr in range(-2, 3):
                blocked.discard((c0 + dc, r0 + dr))
    for x, y in _host_tiles(ST):
        blocked.discard((x, y))
    return props, blocked


def _host_tiles(ST):
    """Tile coords the hosts stand on (kept walkable)."""
    out = []
    for stop in ST.STOPS:
        c, r = stop["pos"]
        out.append((c + sc(1), r))
        out.append((c + sc(2), r))
    return out


def _STOPS_WITH_PROLOGUE():
    from . import story as ST
    return ST.STOPS + [ST.PROLOGUE]


def grid_ascii(tm, step=4):
    kinds = {"G": ".", "D": ":", "A": "~", "S": "+", "W": "=", "H": "#",
             "T": "t", "U": "u", "R": "/", "E": "e", "P": "o",
             "F": "f"}
    out = []
    for r in range(0, tm.rows, step):
        out.append("".join(kinds[tm.grid[r][c]] for c in range(0, tm.cols, step)))
    return "\n".join(out)
