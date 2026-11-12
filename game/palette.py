"""Colour science for the pixel-art pipeline.

Real pixel art almost never lightens/darkens a colour evenly (that is what makes
flat shapes look like HTML). Instead shadows are pulled toward cool blue/purple and
highlights toward warm yellow, saturation rises in the mid-tones, and gradients are
broken up with an ordered (Bayer) dither so banding reads as texture.
"""

import colorsys

# 4x4 ordered dither matrix (values 0..15)
BAYER4 = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)


def _clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def rgb(t):
    return (int(t[0]), int(t[1]), int(t[2]))


def rgb01(t):
    return (int(t[0] * 255), int(t[1] * 255), int(t[2] * 255))


def mix(a, b, t):
    t = _clamp(t)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(color, amount):
    """amount < 0 darkens toward cool, amount > 0 lightens toward warm."""
    c = colorsys.rgb_to_hsv(*[v / 255.0 for v in color[:3]])
    h, s, v = c
    if amount < 0:
        k = _clamp(-amount)
        h = _toward(h, 0.66, 0.16 * k)
        s = _clamp(s * (1 + 0.18 * k))
        v = _clamp(v * (1 - 0.55 * k))
    else:
        k = _clamp(amount)
        h = _toward(h, 0.13, 0.14 * k)
        s = _clamp(s * (1 - 0.18 * k))
        v = _clamp(v + (1 - v) * 0.62 * k)
    return rgb01(colorsys.hsv_to_rgb(h, s, v))


def _toward(h, target, amount):
    d = (target - h + 0.5) % 1.0 - 0.5
    return (h + d * amount) % 1.0


def ramp(base, n=5, dark_hue=0.66, light_hue=0.12, pull=0.16):
    """A shading ramp from darkest (index 0) to lightest (index n-1)."""
    h, s, v = colorsys.rgb_to_hsv(*[c / 255.0 for c in base[:3]])
    out = []
    for i in range(n):
        f = i / (n - 1.0)
        if f < 0.5:
            k = (0.5 - f) / 0.5
            hh = _toward(h, dark_hue, pull * k)
            ss = _clamp(s * (1 + 0.22 * k))
            vv = v * (0.40 + 0.60 * (f / 0.5))
        else:
            k = (f - 0.5) / 0.5
            hh = _toward(h, light_hue, pull * k)
            ss = _clamp(s * (1 - 0.22 * k))
            vv = v + (1 - v) * 0.66 * k
        out.append(rgb01(colorsys.hsv_to_rgb(hh, ss, vv)))
    return out


def hexc(color):
    return "#%02x%02x%02x" % rgb(color)


def luminance(color):
    r, g, b = color[:3]
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
