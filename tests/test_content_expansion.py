"""Side quests, road encounters, the deeper beats and the AI pipeline."""

import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

import main  # noqa: E402
from game import encounters as EN  # noqa: E402
from game import save  # noqa: E402
from game import sidequests as SQ  # noqa: E402
from game import story as ST  # noqa: E402


class TestSideQuests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    def setUp(self):
        self.game.state.reset()
        self.game.state.visited = ["prologue"]
        save.clear()
        self.game.switch("overworld")
        self.scene = self.game.current

    def test_there_are_enough_side_quests(self):
        self.assertGreaterEqual(len(SQ.SIDE_QUESTS), 15)

    def test_every_quest_has_a_place_and_a_reward(self):
        landmark_ids = set()
        for marks in ST.__dict__.get("LANDMARKS", {}).values():
            pass
        from game import landmarks as LM
        for marks in LM.LANDMARKS.values():
            for mark in marks:
                landmark_ids.add(mark["id"])
        for qid, quest in SQ.SIDE_QUESTS.items():
            self.assertIn(quest["from"], ST.STOP_BY_ID, qid)
            self.assertIn(quest["at"], landmark_ids, qid)
            self.assertTrue(quest["ask"])
            self.assertTrue(quest["answer"])
            self.assertIn("respect", quest.get("reward", {}))

    def test_a_quest_can_be_given_taken_and_paid(self):
        stop = ST.STOP_BY_ID["chumphon"]
        self.game.state.complete_stop(stop)
        self.scene.player = pygame.Vector2(*self.scene._host_px(stop))
        self.scene._host_lines(stop)
        self.assertIn("sq_chumphon_lens_given", self.game.state.flags)
        # go and stand at the place the quest is about
        spot = [m for m in self.scene.landmarks
                if m["id"] == "longtail_wreck"][0]
        c, r = spot["pos"]
        self.scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        self.scene.update(1.0 / 60.0)
        self.assertIn("sq_chumphon_lens_ready", self.game.state.flags)
        # come back and be paid
        self.scene._close_modal()
        self.scene.player = pygame.Vector2(*self.scene._host_px(stop))
        respect = self.game.state.respect
        self.scene._host_lines(stop)
        self.assertIn("sq_chumphon_lens_done", self.game.state.flags)
        self.assertGreater(self.game.state.respect, respect)
        self.assertIn("The Wreck's Name", self.game.state.cards)

    def test_the_journal_has_a_quest_log(self):
        menu = self.game.journal
        self.assertIn("QUESTS", menu.TABS)
        menu.open()
        menu.tab = menu.TABS.index("QUESTS")
        menu.draw(self.game.canvas)          # draws even when empty


class TestEncounters(unittest.TestCase):
    def test_encounters_exist_for_every_region(self):
        from game import regions as RG
        for region in RG.REGIONS:
            here = [e for e in EN.ENCOUNTERS if e.get("where") == region]
            self.assertGreaterEqual(len(here), 2, region)
        anywheres = [e for e in EN.ENCOUNTERS if e.get("where") == "any"]
        self.assertGreaterEqual(len(anywheres), 5)

    def test_an_encounter_fires_while_walking(self):
        game = main.Game()
        game.state.reset()
        game.state.visited = ["prologue"]
        game.switch("overworld")
        scene = game.current
        game.state.act_seen = 1        # the act beat has already played
        scene._modal = None
        game.box.hide()
        # stand out on the road, away from any town
        scene.player = pygame.Vector2(300, 300)
        scene._near = None
        scene._road_t = 42.0
        scene.speed = 100.0
        scene.update(1.0 / 60.0)
        self.assertIsNotNone(scene.noi_bark)
        scene.draw(game.canvas)


class TestDeeperBeats(unittest.TestCase):
    def test_every_stop_has_deeper_beats(self):
        for stop in ST.STOPS:
            scene = ST.SCENES.get(stop["id"], {})
            for beat in ("arrive", "mid", "spark"):
                self.assertGreaterEqual(len(scene.get(beat, [])), 4,
                                        "%s %s" % (stop["id"], beat))

    def test_the_story_grew_a_lot(self):
        words = 0
        for stop in ST.STOPS:
            words += sum(len(l[-1].split()) for l in stop["lines"])
            scene = ST.SCENES.get(stop["id"], {})
            for beat in scene.values():
                words += sum(len(l[-1].split()) for l in beat)
        self.assertGreater(words, 12000)

    def test_there_are_five_acts_now(self):
        self.assertEqual(len(ST.ACTS), 5)
        for act in (1, 2, 3, 4, 5):
            self.assertIn(act, ST.PLOT, "act %d has no story beat" % act)

    def test_every_act_has_a_finale_stop_with_a_call(self):
        last = {}
        for stop in ST.STOPS:
            last[stop["act"]] = stop
        for act, stop in last.items():
            self.assertIn("call", stop, act)


class TestAIArtPipeline(unittest.TestCase):
    def test_the_palette_lock_makes_one_art_set(self):
        sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "tools"))
        import ai_unify
        pygame.display.init()
        pygame.display.set_mode((16, 16))
        # three deliberately clashing colours
        sheet = pygame.Surface((96, 32), pygame.SRCALPHA)
        for i, col in enumerate([(210, 60, 60), (60, 200, 120), (90, 90, 230)]):
            pygame.draw.circle(sheet, col, (16 + i * 32, 16), 12)
        locked = ai_unify.lock_palette(sheet)
        colours = set()
        for x in range(locked.get_width()):
            for y in range(locked.get_height()):
                colours.add(locked.get_at((x, y))[:3])
        master = set(ai_unify.MASTER)
        self.assertTrue(colours.issubset(master),
                        "%d colours escaped the master palette" % len(
                            colours - master))
        self.assertLessEqual(len(colours), len(master))

    def test_the_style_bible_exists(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "tools", "style_bible.md")
        self.assertTrue(os.path.exists(path))
        text = open(path, encoding="utf-8").read()
        self.assertIn("3/4 top-down", text)
        self.assertIn("upper left", text)


if __name__ == "__main__":
    unittest.main()
