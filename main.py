"""Yaai's Journal — a Southern Thailand adventure (pygame pixel-art).

Run with:  python main.py
Controls:  Arrows/WASD move  ·  E or Space interact/advance  ·  Ctrl+Enter runs spells
Keys:      [I] items  [J] journal  [M] map  [O] settings  [F1] code help  [F11] display
"""

import sys
import os
import io
import traceback

# Fix for Windows paths and ensure we run from game directory
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
    os.chdir(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR)

import pygame

from game import audio
from game import keymap
from game import options as O
from game import pixel
from game import postfx
from game import save
from game import settings as S
from game.code_panel import CodePanel
from game.dialogue import DialogueBox
from game.game_state import state
from game.player_ui import InventoryMenu, JournalMenu, MapView, OptionsMenu, SaveMenu

try:
    from game import mod_skip

    def _mod_enabled():
        return mod_skip.enabled()
except ImportError:  # mod file deleted -> dev keys simply vanish
    mod_skip = None

    def _mod_enabled():
        return False
from game.scenes.cutscene import CutsceneScene
from game import dev_capture
from game.scenes.cover import CoverScene
from game.scenes.epilogue import EpilogueScene
from game.scenes.hub import HubScene
from game.scenes.overworld import OverworldScene
from game.scenes.shrine import ShrineScene
from game.scenes.splash import SplashScene
from game.scenes.stop import StopScene
from game.scenes.village_naming import NamingScene
from game.scenes.washup import WashupScene
from game.scenes.well import WellScene

DISPLAY_CYCLE = ("Windowed", "Borderless", "Fullscreen")


