"""Regions, the light pass, dithered terrain and the lore documents."""

import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from game import artgen as A  # noqa: E402
from game import lighting  # noqa: E402
from game import regions as RG  # noqa: E402
from game import settings as S  # noqa: E402
from game import story as ST  # noqa: E402
from game import tiles as T  # noqa: E402


class TestRegions(unittest.TestCase):
    def test_every_stop_belongs_to_a_region(self):
        for stop in ST.STOPS:
            rid = RG.region_of_stop(stop["id"])
            self.assertIn(rid, RG.REGIONS, stop["id"])
            self.assertIn(stop["id"], RG.REGIONS[rid]["stops"])

    def test_the_prologue_is_in_the_gulf_shore(self):
        self.assertEqual(RG.region_of_stop("prologue"), "gulf_shore")

    def test_region_for_position_finds_the_nearest_stop(self):
        for stop in ST.STOPS:
            x, y = stop["pos"][0] * 16, stop["pos"][1] * 16
            self.assertEqual(RG.region_for_position(x, y, ST.STOPS),
                             RG.region_of_stop(stop["id"]), stop["id"])

    def test_every_region_has_a_full_palette(self):
        for rid, reg in RG.REGIONS.items():
            for key in ("name", "biome", "stops", "ambient", "light", "fog",
                        "grade", "weather"):
                self.assertIn(key, reg, rid)
            self.assertEqual(len(reg["ambient"]), 3)
            self.assertEqual(len(reg["light"]), 3)
            self.assertEqual(len(reg["fog"]), 2)


class TestLighting(unittest.TestCase):
    def _surface(self):
        surf = pygame.Surface((S.INTERNAL_W, S.INTERNAL_H))
        surf.fill((120, 130, 90))
        return surf

    def test_ambient_tint_changes_the_frame(self):
        surf = self._surface()
        before = surf.get_at((320, 160))[:3]
        lighting.apply(surf, "gulf_shore", [], 0.0)
        after = surf.get_at((320, 160))[:3]
        self.assertNotEqual(before, after)

    def test_lights_add_light(self):
        surf = self._surface()
        lighting.apply(surf, "karst", [], 0.0)
        dark = surf.get_at((320, 160))[:3]
        surf2 = self._surface()
        lighting.apply(surf2, "karst", [(320, 160, 40, 1.0)], 0.0)
        lit = surf2.get_at((320, 160))[:3]
        self.assertGreater(sum(lit), sum(dark))

    def test_night_darkens(self):
        surf = self._surface()
        lighting.apply(surf, "gulf_shore", [], 0.0)
        day = sum(surf.get_at((320, 160))[:3])
        surf2 = self._surface()
        lighting.apply(surf2, "gulf_shore", [], 1.0)
        night = sum(surf2.get_at((320, 160))[:3])
        self.assertLess(night, day)

    def test_unknown_region_is_safe(self):
        surf = self._surface()
        lighting.apply(surf, "nowhere", [], 0.0)      # must not raise


class TestTerrainDither(unittest.TestCase):
    def test_edges_are_dithered_not_hard(self):
        """A grass tile next to sand blends instead of snapping."""
        tm = T.TileMap(4, 4, fill="G")
        tm.grid[1][1] = "A"
        surf = pygame.Surface((64, 64))
        T.draw_view(surf, tm, (0, 0))
        edge = surf.get_at((16, 8))[:3]        # inside the sand tile, top row
        sand = S.__dict__.get("SAND", None)
        from game.tiles import SAND, GRASS
        blended = any(
            edge[i] not in (SAND[1][i], GRASS[1][i]) for i in range(3))
        self.assertTrue(blended, "edge pixel %r is not a blend" % (edge,))


class TestRimLight(unittest.TestCase):
    def test_rim_adds_a_highlight_edge(self):
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        surf.fill((80, 80, 80), pygame.Rect(3, 3, 6, 6))
        rimmed = A.rimmed(surf)
        # the top-left edge pixel of the block should be lighter now
        self.assertGreater(sum(rimmed.get_at((3, 3))[:3]),
                           sum(surf.get_at((3, 3))[:3]))

    def test_rim_is_cached_and_stable(self):
        surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        surf.fill((60, 60, 60), pygame.Rect(2, 2, 5, 5))
        self.assertIs(A.rimmed(surf), A.rimmed(surf))


class TestLore(unittest.TestCase):
    def test_lore_documents_are_unlocked_as_cards(self):
        cards = set()
        for stop in ST.STOPS:
            cards.update(stop.get("cards", []))
        for name in ST.LORE:
            self.assertIn(name, cards, name)

    def test_lore_text_is_readable(self):
        for name, text in ST.LORE.items():
            self.assertGreater(len(text), 80, name)

    def test_host_rumours_are_hidden_until_the_page_is_ours(self):
        extra = ST.extra_of("chumphon")
        self.assertIn("later", extra)
        self.assertTrue(extra["later"])


if __name__ == "__main__":
    unittest.main()
