"""Low-resolution pixel rendering helpers.

Everything is drawn to a small internal canvas (640x320) and upscaled with
nearest-neighbour, so every pixel is a deliberate, chunky block.
"""

import os

import pygame

from . import options as _options

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
FONT_PATH = os.path.join(ASSET_DIR, "fonts", "PressStart2P.ttf")

_font_cache = {}
_falloff_cache = {}
_vignette_cache = {}


def font(size=8):
    if size not in _font_cache:
        if os.path.exists(FONT_PATH):
            _font_cache[size] = pygame.font.Font(FONT_PATH, size)
        else:
            _font_cache[size] = pygame.font.Font(None, size + 2)
    return _font_cache[size]


def text_size(string, size=8):
    return font(size).size(string)


def draw_text(surface, string, pos, color, size=8, shadow=(10, 8, 16)):
    """Crisp (non-antialiased) pixel text with a 1px drop shadow."""
    f = font(size)
    if shadow:
        surface.blit(f.render(string, False, shadow), (pos[0] + 1, pos[1] + 1))
    surface.blit(f.render(string, False, color), pos)


def wrap(string, max_px, size=8):
    f = font(size)
    lines = []
    for paragraph in string.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if f.size(candidate)[0] <= max_px:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    return lines


# ------------------------------------------------------------------- lighting
def _falloff(radius, strength):
    key = ("falloff", radius, round(strength, 2))
    if key in _falloff_cache:
        return _falloff_cache[key]
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    surf.fill((255, 255, 255, 255))
    inner = int(255 * (1.0 - strength))
    for r in range(radius, 0, -1):
        t = r / float(radius)
        a = int(inner + (255 - inner) * (t ** 0.75))
        pygame.draw.circle(surf, (255, 255, 255, a), (radius, radius), r)
    _falloff_cache[key] = surf
    return surf


def light_mask(size, lights):
    """Per-pixel darkness multiplier: 0 alpha where fully lit, 255 where dark."""
    mask = pygame.Surface(size, pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    for x, y, radius, strength in lights:
        g = _falloff(radius, strength)
        mask.blit(g, (int(x - radius), int(y - radius)), special_flags=pygame.BLEND_RGBA_MIN)
    return mask


def add_glow(surface, center, radius, color, max_alpha=170):
    key = ("glow", radius, color, max_alpha)
    if key not in _falloff_cache:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -1):
            a = int(max_alpha * (1.0 - r / float(radius)) ** 1.7)
            pygame.draw.circle(surf, (*color, a), (radius, radius), r)
        _falloff_cache[key] = surf
    surface.blit(_falloff_cache[key], (int(center[0] - radius), int(center[1] - radius)),
                 special_flags=pygame.BLEND_RGBA_ADD)


def vignette(size, strength=110):
    key = ("vig", size, strength)
    if key in _vignette_cache:
        return _vignette_cache[key]
    small_w, small_h = max(size[0] // 8, 2), max(size[1] // 8, 2)
    small = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
    cx, cy = (small_w - 1) / 2.0, (small_h - 1) / 2.0
    max_d = (cx ** 2 + cy ** 2) ** 0.5
    for y in range(small_h):
        for x in range(small_w):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / max_d
            a = int(strength * max(0.0, (d - 0.55) / 0.45) ** 1.6)
            small.set_at((x, y), (6, 8, 16, min(a, 255)))
    vig = pygame.transform.smoothscale(small, size)
    _vignette_cache[key] = vig
    return vig


def atmosphere(surface, lights, dark=150, dark_color=(10, 14, 32), tint=None, vignette_strength=110):
    """Apply warm glows, then a darkness layer with holes at each light."""
    if not _options.options.vignette_on():
        vignette_strength = 0
    for x, y, radius, strength in lights:
        add_glow(surface, (x, y), radius, (255, 196, 120), max_alpha=int(90 * strength))
    if dark > 0:
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        layer.fill((*dark_color, dark))
        layer.blit(light_mask(surface.get_size(), lights), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(layer, (0, 0))
    if tint:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill(tint)
        surface.blit(overlay, (0, 0))
    if vignette_strength > 0:
        surface.blit(vignette(surface.get_size(), vignette_strength), (0, 0))


def panel(surface, rect, fill, border, inner_highlight=None):
    pygame.draw.rect(surface, border, rect)
    pygame.draw.rect(surface, fill, rect.inflate(-2, -2))
    if inner_highlight:
        pygame.draw.line(surface, inner_highlight, (rect.left + 1, rect.top + 1), (rect.right - 2, rect.top + 1))


# --------------------------------------------------------------- dithering
BAYER4 = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)


def dither_rect(surface, rect, color_a, color_b, ratio=0.5):
    """Fill with a Bayer-dithered blend of two colours (ratio = share of color_b)."""
    for y in range(rect.top, rect.bottom):
        for x in range(rect.left, rect.right):
            threshold = (BAYER4[(y - rect.top) % 4][(x - rect.left) % 4] + 0.5) / 16.0
            surface.set_at((x, y), color_b if ratio > threshold else color_a)


def vgradient(surface, rect, colors, dither=True):
    """Vertical gradient through a list of colours, dithered between stops."""
    n = len(colors)
    if n == 1:
        pygame.draw.rect(surface, colors[0], rect)
        return
    for y in range(rect.top, rect.bottom):
        f = (y - rect.top) / max(1, rect.height - 1) * (n - 1)
        i = min(n - 2, int(f))
        local = f - i
        c0, c1 = colors[i], colors[i + 1]
        for x in range(rect.left, rect.right):
            if dither:
                threshold = (BAYER4[(y - rect.top) % 4][(x - rect.left) % 4] + 0.5) / 16.0
                color = c1 if local > threshold else c0
            else:
                color = c1 if local >= 0.5 else c0
            surface.set_at((x, y), color)


def flicker(t, seed=0.0, low=0.82):
    """Organic 0.82..1.0 flicker for lamps, candles and fireflies."""
    import math
    wave = 0.5 + 0.5 * math.sin(t * 7.3 + seed)
    jitter = 0.5 + 0.5 * math.sin(t * 17.1 + seed * 2.3) * 0.5
    return low + (1 - low) * (0.6 * wave + 0.4 * jitter)


def reflection(surface, x, y, height, color, t, seed=0.0):
    """A wobbling vertical light streak, for lights seen on water."""
    import math
    for i in range(height):
        wobble = int(math.sin(t * 3 + i * 0.7 + seed) * 2)
        ratio = (1 - i / float(height)) ** 1.4
        threshold = (BAYER4[i % 4][(x + wobble) % 4] + 0.5) / 16.0
        if ratio > threshold:
            px = x + wobble
            yy = y + i
            if 0 <= px < surface.get_width() and 0 <= yy < surface.get_height():
                existing = surface.get_at((px, yy))
                blend = mix(existing, (*color, 255), 0.45)
                surface.set_at((px, yy), (blend[0], blend[1], blend[2]))
    del seed


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
