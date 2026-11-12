"""Weather — what the air is doing in each region.

The light pass decides the mood; this decides what is in the air. Rain
over the rainforest, mist in the mangrove, rubber smoke in the
plantations, fireflies after dark, and the small drifting things that
make a place feel inhabited.

Particles live in world space, so they scroll with the camera and the
wind can push them across the whole region.
"""

import math
import random

import pygame

from . import pixel

# kind -> (spawn rate per second, colour, life, speed)
PROFILES = {
    "clear": (0.0, (255, 255, 255), 0.0, 0.0),
    "rain": (34.0, (168, 202, 236), 0.9, 260.0),
    "mist": (7.0, (206, 220, 232), 14.0, 8.0),
    "haze": (6.0, (238, 214, 168), 11.0, 5.0),
    "squall": (48.0, (176, 208, 240), 0.8, 330.0),
}

NIGHT_FIREFLIES = {"green_deep", "sweet_islands", "mangrove"}


class Weather:
    """The air over the player's head, for the region they are in."""

    def __init__(self, region_id="gulf_shore"):
        self.region = region_id
        self.kind = "clear"
        self.t = 0.0
        self.particles = []
        self._fireflies = []
        self._spawn = 0.0
        self._rng = random.Random(4242)
        self.set_region(region_id)

    # ------------------------------------------------------------------ setup
    def set_region(self, region_id):
        from . import regions as R
        if region_id == self.region:
            return
        self.region = region_id
        reg = R.REGIONS.get(region_id, R.REGIONS[R.DEFAULT_REGION])
        self.kind = reg.get("weather", "clear")
        self.particles = []
        self._fireflies = []
        self._spawn = 0.0

    # ----------------------------------------------------------------- update
    def update(self, dt, player_x, player_y):
        self.t += dt
        rate, colour, life, speed = PROFILES.get(self.kind, PROFILES["clear"])
        if rate > 0.0:
            self._spawn += rate * dt
            while self._spawn >= 1.0:
                self._spawn -= 1.0
                self.particles.append(self._make(colour, life, speed))
        for p in self.particles:
            p["life"] -= dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
        self.particles = [p for p in self.particles if p["life"] > 0.0]

        # fireflies come out after dark, in the green places
        if self.region in NIGHT_FIREFLIES:
            if len(self._fireflies) < 14 and self._rng.random() < dt * 2.0:
                self._fireflies.append({
                    "x": player_x + self._rng.uniform(-260, 260),
                    "y": player_y + self._rng.uniform(-180, 180),
                    "ph": self._rng.uniform(0, 6.28),
                    "sp": self._rng.uniform(0.6, 1.7),
                })
        for f in self._fireflies:
            f["ph"] += dt * f["sp"]
            f["x"] += math.sin(f["ph"]) * 6.0 * dt
            f["y"] += math.cos(f["ph"] * 0.7) * 4.0 * dt
        self._fireflies = [f for f in self._fireflies
                           if abs(f["x"] - player_x) < 420
                           and abs(f["y"] - player_y) < 320]

    def _make(self, colour, life, speed):
        rng = self._rng
        x = rng.uniform(-320, 320)
        y = rng.uniform(-200, 200)
        if self.kind in ("rain", "squall"):
            return {"x": x, "y": y, "vx": -40.0, "vy": speed,
                    "life": life, "max": life, "col": colour,
                    "len": rng.randint(4, 9)}
        if self.kind == "mist":
            return {"x": x, "y": y, "vx": speed, "vy": rng.uniform(-1.5, 1.5),
                    "life": life, "max": life, "col": colour,
                    "w": rng.randint(40, 110), "h": rng.randint(3, 7)}
        return {"x": x, "y": y, "vx": rng.uniform(-6, 6),
                "vy": rng.uniform(-9, -2), "life": life, "max": life,
                "col": colour, "w": rng.randint(1, 2)}

    # ------------------------------------------------------------------- draw
    def draw(self, screen, ox, oy, night=0.0):
        if not self.particles and not self._fireflies:
            return
        for p in self.particles:
            x = int(p["x"] - ox)
            y = int(p["y"] - oy)
            if -20 <= x <= 640 + 20 and -20 <= y <= 320 + 20:
                if self.kind in ("rain", "squall"):
                    a = int(150 * min(1.0, p["life"] / p["max"]))
                    ln = p["len"]
                    pygame.draw.line(screen, (p["col"][0], p["col"][1], p["col"][2], a),
                                     (x, y), (x - 2, y - ln), 1)
                elif self.kind == "mist":
                    a = int(16 * min(1.0, p["life"] / p["max"]))
                    w, h = p["w"], p["h"]
                    s = pygame.Surface((w, h), pygame.SRCALPHA)
                    s.fill((p["col"][0], p["col"][1], p["col"][2], a))
                    screen.blit(s, (x, y))
                else:
                    a = int(120 * min(1.0, p["life"] / p["max"]))
                    screen.set_at((max(0, min(639, x)), max(0, min(319, y))),
                                  (p["col"][0], p["col"][1], p["col"][2], a))
        for f in self._fireflies:
            x = int(f["x"] - ox)
            y = int(f["y"] - oy)
            if -8 <= x <= 648 and -8 <= y <= 328:
                blink = 0.5 + 0.5 * math.sin(f["ph"] * 2.0)
                if blink < 0.35:
                    continue
                pixel.add_glow(screen, (x, y), 5, (190, 255, 150),
                               max_alpha=int(70 * blink))
                screen.set_at((x, y), (226, 255, 190))
