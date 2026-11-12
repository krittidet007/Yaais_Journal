"""Shared helpers for the tests."""

import pygame

CONFIRM = pygame.K_e


def finish_activity(game):
    """Play a town's local activity to the end.

    Since the flow is code -> activity -> page, a test that solves the
    tablet still has to finish the activity before the page is theirs.
    """
    scene = game.current
    if hasattr(scene, "_finish_activity"):
        scene._finish_activity()
        game.switch("overworld")
        return game.current
    return scene


def play_activity(game, answer=True):
    """Actually play the activity, the way a player would.

    Each activity type has its own little skill; this plays them all
    properly so the tests exercise the real thing rather than skipping
    it. Returns the scene when the activity is finished.
    """
    scene = game.current
    kind = scene.act["type"]
    for _ in range(24):
        if scene.phase != "activity":
            break
        if kind == "choice":
            scene._cursor = 0
            scene._pick_choice()
        elif kind == "match":
            cand = scene._candidates()
            want = scene.act["options"][len(scene._picks)]
            if want in cand:
                scene._cursor = cand.index(want)
            scene._attempt_match()
        elif kind == "timing":
            zone = scene.act.get("zone", 0.5)
            scene._marker = 0.5
            scene._event_timing(pygame.event.Event(pygame.KEYDOWN,
                                                   key=CONFIRM))
        elif kind == "rhythm":
            seq = scene.act["sequence"]
            if scene._seq_i < len(seq):
                scene._press_rhythm(seq[scene._seq_i])
        elif kind == "calm":
            scene._event_calm(pygame.event.Event(pygame.KEYDOWN,
                                                 key=CONFIRM))
    return scene
