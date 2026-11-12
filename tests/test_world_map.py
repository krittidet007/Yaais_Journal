"""The open world: a peninsula-shaped map that is walkable,
glide-able, and has every stop pinned on reachable land."""

import unittest

import pygame
from collections import deque

from game import story as ST
from game import tiles as T
from game import world_map as WM

ISLANDS = ("ko_tao", "ko_pha_ngan", "ko_samui", "surin_islands",
           "similan", "ko_phi_phi", "ko_kradan", "ko_lipe")


def _map():
    """Build the world once and share it across the tests."""
    if not hasattr(_map, "tm"):
        _map.tm = WM.south_map()
    return _map.tm


def _reachable(tm, start, glide=False):
    """Tiles reachable from ``start`` on foot (or gliding)."""
    def walk(c, r):
        if not (0 <= r < tm.rows and 0 <= c < tm.cols):
            return False
        k = tm.grid[r][c]
        return (k != "H") if glide else (k not in ("W", "H"))
    seen = {start}
    q = deque([start])
    while q:
        c, r = q.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (c + dc, r + dr)
            if nxt not in seen and walk(*nxt):
                seen.add(nxt)
                q.append(nxt)
    return seen


class TestWorldMap(unittest.TestCase):

    def test_dimensions(self):
        tm = _map()
        self.assertEqual((tm.cols, tm.rows), (WM.WORLD_COLS, WM.WORLD_ROWS))
        # the playable South is finer than the GADM mask, so the whole
        # peninsula reads as a country you cross on foot, not a speck
        self.assertEqual((WM.WORLD_COLS, WM.WORLD_ROWS),
                         (WM.BASE_COLS * WM.MAP_SCALE, WM.BASE_ROWS * WM.MAP_SCALE))
        self.assertGreaterEqual(WM.MAP_SCALE, 2)

    def test_land_ratio(self):
        tm = _map()
        land = sum(1 for row in tm.grid for k in row if k != "W")
        ratio = land / (tm.rows * tm.cols)
        # real southern-Thailand provinces inside a sea-framed box
        self.assertTrue(0.15 <= ratio <= 0.35, "land ratio %.2f" % ratio)

    def test_every_stop_on_walkable_land(self):
        tm = _map()
        for stop in ST.STOPS + [ST.PROLOGUE]:
            c, r = stop["pos"]
            cell = tm.cell(r, c)
            self.assertIsNotNone(cell, "%s is off the map" % stop["id"])
            self.assertNotIn(cell, ("W", "H"),
                             "%s sits on %s" % (stop["id"], cell))

    def test_islands_are_offshore(self):
        """An island has open water on at least two sides."""
        tm = _map()
        probe = 6 * WM.MAP_SCALE
        for stop in ST.STOPS:
            if stop["id"] not in ISLANDS:
                continue
            c, r = stop["pos"]
            card = [tm.cell(r + dr, c + dc)
                    for dc, dr in ((probe, 0), (-probe, 0), (0, probe), (0, -probe))]
            water = sum(1 for k in card if k == "W")
            self.assertGreaterEqual(water, 2,
                                    "%s is not offshore (%s)" % (stop["id"], card))

    def test_mainland_stops_are_not_islands(self):
        tm = _map()
        for stop in ST.STOPS:
            if stop["id"] in ISLANDS:
                continue
            c, r = stop["pos"]
            card = [tm.cell(r + dr, c + dc)
                    for dc, dr in ((6, 0), (-6, 0), (0, 6), (0, -6))]
            water = sum(1 for k in card if k == "W")
            # a mainland stop is on the mass, not ringed by sea
            self.assertLess(water, 4,
                            "%s looks like an island (%s)" % (stop["id"], card))

    def test_journey_is_connected(self):
        """Every mainland stop is reachable on foot; every island
        is reachable only by gliding over the water."""
        tm = _map()
        pc, pr = ST.PROLOGUE["pos"]
        on_foot = _reachable(tm, (pc, pr), glide=False)
        by_glide = _reachable(tm, (pc, pr), glide=True)
        for stop in ST.STOPS:
            c, r = stop["pos"]
            if stop["id"] in ISLANDS:
                self.assertNotIn((c, r), on_foot,
                                 "%s is reachable on foot — not an island" % stop["id"])
                self.assertIn((c, r), by_glide,
                              "%s is unreachable even by glide" % stop["id"])
            else:
                self.assertIn((c, r), on_foot,
                              "%s is unreachable on foot" % stop["id"])

    def test_roads_use_dirt(self):
        """The route between stops is marked with dirt (D)."""
        tm = _map()
        dirt = sum(1 for row in tm.grid for k in row if k == "D")
        self.assertGreater(dirt, 200, "the road network is too thin")

    def test_grid_ascii_shape(self):
        tm = _map()
        art = WM.grid_ascii(tm, step=8)
        lines = art.split("\n")
        self.assertEqual(len(lines), WM.WORLD_ROWS // 8)
        self.assertEqual(len(lines[0]), WM.WORLD_COLS // 8)

    def test_stop_pos_lookup(self):
        for stop in ST.STOPS:
            self.assertEqual(WM.stop_pos(stop["id"]), stop["pos"])
        self.assertEqual(WM.stop_pos("prologue"), ST.PROLOGUE["pos"])
        self.assertIsNone(WM.stop_pos("nope"))

    def test_default_fill_is_water(self):
        """A fresh map is all sea until land is stamped in."""
        tm = T.TileMap(4, 4, fill="W")
        self.assertEqual({tm.cell(r, c) for r in range(4) for c in range(4)}, {"W"})

    def test_hidden_sparks_are_foot_walkable(self):
        tm = _map()
        for stop in ST.STOPS:
            c, r = WM.hidden_spot(tm, stop)
            cell = tm.cell(r, c)
            self.assertNotIn(cell, ("W", "H", None),
                             "%s spark sits on %s" % (stop["id"], cell))

    def test_hidden_sparks_not_on_the_pin(self):
        """A spark must never auto-trigger the moment you arrive."""
        tm = _map()
        for stop in ST.STOPS:
            c, r = WM.hidden_spot(tm, stop)
            c0, r0 = stop["pos"]
            dist_px = ((c - c0) ** 2 + (r - r0) ** 2) ** 0.5 * 16
            self.assertGreaterEqual(
                dist_px, 12.0, "%s spark trips on arrival" % stop["id"])

    def test_docks_are_water_with_shore(self):
        tm = _map()
        docks = WM.dock_spots(tm)
        self.assertGreaterEqual(len(docks), 8)   # every island + the coast
        seen = set()
        for dock in docks:
            c, r = dock["pos"]
            self.assertEqual(tm.cell(r, c), "W", dock)
            shore = any(tm.cell(r + dr, c + dc) not in ("W", "H", None)
                        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            self.assertTrue(shore, dock)
            self.assertNotIn(dock["stop"], seen)  # one dock per stop
            seen.add(dock["stop"])

    def test_mountains_are_ranges_not_a_smear(self):
        """Granite forms narrow ridges (with passes) — never a grey
        blanket over the interior, which made the South read as rock."""
        tm = _map()
        land = sum(1 for row in tm.grid for k in row if k != "W")
        stone = sum(1 for row in tm.grid for k in row if k == "S")
        self.assertGreater(stone, 200, "no mountains at all")
        self.assertLess(stone / land, 0.08,
                        "the mountains smother the map again (%.1f%%)"
                        % (100 * stone / land))
        # and the ranges never seal a row: every sampled row of the
        # spine still has ground you can walk, so you can always cross
        for r in range(120, 900, 8):
            span = WM._row_span(r)
            if span is None:
                continue
            lo, hi = span
            row = tm.grid[r]
            self.assertTrue(
                any(row[c] not in ("S", "H") for c in range(lo, hi + 1)),
                "row %d is walled off by rock and forest" % r)

    def test_scenery_is_deterministic(self):
        from game import world_map as WM2
        tm = _map()
        again, _ = WM2.scenery(tm)
        props, _ = WM.scenery(tm)
        self.assertEqual(props, again)
        self.assertGreater(len(props), 400, "the map feels empty")

    def test_scenery_suits_its_terrain(self):
        tm = _map()
        props, blocked = WM.scenery(tm)
        home = {stop["pos"] for stop in ST.STOPS + [ST.PROLOGUE]}
        for x, y, kind, _variant in props:
            c, r = int(x) // 16, int(y) // 16
            cell = tm.cell(r, c)
            # nothing floats in the sea but a boat
            if cell == "W":
                self.assertEqual(kind, "boat", (kind, c, r))
                continue
            if kind == "palm":
                self.assertIn(cell, ("A", "G", "H", "T", "U", "R"), (kind, c, r))
            elif kind in ("hut", "lamp", "flags", "well", "shrine",
                          "dryingrack", "fence", "flowers", "banana",
                          "stump", "fishtrap"):
                self.assertNotEqual(cell, "W", (kind, c, r))
        # pins and host tiles are never walled off
        for c0, r0 in home:
            for dc in range(-2, 3):
                for dr in range(-2, 3):
                    self.assertNotIn((c0 + dc, r0 + dr), blocked)
        for stop in ST.STOPS:
            c, r = stop["pos"]
            self.assertNotIn((c + 1, r), blocked)
            self.assertNotIn((c + 2, r), blocked)

    def test_towns_stand_on_raised_ground_with_steps(self):
        """Temples and stupas do not stand on flat grass."""
        tm = _map()
        for stop in ST.STOPS:
            c, r = stop["pos"]
            around = [tm.cell(r + dr, c + dc)
                      for dr in range(-10, 11) for dc in range(-10, 11)
                      if (dr or dc) and abs(dr) + abs(dc) <= 10]
            self.assertTrue(any(cell in ("T", "U", "R") for cell in around),
                            "no terrace at %s" % stop["id"])

    def test_every_stop_has_dressing(self):
        from game import artgen as A
        fns = {"hut": A.hut, "palm": A.palm, "banana": A.banana,
               "well": A.well, "shrine": A.shrine, "boat": A.boat,
               "lamp": A.lamp, "fence": A.fence, "fishtrap": A.fishtrap,
               "dryingrack": A.dryingrack, "flags": A.flags,
               "rock": A.rock, "bush": A.bush, "stump": A.stump,
               "tree": A.tree, "bigrock": A.bigrock, "flowers": A.flowers,
               "stupa": A.stupa, "karst": A.karst, "mosque": A.mosque,
               "lighthouse": A.lighthouse, "wat": A.wat,
               "shophouse": A.shophouse, "puppet_stage": A.puppet_stage,
               "market_stall": A.market_stall, "windmill": A.windmill,
               "spirit_house": A.spirit_house, "stilt": A.stilt,
               "mangrove": A.mangrove, "rubber": A.rubber,
               "fern": A.fern, "ruin": A.ruin, "carving": A.carving,
               "kiln": A.kiln, "buddha": A.buddha}
        for stop in ST.STOPS:
            self.assertIn(stop["id"], WM.DRESSING, stop["id"])
            self.assertGreaterEqual(len(WM.DRESSING[stop["id"]]), 2)
            for kind, _variant, _dx, _dy in WM.DRESSING[stop["id"]]:
                self.assertIn(kind, fns, (stop["id"], kind))
                try:
                    fns[kind](0)
                except TypeError:
                    fns[kind]()

    def test_landmarks_stand_where_they_should(self):
        kinds = {stop["id"]: [k for k, _v, _x, _y in WM.DRESSING[stop["id"]]]
                 for stop in ST.STOPS}
        self.assertIn("stupa", kinds["surat_thani"])    # Chaiya chedi
        self.assertIn("stupa", kinds["nakhon"])         # Phra Mahathat
        self.assertIn("karst", kinds["phang_nga"])      # the bay
        self.assertIn("karst", kinds["krabi"])           # Tiger Cave cliffs
        self.assertIn("mosque", kinds["pattani"])       # Krue Se
        self.assertIn("well", kinds["ranong"])          # hot springs


if __name__ == "__main__":
    unittest.main()


class TestVariety(unittest.TestCase):
    """Nothing may look the same twice in a row: every prop has a family
    of shapes, and the scatter spreads them out."""

    def test_every_common_prop_has_several_shapes(self):
        from game import artgen as A
        for name in ("palm", "tree", "bush", "flowers", "rock", "bigrock",
                     "banana", "mangrove", "rubber", "shophouse",
                     "spirit_house", "fern"):
            fn = getattr(A, name)
            shapes = set()
            for v in range(6):
                surf = fn(v)
                # compare the actual pixels: that is what the eye sees
                shapes.add(pygame.image.tostring(surf, "RGBA"))
            self.assertGreaterEqual(len(shapes), 3,
                                    "%s has only %d shapes" % (name, len(shapes)))
            self.assertEqual(len(shapes), 6,
                             "%s: %d distinct shapes out of 6 variants"
                             % (name, len(shapes)))
            del shapes

    def test_the_scatter_spreads_the_variants(self):
        tm = _map()
        props, _blocked = WM.scenery(tm)
        for kind in ("palm", "tree", "bush", "rock"):
            variants = set(v for _x, _y, k, v in props if k == kind)
            self.assertGreaterEqual(len(variants), 4,
                                    "%s only uses %d variants" % (kind, len(variants)))

    def test_neighbours_are_not_all_the_same(self):
        tm = _map()
        props, _blocked = WM.scenery(tm)
        at = {}
        for x, y, kind, _v in props:
            at[(x // 16, y // 16)] = kind
        same = 0
        checked = 0
        for (c, r), kind in at.items():
            for dc, dr in ((1, 0), (0, 1)):
                other = at.get((c + dc, r + dr))
                if other is None:
                    continue
                checked += 1
                if other == kind:
                    same += 1
        # some neighbours will match, but not most of them
        self.assertGreater(checked, 100)
        self.assertLess(same / float(checked), 0.25,
                         "%.0f%% of neighbours are the same prop"
                         % (100.0 * same / checked))
