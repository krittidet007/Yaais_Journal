"""Ten iconic things per province, and the SIGHTS journal tab."""

import unittest

import pygame

import main
from game import save
from game import story as ST


class TestIcons(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    @classmethod
    def tearDownClass(cls):
        cls.game.window = None
        save.clear()

    def setUp(self):
        self.game.state.reset()

    def test_fourteen_provinces_times_ten(self):
        provinces = [s["id"] for s in ST.STOPS if s["kind"] == "province"]
        self.assertEqual(len(provinces), 14)
        self.assertEqual(set(ST.ICONS), set(provinces))
        for pid, icons in ST.ICONS.items():
            with self.subTest(province=pid):
                self.assertEqual(len(icons), 10)
                for icon in icons:
                    self.assertTrue(isinstance(icon, str) and len(icon) > 12)

    def test_icons_unique_enough(self):
        seen = {}
        for pid, icons in ST.ICONS.items():
            for icon in icons:
                self.assertNotIn(icon, seen,
                                 "%r repeats in %s and %s" % (icon, pid, seen.get(icon)))
                seen[icon] = pid

    def test_sights_tab_lists_walked_provinces(self):
        game = self.game
        game.state.complete_stop(ST.STOP_BY_ID["krabi"])
        menu = game.journal
        menu.open()
        menu.tab = menu.TABS.index("SIGHTS")
        entries = menu._entries()
        self.assertEqual(len(entries), 10)
        self.assertTrue(all(head.startswith("Chapter 14") for head, _t in entries))
        menu.draw(game.canvas)

    def test_secrets_have_no_icons(self):
        for stop in ST.STOPS:
            if stop["kind"] == "secret":
                self.assertEqual(ST.icons_of(stop["id"]), [])


if __name__ == "__main__":
    unittest.main()