class Game:
    def __init__(self):
        audio.pre_init()
        pygame.init()
        audio.init()
        self.window = pygame.display.set_mode(self._window_size(), pygame.RESIZABLE)
        pygame.display.set_caption(S.TITLE)
        self.clock = pygame.time.Clock()
        self.canvas = pygame.Surface((S.INTERNAL_W, S.INTERNAL_H))
        self.state = state
        self.box = DialogueBox(S.INTERNAL_W, S.INTERNAL_H)
        self.ended = False
        self.running = True
        self.inventory = InventoryMenu()
        self.journal = JournalMenu(self)
        self.map_view = MapView(self)
        self.settings_menu = OptionsMenu()
        self.save_menu = SaveMenu(self)
        self._overlay = None
        self.next_stop = None
        self._display_key = None

        self.scenes = {
            "splash": SplashScene(self),
            "cover": CoverScene(self),
            "washup": WashupScene(self),
            "hub": HubScene(self),
            "overworld": OverworldScene(self),
            "stop": StopScene(self),
            "cutscene": CutsceneScene(self),
            "village_naming": NamingScene(self),
            "shrine": ShrineScene(self),
            "well": WellScene(self),
            "epilogue": EpilogueScene(self),
        }
        self.current = None
        # hand-off between the overworld and a stop's local activity
        self.pending_activity = None
        self.pending_reward = None
        # cutscenes: a scene plays, then hands back
        self.pending_cutscene = None
        self.cutscene_id = None
        self.cutscene_finished = None
        self.cutscene_return = None

    # ----------------------------------------------------------- transitions
    # ``overlay`` is the open menu (Inventory / Journal / Map / Options /
    # Save). Older scene code assigned menu *names* ("save", "options")
    # instead of the object; the property maps those to the real menus and
    # drops anything else that is not a menu, so a bad assignment can never
    # crash the draw/event loop (that was the 'game just closes' bug).
    @property
    def overlay(self):
        return self._overlay

    @overlay.setter
    def overlay(self, value):
        if isinstance(value, str):
            value = {
                "options": getattr(self, "settings_menu", None),
                "save": getattr(self, "save_menu", None),
                "map": getattr(self, "map_view", None),
                "items": getattr(self, "inventory", None),
                "journal": getattr(self, "journal", None),
            }.get(value.strip().lower(), None)
        if value is not None and not hasattr(value, "visible"):
            value = None                # not a menu -> never crash the loop
        self._overlay = value

    def switch(self, name):
        sc = self.scenes.get(name)
        if sc is None:
            return
        if self.current is not None and hasattr(self.current, "leave"):
            self.current.leave()
        self.current = sc
        self.overlay = None
        # scenes name their entry hook ``on_enter``; older code used ``enter``
        if hasattr(sc, "on_enter"):
            sc.on_enter()
        # a scene may ask for a cutscene to play over it
        if self.pending_cutscene:
            cid = self.pending_cutscene
            self.pending_cutscene = None
            self.cutscene_id = cid
            self.cutscene_return = name
            self.switch("cutscene")
            return
        elif hasattr(sc, "enter"):
            sc.enter()
        # the autosave: the cover's CONTINUE reads this back
        if name in save.RESUMABLE:
            save.write(self.state, name)

    def _to_canvas_pos(self, pos):
        """Map a window coordinate onto the internal 640x320 canvas.

        Scenes and menus draw (and hit-test) in canvas coordinates, but the
        window may be any size with black letterbox bars around the view.
        """
        win_w, win_h = self.window.get_size()
        scale = min(win_w / S.INTERNAL_W, win_h / S.INTERNAL_H)
        scale = max(scale, 1.0)
        dw, dh = int(S.INTERNAL_W * scale), int(S.INTERNAL_H * scale)
        ox, oy = (win_w - dw) // 2, (win_h - dh) // 2
        return (int((pos[0] - ox) / scale), int((pos[1] - oy) / scale))

    def _remap_mouse(self, ev):
        if ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
                       pygame.MOUSEBUTTONUP):
            attrs = {k: getattr(ev, k) for k in ev.__dict__}
            attrs["pos"] = self._to_canvas_pos(attrs["pos"])
            return pygame.event.Event(ev.type, attrs)
        return ev

    def goto(self, name):
        self.switch(name)

    def cutscene_done(self):
        """The cutscene finished: hand control back to the world first,
        then let the scene that asked for it continue."""
        callback = self.cutscene_finished
        self.cutscene_finished = None
        self.cutscene_id = None
        back = self.cutscene_return or "overworld"
        self.cutscene_return = None
        self.switch(back)
        if callback is not None:
            callback()

    def make_panel(self, on_run):
        return CodePanel(on_run)

    def _window_size(self):
        """Never open a window bigger than the desktop — S.WINDOW_W/H is
        4x the internal canvas, which overflows a 1080p/768p screen."""
        info = pygame.display.Info()
        w, h = S.WINDOW_W, S.WINDOW_H
        if info.current_w > 0:
            w = min(w, info.current_w)
        if info.current_h > 0:
            h = min(h, info.current_h)
        return w, h

    # --------------------------------------------------------------- loop
    def _log_crash(self):
        """Record an unexpected error instead of letting the window die."""
        edge = io.StringIO()
        traceback.print_exc(file=edge)
        text = edge.getvalue()
        sys.stderr.write(text)
        try:
            os.makedirs(O.CONFIG_DIR, exist_ok=True)
            with open(os.path.join(O.CONFIG_DIR, "crash.log"), "a",
                      encoding="utf-8") as fh:
                fh.write(text + "\n")
        except OSError:
            pass

    def run(self):
        self.switch("splash")
        if dev_capture.enabled():
            dev_capture.start(self)
        while self.running:
            try:
                dt = self.clock.tick(S.FPS) / 1000.0
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        self.running = False
                        break
                    if self._handle(self._remap_mouse(ev)):
                        continue
                if not self.running:
                    break
                if self.current is not None:
                    if getattr(self.current, "name", "") != "cutscene":
                        self.box.update(dt)      # the typewriter reveal
                    self.current.update(dt)
                dev_capture.tick(self)
                dev_capture.keep(self)
                self._draw()
            except Exception:
                # an error in one scene or frame must never close the game
                self._log_crash()
                self.clock.tick(2)       # slow the error loop, don't spin hot
            if self.ended:
                break
        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------ events
    def _handle(self, ev):
        # F11 toggles display mode
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
            self._cycle_display()
            return True
        if ev.type == pygame.VIDEORESIZE:
            self.window = pygame.display.set_mode(ev.size, pygame.RESIZABLE)
            return True
        menu = self.overlay
        if menu is not None and menu.visible:
            # Deliver the event exactly once. (The old code fed every key and
            # click to the menu twice, and re-read game.overlay after the menu
            # may have already closed itself or loaded a save — which set
            # overlay to None mid-statement and crashed the loop.)
            result = menu.handle_event(ev)
            if result == "close" or not menu.visible or self.overlay is not menu:
                self.overlay = None      # menu closed / loaded a save
            return True
        if self.current is not None and self.current.handle_event(ev):
            return True
        if ev.type == pygame.KEYDOWN:
            if keymap.pressed("items", ev):
                if not self.inventory.visible:
                    self.inventory.open()
                    self.overlay = self.inventory
                else:
                    self.inventory.close()
                    self.overlay = None
                return True
            if keymap.pressed("journal", ev):
                if not self.journal.visible:
                    self.journal.open()
                    self.overlay = self.journal
                else:
                    self.journal.close()
                    self.overlay = None
                return True
            if ev.key == pygame.K_m:
                if not self.map_view.visible:
                    self.map_view.open()
                    self.overlay = self.map_view
                else:
                    self.map_view.close()
                    self.overlay = None
                return True
            if ev.key == pygame.K_o:
                if not self.settings_menu.visible:
                    self.settings_menu.open()
                    self.overlay = self.settings_menu
                else:
                    self.settings_menu.close()
                    self.overlay = None
                return True
        return False

    def _cycle_display(self):
        try:
            idx = DISPLAY_CYCLE.index(self._display_key) if self._display_key else 0
        except ValueError:
            idx = 0
        idx = (idx + 1) % len(DISPLAY_CYCLE)
        self._display_key = DISPLAY_CYCLE[idx]
        if self._display_key == "Windowed":
            self.window = pygame.display.set_mode(self._window_size(), pygame.RESIZABLE)
        elif self._display_key == "Borderless":
            info = pygame.display.Info()
            self.window = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
        else:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def finish_region(self):
        """The journey is over — leave the loop and close the window."""
        self.ended = True

    # -------------------------------------------------------------- draw
    def _draw(self):
        if self.current is not None:
            self.current.draw(self.canvas)
        else:
            self.canvas.fill((12, 10, 16))
        self.box.draw(self.canvas)
        if self.overlay is not None and self.overlay.visible:
            self.overlay.draw(self.canvas)
        try:
            from game import options as _O
            surf = postfx.apply(self.canvas, _O.options.brightness(), _O.options.contrast())
        except Exception:
            try:
                surf = postfx.apply(self.canvas, 100, 100)
            except Exception:
                surf = self.canvas
        win_w, win_h = self.window.get_size()
        scale = min(win_w / S.INTERNAL_W, win_h / S.INTERNAL_H)
        scale = max(scale, 1.0)
        dw, dh = int(S.INTERNAL_W * scale), int(S.INTERNAL_H * scale)
        # always nearest-neighbour: pixel art must stay crisp, never blurry
        scaled = pygame.transform.scale(surf, (dw, dh))
        self.window.fill((0, 0, 0))
        self.window.blit(scaled, ((win_w - dw) // 2, (win_h - dh) // 2))
        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
