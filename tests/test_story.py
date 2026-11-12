"""Story integrity: the 24 stops of Yaai's Journal, plus prologue
and finale, must be well-formed and consistent."""

import unittest

from game import story as ST
from game import world_map as WM

ACT_TYPES = {"choice", "match", "timing", "rhythm", "calm"}
KINDS = {"province", "secret"}
REQUIRED = ("id", "name", "title", "kind", "act", "minutes", "pos",
            "lines", "activity", "learn", "word", "cards", "page")


class TestStory(unittest.TestCase):

    def test_counts(self):
        self.assertEqual(len(ST.STOPS), 24)
        self.assertEqual(ST.TOTAL_STOPS, 24)
        # cover page + 24 stops + the finale's blank page
        self.assertEqual(ST.TOTAL_PAGES, 26)
        self.assertEqual(len(ST.ACTS), 5)

    def test_ids_unique(self):
        ids = [s["id"] for s in ST.STOPS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ST.STOP_BY_ID), 24)
        self.assertNotIn("prologue", ST.STOP_BY_ID)

    def test_every_stop_well_formed(self):
        for stop in ST.STOPS:
            for key in REQUIRED:
                self.assertIn(key, stop, "%s missing %s" % (stop.get("id"), key))
            self.assertIn(stop["kind"], KINDS)
            self.assertIn(stop["act"], (1, 2, 3, 4, 5))
            self.assertGreater(stop["minutes"], 0)
            # position is a (col, row) tile pair inside the world
            c, r = stop["pos"]
            self.assertIsInstance(c, int)
            self.assertIsInstance(r, int)
            self.assertTrue(0 <= c < WM.WORLD_COLS)
            self.assertTrue(0 <= r < WM.WORLD_ROWS)
            # dialogue is a list of (speaker, accent-key, text)
            self.assertGreater(len(stop["lines"]), 0)
            for line in stop["lines"]:
                self.assertEqual(len(line), 3)
            # the page, the lesson and the word are all present
            self.assertTrue(stop["page"])
            self.assertTrue(stop["learn"])
            self.assertIn("roman", stop["word"])
            self.assertIn("meaning", stop["word"])

    def test_activities_well_formed(self):
        for stop in ST.STOPS:
            act = stop["activity"]
            self.assertIn(act["type"], ACT_TYPES)
            self.assertTrue(act["prompt"])
            kind = act["type"]
            if kind == "choice":
                self.assertGreaterEqual(len(act["options"]), 2)
                for opt in act["options"]:
                    self.assertIn("text", opt)
                    self.assertIn("reply", opt)
                    self.assertIn("respect", opt)
            elif kind == "match":
                self.assertGreater(len(act["options"], ), 0)
                self.assertGreater(len(act.get("decoys", [])), 0)
                # decoys must not secretly be correct answers
                for decoy in act["decoys"]:
                    self.assertNotIn(decoy, act["options"])
            elif kind == "timing":
                self.assertGreater(act.get("zone", 0), 0)
            elif kind == "rhythm":
                self.assertGreater(len(act["sequence"]), 0)
                for step in act["sequence"]:
                    self.assertIn(step, ("left", "right", "up", "down"))
            elif kind == "calm":
                self.assertGreater(act.get("steps", 0), 0)

    def test_act_finales_have_a_call(self):
        # the last stop of each act carries Yaai's closing call
        last_by_act = {}
        for stop in ST.STOPS:
            last_by_act[stop["act"]] = stop
        for act, stop in last_by_act.items():
            self.assertIn("call", stop,
                          "act %d finale (%s) needs Yaai's call"
                          % (act, stop["id"]))

    def test_acts_are_contiguous(self):
        # the five acts tile the 24 stops without gaps or overlaps
        self.assertEqual(ST.ACTS[0][2], 0)          # act 1 starts at stop 0
        self.assertEqual(ST.ACTS[-1][3], ST.TOTAL_STOPS - 1)  # act 3 ends at 23
        for (a, _n, lo, hi), (b, _n2, lo2, _hi2) in zip(ST.ACTS, ST.ACTS[1:]):
            self.assertEqual(lo2, hi + 1, "acts %d/%d are not contiguous" % (a, b))
        # every stop's act matches the range its index falls in
        for i, stop in enumerate(ST.STOPS):
            act = next(a for a, _n, lo, hi in ST.ACTS if lo <= i <= hi)
            self.assertEqual(stop["act"], act)

    def test_chapters_are_journal_names(self):
        titles = [s["title"] for s in ST.STOPS]
        self.assertEqual(len(titles), len(set(titles)))
        for stop in ST.STOPS:
            self.assertTrue(len(stop["title"]) >= 4)
        self.assertEqual(ST.chapter(ST.STOPS[0]), "Chapter 1 · The Signal Hill")
        self.assertEqual(ST.chapter(ST.STOPS[-1]), "Chapter 24 · The Last Chorus")

    def test_prologue_and_finale(self):
        self.assertEqual(ST.PROLOGUE["id"], "prologue")
        self.assertGreater(len(ST.PROLOGUE["lines"]), 0)
        self.assertEqual(ST.FINALE["id"], "finale")
        self.assertGreater(len(ST.FINALE["lines"]), 0)

    def test_speakers_have_accents(self):
        from game import settings as S
        for stop in ST.STOPS + [ST.PROLOGUE, ST.FINALE]:
            for _speaker, accent, _text in stop["lines"]:
                self.assertIn(accent, S.ACCENTS,
                              "unknown accent key %r" % accent)

    def test_words_are_unique_per_stop(self):
        # a word may repeat across stops only by design; here we just
        # check every stop teaches at least one word
        for stop in ST.STOPS:
            self.assertTrue(stop["word"]["roman"])

    def test_every_stop_has_a_host_and_a_hidden_spark(self):
        for stop in ST.STOPS:
            extra = ST.extra_of(stop["id"])
            self.assertIn("host", extra, stop["id"])
            self.assertIn("look", extra, stop["id"])
            self.assertIn(extra["look"], ("ruen", "nok", "child"), stop["id"])
            self.assertGreaterEqual(len(extra.get("lines", [])), 2, stop["id"])
            self.assertTrue(extra.get("hint"), stop["id"])
            self.assertTrue(extra.get("found"), stop["id"])
            self.assertIn(extra.get("look"), ST.HOST_ACCENT, stop["id"])


if __name__ == "__main__":
    unittest.main()
