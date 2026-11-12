"""The cutscene scene: the world keeps running, the camera does not.

It draws the overworld underneath (with the HUD hidden), points the
camera wherever the shot says, pushes in on the focus, and closes the
letterbox bars over the picture.
"""

import pygame

from .. import cutscene as CS
from .. import cutscenes as CSD
from .. import keymap
from .. import mouse
from .. import pixel
from .. import settings as S
from .. import story as ST


class CutsceneScene:
    name = "cutscene"

    def __init__(self, game):
        self.game = game
        self.cine = None
        self.t = 0.0

    # ------------------------------------------------------------- life cycle
    def on_enter(self):
        spec = CSD.CUTSCENES.get(self.game.cutscene_id)
        self.cine = CS.Cutscene(self.game, spec, ST.STOP_BY_ID, ST)
        self.t = 0.0
        self.game.box.hide()
        # lift the dialogue into the frame, above the letterbox bar
        self._box_y = self.game.box.rect.y
        self.game.box.rect.y = (S.INTERNAL_H - 90
                                - int(S.INTERNAL_H * CS.LETTERBOX))
        from .. import audio
        mood = (spec or {}).get("music")
        if mood:
            audio.set_mood(mood)

    def leave(self):
        self.game.box.hide()
        y = getattr(self, "_box_y", None)
        if y is not None:
            self.game.box.rect.y = y

    # ------------------------------------------------------------------ input
    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN and (
                ev.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER)
                or keymap.pressed("confirm", ev)):
            self.cine.advance()
            return True
        if ev.type == pygame.KEYDOWN and (
                ev.key == pygame.K_ESCAPE or keymap.pressed("cancel", ev)):
            self.cine.skip()
            return True
        if mouse.cancelled(ev):
            self.cine.skip()
            return True
        if mouse.clicked(ev):
            self.cine.advance()
            return True
        return False

    # ----------------------------------------------------------------- update
    def update(self, dt):
        self.t += dt
        # the cutscene drives its own dialogue, so it plays the same
        # wherever it is called from
        self.game.box.update(dt)
        self.cine.update(dt)
        if self.cine.done():
            self.game.cutscene_done()

    # ------------------------------------------------------------------- draw
    def draw(self, screen):
        over = self.game.scenes.get("overworld")
        focus = self.cine.focus()
        if over is not None:
            # point the camera at the shot BEFORE the world is drawn
            if focus is not None:
                over.cam.x = focus[0] - S.INTERNAL_W / 2
                over.cam.y = focus[1] - S.INTERNAL_H / 2
                over.cam.clamp()
            over.draw(screen, cinematic=True)
        else:
            screen.fill(S.BG)
        zoom = self.cine.zoom()
        if zoom > 1.001:
            scaled = CS.zoom_around(screen, focus, zoom,
                                   (S.INTERNAL_W, S.INTERNAL_H))
            screen.blit(scaled, (0, 0))
        self.cine.draw_overlay(screen, S.INTERNAL_W, S.INTERNAL_H)
        self.game.box.draw(screen)
