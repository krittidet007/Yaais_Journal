"""Mouse support: buttons, options, slots and dialogue all click."""

import unittest

import pygame

import main
from game import options as O
from game import save
from game import settings as S
from game import story as ST


CONFIRM = pygame.K_SPACE


def _click(game, pos):
    game.current.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1))


def _win_click(game, canvas_pos):
    """Click through Game._handle with a *window* coordinate, as on a
    real machine where the canvas is scaled with letterbox borders."""
    game._handle(game._remap_mouse(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=canvas_pos, button=1)))


def _win_pos(game, canvas_pos):
    """Invert Game._to_canvas_pos for a canvas point -> window point."""
    win_w, win_h = game.window.get_size()
    scale = max(min(win_w / S.INTERNAL_W, win_h / S.INTERNAL_H), 1.0)
    dw, dh = int(S.INTERNAL_W * scale), int(S.INTERNAL_H * scale)
    ox, oy = (win_w - dw) // 2, (win_h - dh) // 2
    return (int(canvas_pos[0] * scale) + ox, int(canvas_pos[1] * scale) + oy)


def _click_times(game, pos, n):
    for _ in range(n):
        game.box.update(10.0)
        _click(game, pos)


def _advance_dialogue(game, cap=60):
    """Click through story dialogue: until the scene changes or its
    modal runs dry (covers base scenes, overworld, region)."""
    scene = game.current
    for _ in range(cap):
        if game.current is not scene:
            return
        modal = getattr(scene, "_modal", getattr(scene, "modal", "missing"))
        if modal is None:
            return
        game.box.update(10.0)
        game.current.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               pos=(S.INTERNAL_W // 2, S.INTERNAL_H // 2),
                               button=1))


