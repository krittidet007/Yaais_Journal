"""The temporary skip mod (deleted before release)."""

import os
import unittest

import pygame

import main
from game import mod_skip
from game import save
from game import settings as S
from game import story as ST
from game.game_state import GameState


class TestMod(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    @classmethod
    def tearDownClass(cls):
        cls.game.window = None
        save.clear()

    def test_gated_by_env(self):
        old = os.environ.get("WICHA_MOD")
        try:
            os.environ.pop("WICHA_MOD", None)
            self.assertFalse(mod_skip.enabled())
            os.environ["WICHA_MOD"] = "1"
            self.assertTrue(mod_skip.enabled())
        finally:
            if old is None:
                os.environ.pop("WICHA_MOD", None)
            else:
                os.environ["WICHA_MOD"] = old

    def test_unlock_all(self):
        st = GameState()
        mod_skip.unlock_all(st)
        self.assertTrue(st.journey_done())
        self.assertTrue(st.named)
        self.assertEqual(st.journal_count(), ST.TOTAL_STOPS)
        self.assertEqual(st.spice, 5)

    def test_finish_here(self):
        game = self.game
        game.state.reset()
        game.state.visited = ["prologue"]
        game.switch("overworld")
        scene = game.current
        scene._modal = None
        game.box.hide()
        stop = ST.STOP_BY_ID["chumphon"]
        c, r = stop["pos"]
        scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        scene.update(1.0 / S.FPS)
        self.assertTrue(mod_skip.finish_here(game))
        self.assertTrue(game.state.stop_done("chumphon"))


if __name__ == "__main__":
    unittest.main()
