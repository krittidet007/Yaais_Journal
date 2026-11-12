"""Noi walks with you: scouting, barks, and the map screen."""

import unittest

import pygame

import main
from game import save
from game import settings as S
from game import story as ST


class TestCompanion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    @classmethod
    def tearDownClass(cls):
        cls.game.window = None
        save.clear()

    def setUp(self):
        self.game.state.reset()

    def _enter(self):
        self.game.state.visited = ["prologue"]
        self.game.state.pos = None
        self.game.switch("overworld")
        scene = self.game.current
        scene._modal = None
        self.game.box.hide()
        return scene

    def test_noi_scouts_toward_the_target(self):
        scene = self._enter()
        scene.update(1.0 / S.FPS)
        tgt = scene._target
        self.assertIsNotNone(tgt)
        noi = scene._noi_pos()
        c, r = tgt["pos"]
        dest = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        # Noi stands ahead of the player, toward the quest
        self.assertLess(noi.distance_to(dest),
                        scene.player.distance_to(dest))

    def test_noi_barks_at_storms(self):
        scene = self._enter()
        storm = scene.storms[0]
        storm["x"], storm["y"] = scene.player.x + 100, scene.player.y
        scene.update(1.0 / S.FPS)
        self.assertIsNotNone(scene.noi_bark)

    def test_noi_barks_on_thin_wind(self):
        scene = self._enter()
        self.game.state.fuel = 10.0
        scene.update(1.0 / S.FPS)
        self.assertIsNotNone(scene.noi_bark)
        self.assertIn("spark", scene.noi_bark["text"])

    def test_barks_fade(self):
        scene = self._enter()
        scene._bark("Hello!")
        scene.update(4.0)
        self.assertIsNone(scene.noi_bark)
        scene._bark("Hello!")
        scene.draw(self.game.canvas)       # bubble draws without crashing

    def test_festival_bark(self):
        game = self.game
        game.state.visited = ["prologue"]
        game.switch("overworld")
        scene = game.current
        scene._modal = None
        game.box.hide()
        game.state.quests["krabi"] = 3
        game.state.flags.append("code_tutorial")
        scene._open_tablet(ST.STOP_BY_ID["krabi"])
        scene._on_run('steps = 9\nfor i in range(1, steps + 1):\n'
                      '    print("breathe" if i % 3 == 0 else "step")')
        # the code is only half of it: the town has its own activity too
        from tests.helpers import play_activity
        play_activity(game)
        self.assertTrue(game.state.stop_done("krabi"))
        kinds = [f["kind"] for f in scene.fx]
        self.assertIn("festival", kinds)     # the boss throws a festival


class TestMapUI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    @classmethod
    def tearDownClass(cls):
        cls.game.window = None
        save.clear()

    def setUp(self):
        self.game.state.reset()

    def test_map_opens_draws_closes(self):
        game = self.game
        game.state.visited = ["prologue"]
        game.switch("overworld")
        menu = game.map_view
        menu.open()
        self.assertTrue(menu.visible)
        menu.draw(game.canvas)
        result = menu.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
        self.assertEqual(result, "close")
        self.assertFalse(menu.visible)

    def test_map_marks_done_towns(self):
        game = self.game
        game.state.visited = ["prologue"]
        game.state.complete_stop(ST.STOP_BY_ID["chumphon"])
        game.switch("overworld")
        game.map_view.open()
        game.map_view.draw(game.canvas)    # green dot, no crash

    def test_map_key_bound(self):
        from game import options as O
        self.assertEqual(O.options.key_name("map"), "m")


if __name__ == "__main__":
    unittest.main()
