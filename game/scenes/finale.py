"""Finale — the Wai Khru.

You return to Yaai's village at dusk. The twenty-four pages
rise from the journal and form a song and a recipe. You
perform the Rong Khru with Noi, Yaai joins at the end, and
page twenty-five — the blank one — is yours to write.
"""

import math

import pygame

from .. import keymap
from .. import mouse
from .. import pixel
from .. import settings as S
from .. import story as ST
from .. import tiles as T
from .. import views
from .. import world_map as WM

W, H = S.INTERNAL_W, S.INTERNAL_H


class FinaleScene:
    name = "finale"

    def __init__(self, game):
        self.game = game
        self.t = 0.0
        self.box = game.box
        self._lines = list(ST.FINALE["lines"])
        self._after = list(ST.FINALE.get("after", []))
        self._index = -1
        self._stage = "lines"        # lines | tablet | after | done
        self._done = False
        self.panel = None

    # -------------------------------------------------------------- life cycle
    def on_enter(self):
        self.t = 0.0
        self._index = -1
        self._stage = "lines"
        self._done = False
        self.panel = self.game.make_panel(self._on_run)
        self.game.box.hide()
        self._advance()

    def handle_event(self, ev):
        if self.panel is not None and self.panel.visible:
            result = self.panel.handle_event(ev)
            if result == "close":
                self.panel.close()
            return
        confirm = ev.type == pygame.KEYDOWN and (
            ev.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER)
            or keymap.pressed("confirm", ev))
        cancel = (ev.type == pygame.KEYDOWN and keymap.pressed("cancel", ev)) \
            or mouse.cancelled(ev)
        if self._done:
            if confirm or cancel or mouse.clicked(ev):
                self.game.finish_region()
            return
        if cancel:
            self._skip_to_end()
            return
        if not (confirm or mouse.clicked(ev)):
            return
        if self._stage == "tablet" and not self.panel.visible:
            self._open_tablet()      # confirm reopens the wind tablet
            return
        self._advance()

    def update(self, dt):
        self.t += dt
        if self.panel is not None and self.panel.visible:
            self.panel.update(dt)

    def _advance(self):
        box = self.game.box
        if box.is_revealing():
            box.skip()
            return
        self._index += 1
        lines = self._after if self._stage == "after" else self._lines
        if self._index < len(lines):
            speaker, accent, text = lines[self._index]
            box.show(speaker, accent, text)
        elif self._stage == "lines":
            box.hide()
            self._open_tablet()
        else:
            box.hide()
            self._done = True

    def _skip_to_end(self):
        self.game.box.hide()
        if self.panel is not None:
            self.panel.close()
        self._done = True

    # ------------------------------------------------------------------ tablet
    def _open_tablet(self):
        self._stage = "tablet"
        spec = ST.FINALE["code"]
        title = spec["title"]
        status = spec.get("status", "")
        if spec.get("broken"):
            title = "BROKEN " + title
            status = "BROKEN SPELL! " + spec["broken"] + "\n" + status
        self.panel.open(title, spec.get("prefill", ""), status)

    def _on_run(self, code):
        from .. import audio
        from .. import tablets as TB
        ok, console, status = TB.validate(ST.FINALE["code"], code)
        self.panel.set_console(console)
        self.panel.set_status(status, S.MUTED)
        if ok:
            audio.sfx("success")
            self.panel.close()
            self.game.box.hide()
            self.game.state.finale_done = True
            self._stage = "after"
            self._index = -1
            self._advance()
        else:
            audio.sfx("error")

    # ------------------------------------------------------------------ draw
    def draw(self, screen):
        # Yaai's village at dusk, lamps lit under the stage canopy
        screen.fill((26, 20, 34))
        cx, cy = W // 2, H // 2 + 8
        # a warm lamp glow and the stage canopy
        pixel.add_glow(screen, (cx, cy), 70, (255, 170, 90),
                           max_alpha=70)
        pygame.draw.rect(screen, (60, 40, 30),
                         pygame.Rect(cx - 60, cy - 40, 120, 60))
        pygame.draw.rect(screen, (255, 200, 120),
                         pygame.Rect(cx - 60, cy - 40, 120, 3))
        # the rising pages — every recovered page lifts into the lamplight
        st = self.game.state
        for i in range(ST.TOTAL_STOPS):
            angle = i * 0.35 + self.t * 0.25
            radius = 34 + (i % 5) * 9
            x = cx + math.cos(angle) * radius
            y = cy - 10 + math.sin(angle) * radius * 0.4
            on = i < st.journal_count()
            col = (255, 226, 160) if on else (70, 60, 80)
            screen.fill(col, pygame.Rect(int(x), int(y), 5, 6))
        # Yaai, Noi and you, side by side under the lamps
        views.blit_character(screen, cx - 30, cy + 22, "ruen", "down", 0)
        views.blit_character(screen, cx + 30, cy + 22, "player", "down", 0)
        if st.stop_done("prologue"):
            self._draw_noi(screen, cx + 6, cy + 18)

        if self._done:
            title = "PAGE TWENTY-FIVE IS YOURS"
            pixel.draw_text(screen, title,
                                    ((W - pixel.text_size(title)[0]) // 2,
                                     18), S.RUEN)
            sub = "write the story you loved most"
            pixel.draw_text(screen, sub,
                                    ((W - pixel.text_size(sub)[0]) // 2,
                                     30), S.TEXT, shadow=None)
            hint = "press any key"
            pixel.draw_text(screen, hint,
                                    ((W - pixel.text_size(hint)[0]) // 2,
                                     H - 16), S.MUTED, shadow=None)
        if self.panel is not None and self.panel.visible:
            self.panel.draw(screen)
        self.game.box.draw(screen)

    @staticmethod
    def _draw_noi(screen, x, y):
        pixel.add_glow(screen, (x, y), 4, (196, 150, 96), max_alpha=60)
        screen.fill((90, 58, 40), pygame.Rect(x - 4, y - 3, 9, 7))
        screen.fill((150, 100, 62), pygame.Rect(x - 3, y - 2, 7, 5))
        screen.fill((240, 232, 214), pygame.Rect(x - 2, y - 1, 2, 2))
        screen.fill((240, 232, 214), pygame.Rect(x + 1, y - 1, 2, 2))
