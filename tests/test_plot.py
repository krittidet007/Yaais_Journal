"""The story has a spine: a thief of memory, a plot beat per province,
and a first-time-coder lesson before the first tablet."""

import unittest

import pygame

import main
from game import settings as S
from game import story as ST

CONFIRM = pygame.K_SPACE


def _tap(game):
    game.box.update(10.0)
    game.current.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))


class TestPlot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = main.Game()

    @classmethod
    def tearDownClass(cls):
        cls.game.window = None

    def setUp(self):
        self.game.state.reset()
        self.game.state.visited = ["prologue"]
        self.game.state.spirit_name = "Phi"
        self.game.state.named = True

    def _overworld(self):
        self.game.switch("overworld")
        scene = self.game.current
        scene._modal = None
        self.game.box.hide()
        return scene

    # ------------------------------------------------------------- the plot
    def test_there_is_a_villain_and_an_arc(self):
        # Lom taunts between acts, and speaks again at the end
        self.assertIn(2, ST.PLOT)
        self.assertIn(3, ST.PLOT)
        speakers = {line[0] for line in ST.PLOT[2] + ST.PLOT[3]}
        self.assertIn("LOM", speakers)

    def test_act_cutscene_fires_once(self):
        game = self.game
        for stop in ST.STOPS:
            if stop["act"] == 1:
                game.state.complete_stop(stop)
        scene = self._overworld()
        scene.update(1.0 / S.FPS)
        self.assertIsNotNone(scene._modal)
        self.assertIn("LOM", [ln[0] for ln in scene._modal["lines"]])
        scene._modal = None
        scene.update(1.0 / S.FPS)
        self.assertIsNone(scene._modal)          # never twice

    def test_every_stop_has_a_plot_beat(self):
        for stop in ST.STOPS:
            beats = ST.SCENES.get(stop["id"], {})
            for key in ("arrive", "mid", "spark"):
                self.assertIn(key, beats, "%s lacks %s" % (stop["id"], key))
                self.assertGreaterEqual(len(beats[key]), 2,
                                        "%s/%s is too thin" % (stop["id"], key))

    def test_sight_beat_chains_into_plot(self):
        game = self.game
        scene = self._overworld()
        stop = ST.STOP_BY_ID["ko_tao"]
        game.state.act_seen = stop["act"]
        game.state.quests["ko_tao"] = 1
        scene.player = scene._sight_px(stop).copy()
        scene.update(1.0 / S.FPS)
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        seen_plot = False
        for _ in range(30):
            if scene._modal is None:
                break
            if scene._modal.get("kind") == "plot":
                seen_plot = True
            _tap(game)
        self.assertTrue(seen_plot)
        self.assertEqual(game.state.quests.get("ko_tao"), 2)

    # ------------------------------------------------ learning to code
    def test_journal_has_a_story_tab(self):
        game = self.game
        game.state.visited = ["prologue", "chumphon", "ko_tao"]
        game.state.pages = ["chumphon"]
        menu = game.journal
        menu.open()
        menu.tab = menu.TABS.index("STORY")
        rows = menu._entries()
        heads = [a for a, _b in rows]
        self.assertTrue(any(h.startswith("Chapter") for h in heads))
        self.assertTrue(any("Lom" in h for h in heads))
        self.assertTrue(any(ST.STOP_BY_ID["chumphon"]["title"] in h for h in heads))

    def test_tutorial_opens_before_the_first_tablet(self):
        game = self.game
        scene = self._overworld()
        stop = ST.STOP_BY_ID["ko_tao"]
        game.state.act_seen = stop["act"]
        game.state.quests["ko_tao"] = 3
        scene.player = scene._tablet_px(stop).copy()
        scene.update(1.0 / S.FPS)
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=CONFIRM))
        self.assertFalse(scene.panel.visible)     # the lesson comes first
        self.assertIsNotNone(scene._modal)
        for _ in range(2 * len(ST.CODE_TUTORIAL) + 8):
            if scene.panel.visible:
                break
            _tap(game)
        self.assertIn("code_tutorial", game.state.flags)
        self.assertTrue(scene.panel.visible)      # then the tablet itself

    def test_primer_teaches_the_basics(self):
        text = "\n".join(ST.PY_PRIMER)
        for token in ("print", "=", "if", "for", "while"):
            self.assertIn(token, text)

    def test_help_overlay_toggles(self):
        game = self.game
        panel = game.make_panel(lambda code: None)
        panel.open("TEST", "", "do a thing", teach="print the word")
        self.assertEqual(panel.teach, "print the word")
        panel.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1))
        self.assertTrue(panel.help)
        panel.draw(game.canvas)                   # overlay draws cleanly
        panel.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1))
        self.assertFalse(panel.help)


if __name__ == "__main__":
    unittest.main()
