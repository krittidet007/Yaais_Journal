"""Headless bootstrap for the test suite.

Importing this package, before any test module imports
``game``, does three things:

  * points ``XDG_CONFIG_HOME`` at a fresh temp dir so the
    suite never reads or overwrites the player's real
    options and saves;
  * sets the SDL dummy drivers so pygame needs no display
    or audio device;
  * opens a 1x1 window, which ``convert_alpha`` and friends
    require.

Run the suite from the project root:

    .venv/bin/python -m unittest discover -s tests -t .
"""

import atexit
import os
import shutil
import tempfile

# Isolate the game's config/save dir from the player's real one.
_CONFIG_HOME = tempfile.mkdtemp(prefix="wicha-test-")
os.environ["XDG_CONFIG_HOME"] = _CONFIG_HOME

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402


def _cleanup():
    shutil.rmtree(_CONFIG_HOME, ignore_errors=True)


atexit.register(_cleanup)

pygame.init()
if pygame.display.get_init() and not pygame.display.get_surface():
    pygame.display.set_mode((1, 1))
