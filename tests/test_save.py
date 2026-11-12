"""Autosave and the three manual save slots."""

import os
import unittest

import main

from game import save
from game import story as ST
from game.game_state import GameState


def _filled_state():
    st = GameState()
    st.spirit_name = "Phi"
    st.named = True
    for stop in ST.STOPS[:3]:
        st.complete_stop(stop)
    st.bump_spice(2)
    st.bump_respect(3)
    return st


class TestSave(unittest.TestCase):

    def test_resumable_includes_the_journey(self):
        for name in ("washup", "village_naming", "overworld", "epilogue"):
            self.assertIn(name, save.RESUMABLE)

    def test_write_and_read_roundtrip(self):
        st = _filled_state()
        self.assertTrue(save.write(st, "overworld"))
        data = save.read()
        self.assertIsNotNone(data)
        self.assertEqual(data["scene"], "overworld")
        self.assertEqual(data["state"]["spirit_name"], "Phi")
        self.assertEqual(data["state"]["spice"], 2)

    def test_read_rejects_non_resumable(self):
        st = _filled_state()
        save.write(st, "cover")           # not resumable
        self.assertIsNone(save.read())

    def test_read_missing_file(self):
        save.clear()
        self.assertIsNone(save.read())

    def test_clear(self):
        save.write(_filled_state(), "overworld")
        save.clear()
        self.assertFalse(os.path.exists(save.path()))
        self.assertIsNone(save.read())

    def test_switch_autosaves_resumable_scenes(self):
        """main.Game.switch() keeps save.json fresh, so the cover's
        CONTINUE button appears after any real progress."""
        game = main.Game()
        self.assertFalse(save.has_save())
        game.switch("washup")              # resumable: autosaves at entry
        self.assertTrue(save.has_save())
        data = save.read()
        self.assertEqual(data["scene"], "washup")

        game.switch("village_naming")       # another resumable hop
        data = save.read()
        self.assertEqual(data["scene"], "village_naming")

        save.clear()
        game.switch("cover")               # not resumable: leaves it alone
        self.assertFalse(save.has_save())
        game.window = None

    def test_switch_never_crashes_on_unknown_scene(self):
        game = main.Game()
        game.switch("cover")
        before = game.current.name
        game.switch("no_such_place")
        self.assertEqual(game.current.name, before)

    def test_slots(self):
        save.clear()
        for i in (1, 2, 3):
            self.assertIsNone(save.read_slot(i))
        self.assertFalse(save.has_slots())

        st = _filled_state()
        self.assertTrue(save.write_slot(1, st, "overworld"))
        self.assertTrue(save.write_slot(2, st, "overworld"))
        self.assertTrue(save.has_slots())

        one = save.read_slot(1)
        self.assertIsNotNone(one)
        self.assertEqual(one["scene"], "overworld")
        info = save.slot_info(1)
        self.assertEqual(info["name"], "Phi")
        self.assertEqual(info["items"], len(st.items))

    def test_slot_rejects_bad_scene(self):
        save.clear()
        # a slot holding a non-resumable scene is treated as empty
        import json
        os.makedirs(os.path.dirname(save.SLOTS_PATH), exist_ok=True)
        with open(save.SLOTS_PATH, "w", encoding="utf-8") as fh:
            json.dump({"1": {"scene": "splash", "state": {}}}, fh)
        self.assertIsNone(save.read_slot(1))
        self.assertIsNone(save.slot_info(1))


if __name__ == "__main__":
    unittest.main()
