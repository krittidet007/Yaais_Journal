"""Scene composition.

The hub, shrine, well and epilogue scenes share ONE tall valley world
(``tiles.big_map``, 30x30 tiles + a dusk sky strip at its north end) so
progress (shrine lit, well water drawn) stays visible as the **camera
follows the player**. Travel is mostly along Y: north, past the mountain
lake, is the shrine terrace under the sky; the village sits mid-valley; a
river cuts across the south toward a big lake.

Scenes are built in layers:

  sky (world-top gradient + sun + drifting clouds) -> hills -> ground -> back
  props -> characters (depth-sorted) -> front props -> particles -> atmosphere

``Camera`` scrolls a 640x320 view over the world; everything world-anchored
is offset by the camera, screen HUD/backdrops stay fixed. Static props are
split into back/front layers so characters walking past houses/wells are
occluded correctly.
"""

import math

import pygame

from . import artgen as A
from . import options as O
from . import palette as P
from . import pixel
from . import settings as S
from . import tiles as T

W, H = S.INTERNAL_W, S.INTERNAL_H
GROUND_Y = 62            # world y where the terrain begins (the horizon line)
SKY_H = 96               # world-top sky/hills strip, scrolled away going south

WORLD_W = T.BIG_COLS * T.TILE
WORLD_H = GROUND_Y + T.BIG_ROWS * T.TILE
CAM_MAX_X = max(0, WORLD_W - W)
CAM_MAX_Y = max(0, WORLD_H - H)


class Camera:
    """Smooth clamp-follow camera over the tall world.

    ``max_x``/``max_y`` override the default village-world bounds so
    the same camera works for the open world.
    """

    def __init__(self, max_x=None, max_y=None):
        self.x = 0.0
        self.y = 0.0
        self.max_x = CAM_MAX_X if max_x is None else max_x
        self.max_y = CAM_MAX_Y if max_y is None else max_y

    def follow(self, tx, ty, dt, snap=5.0):
        k = min(1.0, dt * snap)
        self.x += (tx - W / 2 - self.x) * k
        self.y += (ty - H / 2 - self.y) * k
        self.clamp()

    def snap_to(self, x, y):
        self.x = x - W / 2
        self.y = y - H / 2
        self.clamp()

    def clamp(self):
        self.x = max(0.0, min(self.max_x, self.x))
        self.y = max(0.0, min(self.max_y, self.y))

    def offset(self):
        return int(self.x), int(self.y)


def _off(cam):
    """Accept either a Camera or a plain (ox, oy) tuple."""
    if hasattr(cam, "offset"):
        return cam.offset()
    return (int(cam[0]), int(cam[1]))


def anchor(c, r):
    """Feet-anchor px for a prop standing on tile (col, row)."""
    return (c * T.TILE + 8, GROUND_Y + (r + 1) * T.TILE)


# The big-world layout. Prop positions are feet anchors on the tile map.
VILLAGE = {
    "huts_front": [anchor(8, 8), anchor(19, 8)],
    "huts_back": [anchor(13, 6)],
    "flags": anchor(14, 8),
    "lamp": anchor(14, 7),
    "fence": (24, 270),
    "banana": (58, 214),
    "dryingrack": (86, 218),
    "fishtrap": (196, 398),
    "boat": (408, 262),
    "pond": anchor(26, 12),
    "shrine": anchor(13, 4),
    "well": anchor(22, 11),
    "npc_ruen": (98, 232),
    "npc_child": anchor(13, 8),
    "npc_nok": anchor(21, 10),
    # nature scatter (feet anchors)
    "palms": [(48, 206), (440, 216), (128, 290), (296, 164)],
    "trees": [(104, 150), (330, 150), (150, 302), (302, 302), (76, 372),
              (392, 372), (240, 428), (362, 414), (118, 394), (446, 380)],
    "bigrocks": [(40, 376), (300, 478), (470, 380)],
    "rocks": [(308, 194), (96, 150), (356, 204), (200, 300), (452, 380)],
    "bushes": [(120, 258), (196, 214), (300, 240), (420, 190), (56, 288), (360, 304)],
    "flowers": [(140, 254), (228, 214), (88, 266), (316, 216), (404, 300), (180, 314)],
}

FIREFLIES = [(216, 202), (92, 224), (352, 244), (404, 254), (232, 330),
             (300, 424), (140, 304), (84, 352)]

_cache = {}


def _cached(key, build):
    if key not in _cache:
        _cache[key] = build()
    return _cache[key]


