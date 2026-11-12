"""Mouse helpers shared by scenes and menus.

Keyboard stays the primary input; the mouse is a convenience layer on
top of it. Every clickable thing follows one rule so it feels the
same everywhere:

* click a row, slot or option once to **select** it;
* click the already-selected one again (or press confirm) to **use** it;
* clicking anywhere with no rows on screen counts as **confirm**.
"""

import pygame


def clicked(ev):
    """True for a left-mouse click (the 'use it' button)."""
    return ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1


def cancelled(ev):
    """True for a right-mouse click (the 'back out' button)."""
    return ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3


def hit(rects, pos):
    """Index of the first rect containing ``pos``, or None."""
    for i, rect in enumerate(rects):
        if rect.collidepoint(pos):
            return i
    return None
