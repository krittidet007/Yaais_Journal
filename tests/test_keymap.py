"""Key bindings resolve to real keys and report presses."""

import unittest

import pygame

from game import keymap
from game import options as O


class TestKeymap(unittest.TestCase):

    def test_every_action_has_a_code(self):
        for action, _label in O.KEY_ACTIONS:
            code = keymap.code(action)
            self.assertIsInstance(code, int, "%s has no keycode" % action)
            self.assertGreaterEqual(code, 0)

    def test_labels_are_uppercase(self):
        for action, _label in O.KEY_ACTIONS:
            name = keymap.label(action)
            self.assertTrue(name)
            self.assertEqual(name, name.upper())

    def test_pressed_and_released(self):
        confirm = keymap.code("confirm")
        down = pygame.event.Event(pygame.KEYDOWN, key=confirm)
        up = pygame.event.Event(pygame.KEYUP, key=confirm)
        other = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)
        self.assertTrue(keymap.pressed("confirm", down))
        self.assertFalse(keymap.pressed("confirm", other))
        self.assertTrue(keymap.released("confirm", up))
        self.assertFalse(keymap.released("confirm", down))

    def test_held_reflects_keyboard(self):
        # with no keys physically down, every action reads as not-held
        for action, _label in O.KEY_ACTIONS:
            self.assertFalse(keymap.held(action))

    def test_defaults(self):
        self.assertEqual(O.options.key_name("confirm"), "e")
        self.assertEqual(O.options.key_name("glide"), "x")
        self.assertEqual(O.options.key_name("run"), "left shift")


if __name__ == "__main__":
    unittest.main()
