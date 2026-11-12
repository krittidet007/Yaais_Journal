"""Danger on the road: Lom's magpies and the wild boar hunt on foot."""

import unittest

import pygame

import main
from game import save
from game import tiles as T
from game import world_map as WM
from game.scenes import overworld as OW


class TestMobs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    @classmethod
    def tearDownClass(cls):
        cls.game.window = None
        save.clear()

    def setUp(self):
        self.game.state.reset()
        self.game.next_stop = None
        self.game.state.visited = ["prologue"]
        self.game.state.pos = None
        self.game.switch("overworld")
        self.scene = self.game.current
        self.scene.mobs = self.scene._spawn_mobs()   # tests may shove mobs about
        self.scene._modal = None
        self.game.box.hide()

    def _lure(self, kind="magpie", dist=34.0):
        """Park one mob just ahead of the player and hand it back."""
        sc = self.scene
        m = sc.mobs[0]
        m["kind"] = kind
        m["chase"] = 106.0 if kind == "magpie" else 84.0
        m["x"], m["y"] = sc.player.x + dist, sc.player.y
        m["hx"], m["hy"] = m["x"], m["y"]
        m["state"] = "idle"
        return m

    # ------------------------------------------------------------- spawning
    def test_mobs_spawn_on_open_land(self):
        sc = self.scene
        self.assertGreaterEqual(len(sc.mobs), 12)
        for m in sc.mobs:
            c, r = int(m["x"]) // T.TILE, int(m["y"]) // T.TILE
            self.assertIn(sc.tm.cell(r, c), ("G", "A", "D"),
                          "a mob spawned where only water or forest lives")

    def test_mobs_keep_clear_of_the_towns(self):
        sc = self.scene
        pins = sc._pin_tiles()
        for m in sc.mobs:
            c, r = int(m["x"]) // T.TILE, int(m["y"]) // T.TILE
            for pc, pr in pins:
                self.assertFalse(abs(c - pc) < 8 and abs(r - pr) < 8,
                                 "a mob camps a stop pin")

    # ------------------------------------------------------------- chasing
    def test_a_nearby_mob_gives_chase(self):
        sc = self.scene
        self._lure(dist=60.0)
        sc.update(1 / 60)
        self.assertIsNotNone(sc._danger)
        self.assertEqual(sc.mobs[0]["state"], "chase")

    def test_far_mobs_leave_you_alone(self):
        sc = self.scene
        for m in sc.mobs:
            m["x"], m["y"] = sc.player.x + 400, sc.player.y
            m["hx"], m["hy"] = m["x"], m["y"]
            m["state"] = "idle"
        sc.update(1 / 60)
        self.assertIsNone(sc._danger)

    def test_caught_costs_a_mark_and_wind(self):
        sc = self.scene
        st = self.game.state
        st.respect = 5
        st.fuel = 100.0
        st.combo = 4
        self._lure(dist=16.0)
        before = st.caught
        for _ in range(240):
            sc.update(1 / 60)
            if st.caught > before:
                break
        self.assertEqual(st.caught, before + 1)
        self.assertEqual(st.respect, 4)
        self.assertLess(st.fuel, 100.0)
        self.assertEqual(st.combo, 0)
        self.assertGreater(sc._stun, 0.0)
        self.assertGreater(sc._shake, 0.0)

    def test_first_catch_reaches_a_blueprint(self):
        sc = self.scene
        self.game.state.caught = 0
        self._lure(dist=16.0)
        for _ in range(240):
            sc.update(1 / 60)
            if self.game.state.caught:
                break
            if sc._modal is not None:
                break
        self.assertIsNotNone(sc._modal)

    def test_stun_holds_the_player_still(self):
        sc = self.scene
        sc._stun = 1.0
        sc.keys = {pygame.K_RIGHT}
        x0 = sc.player.x
        for _ in range(30):
            sc.update(1 / 60)
        self.assertAlmostEqual(sc.player.x, x0, delta=1.0)

    # ------------------------------------------------------------- fleeing
    def test_running_outruns_a_magpie(self):
        sc = self.scene
        m = self._lure(dist=40.0)
        self.assertLess(m["chase"], OW.RUN)
        self.assertGreater(m["chase"], OW.WALK)

    def test_mobs_cannot_take_to_the_water(self):
        sc = self.scene
        # find a land tile with deep water immediately to its right
        bank = None
        for r in range(20, WM.WORLD_ROWS - 20, 7):
            span = WM._row_span(r)
            if span is None:
                continue
            lo, hi = span
            for c in range(lo, hi - 2):
                if sc.tm.cell(r, c) in ("G", "A", "D") \
                        and sc.tm.cell(r, c + 1) == "W" \
                        and sc.tm.cell(r, c + 2) == "W":
                    bank = (c, r)
                    break
            if bank:
                break
        self.assertIsNotNone(bank, "the world should have water to flee across")
        c, r = bank
        m = sc.mobs[0]
        m["x"], m["y"] = c * T.TILE + 8.0, r * T.TILE + 8.0
        for _ in range(120):
            sc._mob_step(m, 4.0, 0.0)          # shove it hard at the sea
        self.assertNotEqual(sc.tm.cell(int(m["y"]) // T.TILE,
                                       int(m["x"]) // T.TILE), "W")

    def test_the_south_keeps_a_record_of_pain(self):
        st = self.game.state
        st.caught = 3
        blob = st.to_dict()
        self.assertEqual(blob["caught"], 3)
        fresh = type(st)()
        fresh.from_dict(blob)
        self.assertEqual(fresh.caught, 3)


if __name__ == "__main__":
    unittest.main()
