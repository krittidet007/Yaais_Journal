"""Scene 1 — Washed Up."""

from .. import settings as S
from ..views import draw_washup
from .base import DialogueScene


class WashupScene(DialogueScene):
    name = "washup"

    def intro_lines(self):
        return [
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "...warm. you're... warm. why can I feel that."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "who \u2014 no. wait. wait, I know this. I should know this."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "you're not \u2014 you're not one of mine. but you're here. and I'm \u2014"},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "I don't remember how long I've been alone."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "...sorry. that was \u2014 I don't usually say things like that out loud. I don't think I've said anything out loud in a long time."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "there. people. go \u2014 go there. I'll follow. I don't have much choice, honestly, you're the only warm thing I've felt in longer than I can count."},
        ]

    def has_panel(self):
        return False

    def next_scene(self):
        return "village_naming"

    def draw_backdrop(self, screen):
        draw_washup(screen, self.t)
