"""The light pass — one place where the frame's mood is decided.

Three cheap layers over the finished scene:

1. **ambient** — a colour multiplied over the whole frame. This is what
   makes a mangrove feel green-gold and a karst feel cold: one multiply
   of a 640x320 surface, no per-object work.
2. **lights** — additive pools from lamps, fires, beacons and the spirit.
   Real falloff, so a lantern lights the ground around it and leaves the
   distance dark.
3. **haze** — the air of the place (sea mist, rubber smoke, highland fog)
   and a small final colour grade.

Everything is cached, so the whole pass costs a couple of blits a frame.
"""

import pygame

from . import regions as R

_radial_cache = {}
_fog_cache = {}


def _radial(radius, color):
    """A soft white-ish disc, cached per (radius, colour)."""
    key = (int(radius), color)
    surf = _radial_cache.get(key)
    if surf is not None:
        return surf
    r = max(2, int(radius))
    size = r * 2 + 2
    disc = pygame.Surface((size, size), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        f = 1.0 - (i / float(r))
        alpha = int(255 * (f ** 1.7))
        pygame.draw.circle(disc, (color[0], color[1], color[2], alpha),
                           (r + 1, r + 1), i)
    _radial_cache[key] = disc
    return disc


def _fog_surface(size, color, alpha):
    """A soft haze that thickens toward the bottom of the frame."""
    key = (size, color, alpha)
    surf = _fog_cache.get(key)
    if surf is not None:
        return surf
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        f = (y / float(max(1, h - 1)))
        a = int(alpha * (0.35 + 0.65 * f))
        pygame.draw.line(surf, (color[0], color[1], color[2], a), (0, y), (w, y))
    _fog_cache[key] = surf
    return surf


def apply(surface, region_id, lights=(), night=0.0, grade=None):
    """Grade the finished frame for a region.

    ``lights`` is a sequence of ``(x, y, radius, strength)`` in *screen*
    coordinates. ``night`` (0..1) deepens the ambient toward blue.
    """
    reg = R.REGIONS.get(region_id) or R.REGIONS[R.DEFAULT_REGION]
    size = surface.get_size()

    # ---------------------------------------------------- 1. ambient tint
    amb = list(reg["ambient"])
    if night > 0.0:
        # night pulls every colour toward the blue of the Gulf night
        amb = [int(c * (1.0 - 0.55 * night) + 26 * night) for c in amb]
        amb = [min(255, int(c * 0.86 + 14)) for c in amb]
    layer = pygame.Surface(size, pygame.SRCALPHA)
    layer.fill((amb[0], amb[1], amb[2], 255))
    surface.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    # ------------------------------------------------------- 2. light pools
    if lights:
        buf = pygame.Surface(size, pygame.SRCALPHA)
        lamp = reg["light"]
        for item in lights:
            x, y, radius, strength = item
            strength = float(strength)
            if strength <= 0.01:
                continue
            col = (min(255, int(lamp[0] * strength)),
                   min(255, int(lamp[1] * strength)),
                   min(255, int(lamp[2] * strength)))
            disc = _radial(radius, col)
            buf.blit(disc, (int(x - disc.get_width() / 2),
                            int(y - disc.get_height() / 2)))
        surface.blit(buf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # ------------------------------------------------------------- 3. haze
    fog_col, fog_alpha = reg["fog"]
    if night > 0.35:
        fog_alpha = int(fog_alpha * 1.4)
    if fog_alpha > 0:
        surface.blit(_fog_surface(size, fog_col, fog_alpha), (0, 0))

    # ------------------------------------------------------------- 4. grade
    sat, temp = reg["grade"]
    if grade is not None:
        sat, temp = grade
    if abs(sat - 1.0) > 0.01 or abs(temp) > 0.01:
        _grade(surface, sat, temp)
    return surface


_grade_luts = {}


def _grade_lut(sat, temp):
    """A 16x16x16 colour cube for the final grade.

    Building the cube once and indexing it is far cheaper than doing
    float maths on every pixel of every frame.
    """
    key = (round(sat, 3), round(temp, 3))
    lut = _grade_luts.get(key)
    if lut is not None:
        return lut
    try:
        import numpy as np
        steps = 16
        axis = np.linspace(0, 255, steps, dtype=np.float32)
        r, g, b = np.meshgrid(axis, axis, axis, indexing="ij")
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        r = lum + (r - lum) * sat
        g = lum + (g - lum) * sat
        b = lum + (b - lum) * sat
        r = np.clip(r + temp * 255.0, 0, 255)
        b = np.clip(b - temp * 255.0, 0, 255)
        g = np.clip(g, 0, 255)
        lut = np.stack([r, g, b], axis=-1).astype(np.uint8)
        _grade_luts[key] = lut
        return lut
    except Exception:
        _grade_luts[key] = None
        return None


def _grade(surface, sat, temp):
    """A gentle saturation + temperature pass (numpy when available)."""
    if abs(sat - 1.0) < 0.005 and abs(temp) < 0.005:
        return
    try:
        import numpy as np
    except ImportError:
        return
    lut = _grade_lut(sat, temp)
    if lut is None:
        return
    try:
        arr = pygame.surfarray.pixels3d(surface)
        idx = ((arr[:, :, 0].astype(np.uint16) >> 4) << 8) | \
              ((arr[:, :, 1].astype(np.uint16) >> 4) << 4) | \
              (arr[:, :, 2].astype(np.uint16) >> 4)
        arr[:] = lut.reshape(-1, 3)[idx]
    except Exception:
        pass
