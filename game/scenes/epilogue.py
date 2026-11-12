"""Scene 7 (slice ending) — the spirit remembers a temple."""

from .. import settings as S
from .. import views
from ..views import draw_epilogue
from .base import DialogueScene


class EpilogueScene(DialogueScene):
    name = "epilogue"

    def __init__(self, game):
        super().__init__(game)
        self.warm = 0.0

    def intro_lines(self):
        return [
            {"speaker": "YAAI", "accent": S.RUEN, "skin": "wood",
             "text": "Rong Khru is where a dancer honours her teachers and her ancestors. We do it with you."},
            {"speaker": "NOI", "accent": S.SPIRIT, "skin": "spirit",
             "text": "All twenty-four pages found. The South remembers."},
            {"speaker": "YAAI", "accent": S.RUEN, "skin": "wood",
             "text": "You wrote page twenty-five with your heart. Keep writing the stories of this land."},
            {"speaker": "NOI", "accent": S.SPIRIT, "skin": "spirit",
             "text": "มา! Come back anytime. Yaai's door is always open."},
        ]

    def has_panel(self):
        return False

    def on_update(self, dt):
        self.warm = min(1.0, self.warm + dt / 1.5)

    def draw_backdrop(self, screen):
        cam = self.cam
        cx, cy = views.VILLAGE["npc_child"]
        cam.snap_to(cx, cy)
        ox, oy = cam.offset()
        draw_epilogue(screen, self.t, cam=(ox, oy), warm=self.warm)

    def next_scene(self):
        return None
