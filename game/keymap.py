"""Turn the string key names stored in options into pygame key codes."""

import pygame

from . import options as O


def code(action):
    name = O.options.key_name(action)
    try:
        return pygame.key.key_code(name)
    except (ValueError, pygame.error):
        return None


def pressed(action, ev):
    return ev.type == pygame.KEYDOWN and ev.key == code(action)


def released(action, ev):
    return ev.type == pygame.KEYUP and ev.key == code(action)


def held(action):
    """True while the action's key is physically held down."""
    k = code(action)
    if k is None:
        return False
    try:
        return bool(pygame.key.get_pressed()[k])
    except (pygame.error, IndexError, TypeError):
        return False


def label(action):
    try:
        return pygame.key.name(code(action)).upper()
    except (ValueError, TypeError, pygame.error):
        return "?"
