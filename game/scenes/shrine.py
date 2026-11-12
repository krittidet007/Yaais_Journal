"""Scene 3 — First Shrine (output with print)."""

from .. import settings as S
from .. import views
from ..runner import run_code
from ..views import draw_shrine_backdrop
from .base import DialogueScene


class ShrineScene(DialogueScene):
    name = "shrine"

    PREFILL = (
        "# the shrine needs a voice\n"
        'print("the shrine is warm")'
    )

    def __init__(self, game):
        super().__init__(game)
        self.lit = 0.0
        self.solved = False

    def intro_lines(self):
        return [
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "Now \u2014 since you're clearly no ordinary traveler, might as well be useful. That shrine's gone quiet. Started maybe a season back. Nothing serious, we told ourselves. Just... wrong."},
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "Try it. See if you remember more than you think you do."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "I can feel it. It's not broken, exactly. It's just \u2014 quiet. Like it forgot how to speak."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "Try telling it something. An offering, a greeting \u2014 anything. It needs to hear a voice again before it remembers how to answer."},
        ]

    def success_lines(self):
        return [
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "Oh \u2014 oh, that's \u2014 yes! That's exactly right. I don't know how I know that was right, but I know it was."},
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "There it is. Good. That's one."},
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "Wish that was the worst of it. Come on \u2014 there's a bigger problem down by the well."},
        ]

    def panel_title(self):
        return "FLAME OF THE SHRINE"

    def panel_prefill(self):
        return self.PREFILL

    def panel_status(self):
        return "A rune panel spreads open across the shrine's dark front. It needs to speak itself warm again."

    def next_scene(self):
        return "hub"

    def validate(self, code):
        result = run_code(code)
        if not result["ok"]:
            return False, "The shrine flinches.", self._error(result)
        spoken = result["output"].strip()
        if not spoken:
            return False, "Silence.", "The shrine stays quiet. Whatever you wrote, it had nothing to say back \u2014 try a print() with words in it."
        self.game.state.offering = spoken
        self._spoken = spoken
        return True, "The shrine answers: %s" % spoken, "Warmth returns to the little shrine."

    def _spoken_text(self):
        return getattr(self, "_spoken", "")

    def _error(self, result):
        line = result["line"]
        if line > 0:
            return "The shrine flinches at rune %d \u2014 %s" % (line, result["message"])
        return "The shrine flinches \u2014 %s" % result["message"]

    def on_solved(self):
        self.solved = True
        self.game.state.shrine_done = True
        self.game.state.give_item("shrine_ember")

    def on_update(self, dt):
        if self.solved and self.lit < 1.0:
            self.lit = min(1.0, self.lit + dt / 1.0)

    def draw_backdrop(self, screen):
        cam = self.cam
        sx, sy = views.VILLAGE["shrine"]
        cam.snap_to(sx, sy - 16)
        ox, oy = cam.offset()
        draw_shrine_backdrop(screen, self.t, cam=(ox, oy), lit=self.lit)
