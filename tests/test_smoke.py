"""Boot smoke test: the game constructs, every scene enters
and draws, and a full stop plays end to end."""

import unittest

import pygame

import main
from game import options as O
from game import save
from game import settings as S
from game import story as ST
from game import world_map as WM

CONFIRM = pygame.K_SPACE


def _tap(game):
    """A single confirm press (double presses re-trigger nearby spots)."""
    game.box.update(10.0)
    game.current.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))


def _confirm(game):
    """Advance dialogue one step: first press finishes the typewriter
    reveal, second press moves to the next line."""
    for _ in range(2):
        game.box.update(10.0)
        game.current.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))


class TestSmoke(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    @classmethod
    def tearDownClass(cls):
        cls.game.window = None
        save.clear()

    def _enter(self, name, **setup):
        for key, value in setup.items():
            setattr(self.game, key, value)
        self.game.switch(name)
        return self.game.current

    def test_game_constructs(self):
        self.assertIsNotNone(self.game.current)
        self.assertEqual(len(self.game.scenes), 11)   # stop + cutscene too

    def test_every_scene_enters_and_draws(self):
        for name in self.game.scenes:
            with self.subTest(scene=name):
                scene = self._enter(name, next_stop="chumphon")
                for _ in range(3):
                    scene.update(1.0 / S.FPS)
                scene.draw(self.game.canvas)

    def test_overworld_is_the_big_world(self):
        scene = self._enter("overworld")
        self.assertEqual((scene.tm.cols, scene.tm.rows),
                         (WM.WORLD_COLS, WM.WORLD_ROWS))
        self.assertGreater(scene.player.x, 0)

    def test_overworld_movement(self):
        self.game.switch("cover")      # leave first, so no pos snapshot
        self.game.state.pos = None     # fresh spawn at Yaai's house
        scene = self._enter("overworld")
        scene._modal = None          # clear any prologue dialogue
        self.game.box.hide()
        start = scene.player.copy()
        moved = False
        for key in (pygame.K_RIGHT, pygame.K_LEFT,
                    pygame.K_DOWN, pygame.K_UP):
            scene.keys.add(key)
            for _ in range(10):
                scene.update(1.0 / S.FPS)
            scene.keys.discard(key)
            if scene.player.distance_to(start) > 0.5:
                moved = True
                break
        self.assertTrue(moved, "player could not move in any direction")

    def test_glide_floats_over_water(self):
        from game import tiles as T
        scene = self._enter("overworld")
        scene._modal = None
        # stand on water a few tiles east of the isthmus
        scene.player = pygame.Vector2(200 * T.TILE, 30 * T.TILE)
        scene._glide = True
        scene.keys.add(pygame.K_RIGHT)
        before = scene.player.x
        scene.update(1.0 / S.FPS)
        scene.keys.discard(pygame.K_RIGHT)
        self.assertGreater(scene.player.x, before)

    def test_full_province_flow(self):
        """The whole quest on one map: welcome, sight, spark, tablet, page."""
        game = self.game
        game.state.reset()
        game.state.visited = ["prologue"]      # skip the prologue modal
        game.state.spirit_name = "Phi"
        game.state.named = True

        overworld = self._enter("overworld")
        self.assertIsNone(overworld._modal)

        # walk into Ko Tao town: the welcome plays on arrival
        stop = ST.STOP_BY_ID["ko_tao"]
        c, r = stop["pos"]
        overworld.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        overworld.update(1.0 / S.FPS)
        self.assertEqual(overworld._near["id"], "ko_tao")
        self.assertIsNotNone(overworld._modal)

        # read the welcome (meet: beat 1)
        for _ in range(2 * len(overworld._modal["lines"]) + 4):
            if overworld._modal is None:
                break
            _tap(game)
        self.assertIsNone(overworld._modal)
        self.assertEqual(game.state.quests.get("ko_tao"), 1)

        # the tablet is locked before the sight
        overworld.player = overworld._tablet_px(stop).copy()
        overworld.update(1.0 / S.FPS)
        overworld.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertFalse(overworld.panel.visible)   # Noi refuses: look first
        for _ in range(4):
            if overworld._modal is None:
                break
            _tap(game)

        # walk to the sight and look (look: beat 2)
        overworld.player = overworld._sight_px(stop).copy()
        overworld.update(1.0 / S.FPS)
        self.assertIn("look at", overworld.prompt)
        overworld.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertIsNotNone(overworld._modal)
        for _ in range(24):
            if overworld._modal is None:
                break
            _tap(game)
        self.assertEqual(game.state.quests.get("ko_tao"), 2)

        # the tablet is still locked before the spark
        overworld.player = overworld._tablet_px(stop).copy()
        overworld.update(1.0 / S.FPS)
        overworld.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertFalse(overworld.panel.visible)
        for _ in range(4):
            if overworld._modal is None:
                break
            _tap(game)

        # find Noi's hidden spark out in the wild (spark: beat 3)
        overworld.player = overworld.sparks["ko_tao"].copy()
        overworld.update(1.0 / S.FPS)
        self.assertIn("ko_tao", game.state.found)
        self.assertEqual(game.state.quests.get("ko_tao"), 3)
        for _ in range(8):
            if overworld._modal is None:
                break
            _tap(game)

        # back at the tablet: Noi teaches coding first, then it opens
        overworld.player = overworld._tablet_px(stop).copy()
        overworld.update(1.0 / S.FPS)
        self.assertNotIn("code_tutorial", game.state.flags)
        overworld.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertFalse(overworld.panel.visible)      # the lesson comes first
        self.assertIsNotNone(overworld._modal)
        for _ in range(2 * len(ST.CODE_TUTORIAL) + 8):
            if overworld.panel.visible:
                break
            if overworld._modal is None:
                break
            _tap(game)
        self.assertIn("code_tutorial", game.state.flags)
        self.assertTrue(overworld.panel.visible)       # and then the tablet
        overworld.panel.lines = ["turtles = 4"]
        overworld.panel.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_RETURN, mod=pygame.KMOD_CTRL))
        # the code is half of it: the town has its own activity too
        from tests.helpers import play_activity
        self.assertEqual(game.current.name, "stop")
        play_activity(game)
        game.switch("overworld")
        self.assertIsNotNone(overworld._modal)   # the page reward

        # take the page, still on the same big map
        for _ in range(2 * len(overworld._modal["lines"]) + 8):
            if overworld._modal is None:
                break
            _tap(game)
        self.assertEqual(game.current.name, "overworld")

        self.assertTrue(game.state.stop_done("ko_tao"))
        self.assertIn("ko_tao", game.state.pages)
        self.assertIn("Turtle Watch", game.state.cards)
        self.assertIn("tao", [w["roman"] for w in game.state.words])

    def test_finale_flow(self):
        """The Wai Khru at home: lines, wind tablet, after-lines, endcard."""
        game = self.game
        game.state.reset()
        game.state.visited = ["prologue"]
        for stop in ST.STOPS:
            game.state.complete_stop(stop)
        self.assertTrue(game.state.journey_done())

        overworld = self._enter("overworld")
        pc, pr = ST.PROLOGUE["pos"]
        overworld.player = pygame.Vector2(pc * 16 + 8, pr * 16 + 8)
        overworld.update(1.0 / S.FPS)
        # the last act speaks first (the story beat at the end of the road)
        for _ in range(40):
            if overworld._modal is None:
                break
            _tap(game)
        overworld.update(1.0 / S.FPS)
        # the ceremony opens as the cup cutscene
        overworld.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        for _ in range(400):
            if game.current.name != "cutscene":
                break
            _tap(game)
            game.current.update(1.0 / S.FPS)
        overworld = game.current
        self.assertIsNotNone(overworld._modal)   # the ceremony opens
        for _ in range(2 * len(ST.FINALE["lines"]) + 8):
            if overworld.panel.visible:
                break
            if overworld._modal is None:
                break
            _tap(game)
        self.assertTrue(overworld.panel.visible)   # Lom's wind tablet
        overworld.panel.lines = ["knots = 3",
                                 "for i in range(3):",
                                 '    print("hush")',
                                 "def release(wind):",
                                 '    return "sky: clear"']
        overworld.panel.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_RETURN, mod=pygame.KMOD_CTRL))
        self.assertTrue(game.state.finale_done)
        for _ in range(2 * len(ST.FINALE.get("after", [])) + 8):
            if game.ended:
                break
            if overworld._modal is None:
                break
            _tap(game)
        self.assertTrue(game.ended)


if __name__ == "__main__":
    unittest.main()
