"""Cutscenes: the engine, the two scenes, and the hand-back."""

import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

import main  # noqa: E402
from game import cutscenes as CSD  # noqa: E402
from game import save  # noqa: E402
from game import story as ST  # noqa: E402


class TestCutscenes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    def setUp(self):
        self.game.state.reset()
        save.clear()

    def _play(self, game, limit=4000):
        for _ in range(limit):
            game.box.update(1 / 60.0)
            game.current.handle_event(pygame.event.Event(
                pygame.KEYDOWN, key=pygame.K_SPACE))
            game.current.update(1 / 60.0)
            game.current.draw(game.canvas)
            if game.current.name != "cutscene":
                return True
        return False

    def test_every_cutscene_has_shots_and_lines(self):
        for name, spec in CSD.CUTSCENES.items():
            self.assertIn("shots", spec, name)
            self.assertGreaterEqual(len(spec["shots"]), 2, name)
            for shot in spec["shots"]:
                self.assertIn("lines", shot, name)
                self.assertGreaterEqual(len(shot["lines"]), 1, name)

    def test_the_storm_opens_a_new_game(self):
        game = self.game
        game.switch("cover")
        game.current._new_game()
        self.assertEqual(game.current.name, "cutscene")
        self.assertEqual(game.cutscene_id, "the_storm")
        self.assertTrue(self._play(game))
        # and then Yaai's house
        self.assertEqual(game.current.name, "washup")

    def test_the_cup_plays_before_the_ceremony(self):
        game = self.game
        game.state.visited = ["prologue"]
        for stop in ST.STOPS:
            game.state.complete_stop(stop)
        game.switch("overworld")
        scene = game.current
        scene._modal = None
        pc, pr = ST.PROLOGUE["pos"]
        scene.player = pygame.Vector2(pc * 16 + 8, pr * 16 + 8)
        scene.update(1.0 / 60.0)
        scene._start_finale()
        self.assertEqual(game.current.name, "cutscene")
        self.assertEqual(game.cutscene_id, "the_cup")
        self.assertTrue(self._play(game))
        self.assertEqual(game.current.name, "overworld")
        self.assertIsNotNone(game.current._modal)     # the ceremony speaks
        self.assertEqual(game.current._modal["kind"], "finale_lines")

    def test_a_cutscene_can_be_skipped(self):
        game = self.game
        game.switch("cover")
        game.current._new_game()
        game.current.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_ESCAPE))
        game.current.update(1.0 / 60.0)
        self.assertEqual(game.current.name, "washup")

    def test_the_camera_focus_resolves(self):
        from game import cutscene as CS
        shot = CS.Shot(CSD.CUTSCENES["the_storm"]["shots"][0])
        point = shot.world_point(ST.STOP_BY_ID, ST)
        self.assertIsNotNone(point)
        self.assertGreater(point[0], 0)

    def test_the_endgame_hud_does_not_crash(self):
        """Heading home with every page used to raise KeyError."""
        game = self.game
        game.state.visited = ["prologue"]
        for stop in ST.STOPS:
            game.state.complete_stop(stop)
        game.switch("overworld")
        scene = game.current
        scene._modal = None
        pc, pr = ST.PROLOGUE["pos"]
        scene.player = pygame.Vector2(pc * 16 + 8, pr * 16 + 8)
        scene.update(1.0 / 60.0)
        scene.draw(game.canvas)          # must not raise


if __name__ == "__main__":
    unittest.main()
