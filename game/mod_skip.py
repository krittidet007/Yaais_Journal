"""TEMPORARY dev mod: skip the story while testing.

 gated by the WICHA_MOD=1 environment variable, so normal players can
 never trigger it. Keys (handled in main.py):

   F6  finish the stop you are in (page, cards, word)
   F7  finish ALL 24 stops (journal full, finale ready)

There is no teleport key and none will be added: the game has no
teleporting, not even for testing. Walk, glide and sail everywhere.

TO REMOVE: delete this file, drop the ``mod_skip`` hook in main.py,
and delete tests/test_mod.py.
"""

import os

from . import story as ST


def enabled():
    return os.environ.get("WICHA_MOD") == "1"


def unlock_all(state):
    """Complete every stop: pages, cards, words, meters, naming."""
    if not state.named:
        state.spirit_name = state.spirit_name or "Phi"
        state.named = True
    if "prologue" not in state.visited:
        state.visited.append("prologue")
    for stop in ST.STOPS:
        state.complete_stop(stop)
        state.quests[stop["id"]] = 3
    state.bump_spice(5)
    state.bump_respect(5)
    state.noi_rank = len(state.found)
    return True


def finish_here(game):
    """Complete the stop under your feet, if any. No travel, ever."""
    scene = game.current
    if getattr(scene, "name", "") != "overworld":
        return False
    near = scene._near
    if near is None or near is ST.PROLOGUE:
        return False
    fresh, _gained = game.state.complete_stop(near)
    if fresh:
        game.state.bump_spice(1 if near["kind"] == "province" else 0)
    from . import audio
    audio.sfx("collect")
    return True
