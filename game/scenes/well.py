"""Scene 4 — The Well (conditionals)."""

from .. import settings as S
from .. import views
from ..runner import run_code
from ..views import draw_well_backdrop
from .base import DialogueScene


class WellScene(DialogueScene):
    name = "well"

    PREFILL = (
        "# bucket_lowered is True\n"
        "# when the bucket is down\n"
        '# end on "draw" if lowered,\n'
        '# "hold" if it is not\n'
        'print("draw")'
    )

    HINT = "A faint glow steadies: \"Finish on 'draw' when it is down, 'hold' when it is not.\""

    def __init__(self, game):
        super().__init__(game)
        self.attempts = 0
        self.water = 0.0
        self.solved = False

    def intro_lines(self):
        return [
            {"speaker": "NOK", "accent": S.NOK, "skin": "wood",
             "text": "Oh \u2014 hello. Sorry, don't mind me, just having a wonderful time with this well that only works when it feels like it."},
            {"speaker": "NOK", "accent": S.NOK, "skin": "wood",
             "text": "Some days you lower the bucket, it draws water fine. Other days \u2014 nothing. Rope just sits there like the well's decided it doesn't like me today."},
            {"speaker": "GRANDMA RUEN", "accent": S.RUEN, "skin": "wood",
             "text": "Nok's not exaggerating, for once. It's not random, though \u2014 the old ward that runs it just isn't listening right anymore. Everything's got rules underneath, even magic. This one's rules are just... broken."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "I can see the shape of it. It's meant to check something before it decides to draw \u2014 but the checking part isn't checking anymore. It's just... guessing."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "Look \u2014 see how it's supposed to work? If the bucket is lowered, draw water. If not, don't. Simple. But something in the if has come loose."},
        ]

    def success_lines(self):
        return [
            {"speaker": "NOK", "accent": S.NOK, "skin": "wood",
             "text": "(genuinely delighted) Oh, hey! Hey, look at that!"},
            {"speaker": "NOK", "accent": S.NOK, "skin": "wood",
             "text": "You know, I was fully prepared to just carry water from the river for the rest of my life. This is objectively better."},
            {"speaker": "SPIRIT", "accent": S.SPIRIT, "skin": "spirit",
             "text": "(quiet, to you) That felt different than the shrine. Like something actually understood something \u2014 not just repeated it back."},
        ]

    def panel_title(self):
        return "THE WELL'S WARD"

    def panel_prefill(self):
        return self.PREFILL

    def panel_status(self):
        return "Runes surface along the well's rim, waiting for the rule that decides: draw, or hold."

    def solve_pause(self):
        return 1.4

    def next_scene(self):
        return "epilogue"

    # --------------------------------------------------------------- validation
    def validate(self, code):
        down = run_code(code, {"bucket_lowered": True})
        up = run_code(code, {"bucket_lowered": False})
        self.attempts += 1

        if not down["ok"] or not up["ok"]:
            failed = down if not down["ok"] else up
            return False, "The ward sputters.", self._with_hint(self._error(failed))

        if self._last_line(down["output"]) != "draw":
            console = ("bucket lowered \u2192 output ends: %s\nbucket raised \u2192 output ends: %s"
                       % (self._last_line(down["output"]), self._last_line(up["output"])))
            return False, console, self._with_hint(
                "The ward waits with the bucket lowered \u2014 it never finishes against \"draw\".")

        if self._last_line(up["output"]) != "hold":
            console = "bucket raised \u2192 output ends: %s" % self._last_line(up["output"])
            return False, console, self._with_hint(
                "The ward gushes while the bucket is raised \u2014 it never finishes against \"hold\".")

        return True, "The well hums, low and even.", "Water draws smooth and clean."

    def _error(self, result):
        line = result["line"]
        if line > 0:
            return "The ward sputters at rune %d \u2014 %s" % (line, result["message"])
        return "The ward sputters \u2014 %s" % result["message"]

    def _with_hint(self, status):
        return status + ("\n\n" + self.HINT if self.attempts >= 1 else "")

    @staticmethod
    def _last_line(output):
        lines = output.strip().split("\n")
        return lines[-1] if lines and lines != [""] else ""

    def on_solved(self):
        self.solved = True
        self.game.state.well_done = True
        self.game.state.give_item("well_water")

    def on_update(self, dt):
        if self.solved and self.water < 0.92:
            self.water = min(0.92, self.water + dt * (0.92 / 1.8))

    def draw_backdrop(self, screen):
        cam = self.cam
        wx, wy = views.VILLAGE["well"]
        cam.snap_to(wx, wy)
        ox, oy = cam.offset()
        draw_well_backdrop(screen, self.t, cam=(ox, oy), water=self.water)
