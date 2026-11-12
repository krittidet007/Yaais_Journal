"""The rune tablets: every stop's spell solves, and no prefill is free."""

import unittest

from game import story as ST
from game import tablets as TB

# the intended solution for each stop's tablet
SOLUTIONS = {
    "chumphon": 'print("hold fast")',
    "ko_tao": "turtles = 4",
    "ko_pha_ngan": 'print("".join(["V", "P", "B"]))',
    "ko_samui": 'print("grandfather")\nprint("grandmother")\nprint("stone")',
    "surat_thani": 'rope = 4\nfor i in range(rope):\n    print("pull")',
    "ranong": 'if water == "clear":\n    print("keep")\nelse:\n    print("swirl")',
    "surin_islands": 'if sea_pulls_back:\n    print("go up")\nelse:\n    print("sail")',
    "khao_lak": 'print("we remember")',
    "similan": 'for i in range(1, 10):\n    print(f"island {i}")',
    "phang_nga": 'if ball_dry:\n    print("pass")\nelse:\n    print("fetch")',
    "phuket": 'if sails == "ships":\n    print("light")\nelse:\n    print("wait")',
    "promthep": 'if sun == "low":\n    print("click")\nelse:\n    print("wait")',
    "ko_phi_phi": 'lamp = 0\nwhile lamp < 3:\n    print("steady")\n    lamp = lamp + 1',
    "krabi": 'steps = 9\nfor i in range(1, steps + 1):\n    print("breathe" if i % 3 == 0 else "step")',
    "nakhon": 'calls = [p.upper() for p in ["left", "down", "right", "up"]]',
    "phatthalung": 'troupe = {"hero": 1, "clown": 3, "demon": 1}\nvoices = sum(troupe.values())',
    "trang": 'for n in range(1, 13):\n    print(f"cup {n}")',
    "ko_kradan": 'print("float")',
    "satun": 'def mend(page):\n    try:\n        return page + " (mended)"\n    except TypeError:\n        return "unknown (mended)"',
    "ko_lipe": 'def send(worry):\n    return "gone: " + worry',
    "songkhla": 'pattern = "indigo,silk,temple".split(",")',
    "pattani": 'if shoes_off:\n    print("welcome")\nelse:\n    print("wait")',
    "yala": 'class Stamp:\n    color = "blue"\n    def press(self, cloth):\n        return cloth + " batik"',
    "narathiwat": 'def chorus(call):\n    return call + "!"\nprint(chorus("home"))',
}


class TestTablets(unittest.TestCase):

    def test_every_stop_has_a_puzzle(self):
        self.assertEqual(set(ST.CODE), {s["id"] for s in ST.STOPS})
        for stop_id, spec in ST.CODE.items():
            self.assertIn(spec["kind"], ("say", "lines", "set", "table", "func", "safe", "class", "gauntlet"))
            self.assertTrue(spec["title"])
            self.assertTrue(spec["status"])
            self.assertTrue(spec["hint"])
            self.assertIn("prefill", spec)

    def test_solutions_cover_every_stop(self):
        self.assertEqual(set(SOLUTIONS), {s["id"] for s in ST.STOPS})

    def test_every_solution_passes(self):
        for stop_id, code in SOLUTIONS.items():
            with self.subTest(stop=stop_id):
                ok, _console, _status = TB.validate(ST.CODE[stop_id], code)
                self.assertTrue(ok)

    def test_no_prefill_is_free(self):
        for stop_id, spec in ST.CODE.items():
            with self.subTest(stop=stop_id):
                ok, _console, _status = TB.validate(spec, spec["prefill"])
                self.assertFalse(ok)

    def test_broken_code_fails_kindly(self):
        spec = ST.CODE["ko_tao"]
        ok, console, status = TB.validate(spec, "turtles = = 4")
        self.assertFalse(ok)
        self.assertTrue(status)   # the tablet still teaches
        ok, _c, _s = TB.validate(spec, "turtles = 5")
        self.assertFalse(ok)

    def test_unknown_kind_rejected(self):
        ok, _c, _s = TB.validate({"kind": "summon"}, "x = 1")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
