"""A short, skippable title splash shown before the cover (unless skipped)."""

import pygame

from .. import pixel
from .. import settings as S


class SplashScene:
    name = "splash"
    DURATION = 1.9

    def __init__(self, game):
        self.game = game
        self.t = 0.0
        self._done = False

    def on_enter(self):
        self.t = 0.0
        self._done = False
        self.game.box.hide()

    def _finish(self):
        if not self._done:
            self._done = True
            self.game.switch("cover")

    def handle_event(self, ev):
        if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self._finish()

    def update(self, dt):
        self.t += dt
        if self.t >= self.DURATION:
            self._finish()

    def draw(self, screen):
        screen.fill((8, 9, 16))
        alpha = 255
        if self.t < 0.4:
            alpha = int(255 * self.t / 0.4)
        elif self.t > self.DURATION - 0.4:
            alpha = int(255 * (self.DURATION - self.t) / 0.4)
        alpha = max(0, min(255, alpha))

        title = pixel.font(20).render("YAAI'S JOURNAL", False, (240, 240, 220))
        title.set_alpha(alpha)
        screen.blit(title, ((S.INTERNAL_W - title.get_width()) // 2,
                            (S.INTERNAL_H - title.get_height()) // 2 - 8))
        line = "a Southern Thailand adventure"
        shadow = pixel.font(8).render(line, False, (120, 130, 160))
        shadow.set_alpha(alpha)
        screen.blit(shadow, ((S.INTERNAL_W - shadow.get_width()) // 2,
                             S.INTERNAL_H // 2 + 12))
