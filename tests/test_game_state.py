"""The journal state: pages, cards, words, meters, and saves."""

import unittest

from game import game_state as GS
from game import story as ST
from game.game_state import GameState


def _first_stop():
    return ST.STOPS[0]


class TestGameState(unittest.TestCase):

    def setUp(self):
        self.st = GameState()

    def test_fresh_state(self):
        self.assertEqual(self.st.journal_count(), 0)
        self.assertEqual(self.st.journal_total(), ST.TOTAL_PAGES)
        self.assertFalse(self.st.journey_done())
        self.assertFalse(self.st.named)
        self.assertEqual(self.st.spice, 0)
        self.assertEqual(self.st.respect, 0)

    def test_complete_stop_records_everything(self):
        stop = _first_stop()
        fresh, gained = self.st.complete_stop(stop)
        self.assertTrue(fresh)
        self.assertIn(stop["id"], self.st.pages)
        self.assertIn(stop["id"], self.st.visited)
        for card in stop["cards"]:
            self.assertIn(card, self.st.cards)
        self.assertIn(stop["word"]["roman"], [w["roman"] for w in self.st.words])
        self.assertTrue(self.st.stop_done(stop["id"]))
        self.assertTrue(self.st.stop_known(stop["id"]))

    def test_complete_stop_is_idempotent(self):
        stop = _first_stop()
        fresh_one, _ = self.st.complete_stop(stop)
        fresh_two, _ = self.st.complete_stop(stop)
        self.assertTrue(fresh_one)
        self.assertFalse(fresh_two)
        self.assertEqual(self.st.journal_count(), 1)

    def test_add_page_card_word_dedupe(self):
        stop = _first_stop()
        self.assertTrue(self.st.add_page(stop["id"]))
        self.assertFalse(self.st.add_page(stop["id"]))
        card = stop["cards"][0]
        self.assertTrue(self.st.add_card(card))
        self.assertFalse(self.st.add_card(card))
        word = stop["word"]
        self.assertTrue(self.st.add_word(word))
        self.assertFalse(self.st.add_word(word))   # same roman

    def test_meters_clamp(self):
        self.st.bump_spice(10)
        self.assertEqual(self.st.spice, 5)
        self.st.bump_spice(-10)
        self.assertEqual(self.st.spice, 0)
        self.st.bump_respect(-5)
        self.assertEqual(self.st.respect, 0)
        self.st.bump_respect(50)
        self.assertGreater(self.st.respect, 0)

    def test_act_progresses(self):
        self.assertEqual(self.st.act_of(), 1)
        for stop in ST.STOPS:
            if stop["act"] == 1:
                self.st.complete_stop(stop)
        # act 1 is done, so the journey is working on act 2 now
        self.assertEqual(self.st.act_of(), 2)
        for stop in ST.STOPS:
            if stop["act"] == 2:
                self.st.complete_stop(stop)
                break
        self.assertEqual(self.st.act_of(), 2)

    def test_journey_done(self):
        for stop in ST.STOPS:
            self.st.complete_stop(stop)
        self.assertTrue(self.st.journey_done())
        self.assertEqual(self.st.journal_count(), ST.TOTAL_STOPS)

    def test_to_dict_from_dict_roundtrip(self):
        for stop in ST.STOPS[:6]:
            self.st.complete_stop(stop)
        self.st.bump_spice(3)
        self.st.bump_respect(4)
        self.st.spirit_name = "Phi"
        self.st.named = True
        data = self.st.to_dict()
        other = GameState()
        other.from_dict(data)
        self.assertEqual(other.pages, self.st.pages)
        self.assertEqual(other.cards, self.st.cards)
        self.assertEqual(other.words, self.st.words)
        self.assertEqual(other.visited, self.st.visited)
        self.assertEqual(other.spice, self.st.spice)
        self.assertEqual(other.respect, self.st.respect)
        self.assertEqual(other.spirit_name, "Phi")
        self.assertTrue(other.named)
        self.assertTrue(other.journey_done() == self.st.journey_done())

    def test_from_dict_ignores_rubbish(self):
        st = GameState()
        st.from_dict(None)
        self.assertEqual(st.journal_count(), 0)
        st.from_dict({"pages": "not-a-list", "words": [42, {"roman": "roi"}]})
        self.assertEqual(st.pages, [])
        self.assertEqual([w["roman"] for w in st.words], ["roi"])

    def test_reset_clears_all(self):
        for stop in ST.STOPS:
            self.st.complete_stop(stop)
        self.st.reset()
        self.assertEqual(self.st.journal_count(), 0)
        self.assertFalse(self.st.named)
        self.assertFalse(self.st.journey_done())
        self.assertEqual(self.st.cards, [])

    def test_display_spirit_name(self):
        self.assertEqual(self.st.display_spirit_name(), "SPIRIT")
        self.st.spirit_name = "Phi"
        self.assertEqual(self.st.display_spirit_name(), "Phi")

    def test_module_singleton(self):
        self.assertIsInstance(GS.state, GameState)

    def test_pos_and_found_roundtrip(self):
        self.st.pos = [1928.0, 424.0]
        self.st.found = ["chumphon", "ko_tao"]
        other = GameState()
        other.from_dict(self.st.to_dict())
        self.assertEqual(other.pos, [1928.0, 424.0])
        self.assertEqual(other.found, ["chumphon", "ko_tao"])
        self.st.reset()
        self.assertIsNone(self.st.pos)
        self.assertEqual(self.st.found, [])

    def test_pos_rejects_rubbish(self):
        self.st.from_dict({"pos": "beach", "found": "nope"})
        self.assertIsNone(self.st.pos)
        self.assertEqual(self.st.found, [])

    def test_catches_playtime_fuel_combo_roundtrip(self):
        self.st.catches = ["mackerel", "moonfish"]
        self.st.play_t = 123.5
        self.st.fuel = 42.0
        self.st.combo = 4
        other = GameState()
        other.from_dict(self.st.to_dict())
        self.assertEqual(other.catches, ["mackerel", "moonfish"])
        self.assertAlmostEqual(other.play_t, 123.5)
        self.assertAlmostEqual(other.fuel, 42.0)
        self.assertEqual(other.combo, 4)
        self.st.reset()
        self.assertEqual(self.st.catches, [])
        self.assertEqual(self.st.play_t, 0.0)
        self.assertEqual(self.st.fuel, 100.0)
        self.assertEqual(self.st.combo, 0)


if __name__ == "__main__":
    unittest.main()
