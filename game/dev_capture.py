"""Development helper: open a stop's rune tablet by itself, for capture.

Enabled only with the ``WICHA_CAPTURE`` environment variable, e.g.

    WICHA_CAPTURE=nakhon python main.py

The game then continues the autosave instead of showing the cover, stands the
player at that stop and opens its rune tablet with the real game code, then
stays there so the tablet can be photographed from the screen.  With the
variable unset nothing happens: ordinary players never meet this.
"""

import os

from . import save as SAVE

_STARTED = False
_OPENED = False


def enabled():
    return bool(os.environ.get("WICHA_CAPTURE"))


def target():
    return os.environ.get("WICHA_CAPTURE", "").strip()


def start(game):
    """Skip the cover and continue the saved game, so we land in the world."""
    global _STARTED
    if _STARTED:
        return
    _STARTED = True
    data = SAVE.read()
    if not data:
        return
    game.state.from_dict(data["state"])
    game.switch(data["scene"])


def tick(game):
    """Open the wanted stop's tablet once the world is running."""
    global _OPENED
    if _OPENED or not enabled():
        return
    scene = game.current
    if getattr(scene, "name", "") != "overworld":
        return
    from . import story as ST
    stop = next((s for s in ST.STOPS if s["id"] == target()), None)
    _OPENED = True
    if stop is None:
        return
    state = game.state
    if "code_tutorial" not in state.flags:
        state.flags.append("code_tutorial")
    state.quests[stop["id"]] = 3
    scene._open_tablet(stop)


def keep(game):
    """While capturing, keep the tablet open and the story box out of the way."""
    if not enabled():
        return
    scene = game.current
    if getattr(scene, "name", "") != "overworld":
        return
    from . import story as ST
    stop = next((s for s in ST.STOPS if s["id"] == target()), None)
    if stop is None:
        return
    game.box.hide()
    if not getattr(scene.panel, "visible", False):
        scene._open_tablet(stop)
