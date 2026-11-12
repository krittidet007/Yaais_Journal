#!/usr/bin/env python3
"""Render the game icon set from the game's own pixel art.

Produces (in installer/icons/):
    icon-<size>.png   square PNGs at every size we pack
    icon.ico          Windows icon (PNG-compressed entries, Vista+)
    icon.icns         macOS icon (PNG-compressed ic07..ic14 chunks)

No PIL needed: both containers can embed PNG data, which we write by hand.
Run from the repo root:   .venv/bin/python installer/make_icons.py
"""

import os
import struct
import sys
import zlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from game import artgen as A  # noqa: E402
from game import pixel, views  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)
ICNS_ENTRIES = (  # (chunk type, pixel size)
    ("ic07", 128), ("ic08", 256), ("ic09", 512), ("ic10", 512),
    ("ic11", 32), ("ic12", 64), ("ic13", 256), ("ic14", 512),
)


def render_master(size=256):
    """A dusk scene: karst silhouettes, palms, the spirit and the lost page."""
    s = pygame.Surface((size, size))
    r = s.get_rect()
    # dusk sky, brighter low like the cover
    sky = [(30, 28, 58), (58, 38, 70), (108, 58, 72), (168, 84, 72),
           (226, 148, 94), (244, 180, 118)]
    pixel.vgradient(s, r, sky)
    # stars
    for i in range(26):
        x = int(A._rng(i, 2) * size)
        y = int(A._rng(i, 5) * size * 0.45)
        s.set_at((min(x, size - 1), y), (206, 220, 244))
    # sea
    horizon = int(size * 0.62)
    s.fill((28, 44, 62), pygame.Rect(0, horizon, size, size - horizon))
    for i in range(3):                      # shimmer bands
        y = horizon + 4 + i * 5
        pygame.draw.rect(s, (54, 84, 104), pygame.Rect(
            int(size * 0.1 + i * 7), y, int(size * 0.35 - i * 6), 2))
    # karst towers on the horizon (the South's limestone sentinels)
    for i, (x, sc) in enumerate(((0.18, 0.8), (0.30, 1.0), (0.44, 0.7),
                                 (0.70, 0.9), (0.83, 0.65))):
        k = views._silhouette(A.karst())
        k = pygame.transform.scale(k, (int(k.get_width() * sc * size / 256),
                                       int(k.get_height() * sc * size / 256)))
        views.blit_base(s, k, x * size, horizon - 1)
    # palms + a hut, close to shore
    for surf, fx in ((A.palm(0), 0.10), (A.palm(1), 0.16), (A.hut(False), 0.92)):
        sil = views._silhouette(surf)
        sil = pygame.transform.scale(sil, (int(sil.get_width() * size / 256),
                                           int(sil.get_height() * size / 256)))
        views.blit_base(s, sil, fx * size, horizon - 2)
    # the spirit (Noi's guiding light) with the glowing lost page
    cx, cy = int(size * 0.52), int(size * 0.55)
    # the journal page: warm parchment, catching the light
    pw, ph = int(size * 0.30), int(size * 0.38)
    page = pygame.Rect(cx - pw // 2, cy - ph // 2 - int(size * 0.02), pw, ph)
    pixel.add_glow(s, page.center, int(size * 0.30), (255, 226, 150), max_alpha=150)
    s.fill((240, 226, 190), page)
    s.fill((216, 196, 156), pygame.Rect(page.x + 2, page.y + 2, pw - 4, ph - 4))
    # ruled lines — it is a journal after all
    for i in range(5):
        yy = page.y + int(ph * (0.28 + i * 0.13))
        s.fill((150, 130, 100), pygame.Rect(page.x + int(pw * 0.18), yy,
                                           int(pw * 0.64), max(1, size // 128)))
    # a magpie feather pinned on the corner — the storm thief's calling card
    s.fill((30, 30, 38), pygame.Rect(page.right - int(pw * 0.22),
                                     page.y + int(ph * 0.12),
                                     max(2, size // 64), max(4, size // 32)))
    # the spirit hovers above the page, blessing the find
    sp = pygame.transform.scale(A.spirit(0), (size // 4, size // 4))
    pixel.add_glow(s, (cx, page.top - int(size * 0.06)), int(size * 0.16),
                   (90, 235, 220), max_alpha=120)
    s.blit(sp, sp.get_rect(center=(cx, page.top - int(size * 0.06))))
    # gold frame, like the journal's cloth cover
    pygame.draw.rect(s, (232, 198, 110), r, max(2, size // 48))
    return s


def png_bytes(surface):
    raw = pygame.image.tobytes(surface, "RGBA")
    w, h = surface.get_size()

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(
            ">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    stride = w * 4
    body = b"".join(b"\x00" + raw[y * stride:(y + 1) * stride] for y in range(h))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(body, 9)) + chunk(b"IEND", b""))


def pack_ico(pngs):
    """pngs: {size: bytes} -> Windows .ico with PNG entries."""
    sizes = sorted(pngs)
    header = struct.pack("<HHH", 0, 1, len(sizes))
    entries, blobs = [], []
    off = 6 + 16 * len(sizes)
    for sz in sizes:
        data = pngs[sz]
        entries.append(struct.pack("<BBBBHHII", 0 if sz >= 256 else sz,
                                   0 if sz >= 256 else sz, 0, 0, 1, 32,
                                   len(data), off))
        blobs.append(data)
        off += len(data)
    return header + b"".join(entries) + b"".join(blobs)


def pack_icns(pngs):
    """pngs: {size: bytes} -> macOS .icns with PNG-compressed chunks."""
    chunks = []
    for tag, sz in ICNS_ENTRIES:
        data = pngs.get(sz)
        if data:
            chunks.append(tag.encode("ascii") + struct.pack(">I", 8 + len(data)) + data)
    body = b"".join(chunks)
    return b"icns" + struct.pack(">I", 8 + len(body)) + body


def main():
    os.makedirs(OUT, exist_ok=True)
    master = render_master(256)
    wanted = sorted(set(ICO_SIZES) | {sz for _t, sz in ICNS_ENTRIES})
    pngs = {}
    for sz in wanted:
        surf = pygame.transform.scale(master, (sz, sz)) if sz != 256 else master
        data = png_bytes(surf)
        pngs[sz] = data
        with open(os.path.join(OUT, "icon-%d.png" % sz), "wb") as fh:
            fh.write(data)
    with open(os.path.join(OUT, "icon.ico"), "wb") as fh:
        fh.write(pack_ico({k: pngs[k] for k in ICO_SIZES if k in pngs}))
    with open(os.path.join(OUT, "icon.icns"), "wb") as fh:
        fh.write(pack_icns(pngs))
    print("wrote %s (ico %dB, icns %dB)"
          % (OUT, os.path.getsize(os.path.join(OUT, "icon.ico")),
             os.path.getsize(os.path.join(OUT, "icon.icns"))))


if __name__ == "__main__":
    pygame.display.init()
    main()
