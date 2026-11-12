"""Dialogue-driven scene flow, ported from RegionScene (Godot)."""

import pygame

from .. import audio
from .. import keymap
from .. import mouse
from .. import settings as S
from .. import views


class DialogueScene:
    """Intro dialogue -> (rune tablet puzzle) -> success dialogue -> next scene."""

    name = "scene"

    def __init__(self, game):
        self.game = game
        self.stage = "dialogue"
        self.line_index = -1
        self.wait = 0.0
        self.t = 0.0
        self.panel = None
        self._status_color = S.MUTED
        self.cam = views.Camera()   # static camera the tableaux snap to

    # ------------------------------------------------------------ config hooks
    def intro_lines(self):
        return []

    def success_lines(self):
        return []

    def panel_title(self):
        return "RUNE TABLET"

    def panel_prefill(self):
        return ""

    def panel_status(self):
        return ""

    def has_panel(self):
        return True

    def next_scene(self):
        return None

    def solve_pause(self):
        return 0.8

    def validate(self, code):
        return False, "", "This mechanism has no rule yet."

    # -------------------------------------------------------------- life cycle
    def on_enter(self):
        self.stage = "dialogue"
        self.line_index = -1
        self.wait = 0.0
        self._status_color = S.MUTED
        if self.has_panel():
            self.panel = self.game.make_panel(self._on_run)
        self._advance_line()

    def update(self, dt):
        self.t += dt
        if self.stage == "wait":
            self.wait -= dt
            if self.wait <= 0.0:
                self.stage = "success"
                self.line_index = -1
                self._advance_line()
        self.on_update(dt)

    def on_update(self, dt):
        pass

    def on_solved(self):
        pass

    # ----------------------------------------------------------------- helpers
    def display_name(self, speaker):
        if speaker == "SPIRIT":
            return self.game.state.display_spirit_name()
        return speaker

    def prepare(self, line):
        text = line["text"].replace("@NAME@", self.game.state.spirit_name)
        return {
            "speaker": self.display_name(line["speaker"]),
            "accent": line["accent"],
            "text": text,
            "skin": line.get("skin", "wood"),
        }

    def _current_lines(self):
        return self.success_lines() if self.stage == "success" else self.intro_lines()

    def _advance_line(self):
        box = self.game.box
        if self.stage in ("dialogue", "success") and box.is_revealing():
            box.skip()
            return
        self.line_index += 1
        lines = self._current_lines()
        if self.line_index < len(lines):
            line = self.prepare(lines[self.line_index])
            box.show(line["speaker"], line["accent"], line["text"], line["skin"])
        elif self.stage == "dialogue":
            self._intro_complete()
        else:
            self._finish()

    def _skip_dialogue(self):
        """Bail out of the whole conversation (Esc / right-click)."""
        if self.game.box.is_revealing():
            self.game.box.skip()
        self.line_index = len(self._current_lines())
        self._advance_line()

    def _intro_complete(self):
        if self.has_panel():
            self.stage = "puzzle"
            self.game.box.hide()
            self.panel.open(self.panel_title(), self.panel_prefill(), self.panel_status())
        else:
            self._finish()

    def _finish(self):
        self.stage = "done"
        self.game.box.hide()
        nxt = self.next_scene()
        if nxt:
            self.game.switch(nxt)
        else:
            self.game.finish_region()

    # ------------------------------------------------------------------- input
    def handle_event(self, ev):
        advance = (ev.type == pygame.KEYDOWN and (
            ev.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER)
            or keymap.pressed("confirm", ev)
        )) or mouse.clicked(ev)
        cancel = (ev.type == pygame.KEYDOWN and keymap.pressed("cancel", ev)) \
            or mouse.cancelled(ev)
        if self.stage in ("dialogue", "success"):
            if cancel:
                self._skip_dialogue()
            elif advance:
                self._advance_line()
            return
        if self.stage == "puzzle":
            if self.panel.visible:
                if self.panel.handle_event(ev) == "close":
                    self.panel.close()
            elif advance:
                self.panel.reopen()
            return

    # -------------------------------------------------------------------- draw
    def draw(self, screen):
        self.draw_backdrop(screen)
        if self.panel and self.panel.visible:
            self.panel.draw(screen)
        self.game.box.draw(screen)

    def draw_backdrop(self, screen):
        screen.fill(S.BG)

    # --------------------------------------------------------------- validation
    def _on_run(self, code):
        ok, console, status = self.validate(code)
        self.panel.set_console(console)
        self.panel.set_status(status, S.MUTED)
        if ok:
            audio.sfx("success")
            self.on_solved()
            self.stage = "wait"
            self.wait = self.solve_pause()
            self.panel.close()
            self.game.box.hide()
        else:
            audio.sfx("error")
