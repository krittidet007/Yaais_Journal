"""The living world: compass, hosts, hidden sparks, sailing, no-teleport."""

import unittest

import pygame

import main
from game import save
from game import settings as S
from game import story as ST
from game import world_map as WM

CONFIRM = pygame.K_SPACE


def _confirm(game):
    for _ in range(2):
        game.box.update(10.0)
        game.current.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))


class TestTravel(unittest.TestCase):

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

    def _enter(self):
        self.game.state.visited = ["prologue"]   # skip the prologue modal
        self.game.state.pos = None
        self.game.switch("overworld")
        scene = self.game.current
        scene._modal = None
        self.game.box.hide()
        return scene

    # ------------------------------------------------------------- compass
    def test_compass_points_at_missing_page(self):
        scene = self._enter()
        tgt = scene._compass_target()
        self.assertIsNotNone(tgt)
        self.assertNotIn(tgt["id"], self.game.state.pages)
        # finishing everything but one stop aims at that stop
        skip = ST.STOPS[7]
        for stop in ST.STOPS:
            if stop["id"] != skip["id"]:
                self.game.state.complete_stop(stop)
        self.assertEqual(scene._compass_target()["id"], skip["id"])
        # a full journal points home to the Wai Khru
        self.game.state.complete_stop(skip)
        self.assertIs(scene._compass_target(), ST.PROLOGUE)

    # --------------------------------------------------------------- hosts
    def test_host_chats_in_town(self):
        game = self.game
        scene = self._enter()
        stop = ST.STOP_BY_ID["chumphon"]
        game.state.complete_stop(stop)
        scene.player = scene._host_px(stop).copy()
        scene.update(1.0 / S.FPS)
        self.assertIn(ST.extra_of("chumphon")["host"], scene.prompt)
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertIsNotNone(scene._modal)
        speaker = scene._modal["lines"][0][0]
        self.assertEqual(speaker, ST.extra_of("chumphon")["host"])

    # --------------------------------------------------------------- sparks
    def test_hidden_spark_pickup(self):
        game = self.game
        scene = self._enter()
        stop_id = "chumphon"
        scene.player = scene.sparks[stop_id].copy()
        before = game.state.respect
        scene.update(1.0 / S.FPS)
        self.assertIn(stop_id, game.state.found)
        self.assertEqual(game.state.respect, before + 1)
        self.assertIsNotNone(scene._modal)   # Noi cheers

    # --------------------------------------------------------------- sailing
    def test_board_sail_and_land(self):
        game = self.game
        scene = self._enter()
        dock = scene.docks[0]
        c, r = dock["pos"]
        scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        scene.update(1.0 / S.FPS)
        self.assertIsNotNone(scene._dock)
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertTrue(scene._sail)
        # water only: open water goes, land does not
        self.assertTrue(scene._ok(scene.player.x, scene.player.y))
        scene.player = pygame.Vector2(*scene._px(*ST.PROLOGUE["pos"]))
        self.assertFalse(scene._ok(scene.player.x + 4, scene.player.y + 10))
        # back on the water, step ashore onto walkable land
        scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertFalse(scene._sail)
        cell = scene._tile_at(scene.player.x + 4, scene.player.y + 10)
        self.assertNotIn(cell, ("W", "H", None))

    # ----------------------------------------------------------- no teleport
    def test_position_survives_scene_hops(self):
        game = self.game
        scene = self._enter()
        stop = ST.STOP_BY_ID["ko_tao"]
        c, r = stop["pos"]
        scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        game.next_stop = "ko_tao"
        game.switch("cover")             # leaving snapshots the position
        self.assertIsNotNone(game.state.pos)
        game.switch("overworld")         # coming back restores it
        back = game.current.player
        self.assertAlmostEqual(back.x, c * 16 + 8, delta=1.0)
        self.assertAlmostEqual(back.y, r * 16 + 8, delta=1.0)

    # ----------------------------------------------------------------- stakes
    def test_storm_pushes_the_exposed(self):
        scene = self._enter()
        storm = scene.storms[0]
        storm["x"], storm["y"] = 200 * 16.0, 150 * 16.0   # open Gulf water
        scene.player = pygame.Vector2(storm["x"] + 10, storm["y"])
        self.assertFalse(scene._sheltered())
        before = scene.player.copy()
        scene.update(1.0)
        self.assertGreater(scene.player.distance_to(before), 5.0)

    def test_storm_spares_shelter(self):
        scene = self._enter()
        stop = ST.STOP_BY_ID["chumphon"]
        c, r = stop["pos"]
        scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        self.assertTrue(scene._sheltered())
        storm = scene.storms[0]
        storm["x"], storm["y"] = scene.player.x + 10, scene.player.y
        before = scene.player.copy()
        scene.update(0.5)
        self.assertEqual(scene.player.distance_to(before), 0.0)

    def test_glide_burns_fuel_and_empty_grounds_you(self):
        scene = self._enter()
        scene._glide = True
        scene.keys.add(pygame.K_RIGHT)
        scene.update(1.0)
        self.assertLess(self.game.state.fuel, 100.0)
        scene.keys.discard(pygame.K_RIGHT)
        self.game.state.fuel = 0.0
        scene._glide = True
        scene.update(1.0 / S.FPS)
        self.assertNotEqual(scene.speed, 176.0)   # no lift without wind
        scene._glide = False
        scene.update(1.0)
        self.assertGreater(self.game.state.fuel, 0.0)   # feet rest you

    def test_sprite_shove(self):
        scene = self._enter()
        sp = scene.sprites[0]
        sp["x"], sp["y"] = scene.player.x + 5, scene.player.y
        sp["cool"] = 0.0
        before = scene.player.copy()
        scene.update(0.2)
        self.assertGreater(scene.player.distance_to(before), 1.0)
        self.assertGreater(sp["cool"], 0.0)

    def test_oroi_combo(self):
        game = self.game
        game.state.visited = ["prologue"]
        game.switch("overworld")
        scene = game.current
        scene._modal = None
        game.box.hide()
        game.state.quests["ko_tao"] = 3
        game.state.flags.append("code_tutorial")
        scene._open_tablet(ST.STOP_BY_ID["ko_tao"])
        scene._on_run("turtles = 0")       # a failed spell breaks the streak
        self.assertEqual(game.state.combo, 0)
        base = game.state.respect
        for _ in range(3):                 # three clean solves in a row
            scene._on_run("turtles = 4")
            from tests.helpers import finish_activity
            finish_activity(self.game)
            scene._modal = None
            game.box.hide()
        self.assertEqual(game.state.combo, 3)
        self.assertEqual(game.state.respect, base + 1)   # combo bonus
        self.assertTrue(game.state.stop_done("ko_tao"))
        scene = self._enter()
        # find a wide granite patch and walk across it (feet at x+4/x+12
        # peek a tile ahead, so the run must be several tiles wide)
        tm = scene.tm
        spot = None
        for r in range(tm.rows):
            run = 0
            for c in range(tm.cols + 1):
                if c < tm.cols and tm.grid[r][c] == "S":
                    run += 1
                else:
                    if run >= 6:
                        spot = ((c - run + 1) * 16 + 8, r * 16 + 8)
                        break
                    run = 0
            if spot:
                break
        self.assertIsNotNone(spot)
        scene.player = pygame.Vector2(*spot)
        scene.keys.add(pygame.K_RIGHT)
        for _ in range(60):
            scene.update(1.0 / S.FPS)
        scene.keys.discard(pygame.K_RIGHT)
        slow_dist = scene.player.x - spot[0]
        # same time on grass goes further (walk speed 74px/s, granite x0.55)
        self.assertLess(slow_dist, 62.0)
        self.assertGreater(slow_dist, 8.0)    # but you do keep moving

    # ------------------------------------------------------------------- life
    def test_day_and_night_cycle(self):
        scene = self._enter()
        self.game.state.play_t = 10.0
        self.assertEqual(scene._night(), 0.0)
        self.game.state.play_t = 200.0
        self.assertEqual(scene._night(), 1.0)
        before = self.game.state.play_t
        scene.update(1.0)
        self.assertGreater(self.game.state.play_t, before)

    def test_fishing_catch(self):
        game = self.game
        scene = self._enter()
        dock = scene.docks[0]
        c, r = dock["pos"]
        scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        scene.update(1.0 / S.FPS)
        self.assertIsNotNone(scene._dock)
        scene.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.key.key_code("f")))
        self.assertIsNotNone(scene.fish)      # line cast
        scene.fish["wait"] = 0.01
        scene.update(0.05)                     # ...nibble...NOW!
        self.assertGreater(scene.fish["bite"], 0.0)
        scene.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.key.key_code("f")))
        self.assertEqual(len(game.state.catches), 1)
        self.assertIsNone(scene.fish)

    def test_fishing_escapes_and_snaps(self):
        scene = self._enter()
        dock = scene.docks[0]
        c, r = dock["pos"]
        scene.player = pygame.Vector2(c * 16 + 8, r * 16 + 8)
        scene.update(1.0 / S.FPS)
        scene._cast_or_reel()
        scene.fish["wait"] = 0.01
        scene.update(0.05)
        scene.update(2.0)                      # too slow: it slipped away
        self.assertIsNone(scene.fish)
        self.assertEqual(len(self.game.state.catches), 0)
        scene._cast_or_reel()                  # cast again...
        scene.player = pygame.Vector2(8.0, 8.0)
        scene.update(1.0 / S.FPS)              # ...wander off: line snaps
        self.assertIsNone(scene.fish)

    def test_journal_menu_reads_pages(self):
        game = self.game
        game.state.complete_stop(ST.STOP_BY_ID["chumphon"])
        menu = game.journal
        menu.open()
        entries = menu._entries()
        self.assertTrue(any("Signal Hill" in head for head, _tail in entries))
        menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
        self.assertEqual(menu.tab, 1)          # cards tab
        menu.draw(game.canvas)

    # ------------------------------------------------------------------ mystery
    def _stand_at_tablet(self, stop_id):
        game = self.game
        game.state.visited = ["prologue"]
        game.switch("overworld")
        scene = game.current
        scene._modal = None
        game.box.hide()
        game.state.quests[stop_id] = 3    # meet + look + spark done
        game.state.act_seen = ST.STOP_BY_ID[stop_id]["act"]
        game.state.flags.append("code_tutorial")
        stop = ST.STOP_BY_ID[stop_id]
        scene.player = scene._tablet_px(stop).copy()
        scene.update(1.0 / S.FPS)
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertTrue(scene.panel.visible)
        return scene

    def test_forged_page_accuses_then_redeems(self):
        game = self.game
        scene = self._stand_at_tablet("phuket")
        self.assertIn("BEACON ORDERS", scene.panel.title)
        # the copy solves... and Noi smells fresh ink
        scene._on_run('if sails == "ships":\n    print("light")\nelse:\n    print("wait")')
        self.assertFalse(game.state.stop_done("phuket"))
        self.assertIn("phuket_accused", game.state.flags)
        # the tablet now holds Auntie Sim's true dictation
        scene._modal = None
        game.box.hide()
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertIn("TRUE ORDERS", scene.panel.title)
        scene._on_run('print("light")\nprint("hold")\nprint("stand")')
        from tests.helpers import finish_activity
        finish_activity(self.game)
        self.assertTrue(game.state.stop_done("phuket"))
        self.assertIn("phuket_truth", game.state.flags)
        self.assertIn("True Beacon Orders", game.state.cards)


if __name__ == "__main__":
    unittest.main()