# -------------------------------------------------------------------- sky
def _sky_surface(palette, height=GROUND_Y):
    surf = pygame.Surface((W, height))
    pixel.vgradient(surf, surf.get_rect(), palette)
    return surf


def _hills_surface(color, seed, amp=6, width=W + 90):
    surf = pygame.Surface((width, 34), pygame.SRCALPHA)
    pts = [(0, 34)]
    for i in range(9):
        x = int(width / 8.0 * i)
        y = 21 - amp + int(A._rng(i, seed, 3) * amp * 2)
        pts.append((x, y))
    pts.append((width - 1, 34))
    pygame.draw.polygon(surf, color, pts)
    return surf


def _cloud():
    s = pygame.Surface((36, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (242, 152, 112, 80), pygame.Rect(4, 4, 22, 6))
    pygame.draw.ellipse(s, (242, 152, 112, 95), pygame.Rect(10, 2, 16, 6))
    pygame.draw.ellipse(s, (252, 192, 152, 95), pygame.Rect(17, 5, 14, 5))
    return s


def _stars(screen, t, oy=0.0):
    for i in range(46):
        sx = int(A._rng(i, 3) * W)
        sy = int(A._rng(i, 7) * GROUND_Y * 0.8) - oy
        if not (0 <= sy < GROUND_Y):
            continue
        twinkle = 0.5 + 0.5 * math.sin(t * 1.8 + i * 1.7)
        if twinkle > 0.6:
            c = (198, 212, 238) if twinkle > 0.85 else (92, 108, 140)
            screen.set_at((sx, sy), c)
            if twinkle > 0.92:
                screen.set_at((min(W - 1, sx + 1), sy), (130, 150, 190))
                screen.set_at((sx, min(GROUND_Y - 1, sy + 1)), (130, 150, 190))


def sky(screen, t, palette, stars=False, sun=None):
    """Static 320-wide sky (used by the small washup scene)."""
    screen.blit(_cached(("sky", tuple(palette)), lambda: _sky_surface(palette)), (0, 0))
    if stars:
        _stars(screen, t)
    if sun:
        sx, sy = sun
        flick = pixel.flicker(t, seed=4.0, low=0.9)
        pixel.add_glow(screen, (sx, sy), 20, (255, 150, 80), max_alpha=int(42 * flick))
        pygame.draw.circle(screen, (240, 178, 112), (sx, sy), 10)
        pygame.draw.circle(screen, (252, 216, 158), (sx, sy), 6)
        pygame.draw.circle(screen, (255, 244, 214), (sx, sy), 3)


def world_sky(screen, t, cam):
    """The world's dusk sky + sun + hills, scrolled with the camera."""
    ox, oy = _off(cam)
    sky_surf = _cached(("wsky",), lambda: _sky_surface(A.SKY_DUSK, SKY_H))
    screen.blit(sky_surf, (0, -oy))
    # drifting clouds riding the ridge
    for ci, (cx, cy) in enumerate(((60, 24), (210, 26), (150, 30))):
        if (int(t * 0.4) + ci) % 7 != 0:
            continue
        cloud = _cached(("cloud", ci % 2), _cloud)
        screen.blit(cloud, (cx, cy - oy))
    # hills ridges (wide enough for the horizontal scroll)
    for drift, seed, color, amp in ((-int(t * 1.2) % 60, 5, (24, 16, 40, 255), 5),
                                    (int(t * 2.2) % 60, 9, (34, 22, 52, 255), 7)):
        hills = _cached(("hills_b", color, amp),
                        lambda: _hills_surface(color, seed, amp, WORLD_W + 160))
        screen.blit(hills, (-ox - drift, GROUND_Y - 26 - oy))
    # dusk sun
    sx, sy = int(W * 0.56), 42
    sy -= oy
    if -30 <= sy <= H + 30:
        flick = pixel.flicker(t, seed=4.0, low=0.9)
        pixel.add_glow(screen, (sx, sy), 22, (255, 150, 80), max_alpha=int(48 * flick))
        pygame.draw.circle(screen, (240, 178, 112), (sx, sy), 10)
        pygame.draw.circle(screen, (252, 216, 158), (sx, sy), 6)
        pygame.draw.circle(screen, (255, 244, 214), (sx, sy), 3)


# ------------------------------------------------------------------- ground
def fill_texture(surface, rect, ramp, seed, density=0.05, blades=0.02):
    """Calm clustered texture: base colour + scattered clumps + tiny blades."""
    pygame.draw.rect(surface, ramp[1], rect)
    area = rect.width * rect.height
    for i in range(max(1, int(area * density))):
        x = rect.x + int(A._rng(i, seed, 51) * rect.width)
        y = rect.y + int(A._rng(seed, i, 52) * rect.height)
        r = A._rng(i, seed, 53)
        color = ramp[0] if r < 0.55 else ramp[2]
        surface.set_at((x, y), color)
        if r < 0.25 and x + 1 < rect.right:
            surface.set_at((x + 1, y), color)
    for i in range(max(1, int(area * blades))):
        x = rect.x + int(A._rng(i, seed, 61) * rect.width)
        y = rect.y + int(A._rng(seed, i, 62) * max(1, rect.height - 1))
        surface.set_at((x, y), ramp[3])
        surface.set_at((x, y + 1), ramp[2])


def draw_ground(screen, t, cam=(0, 0)):
    """Terrain + animated water for the big world, scrolled by the camera."""
    tm = _cached("big_tiles", T.big_map)
    ox, oy = cam
    static = _cached("big_static", lambda: T.render_static(tm))
    screen.blit(static, (-ox, GROUND_Y - oy))
    T.draw_water(screen, tm, T.phase_for(t), (-ox, GROUND_Y - oy))


def draw_old_ground(screen, t, key, builder):
    tm = _cached(key, builder)
    screen.blit(_cached(key + "_static", lambda: T.render_static(tm)), (0, GROUND_Y))
    T.draw_water(screen, tm, T.phase_for(t), (0, GROUND_Y))


def _washup_ground(screen, t):
    draw_old_ground(screen, t, "washup_tiles", T.washup_map)


# ------------------------------------------------------------------- props
def _silhouette(surface, color=(10, 14, 22)):
    key = ("sil", id(surface))
    if key in _cache:
        return _cache[key]
    s = surface.copy()
    for y in range(s.get_height()):
        for x in range(s.get_width()):
            if s.get_at((x, y))[3] > 0:
                s.set_at((x, y), color)
    _cache[key] = s
    return s


def blit_base(screen, surf, x, base_y):
    screen.blit(A.rimmed(surf), (int(x - surf.get_width() / 2), int(base_y - surf.get_height())))


def shadow(screen, x, y, w=14):
    """A soft contact shadow so characters sit on the ground, not on it."""
    surf = _shadow_surf(w)
    screen.blit(surf, (int(x - w / 2), int(y - 3)))


def _shadow_surf(w=14):
    key = ("shadow", int(w))
    surf = _cached(key, lambda: _make_shadow(int(w)))
    return surf


def _make_shadow(w):
    h = max(4, int(w * 0.42))
    surf = pygame.Surface((w + 2, h), pygame.SRCALPHA)
    for i in range(h):
        f = 1.0 - (i / float(h))
        alpha = int(96 * (f ** 1.4))
        width = max(1, int(w * (0.35 + 0.65 * f)))
        pygame.draw.line(surf, (12, 14, 22, alpha),
                         ((w + 2 - width) // 2, i), ((w + 2 + width) // 2, i))
    return surf


def blit_character(screen, x, y, who, facing="down", frame=0, shadow_on=True):
    if shadow_on:
        shadow(screen, x, y)
    blit_base(screen, A.character(who, facing, frame), x, y)


def blit_spirit(screen, x, y, t):
    surf = A.spirit(int(t * 6) % 4)
    bob = math.sin(t * 3) * 2
    pixel.add_glow(screen, (int(x), int(y + bob)), 11, (90, 235, 220), max_alpha=70)
    screen.blit(surf, (int(x - 9), int(y - 10 + bob)))


def _fireflies(screen, t, cam=(0, 0)):
    if not O.options.particles_on():
        return
    ox, oy = cam
    for i, (x, y) in enumerate(FIREFLIES):
        dx = math.sin(t * 1.2 + i * 2.1) * 6
        dy = math.cos(t * 1.0 + i * 0.8) * 4
        on = 0.5 + 0.5 * math.sin(t * 2.6 + i * 3.7)
        if on < 0.25:
            continue
        fx, fy = int(x + dx) - ox, int(y + dy) - oy
        if not (-8 <= fx < W + 8 and -8 <= fy < H + 8):
            continue
        pixel.add_glow(screen, (fx, fy), 4, (255, 226, 150), max_alpha=int(90 * on))
        screen.set_at((fx, fy), (255, 246, 200))


def _smoke(screen, t, x, y, ox=0, oy=0):
    if not O.options.particles_on():
        return
    for i in range(3):
        phase = (t * 0.35 + i * 0.33) % 1.0
        py = int(y - phase * 12) - oy
        px = x - ox + int(math.sin(t * 0.5 + i) * 2)
        color = (190, 188, 198, int(120 * (1 - phase)))
        if 0 <= px < W and 0 <= py < H:
            screen.fill(color, pygame.Rect(px, py, 2, 2))


def _leaf(screen, t):
    if not O.options.particles_on():
        return
    if int(t * 0.9) % 19 != 0:
        return
    x = int(60 + (t * 3.5) % 90)
    y = int(40 + (t * 5.0) % 120)
    screen.fill((150, 190, 96, 200), pygame.Rect(x + int(math.sin(t * 4) * 2), y, 2, 2))


def draw_foreground(screen, t):
    """Dark silhouetted foliage along the bottom edge — SNES depth framing."""
    base = H + 6
    for i in range(-1, W // 18 + 2):
        x = i * 18
        sway = int(math.sin(t * 0.8 + i * 1.3) * 1.5)
        h = 16 + int(A._rng(i, 41, 7) * 12)
        pygame.draw.ellipse(screen, (15, 26, 18),
                            pygame.Rect(x - 7 + sway, base - h, 26, h * 2))
    for i in range(-1, W // 18 + 2):
        x = i * 18
        sway = int(math.sin(t * 0.8 + i * 1.3) * 1.5)
        h = 16 + int(A._rng(i, 41, 7) * 12)
        pygame.draw.ellipse(screen, (28, 46, 30),
                            pygame.Rect(x - 3 + sway, base - h, 12, 7))
    for i in range(0, W, 6):
        bh = 3 + int(A._rng(i, 43, 9) * 5)
        gx = i + int(math.sin(t * 1.1 + i))
        pygame.draw.line(screen, (36, 60, 38), (gx, H), (gx + int(math.sin(t + i)), H - bh))


def _stone_by_side(screen, t, cam=(0, 0), lit_shrine=False, water=0.0, add_sun=True):
    """Sky + hills + terrain; returns (lights_screen, big_map)."""
    world_sky(screen, t, cam)
    draw_ground(screen, t, cam)
    ox, oy = cam
    lights = []
    if add_sun:
        sx, sy = int(W * 0.56), 42
        if GROUND_Y - 18 <= sy - oy <= H + 24:
            lights.append((sx, sy - oy, 28, 0.22))
    return lights, ox, oy


# ---------------------------------------------------------------- layering
def village_ground(screen, t, cam=(0, 0), lit_shrine=False, water=0.0):
    """Sky, hills, ground and back props of the big world.
    Returns (back_blit, lights) — back props in world coords, lights in
    screen coords."""
    world_sky(screen, t, cam)
    draw_ground(screen, t, cam)
    ox, oy = cam
    lights = []
    sx, sy = int(W * 0.56), 42
    if -30 <= sy - oy <= H + 30:
        lights.append((sx, sy - oy, 28, 0.22))
    back_blit = []

    def add_back(surf, x, y):
        back_blit.append((y, surf, x, y))

    for i, item in enumerate(VILLAGE["huts_back"]):
        add_back(A.hut(False, i % 2), item[0], item[1])
    for i, (x, y) in enumerate(VILLAGE["palms"]):
        add_back(A.palm(i % 2), x, y)
    add_back(A.flags(int(t * 4) % 2), *VILLAGE["flags"])
    for i, (x, y) in enumerate(VILLAGE["trees"]):
        add_back(A.tree(i % 2), x, y)
    for i, (x, y) in enumerate(VILLAGE["bigrocks"]):
        add_back(A.bigrock(i), x, y)
    for i, (x, y) in enumerate(VILLAGE["rocks"]):
        add_back(A.rock(i), x, y)
    sx, sy = VILLAGE["shrine"]
    add_back(A.shrine(lit_shrine), sx, sy)
    if lit_shrine:
        lights.append((sx - ox, sy - 14 - oy, 34, 1.0))
    add_back(A.dryingrack(), *VILLAGE["dryingrack"])
    add_back(A.fence(), *VILLAGE["fence"])
    add_back(A.banana(), *VILLAGE["banana"])
    return back_blit, lights


def draw_back_layer(screen, back_blit, cam=(0, 0)):
    ox, oy = cam
    for y, surf, x, base_y in sorted(back_blit, key=lambda item: item[0]):
        px, py = int(x - surf.get_width() / 2) - ox, int(base_y - surf.get_height()) - oy
        if px < -surf.get_width() or px > W or py > H or py < -surf.get_height():
            continue
        screen.blit(surf, (px, py))


def draw_front_layer(screen, t, cam=(0, 0), water=0.0, lights=None):
    """In-front-of-characters props + particles; appends screen-space lights."""
    if lights is None:
        lights = []
    ox, oy = cam
    blit_base(screen, A.boat(), VILLAGE["boat"][0] - ox, VILLAGE["boat"][1] - oy)
    lx, ly = VILLAGE["lamp"]
    pixel.reflection(screen, lx - 4 - ox, ly + 14 - oy, 14, (252, 214, 140), t, seed=2.0)
    for i, (x, y) in enumerate(VILLAGE["huts_front"]):
        lit = i % 2 == 0
        blit_base(screen, A.hut(lit, i % 2), x - ox, y - oy)
        if lit:
            lights.append((x - 9 - ox, y - 22 - oy, 24, 0.72 * pixel.flicker(t, seed=3.0)))
        _smoke(screen, t, x - 8, y - 30, ox, oy)
    for i, (x, y) in enumerate(VILLAGE["bushes"]):
        blit_base(screen, A.bush(i), x - ox, y - oy)
    for i, (x, y) in enumerate(VILLAGE["flowers"]):
        blit_base(screen, A.flowers(), x - ox, y - oy)
    wx, wy = VILLAGE["well"]
    blit_base(screen, A.well(water), wx - ox, wy - oy)
    if water > 0.05:
        lights.append((wx - ox, wy - 12 - oy, 30, 0.55 * pixel.flicker(t, seed=2.0)))
    blit_base(screen, A.fishtrap(), VILLAGE["fishtrap"][0] - ox, VILLAGE["fishtrap"][1] - oy)
    blit_base(screen, A.lamp(), lx - ox, ly - oy)
    lights.append((lx - ox, ly - 10 - oy, 24, 0.9 * pixel.flicker(t, seed=1.0)))
    _fireflies(screen, t, cam)


def atmosphere(screen, lights, dark=60, tint=(90, 48, 34, 14)):
    inside = [l for l in lights if -70 <= l[0] <= W + 70 and -70 <= l[1] <= H + 70]
    pixel.atmosphere(screen, inside, dark=dark, dark_color=(20, 14, 34), tint=tint,
                     vignette_strength=96)


# ------------------------------------------------------------------- scenes
def draw_washup(screen, t):
    screen.fill((6, 7, 14))
    sky(screen, t, A.SKY_NIGHT, stars=True)
    hills_small = _cached("hills_night", lambda: _hills_surface((10, 14, 26, 255), 5))
    _cached("hills_night2", lambda: _hills_surface((14, 19, 34, 255), 9))
    screen.blit(hills_small, (-int(t * 1.2) % 90, GROUND_Y - 26))
    _washup_ground(screen, t)
    water_top = GROUND_Y
    water_bottom = GROUND_Y + 5 * 16
    pixel.reflection(screen, int(W * 0.8), water_top + 4, 42, (170, 200, 230), t, seed=5.0)
    # a few silhouetted palms on the far sand bank
    sil1 = _silhouette(A.palm(0))
    screen.blit(sil1, (2, water_bottom + 6 - sil1.get_height()))
    sil2 = _silhouette(A.palm(1))
    screen.blit(sil2, (W - 42, water_bottom + 6 - sil2.get_height()))
    for i in range(0, W, 12):               # tall grass fringe on the bank
        hgt = 2 + int(A._rng(i, 21, 7) * 3)
        screen.fill(A.GRASS[1], pygame.Rect(i + 3, water_bottom + 6 - hgt, 2, hgt))

    px, py = 96, 168
    shadow(screen, px + 4, py, w=42)
    lying = _cached("lying", A.lying_player)
    screen.blit(lying, (px - 15, py - lying.get_height()))
    orb = (px + 8, py - 26)
    blit_spirit(screen, orb[0], orb[1], t)
    pixel.reflection(screen, orb[0] - 4, water_bottom - 26, 16, (110, 235, 220), t, seed=3.0)
    if O.options.particles_on():
        for i in range(5):
            fx = int(A._rng(i, 1, 55) * W)
            fy = water_top + 8 + int(A._rng(1, i, 56) * (water_bottom - water_top - 20))
            on = 0.5 + 0.5 * math.sin(t * 2.2 + i * 2.9)
            if on > 0.4:
                screen.set_at((fx, fy), (176, 226, 220) if on > 0.7 else (120, 180, 180))
    draw_foreground(screen, t)
    lights = [(orb[0], orb[1], 26, 0.8), (int(W * 0.8), 20, 70, 0.2)]
    pixel.atmosphere(screen, lights, dark=126, dark_color=(6, 10, 26), tint=(16, 30, 66, 18))


def _scene_base(screen, t, cam, lit_shrine, water):
    back_blit, lights = village_ground(screen, t, cam, lit_shrine, water)
    draw_back_layer(screen, back_blit, cam)
    return lights


def draw_village(screen, t, cam=(0, 0), lit_shrine=False, water=0.0):
    """The village vista: npcs at their world posts + the spirit over Ruen."""
    lights = _scene_base(screen, t, cam, lit_shrine, water)
    ox, oy = cam
    npcs = [("ruen", VILLAGE["npc_ruen"]), ("child", VILLAGE["npc_child"]),
            ("nok", VILLAGE["npc_nok"])]
    for i, (who, (x, y)) in enumerate(sorted(npcs, key=lambda item: item[1][1])):
        facing = "side" if who == "child" else "down"
        blit_character(screen, x - ox, y - oy, who, facing=facing, frame=int(t * 4 + i) % 4)
    rx, ry = VILLAGE["npc_ruen"]
    blit_spirit(screen, rx + 34 - ox, ry - 34 - oy, t)
    lights.append((rx + 34 - ox, ry - 34 - oy, 22, 0.4))
    draw_front_layer(screen, t, cam, water, lights)
    draw_foreground(screen, t)
    atmosphere(screen, lights, dark=58, tint=(96, 48, 32, 14))


def draw_shrine_backdrop(screen, t, cam=(0, 0), lit=0.0):
    """The shrine terrace: a lone burned-old shrine under the dusk sky."""
    lights = _scene_base(screen, t, cam, lit_shrine=lit > 0.15, water=0.0)
    ox, oy = cam
    sx, sy = VILLAGE["shrine"]
    blit_character(screen, sx - 34 - ox, sy - 4 - oy, "ruen", facing="side", frame=0)
    spirit_y = sy - 40
    blit_spirit(screen, sx + 30 - ox, spirit_y - oy, t)
    lights.append((sx + 30 - ox, spirit_y - oy, 26, 0.45))
    draw_front_layer(screen, t, cam, 0.0, lights)
    draw_foreground(screen, t)
    atmosphere(screen, lights, dark=62, tint=(96, 48, 34, 14))


def draw_well_backdrop(screen, t, cam=(0, 0), water=0.0):
    """The well in the east plaza: Nok and Grandma watch you work."""
    lights = _scene_base(screen, t, cam, lit_shrine=False, water=water)
    ox, oy = cam
    wx, wy = VILLAGE["well"]
    blit_character(screen, wx - 26 - ox, wy - 2 - oy, "nok", facing="up", frame=1)
    blit_character(screen, wx + 26 - ox, wy + 8 - oy, "ruen", facing="down", frame=0)
    draw_front_layer(screen, t, cam, water, lights)
    draw_foreground(screen, t)
    atmosphere(screen, lights, dark=60, tint=(96, 48, 32, 14))


def draw_epilogue(screen, t, cam=(0, 0), warm=1.0):
    lights = _scene_base(screen, t, cam, lit_shrine=True, water=0.9)
    ox, oy = cam
    cx, cy = VILLAGE["npc_child"]
    blit_character(screen, VILLAGE["npc_ruen"][0] - ox, VILLAGE["npc_ruen"][1] - oy,
                   "ruen", facing="down", frame=0)
    blit_character(screen, cx - ox, cy - oy, "child", facing="side", frame=int(t * 6) % 4)
    blit_spirit(screen, cx + 20 - ox, cy - 30 - oy, t)
    lights.append((cx + 20 - ox, cy - 30 - oy, 30, 0.6))
    draw_front_layer(screen, t, cam, 0.9, lights)
    draw_foreground(screen, t)
    atmosphere(screen, lights, dark=int(50 - 12 * warm), tint=(120, 58, 34, 12))
    _leaf(screen, t)