class TestClick(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    @classmethod
    def tearDownClass(cls):
        cls.game.window = None
        save.clear()

    def setUp(self):
        self.game.state.reset()

    # ------------------------------------------------------------ cover
    def test_cover_buttons_click(self):
        game = self.game
        game.switch("cover")
        game.current.draw(game.canvas)
        labels = [label for label, _ in game.current.buttons]
        self.assertIn("NEW GAME", labels)
        rect = game.current._rects[labels.index("NEW GAME")]
        _click(game, rect.center)
        # a new game opens with the storm cutscene, then Yaai's house
        self.assertEqual(game.current.name, "cutscene")
        for _ in range(400):
            if game.current.name != "cutscene":
                break
            _click(game, (S.INTERNAL_W // 2, S.INTERNAL_H // 2))
            game.current.update(1.0 / 60.0)
        self.assertEqual(game.current.name, "washup")

    # -------------------------------------------------- dialogue scenes
    def test_washup_dialogue_clicks_through(self):
        game = self.game
        game.switch("washup")
        _advance_dialogue(game)
        # washup has no tablet: intro dialogue runs straight on
        self.assertEqual(game.current.name, "village_naming")

    def test_overworld_modal_click_advances(self):
        game = self.game
        game.switch("overworld")
        scene = game.current
        self.assertIsNotNone(scene._modal)
        _click(game, (S.INTERNAL_W // 2, S.INTERNAL_H // 2))
        self.assertFalse(game.box.is_revealing())

    def test_dialogue_exits(self):
        """Esc (or right-click) bails out of any conversation."""
        game = self.game
        game.switch("overworld")          # prologue modal greets a fresh run
        scene = game.current
        self.assertIsNotNone(scene._modal)
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertIsNone(scene._modal)
        self.assertFalse(game.box.visible)
        # right-click does the same, mid-greeting
        game.state.reset()
        game.switch("overworld")
        scene = game.current
        self.assertIsNotNone(scene._modal)
        scene.handle_event(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, pos=(10, 10), button=3))
        self.assertIsNone(scene._modal)

    def test_base_scene_dialogue_exits(self):
        game = self.game
        game.switch("washup")
        self.assertEqual(game.current.name, "washup")
        game.current.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertEqual(game.current.name, "village_naming")

    def test_finale_dialogue_exits(self):
        game = self.game
        game.state.reset()
        for stop in ST.STOPS:
            game.state.complete_stop(stop)
        game.state.visited = ["prologue"]
        game.switch("overworld")
        scene = game.current
        scene._modal = None
        game.box.hide()
        pc, pr = ST.PROLOGUE["pos"]
        scene.player = pygame.Vector2(pc * 16 + 8, pr * 16 + 8)
        scene.update(1.0 / S.FPS)
        # the last act speaks first (the story beat at the end of the road)
        for _ in range(40):
            if scene._modal is None:
                break
            _click(game, (S.INTERNAL_W // 2, S.INTERNAL_H // 2))
        scene.update(1.0 / S.FPS)
        # the cup at the pass plays as a cutscene before the ceremony
        for _ in range(400):
            if game.current.name != "cutscene":
                break
            _click(game, (S.INTERNAL_W // 2, S.INTERNAL_H // 2))
            game.current.update(1.0 / 60.0)
        # the ceremony starts as the cup cutscene
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        for _ in range(400):
            if game.current.name != "cutscene":
                break
            _click(game, (S.INTERNAL_W // 2, S.INTERNAL_H // 2))
            game.current.update(1.0 / 60.0)
        scene = game.current
        self.assertIsNotNone(scene._modal)   # the ceremony opens
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertTrue(scene.panel.visible)  # skipping words, not destiny

    # -------------------------------------------------- tablets in town
    def _enter_town(self, stop_id):
        game = self.game
        game.state.visited = ["prologue"]
        game.switch("overworld")
        scene = game.current
        scene._modal = None
        game.box.hide()
        stop = ST.STOP_BY_ID[stop_id]
        scene.player = pygame.Vector2(*scene._px(*stop["pos"]))
        scene.update(1.0 / S.FPS)
        for _ in range(80):                   # hear any welcome first
            if scene._modal is None:
                break
            _click(game, (S.INTERNAL_W // 2, S.INTERNAL_H // 2))
        game.state.quests[stop_id] = 3          # meet + look + spark done
        game.state.act_seen = ST.STOP_BY_ID[stop_id]["act"]
        game.state.flags.append("code_tutorial")   # Noi's lesson already heard
        return scene

    def test_tablet_click_run(self):
        """Open the town tablet, type the spell, click RUN, win the page."""
        game = self.game
        scene = self._enter_town("ko_tao")
        stop = ST.STOP_BY_ID["ko_tao"]
        scene.player = scene._tablet_px(stop).copy()
        scene.update(1.0 / S.FPS)
        self.assertIn("tablet", scene.prompt)
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertTrue(scene.panel.visible)
        scene.panel.lines = ["turtles = 4"]
        scene.draw(game.canvas)        # builds the clickable RUN button
        _click(game, scene.panel.run_rect.center)
        from tests.helpers import finish_activity
        finish_activity(game)
        self.assertTrue(game.state.stop_done("ko_tao"))
        self.assertIsNotNone(scene._modal)   # the page reward
        kinds = [f["kind"] for f in scene.fx]
        self.assertIn("swim", kinds)         # the spell visibly happens
        scene.update(10.0)
        self.assertEqual(scene.fx, [])       # effects fade

    def test_tablet_wrong_answer_stays(self):
        game = self.game
        scene = self._enter_town("ko_tao")
        stop = ST.STOP_BY_ID["ko_tao"]
        scene.player = scene._tablet_px(stop).copy()
        scene.update(1.0 / S.FPS)
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        scene.panel.lines = ["turtles = 0"]
        scene.draw(game.canvas)
        _click(game, scene.panel.run_rect.center)
        self.assertFalse(game.state.stop_done("ko_tao"))
        self.assertTrue(scene.panel.visible)   # tablet stays open to retry

    def test_host_click(self):
        game = self.game
        scene = self._enter_town("chumphon")
        stop = ST.STOP_BY_ID["chumphon"]
        scene.player = scene._host_px(stop).copy()
        scene.update(1.0 / S.FPS)
        self.assertIn(ST.extra_of("chumphon")["host"], scene.prompt)
        _click(game, (S.INTERNAL_W // 2, S.INTERNAL_H // 2))
        self.assertIsNotNone(scene._modal)

    # ------------------------------------------------------- window coords
    def test_canvas_pos_maps_letterbox_and_scale(self):
        """A scaled window with black bars clicks the right canvas pixel."""
        game = self.game

        class FakeWindow:
            def __init__(self, size):
                self._size = size

            def get_size(self):
                return self._size

        real_window = game.window
        try:
            # 2x canvas is 1280x640; bars: x=0, y=(960-640)//2=160
            game.window = FakeWindow((1280, 960))
            self.assertEqual(game._to_canvas_pos((20, 320)), (10, 80))
            # the black bars map outside the canvas (nothing hits there)
            self.assertEqual(game._to_canvas_pos((0, 0)), (0, -80))
            # 1.5x canvas is 960x480: exactly full-bleed, no bars
            game.window = FakeWindow((960, 480))
            self.assertEqual(game._to_canvas_pos((30, 45)), (20, 30))
            # 1x window: identity
            game.window = FakeWindow((640, 320))
            self.assertEqual(game._to_canvas_pos((123, 45)), (123, 45))
        finally:
            game.window = real_window

    def test_window_click_reaches_cover_buttons(self):
        """A click reported in window space still activates a cover button —
        this is the NEW GAME regression on any windowed screen."""
        game = self.game
        game.window = pygame.display.set_mode((1280, 960), pygame.RESIZABLE)
        try:
            game.switch("cover")
            game.current.draw(game.canvas)
            labels = [label for label, _ in game.current.buttons]
            rect = game.current._rects[labels.index("NEW GAME")]
            _win_click(game, _win_pos(game, rect.center))
            # a new game opens with the storm cutscene
            self.assertEqual(game.current.name, "cutscene")
            for _ in range(400):
                if game.current.name != "cutscene":
                    break
                _click(game, (S.INTERNAL_W // 2, S.INTERNAL_H // 2))
                game.current.update(1.0 / 60.0)
            self.assertEqual(game.current.name, "washup")
        finally:
            game.window = pygame.display.set_mode((1, 1))
            save.clear()

    def test_center_click_remaps_at_any_window_size(self):
        """A window-space click still reaches the scene at every size."""
        game = self.game
        center = (S.INTERNAL_W // 2, S.INTERNAL_H // 2)
        for size in ((960, 480), (1440, 900)):
            self.game.state.reset()
            game.window = pygame.display.set_mode(size, pygame.RESIZABLE)
            try:
                game.switch("overworld")
                scene = game.current
                self.assertIsNotNone(scene._modal)
                game.box.update(10.0)
                _win_click(game, _win_pos(game, center))
                # the click landed: the modal moved to its next line
                self.assertGreaterEqual(scene._modal["index"], 1)
            finally:
                game.window = pygame.display.set_mode((1, 1))
                save.clear()

    # ------------------------------------------------------------ menus
    def test_options_rows_click(self):
        game = self.game
        menu = game.settings_menu
        menu.open()
        cx = menu.rect.centerx
        y0 = menu._rows_top()
        # click the music_source row once to select it ...
        idx = next(i for i, r in enumerate(O.ROWS) if r[1] == "music_source")
        pos = (cx, y0 + idx * 16 + 8)
        menu.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1))
        self.assertEqual(menu.sel, idx)
        # ... and again to cycle it
        before = O.options.get("music_source")
        menu.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1))
        self.assertNotEqual(O.options.get("music_source"), before)
        O.options.set("music_source", before)
        menu.close()

    def test_options_slider_click(self):
        game = self.game
        menu = game.settings_menu
        menu.open()
        before = O.options.get("master_volume")
        # start from a known middle value: clicking the slider must change it,
        # whatever the stored user options happen to be
        O.options.set("master_volume", 50)
        pos = (menu.rect.centerx, menu._rows_top() + 8)
        menu.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1))
        menu.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1))
        self.assertNotEqual(O.options.get("master_volume"), before)
        O.options.set("master_volume", before)
        menu.close()

    def test_save_slots_click(self):
        game = self.game
        save.clear()
        game.state.visited = ["prologue"]
        game.switch("overworld")
        game.switch("cover")
        menu = game.save_menu
        menu.open(mode="load", save_allowed=True)
        # header click toggles load/save
        menu.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               pos=(menu.rect.centerx, menu.rect.y + 7),
                               button=1))
        self.assertEqual(menu.mode, "save")
        # click a slot twice to save there (current scene must be resumable)
        game.switch("overworld")
        row = menu._slot_rect(2)
        for _ in range(2):
            menu.handle_event(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                   pos=row.center, button=1))
        self.assertIsNotNone(save.read_slot(3))
        menu.close()

    def test_right_click_closes_menus(self):
        game = self.game
        menu = game.settings_menu
        menu.open()
        result = menu.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               pos=(10, 10), button=3))
        self.assertEqual(result, "close")
        self.assertFalse(menu.visible)


if __name__ == "__main__":
    unittest.main()
