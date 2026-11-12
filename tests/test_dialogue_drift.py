"""Conversations never freeze you: walk while they talk, and wander out
of earshot and the dialogue fades (beats still advance)."""

import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

import main  # noqa: E402
from game import save  # noqa: E402
from game import story as ST  # noqa: E402


class TestDialogueDrift(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    def setUp(self):
        self.game.state.reset()
        self.game.next_stop = None
        save.clear()
        self.game.state.visited = ["prologue"]
        self.game.state.pos = None
        self.game.switch("overworld")
        self.scene = self.game.current
        self.scene._modal = None
        self.scene._greeted.clear()          # scenes persist between tests
        self.game.box.hide()

    def _key(self, key, down=True):
        self.scene.handle_event(pygame.event.Event(
            pygame.KEYDOWN if down else pygame.KEYUP, key=key))

    # -------------------------------------------------- movement while talking
    def test_player_moves_during_greeting(self):
        sc = self.scene
        stop = ST.STOPS[0]
        sc.player = pygame.Vector2(*sc._px(*stop["pos"]))
        sc.update(1.0 / 60.0)                    # greeting triggers
        self.assertIsNotNone(sc._modal)
        self.assertEqual(sc._modal["kind"], "greeting")
        x0 = sc.player.x
        self._key(pygame.K_RIGHT)                # keep walking while they talk
        for _ in range(30):
            sc.update(1.0 / 60.0)
        self._key(pygame.K_RIGHT, down=False)
        self.assertGreater(sc.player.x, x0 + 4.0)   # actually moved
        self.assertIsNotNone(sc._modal)             # still talking

    def test_running_still_works_mid_dialogue(self):
        sc = self.scene
        stop = ST.STOPS[0]
        sc.player = pygame.Vector2(*sc._px(*stop["pos"]))
        sc.update(1.0 / 60.0)
        self._key(pygame.K_LSHIFT)                # run
        self._key(pygame.K_RIGHT)
        x0 = sc.player.x
        for _ in range(30):
            sc.update(1.0 / 60.0)
        self._key(pygame.K_RIGHT, down=False)
        self._key(pygame.K_LSHIFT, down=False)
        self.assertGreater(sc.player.x, x0 + 20.0)  # ran, not walked
        self.assertIsNotNone(sc._modal)

    # -------------------------------------------------------- drifting away
    def test_walking_out_of_earshot_ends_the_conversation(self):
        sc = self.scene
        stop = ST.STOPS[0]
        sc.player = pygame.Vector2(*sc._px(*stop["pos"]))
        sc.update(1.0 / 60.0)
        self.assertIsNotNone(sc._modal)
        anchor = sc._modal["anchor"]
        self.assertIsNotNone(anchor)
        # teleport far past the invisible boundary, then keep walking
        sc.player = anchor + pygame.Vector2(SPOT_DRIFT_X, 0)
        sc.update(1.0 / 60.0)
        self.assertIsNone(sc._modal)              # faded away
        self.assertFalse(self.game.box.visible)
        # ...but the town remembers you heard the welcome: beat advanced
        self.assertGreaterEqual(self.game.state.quests.get(stop["id"], 0), 1)

    def test_pinned_dialogues_follow_you(self):
        # the opening prologue cannot be walked away from
        self.game.state.visited = []
        self.game.switch("overworld")
        sc = self.game.current
        self.assertIsNotNone(sc._modal)
        self.assertEqual(sc._modal["kind"], "prologue")
        self.assertIsNone(sc._modal["anchor"])
        sc.player = pygame.Vector2(1000.0, 1000.0)   # miles from Yaai's house
        sc.update(1.0 / 60.0)
        self.assertIsNotNone(sc._modal)               # still with you

    def test_wind_and_memory_dialogues_anchor_to_where_you_stood(self):
        sc = self.scene
        here = pygame.Vector2(*sc._px(*ST.STOPS[3]["pos"]))
        sc.player = here.copy()
        sc._show([("NOI", "NOI", "a voice on the wind")], kind="talk")
        self.assertAlmostEqual(sc._modal["anchor"].x, here.x, places=3)
        self.assertAlmostEqual(sc._modal["anchor"].y, here.y, places=3)
        self.assertGreater(sc._modal["drift"], 0.0)

    # ---------------------------------------------- interruption bookkeeping
    def test_a_catch_mid_greeting_does_not_lose_the_beat(self):
        sc = self.scene
        stop = ST.STOPS[0]
        sc.player = pygame.Vector2(*sc._px(*stop["pos"]))
        sc.update(1.0 / 60.0)                    # greeting playing
        self.assertEqual(sc._modal["kind"], "greeting")
        sc._show([("NOI", "NOI", "A magpie had you!")])   # urgent interruption
        self.assertEqual(sc._modal["kind"], "talk")       # new voice plays
        # the greeting's beat was settled, not lost
        self.assertGreaterEqual(self.game.state.quests.get(stop["id"], 0), 1)

    def test_sight_closed_by_drift_advances_beat(self):
        sc = self.scene
        stop = ST.STOPS[0]
        sc.player = pygame.Vector2(*sc._px(*stop["pos"]))
        sc._show([("NOI", "NOI", "look well")],
                 kind="sight", stop_id=stop["id"])
        anchor = sc._modal["anchor"]
        sc.player = anchor + pygame.Vector2(0, -SPOT_DRIFT_Y)
        sc.update(1.0 / 60.0)
        self.assertGreaterEqual(self.game.state.quests.get(stop["id"], 0), 2)


SPOT_DRIFT_X = 8 * 16 + 2     # just past the town's earshot ring
SPOT_DRIFT_Y = 8 * 16 + 2


if __name__ == "__main__":
    unittest.main()
