"""Cutscenes — the moments that are filmed rather than clicked through.

A cutscene is a list of shots. Each shot points the camera at a place,
holds it, and speaks a few lines. Between shots the world keeps running
underneath: the weather, the sea, the light.

The camera can pan, and it can push in (the frame is scaled around the
focus), and letterbox bars close over the picture so it reads as a
scene rather than as a game.

Focus points are written as ``"stop:<stop id>"`` plus a tile offset, so
a cutscene does not depend on pixel coordinates that change whenever the
world is rebuilt.
"""

import math

import pygame

from . import pixel
from . import settings as S


LETTERBOX = 0.11


class Shot:
    """One framed moment."""

    def __init__(self, data):
        self.data = data
        self.focus = data.get("focus")
        self.zoom = float(data.get("zoom", 1.0))
        self.hold = float(data.get("hold", 1.0))
        self.lines = list(data.get("lines", []))
        self.mood = data.get("mood")
        self.fade = float(data.get("fade", 0.0))

    def world_point(self, stops, home=None):
        """Where the camera looks, in world pixels."""
        if not self.focus:
            return None
        kind, value = self.focus[0], self.focus[1]
        if kind == "stop":
            stop = stops.get(value)
            if stop is None and home is not None:
                stop = getattr(home, "PROLOGUE", None)
            if stop is None:
                return None
            c, r = stop["pos"]
            dx = self.focus[2] if len(self.focus) > 2 else 0
            dy = self.focus[3] if len(self.focus) > 3 else 0
            return (c * 16 + 8 + dx * 16, r * 16 + 8 + dy * 16)
        if kind == "xy":
            return (float(value[0]), float(value[1]))
        return None


class Cutscene:
    """The player: it walks the shot list and keeps the dialogue in step."""

    def __init__(self, game, spec, stops, home=None):
        self.game = game
        self.spec = spec or {}
        self.shots = [Shot(s) for s in self.spec.get("shots", [])]
        self.index = 0
        self.t = 0.0
        self.line = 0
        self.finished = False
        self.choice = None
        self.choice_result = None
        self.stops = stops
        self.stops_home = home
        self._started = False
        self._waiting = False

    # ------------------------------------------------------------------ state
    @property
    def shot(self):
        if 0 <= self.index < len(self.shots):
            return self.shots[self.index]
        return None

    def done(self):
        return self.finished

    def focus(self):
        shot = self.shot
        if shot is None:
            return None
        return shot.world_point(self.stops, self.stops_home)

    def zoom(self):
        shot = self.shot
        return shot.zoom if shot else 1.0

    # ----------------------------------------------------------------- update
    def update(self, dt):
        if self.finished:
            return
        shot = self.shot
        if shot is None:
            self.finished = True
            return
        if not self._started:
            self._started = True
            self._waiting = True
            self._show_line()
            return
        if self._waiting:
            return                      # a line is up: the player moves on
        self.t += dt
        if self.t >= shot.hold:
            self.t = 0.0
            self.index += 1
            self.line = 0
            if self.index >= len(self.shots):
                self.finished = True
                self.game.box.hide()
                return
            self._waiting = True
            self._show_line()

    def _show_line(self):
        shot = self.shot
        if shot is None or self.line >= len(shot.lines):
            self.game.box.hide()
            return
        speaker, accent, text = shot.lines[self.line]
        self.game.box.show(speaker, accent, text)

    def advance(self):
        """The player pressed confirm: finish the line, or the next one."""
        shot = self.shot
        if shot is None:
            return
        if not self._waiting:
            return
        self._waiting = False
        if self.line < len(shot.lines) - 1:
            self.line += 1
            self._show_line()
            self._waiting = True
            return
        # the last line of this shot: hold it, then the next shot
        self.t = shot.hold

    def skip(self):
        """Skip the whole cutscene."""
        self.finished = True
        self.game.box.hide()

    # ------------------------------------------------------------------- draw
    def draw_overlay(self, screen, width, height):
        """Letterbox bars and the fade, over the finished frame."""
        # letterbox
        bar = max(0, int(height * LETTERBOX))
        if bar:
            screen.fill((8, 6, 10), pygame.Rect(0, 0, width, bar))
            screen.fill((8, 6, 10), pygame.Rect(0, height - bar, width, bar))
            screen.fill((120, 96, 60),
                        pygame.Rect(0, bar - 1, width, 1))
            screen.fill((120, 96, 60),
                        pygame.Rect(0, height - bar, width, 1))
        shot = self.shot
        if shot is not None and shot.fade > 0.0:
            veil = pygame.Surface((width, height), pygame.SRCALPHA)
            veil.fill((6, 6, 10, int(200 * min(1.0, shot.fade))))
            screen.blit(veil, (0, 0))


def zoom_around(surface, focus, zoom, out_size):
    """Scale the frame around a point, cropping the overflow.

    Returns the scaled surface to blit; the caller centres it.
    """
    w, h = surface.get_size()
    if zoom <= 1.001:
        return surface
    sw, sh = int(w * zoom), int(h * zoom)
    scaled = pygame.transform.scale(surface, (sw, sh))
    if focus is not None:
        fx = int(focus[0] * zoom)
        fy = int(focus[1] * zoom)
        x = max(0, min(sw - w, fx - w // 2))
        y = max(0, min(sh - h, fy - h // 2))
    else:
        x = (sw - w) // 2
        y = (sh - h) // 2
    return scaled.subsurface((x, y, w, h)).copy()
