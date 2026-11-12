"""Every ``S.<NAME>`` the game uses must exist in game.settings.

The 'game just closes' class of bug has twice been a missing colour
constant (``AMBER``, then ``RED`` in the low-fuel HUD) — a plain
AttributeError in the draw loop. This test sweeps every module for
references like ``S.<CONSTANT>`` and fails on any name settings.py
doesn't define, so the whole family is caught before it ships.
"""

import os
import re
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import settings as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".venv", "__pycache__", ".git", "build", "dist", ".freebuff"}


class TestSettingsConstants(unittest.TestCase):
    def test_every_S_reference_is_defined(self):
        defined = set(re.findall(r"^([A-Z_][A-Z0-9_]*)\s*=", open(
            os.path.join(ROOT, "game", "settings.py")).read(), re.M))
        missing = {}
        for dirpath, dirnames, filenames in os.walk(ROOT):
            if any(part in SKIP_DIRS for part in dirpath.split(os.sep)):
                continue
            for name in filenames:
                if not name.endswith(".py"):
                    continue
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8") as fh:
                    for lineno, line in enumerate(fh, 1):
                        for m in re.finditer(r"\bS\.([A-Z_][A-Z0-9_]*)\b", line):
                            if m.group(1) not in defined:
                                missing.setdefault(m.group(1), []).append(
                                    "%s:%d" % (path, lineno))
        self.assertEqual(missing, {}, "game.settings is missing constants: %r"
                         % missing)

    def test_draw_runs_with_low_fuel(self):
        """The low-fuel HUD path that referenced the missing RED."""
        import pygame  # noqa: F401
        import main
        game = main.Game()
        game.state.reset()
        game.state.visited = ["prologue"]
        game.switch("overworld")
        scene = game.current
        scene._modal = None
        scene.game.state.fuel = 3.0            # under 25 -> warning colour
        scene.update(1.0 / 60.0)
        scene.draw(game.canvas)                # must not raise


if __name__ == "__main__":
    unittest.main()
