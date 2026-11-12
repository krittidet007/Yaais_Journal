"""Title / cover screen — the game opens here, never straight into the story."""

import pygame

from .. import artgen as A
from .. import audio
from .. import keymap
from .. import pixel
from .. import save
from .. import settings as S
from .. import views


class CoverScene:
    name = "cover"

    def __init__(self, game):
        self.game = game
        self.t = 0.0
        self.sel = 0
        self.buttons = []
        self._rects = []
        self._build()

    def _build(self):
        self.buttons = []
        if save.has_save():
            self.buttons.append(("CONTINUE", self._continue))
        self.buttons.append(("NEW GAME", self._new_game))
        self.buttons.append(("SAVE / LOAD", self._save_load))
        self.buttons.append(("SETTINGS", self._settings))
        self.buttons.append(("QUIT", self._quit))

    # -------------------------------------------------------------- life cycle
    def on_enter(self):
        self.t = 0.0
        self.sel = 0
        self._build()
        self.game.box.hide()
        audio.play_music("cover")

    # ------------------------------------------------------------------- input
    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(self.buttons)
                audio.sfx("click")
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(self.buttons)
                audio.sfx("click")
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE) \
                    or keymap.pressed("confirm", ev):
                self._activate(self.sel)
        elif ev.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self._rects):
                if rect.collidepoint(ev.pos):
                    self.sel = i
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for i, rect in enumerate(self._rects):
                if rect.collidepoint(ev.pos):
                    self.sel = i
                    self._activate(i)

    def _activate(self, index):
        audio.sfx("click")
        self.buttons[index][1]()

    # ----------------------------------------------------------------- actions
    def _continue(self):
        data = save.read()
        if not data:
            self._new_game()
            return
        self.game.state.from_dict(data["state"])
        self.game.switch(data["scene"])

    def _new_game(self):
        self.game.state.reset()
        # the night the pages went, before anything else happens
        self.game.pending_cutscene = "the_storm"
        self.game.cutscene_finished = None
        self.game.switch("washup")

    def _settings(self):
        if not self.game.settings_menu.visible:
            self.game.settings_menu.open()
            self.game.overlay = self.game.settings_menu
        else:
            self.game.settings_menu.close()
            self.game.overlay = None

    def _save_load(self):
        menu = self.game.save_menu
        if not menu.visible:
            menu.open(save_allowed=False)
            self.game.overlay = menu
        else:
            menu.close()
            self.game.overlay = None

    def _quit(self):
        self.game.running = False

    # -------------------------------------------------------------------- frame
    def update(self, dt):
        self.t += dt

    def draw(self, screen):
        w, h = S.INTERNAL_W, S.INTERNAL_H
        pixel.vgradient(screen, screen.get_rect(), A.SKY_DUSK)
        for i in range(70):                     # stars
            sx = int(A._rng(i, 2) * w)
            sy = int(A._rng(i, 5) * 120)
            tw = 0.5 + 0.5 * __import__("math").sin(self.t * 1.6 + i)
            if tw > 0.55:
                screen.set_at((sx, sy), (198, 212, 238) if tw > 0.85 else (92, 108, 140))

        ridge = [(0, h)]
        for i in range(11):
            x = w // 10 * i
            ridge.append((x, 150 - 12 + int(A._rng(i, 9, 3) * 10)))
        ridge.append((w, h))
        pygame.draw.polygon(screen, (28, 20, 46), ridge)
        pygame.draw.rect(screen, (18, 30, 24), pygame.Rect(0, 182, w, h - 182))

        for surf, x, y in ((A.hut(False), 74, 196), (A.palm(0), 34, 198),
                           (A.palm(1), 210, 196), (A.bush(0), 150, 200),
                           (A.rock(0), 262, 202)):
            views.blit_base(screen, views._silhouette(surf), x, y)

        views.blit_spirit(screen, w // 2, 116, self.t)

        title = pixel.font(20).render("YAAI'S JOURNAL", False, (246, 246, 224))
        screen.blit(title, ((w - title.get_width()) // 2, 28))
        sub = "A SOUTHERN THAILAND ADVENTURE"
        pixel.draw_text(screen, sub, ((w - pixel.text_size(sub)[0]) // 2, 54),
                        (250, 224, 140))
        # controls, for a player who has never held a game and never coded
        for i, line in enumerate(("arrows / WASD   move      SHIFT  run",
                                  "E  talk, look, use, confirm",
                                  "I items  J journal  M map  X glide",
                                  "F1 code help   Esc back   F11 screen")):
            pixel.draw_text(screen, line,
                            ((w - pixel.text_size(line)[0]) // 2, 66 + i * 9),
                            (168, 178, 208), shadow=None)

        self._draw_buttons(screen)

        foot = "a python-teaching tale"
        pixel.draw_text(screen, foot, ((w - pixel.text_size(foot)[0]) // 2, h - 12),
                        (150, 160, 190), shadow=None)

    def _draw_buttons(self, screen):
        w = S.INTERNAL_W
        bw, bh = 118, 15
        x = (w - bw) // 2
        self._rects = []
        for i, (label, _action) in enumerate(self.buttons):
            y = 132 + i * 16
            rect = pygame.Rect(x, y, bw, bh)
            self._rects.append(rect)
            selected = i == self.sel
            if selected:
                pulse = 0.6 + 0.4 * abs(((self.t * 3) % 2) - 1)
                pixel.add_glow(screen, rect.center, 20, (120, 235, 210),
                               max_alpha=int(64 * pulse))
            pixel.panel(screen, rect,
                        (52, 58, 92) if selected else (34, 38, 62),
                        S.SPIRIT if selected else (86, 94, 138),
                        inner_highlight=(70, 78, 118))
            pixel.draw_text(screen, label,
                            (rect.centerx - pixel.text_size(label)[0] // 2, rect.y + 4),
                            (246, 246, 224) if selected else (196, 200, 226),
                            shadow=None)
