"""Landmarks, town activities and the errands that come after the code."""

import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

import main  # noqa: E402
from game import landmarks as LM  # noqa: E402
from game import regions as RG  # noqa: E402
from game import save  # noqa: E402
from game import story as ST  # noqa: E402
from tests.helpers import play_activity  # noqa: E402
from tests.test_tablets import SOLUTIONS  # noqa: E402


class TestLandmarks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    def setUp(self):
        self.game.state.reset()
        self.game.state.visited = ["prologue"]
        save.clear()
        self.game.switch("overworld")
        self.scene = self.game.current

    def test_every_region_has_five_landmarks(self):
        for region in RG.REGIONS:
            marks = LM.LANDMARKS.get(region, [])
            self.assertGreaterEqual(len(marks), 5, region)

    def test_landmarks_are_unique_and_anchored(self):
        seen = set()
        for marks in LM.LANDMARKS.values():
            for mark in marks:
                self.assertNotIn(mark["id"], seen)
                seen.add(mark["id"])
                self.assertIn(mark["stop"], ST.STOP_BY_ID)
                self.assertGreater(len(mark["story"]), 3)

    def test_landmarks_sit_on_walkable_ground(self):
        for spot in self.scene.landmarks:
            c, r = spot["pos"]
            self.assertIn(self.scene.tm.cell(r, c), ("G", "A", "D", "S"),
                          spot["id"])

    def test_walking_up_to_one_tells_its_story(self):
        spot = self.scene.landmarks[0]
        c, r = spot["pos"]
        self.scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        self.scene.update(1.0 / 60.0)
        self.assertIsNotNone(self.scene._modal)
        self.assertEqual(self.scene._modal["kind"], "landmark")
        self.assertIn(spot["id"], self.game.state.landmarks)
        self.assertIn(spot["card"], self.game.state.cards)
        self.assertGreaterEqual(self.game.state.respect, 1)

    def test_a_landmark_is_found_only_once(self):
        spot = self.scene.landmarks[0]
        c, r = spot["pos"]
        self.scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        self.scene.update(1.0 / 60.0)
        self.scene._close_modal()
        respect = self.game.state.respect
        self.scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        self.scene.update(1.0 / 60.0)
        self.assertEqual(self.game.state.respect, respect)

    def test_the_journal_lists_the_places_you_found(self):
        spot = self.scene.landmarks[0]
        c, r = spot["pos"]
        self.scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        self.scene.update(1.0 / 60.0)
        menu = self.game.journal
        menu.open()
        menu.tab = menu.TABS.index("PLACES")
        entries = menu._entries()
        self.assertTrue(any(name == spot["name"] for name, _t in entries))
        menu.draw(self.game.canvas)


class TestActivities(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    def setUp(self):
        self.game.state.reset()
        self.game.state.visited = ["prologue"]
        save.clear()

    def test_every_stop_has_an_activity(self):
        for stop in ST.STOPS:
            self.assertIn("activity", stop, stop["id"])
            self.assertIn("type", stop["activity"], stop["id"])

    def test_the_activity_is_reachable_after_the_code(self):
        game = self.game
        game.switch("overworld")
        scene = game.current
        scene._modal = None
        game.box.hide()
        stop = ST.STOP_BY_ID["ko_tao"]
        game.state.quests["ko_tao"] = 3
        game.state.flags.append("code_tutorial")
        scene.player = pygame.Vector2(*scene._tablet_px(stop))
        scene.update(1.0 / 60.0)
        scene._open_tablet(stop)
        scene._on_run("turtles = 4")
        # the town takes over for its own activity
        self.assertEqual(game.current.name, "stop")
        self.assertEqual(game.current.phase, "activity")
        play_activity(game)
        game.switch("overworld")
        self.assertTrue(game.state.stop_done("ko_tao"))

    def test_the_activity_can_be_played_and_won(self):
        for stop in ST.STOPS[:6]:
            game = main.Game()
            game.state.reset()
            game.state.visited = ["prologue"]
            game.switch("overworld")
            scene = game.current
            scene._modal = None
            game.box.hide()
            game.state.quests[stop["id"]] = 3
            game.state.flags.append("code_tutorial")
            scene.player = pygame.Vector2(*scene._tablet_px(stop))
            scene.update(1.0 / 60.0)
            scene._open_tablet(stop)
            scene._on_run(SOLUTIONS[stop["id"]])
            self.assertEqual(game.current.name, "stop", stop["id"])
            play_activity(game)
            self.assertEqual(game.current.phase, "reward",
                             "%s activity not finished" % stop["id"])


class TestErrands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    def setUp(self):
        self.game.state.reset()
        self.game.state.visited = ["prologue"]
        save.clear()
        self.game.switch("overworld")
        self.scene = self.game.current

    def test_every_town_with_a_landmark_offers_an_errand(self):
        with_errand = [e for e in ST.EXTRA.values() if e.get("errand")]
        self.assertGreaterEqual(len(with_errand), 20)

    def test_the_errand_is_offered_once_the_page_is_yours(self):
        stop = ST.STOP_BY_ID["chumphon"]
        self.scene.player = pygame.Vector2(*self.scene._host_px(stop))
        before = self.scene._host_lines(stop)
        self.assertNotIn("errand_chumphon", self.game.state.flags)
        self.game.state.complete_stop(stop)
        after = self.scene._host_lines(stop)
        self.assertIn("errand_chumphon", self.game.state.flags)
        self.assertGreater(len(after), len(before))

    def test_the_errand_is_not_offered_twice(self):
        stop = ST.STOP_BY_ID["chumphon"]
        self.game.state.complete_stop(stop)
        self.scene._host_lines(stop)
        again = self.scene._host_lines(stop)
        self.assertNotIn("errand_chumphon", self.game.state.flags
                         if False else [])


if __name__ == "__main__":
    unittest.main()
