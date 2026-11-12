"""Typewriter dialogue box drawn in the pixel UI style."""

import pygame

from . import audio
from . import options
from . import pixel
from . import settings as S


class DialogueBox:
    REVEAL_CHARS_PER_SEC = 42.0

    def __init__(self, screen_w, screen_h):
        self.rect = pygame.Rect(6, screen_h - 90, screen_w - 20, 62)
        self.visible = False
        self.speaker = ""
        self.accent = S.TEXT
        self.skin = "wood"
        self._lines = []
        self._revealed = 0.0
        self._time = 0.0

    def show(self, speaker, accent, text, skin="wood"):
        self.speaker = speaker
        if hasattr(S, 'accent_for'):
            self.accent = S.accent_for(accent)
        else:
            if accent == 'SPIRIT':
                self.accent = S.SPIRIT
            elif accent == 'RUEN' or accent == 'YAAI':
                self.accent = S.RUEN
            elif accent == 'NOK':
                self.accent = S.NOK
            elif accent == 'CHILD':
                self.accent = S.CHILD
            elif accent == 'DANGER':
                self.accent = S.DANGER
            elif accent == 'WARN':
                self.accent = S.WARN
            else:
                self.accent = S.TEXT
        self.skin = skin
        self._lines = pixel.wrap(text, self.rect.width - 16, 8)
        self._revealed = 0.0
        self.visible = True
        audio.sfx("blip")

    def hide(self):
        self.visible = False
        self._revealed = self._total_chars()

    def is_revealing(self):
        return self._revealed < self._total_chars()

    def skip(self):
        self._revealed = self._total_chars()

    def update(self, dt):
        self._time += dt
        if self.is_revealing():
            speed = options.options.text_cps()
            self._revealed = min(self._total_chars(), self._revealed + dt * speed)

    def _total_chars(self):
        return sum(len(line) for line in self._lines)

    def draw(self, screen):
        if not self.visible:
            return

        border = S.SPIRIT if self.skin == "spirit" else S.PANEL_BORDER
        pixel.panel(screen, self.rect, S.PANEL_BG, border, inner_highlight=S.PANEL_EDGE)

        # small corner runes for a tablet feel
        for cx, cy in ((self.rect.left + 3, self.rect.top + 3),
                       (self.rect.right - 5, self.rect.top + 3),
                       (self.rect.left + 3, self.rect.bottom - 5),
                       (self.rect.right - 5, self.rect.bottom - 5)):
            screen.set_at((cx, cy), border)

        if self.speaker:
            pixel.draw_text(screen, self.speaker[:26], (self.rect.x + 6, self.rect.y + 5), self.accent)
            body_top = self.rect.y + 19
        else:
            body_top = self.rect.y + 8

        budget = int(self._revealed)
        y = body_top
        limit = self.rect.bottom - 6
        for line in self._lines:
            if budget <= 0 or y + 8 > limit:
                break
            chunk = line[:budget]
            budget -= len(line)
            pixel.draw_text(screen, chunk, (self.rect.x + 6, y), S.TEXT)
            y += 10

        if not self.is_revealing():
            pulse = 0.5 + 0.5 * abs(((self._time * 2.5) % 2) - 1)
            if pulse > 0.35:
                pixel.draw_text(screen, "v", (self.rect.right - 10, self.rect.bottom - 12),
                                S.MUTED, shadow=None)
        hint = "esc skips"
        pixel.draw_text(screen, hint,
                        (self.rect.right - pixel.text_size(hint)[0] - 4,
                         self.rect.y - 10), S.MUTED, shadow=None)
