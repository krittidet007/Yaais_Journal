"""Full-screen brightness / contrast post-processing.

Uses numpy for a fast 256-entry lookup table when available; otherwise falls
back to a plain additive brightness nudge (contrast needs per-pixel maths).
"""

import pygame

try:
    import numpy as _np
except Exception:                              # pragma: no cover - optional dep
    _np = None

_lut_cache = {}


def available():
    return _np is not None


def _lut(brightness, contrast):
    key = (brightness, contrast)
    lut = _lut_cache.get(key)
    if lut is not None:
        return lut
    c = contrast / 100.0
    offset = (brightness - 100) * 2.55
    lut = _np.empty(256, dtype=_np.uint8)
    for i in range(256):
        value = (i - 128) * c + 128 + offset
        lut[i] = 0 if value < 0 else (255 if value > 255 else int(value))
    _lut_cache[key] = lut
    return lut


def apply(surface, brightness, contrast):
    if brightness == 100 and contrast == 100:
        return surface
    if _np is None:
        return _fallback(surface, brightness)
    out = surface.copy()
    pixels = pygame.surfarray.pixels3d(out)
    pixels[:] = _lut(brightness, contrast)[pixels]
    del pixels
    return out


def _fallback(surface, brightness):
    delta = brightness - 100
    if delta == 0:
        return surface
    out = surface.copy()
    amount = min(255, abs(delta) * 2)
    color = (amount, amount, amount)
    if delta > 0:
        out.fill(color, special_flags=pygame.BLEND_RGB_ADD)
    else:
        out.fill(color, special_flags=pygame.BLEND_RGB_SUB)
    return out
