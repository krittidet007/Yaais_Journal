"""Scene 2 — The Village (Naming)."""

from .. import settings as S
from .. import views
from ..runner import run_code
from .base import DialogueScene


class NamingScene(DialogueScene):
    name = "village_naming"

    PREFILL = (
        "# a name to carry\n"
        'spirit_name = "Phi"'
    )

    def intro_lines(self):
        return [
            {"speaker": "CHILD", "accent": S.CHILD, "skin": "wood",
             "text": "Hey! Hey, are you okay? You look like you fell in the river. Did you fall in the river?"},
            {"speaker": "CHILD", "accent": S.CHILD, "skin": "wood",
             "text": "Grandma Ruen! Grandma Ruen, there's someone here, they fell in the river!"},
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "Fell in, did you. Well, you're breathing, that's the important part. Come on, up you get."},
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "Huh. Now that's not something I've seen in a while."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "(quiet, wary) she can see me?"},
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "Don't look so surprised, little flame. I'm old, not blind. Haven't seen a bound spirit since I was younger than this one \u2014 but I remember what it means."},
            {"speaker": "CHILD", "accent": S.CHILD, "skin": "wood",
             "text": "Wait, there's a ghost?? Where?? I can't see anything!"},
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "(to child) Go tell your mother we've got a guest."},
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "(to you) A spirit doesn't bind to just anyone. Means you can read what most people forgot how to read. That's rare, these days. Useful, too, given our problem."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "I don't \u2014 I don't know what I am, exactly. I know I should. There's a shape to the knowing, but it's empty. Like a jar with no water in it."},
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "Then let's start somewhere small. Spirits like this one need a name to hold onto. Without one, they drift \u2014 lose what little shape they've got left. You're bound to it now, so the naming's yours to do."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "...I'd like that. I think. I don't remember my old one. Give me something to be."},
        ]

    def success_lines(self):
        return [
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "There. Simple as that. Say it, little flame."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "@NAME@. That's \u2014 yes. That's mine now. Thank you."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "(to you, quieter, just you two) That's the first real thing I've had in longer than I know. I won't forget it. Or you, for giving it to me."},
        ]

    def panel_title(self):
        return "THE NAMING TABLET"

    def panel_prefill(self):
        return self.PREFILL

    def panel_status(self):
        return "A carved tablet on Grandma Ruen's lap. It waits for a name to write into spirit_name."

    def next_scene(self):
        return "overworld"

    def validate(self, code):
        result = run_code(code)
        if not result["ok"]:
            return False, "The tablet sputters.", self._error(result)
        value = result["env"].get("spirit_name")
        if not isinstance(value, str) or not value.strip():
            return False, "No name written.", (
                "The tablet hums, but nothing took hold. Write your name into spirit_name \u2014 "
                'for example: spirit_name = "Lin"')
        chosen = value.strip()
        self.game.state.spirit_name = chosen
        self.game.state.named = True
        return True, "The runes warm. A name settles into the gaps.", "The little flame grows bright."

    def _error(self, result):
        line = result["line"]
        if line > 0:
            return "The tablet sputters at rune %d \u2014 %s" % (line, result["message"])
        return "The tablet sputters \u2014 %s" % result["message"]

    def on_solved(self):
        self.game.state.give_item("spirit_charm")
        self.game.state.give_item("rune_tablet")

    def draw_backdrop(self, screen):
        cam = self.cam
        rx, ry = views.VILLAGE["npc_ruen"]
        cam.snap_to(rx, ry)
        ox, oy = cam.offset()
        views.draw_village(screen, self.t, cam=(ox, oy))
