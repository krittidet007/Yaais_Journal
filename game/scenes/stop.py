"""A stop on the journey: dialogue -> local activity -> reward.

Every stop plays the same three beats, because that is the design in
the journal: you hear a story, you do something local, and you win
back a page plus a Culture Card and a Pak Tai word. The activity
comes in five flavours, drawn from the PDF:

  choice   a respectful decision (raises/lowers the Respect Meter)
  match    pick the right things from a list (markets, kings, fossils)
  timing   press confirm inside the moving zone (sunrise, hot springs)
  rhythm   copy a sequence of steps (Nora hands, the Chak Phra rope)
  calm     no game at all — walk, light a lantern, hold still

Failing only costs a try; the stop always ends in a page, so the
journey can never soft-lock.
"""

import pygame

from .. import keymap
from .. import mouse
from .. import options as O
from .. import pixel
from .. import settings as S
from .. import story as ST
from .. import views

W, H = S.INTERNAL_W, S.INTERNAL_H
ARROWS = {"left": "<", "right": ">", "up": "^", "down": "v"}


def _confirm_key(ev):
    return ev.type == pygame.KEYDOWN and (
        ev.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER)
        or keymap.pressed("confirm", ev))


class StopScene:
    name = "stop"

    def __init__(self, game):
        self.game = game
        self.t = 0.0
        self.stop = None
        self.box = game.box
        # dialogue
        self._lines = []
        self._index = -1
        # activity
        self.phase = "dialogue"        # dialogue | activity | reward | done
        self.act = None
        self._tries = 3
        self._cursor = 0
        self._picks = []
        self._marker = 0.0
        self._marker_dir = 1
        self._seq_i = 0
        self._msg = ""
        self._msg_t = 0.0
        # clickable rects, rebuilt every draw; events use last frame's
        self._opt_rects = []
        self._match_rects = []
        self._rhythm_rects = []

    # -------------------------------------------------------------- life cycle
    def on_enter(self):
        self.t = 0.0
        self.stop = ST.STOP_BY_ID.get(self.game.next_stop) or ST.STOPS[0]
        self._lines = list(self.stop["lines"])
        if self.stop.get("call"):
            self._lines.append(("YAAI", "YAAI", self.stop["call"]))
        self._index = -1
        self.phase = "dialogue"
        self._picks = []
        self._cursor = 0
        self._seq_i = 0
        self._marker = 0.0
        self._marker_dir = 1
        self._cand = None
        self._tries = self.stop["activity"].get("tries", 3)
        self._msg = ""
        self._msg_t = 0.0
        self._opt_rects = []
        self._match_rects = []
        self._rhythm_rects = []
        self.game.box.hide()
        # arriving from the overworld after the tablet: the town has
        # already talked, so go straight to the local activity
        if self.game.pending_activity == self.stop["id"]:
            self.game.pending_activity = None
            self.phase = "activity"
            self.act = self.stop["activity"]
            return
        self._advance_dialogue()

    # -------------------------------------------------------------- dialogue
    def _advance_dialogue(self):
        box = self.game.box
        if box.is_revealing():
            box.skip()
            return
        self._index += 1
        if self._index < len(self._lines):
            speaker, accent, text = self._lines[self._index]
            box.show(speaker, accent, text)
            return
        box.hide()
        self.phase = "activity"
        self.act = self.stop["activity"]

    # ---------------------------------------------------------------- input
    def handle_event(self, ev):
        if self.phase == "dialogue":
            if _confirm_key(ev) or mouse.clicked(ev):
                self._advance_dialogue()
            return

        if self.phase == "reward":
            # the activity is done — hand back to the overworld, which
            # plays the reward lines
            if _confirm_key(ev) or mouse.clicked(ev):
                self.game.switch("overworld")
            return

        if self.phase == "done":
            if _confirm_key(ev) or mouse.clicked(ev):
                self._leave()
            return

        # ---- activity phase (keyboard, or clicks on the options)
        kind = self.act["type"]
        if kind == "choice":
            self._event_choice(ev)
        elif kind == "match":
            self._event_match(ev)
        elif kind == "timing":
            self._event_timing(ev)
        elif kind == "rhythm":
            self._event_rhythm(ev)
        elif kind == "calm":
            self._event_calm(ev)

    # ------------------------------------------------------------- update
    def update(self, dt):
        self.t += dt
        if self.phase == "activity" and self.act["type"] == "timing":
            speed = 1.1
            self._marker += self._marker_dir * speed * dt
            if self._marker > 1.0:
                self._marker = 1.0
                self._marker_dir = -1
            elif self._marker < 0.0:
                self._marker = 0.0
                self._marker_dir = 1
        if self._msg_t > 0.0:
            self._msg_t -= dt
            if self._msg_t <= 0.0:
                self._msg = ""

    def _flash(self, text, dur=1.6):
        self._msg = text
        self._msg_t = dur

    # ------------------------------------------------------------ choice
    def _event_choice(self, ev):
        opts = self.act["options"]
        if mouse.clicked(ev):
            i = mouse.hit(self._opt_rects, ev.pos)
            if i is None or i >= len(opts):
                return
            if i == self._cursor:
                self._pick_choice()
            else:
                self._cursor = i
            return
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key in (pygame.K_UP, pygame.K_w):
            self._cursor = (self._cursor - 1) % len(opts)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self._cursor = (self._cursor + 1) % len(opts)
        elif _confirm_key(ev):
            self._pick_choice()

    def _pick_choice(self):
        pick = self.act["options"][self._cursor]
        self.game.state.bump_respect(pick.get("respect", 0))
        self._flash(pick["reply"])
        self._finish_activity()

    # -------------------------------------------------------------- match
    def _candidates(self):
        """Correct answers plus decoys, in a stable shuffled order."""
        if getattr(self, "_cand", None) is None:
            import random
            pool = list(self.act["options"]) + list(self.act.get("decoys", []))
            random.Random(self.stop["id"]).shuffle(pool)
            self._cand = pool
        return self._cand

    def _event_match(self, ev):
        cand = self._candidates()
        if mouse.clicked(ev):
            i = mouse.hit(self._match_rects, ev.pos)
            if i is None or i >= len(cand):
                return
            if i == self._cursor:
                self._attempt_match()
            else:
                self._cursor = i
            return
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key in (pygame.K_LEFT, pygame.K_a):
            self._cursor = (self._cursor - 1) % len(cand)
        elif ev.key in (pygame.K_RIGHT, pygame.K_d):
            self._cursor = (self._cursor + 1) % len(cand)
        elif _confirm_key(ev):
            self._attempt_match()

    def _attempt_match(self):
        cand = self._candidates()
        pick = cand[self._cursor]
        if pick in self.act["options"] and pick not in self._picks:
            self._picks.append(pick)
            self._cursor = (self._cursor + 1) % len(cand)
            if len(self._picks) >= len(self.act["options"]):
                self._flash("Noi: oroi! Well found.")
                self._finish_activity()
            else:
                self._flash("Noi: %s — yes. Keep going." % pick, 1.1)
        else:
            self._tries -= 1
            if self._tries <= 0:
                self._flash("Noi: we can try again, slow and steady.")
                self._tries = self.act.get("tries", 3)
            else:
                self._flash("Noi: not that one. %d tries left." % self._tries)

    # ------------------------------------------------------------- timing
    def _event_timing(self, ev):
        if _confirm_key(ev) or mouse.clicked(ev):
            zone = self.act.get("zone", 0.5)
            lo = 0.5 - zone / 2.0
            hi = 0.5 + zone / 2.0
            if lo <= self._marker <= hi:
                self._flash("Noi: oroi! Perfect timing.")
                self._finish_activity()
            else:
                self._tries -= 1
                if self._tries <= 0:
                    self._flash("Noi: breathe, then try again.")
                    self._tries = self.act.get("tries", 3)
                else:
                    self._flash("Noi: too %s. %d tries left."
                                % ("early" if self._marker < lo else "late",
                                   self._tries))

    # ------------------------------------------------------------- rhythm
    def _event_rhythm(self, ev):
        if mouse.clicked(ev):
            i = mouse.hit(self._rhythm_rects, ev.pos)
            seq = self.act["sequence"]
            if i is not None and i < len(seq):
                self._press_rhythm(seq[i])
            return
        if ev.type != pygame.KEYDOWN:
            return
        key_dir = {pygame.K_LEFT: "left", pygame.K_a: "left",
                   pygame.K_RIGHT: "right", pygame.K_d: "right",
                   pygame.K_UP: "up", pygame.K_w: "up",
                   pygame.K_DOWN: "down", pygame.K_s: "down"}
        for key, direction in key_dir.items():
            if ev.key == key:
                self._press_rhythm(direction)
                return

    def _press_rhythm(self, direction):
        seq = self.act["sequence"]
        if self._seq_i >= len(seq):
            return
        if direction == seq[self._seq_i]:
            self._seq_i += 1
            if self._seq_i >= len(seq):
                self._flash("Noi: the rhythm is yours now.")
                self._finish_activity()
        else:
            self._seq_i = 0
            self._tries -= 1
            if self._tries <= 0:
                self._flash("Noi: we start the dance again.")
                self._tries = self.act.get("tries", 3)
            else:
                self._flash("Noi: the steps broke. %d tries left."
                            % self._tries)

    # --------------------------------------------------------------- calm
    def _event_calm(self, ev):
        if _confirm_key(ev) or mouse.clicked(ev):
            self._seq_i += 1
            if self._seq_i >= self.act.get("steps", 3):
                self._flash("Noi: ...thank you for being gentle.")
                self._finish_activity()
            else:
                self._flash("Noi: one more, slow and quiet.")

    # ------------------------------------------------------------ completion
    def _finish_activity(self):
        self.phase = "reward"
        st = self.game.state
        fresh, gained = st.complete_stop(self.stop)
        if fresh:
            st.bump_spice(1 if self.stop["kind"] == "province" else 0)
        self._gained = gained
        # the overworld plays the reward lines, so hand the stop back
        self.game.pending_reward = self.stop["id"]

    def _leave(self):
        if self.phase == "done":
            self.game.switch("overworld")
            return
        self.phase = "done"

    # ----------------------------------------------------------------- draw
    def draw(self, screen):
        if self.phase == "dialogue":
            # the world behind the dialogue — a dusk field
            screen.fill(S.BG)
            pixel.add_glow(screen, (W // 2, 70), 60, (120, 60, 50),
                           max_alpha=40)
        else:
            self._draw_activity(screen)
        self._draw_progress(screen)
        self.game.box.draw(screen)

    def _draw_activity(self, screen):
        screen.fill(S.BG)
        kind = self.act["type"]
        # header
        pixel.draw_text(screen, self.stop["name"],
                        ((W - pixel.text_size(self.stop["name"])[0]) // 2, 6),
                        S.RUEN)
        pixel.draw_text(screen, self.act["prompt"],
                        ((W - pixel.text_size(self.act["prompt"])[0]) // 2, 18),
                        S.TEXT, shadow=None)
        if kind == "choice":
            self._draw_choice(screen)
        elif kind == "match":
            self._draw_match(screen)
        elif kind == "timing":
            self._draw_timing(screen)
        elif kind == "rhythm":
            self._draw_rhythm(screen)
        elif kind == "calm":
            self._draw_calm(screen)
        self._draw_msg(screen)
        self._draw_hint(screen)

    def _draw_choice(self, screen):
        opts = self.act["options"]
        self._opt_rects = []
        y = 60
        for i, opt in enumerate(opts):
            cur = i == self._cursor
            x = 20
            self._opt_rects.append(pygame.Rect(8, y - 2, W - 16, 13))
            if cur:
                pixel.draw_text(screen, ">", (x, y), S.CHILD)
            pixel.draw_text(screen, opt["text"], (x + 12, y),
                            S.TEXT if cur else S.MUTED, shadow=None)
            y += 14
        pixel.draw_text(screen, "RESPECT %d" % self.game.state.respect,
                        (20, y + 6), S.SPIRIT, shadow=None)

    def _draw_match(self, screen):
        cand = self._candidates()
        # the things still to find
        left = [o for o in self.act["options"] if o not in self._picks]
        label = "Find: " + ", ".join(left)
        pixel.draw_text(screen, label, (16, 40), S.AMBER, shadow=None)
        # candidate buttons along the bottom
        y = 96
        x = 16
        self._match_rects = []
        for i, name in enumerate(cand):
            cur = i == self._cursor
            picked = name in self._picks
            w = pixel.text_size(name)[0] + 12
            if x + w > W - 8:
                x = 16
                y += 20
            color = (120, 226, 120) if picked else (S.PANEL_BORDER if cur else (86, 96, 128))
            box = pygame.Rect(x, y, w, 15)
            self._match_rects.append(box)
            pixel.panel(screen, box, S.PANEL_BG if not picked else (20, 40, 30),
                        color)
            pixel.draw_text(screen, name, (x + 6, y + 4),
                            S.TEXT if not picked else (120, 226, 120), shadow=None)
            if cur:
                pixel.draw_text(screen, "^", (x + (w - 6) // 2, y - 10), S.CHILD)
            x += w + 8

    def _draw_timing(self, screen):
        # a bar with a sweet zone and a sweeping marker
        x0, x1, y = 32, W - 32, 96
        pixel.panel(screen, pygame.Rect(x0, y, x1 - x0, 14),
                    S.PANEL_BG, S.PANEL_BORDER)
        zone = self.act.get("zone", 0.5)
        lo = 0.5 - zone / 2.0
        hi = 0.5 + zone / 2.0
        zx0 = int(x0 + (x1 - x0) * lo)
        zx1 = int(x0 + (x1 - x0) * hi)
        screen.fill((120, 226, 128), pygame.Rect(zx0, y + 2, zx1 - zx0, 10))
        mx = int(x0 + (x1 - x0) * self._marker)
        screen.fill((255, 216, 150), pygame.Rect(mx - 1, y - 3, 3, 20))
        pixel.draw_text(screen, "press confirm in the green",
                        ((W - pixel.text_size("press confirm in the green")[0]) // 2,
                         y + 24), S.MUTED, shadow=None)

    def _draw_rhythm(self, screen):
        seq = self.act["sequence"]
        x = (W - len(seq) * 18) // 2
        y = 66
        self._rhythm_rects = []
        pixel.draw_text(screen, "copy the steps", (x, y - 16), S.MUTED, shadow=None)
        for i, step in enumerate(seq):
            cur = i == self._seq_i
            self._rhythm_rects.append(pygame.Rect(x + i * 18 - 3, y - 2, 14, 12))
            pixel.draw_text(screen, ARROWS[step], (x + i * 18, y),
                            S.CHILD if cur else S.MUTED, shadow=None)
        pixel.draw_text(screen, "you", (x, y + 24), S.MUTED, shadow=None)
        for i in range(len(seq)):
            done = i < self._seq_i
            pixel.draw_text(screen, ARROWS[seq[i]] if done else ".",
                            (x + i * 18, y + 24),
                            (120, 226, 120) if done else S.MUTED, shadow=None)

    def _draw_calm(self, screen):
        steps = self.act.get("steps", 3)
        msg = [
            "be still",
            "breathe with the place",
            "listen",
            "let it be",
            "one more moment",
            "quiet now",
        ]
        pixel.draw_text(screen, msg[min(self._seq_i, len(msg) - 1)],
                        ((W - pixel.text_size(msg[min(self._seq_i, len(msg) - 1)])[0]) // 2,
                         88), S.SPIRIT)
        for i in range(steps):
            x = (W - steps * 12) // 2 + i * 12
            screen.fill((120, 226, 120) if i < self._seq_i else (86, 96, 128),
                        pygame.Rect(x, 120, 8, 8))

    def _draw_msg(self, screen):
        if self._msg:
            w = pixel.text_size(self._msg)[0]
            pixel.draw_text(screen, self._msg, ((W - w) // 2, 168),
                            S.TEXT, shadow=None)

    def _draw_hint(self, screen):
        hint = {"choice": "up/down choose  confirm answer  click ok",
                "match": "left/right browse  confirm pick  click ok",
                "timing": "confirm inside the green  click ok",
                "rhythm": "arrow keys repeat the steps  click ok",
                "calm": "confirm to be still  click ok"}[self.act["type"]]
        pixel.draw_text(screen, hint, (5, H - 11), S.MUTED, shadow=None)

    def _draw_progress(self, screen):
        if self.phase == "reward" or self.phase == "done":
            self._draw_reward(screen)
        else:
            st = self.game.state
            label = "PAGE %d/%d   tries %d" % (st.journal_count(),
                                               ST.TOTAL_STOPS, self._tries)
            pixel.draw_text(screen, label, (5, 5), S.TEXT, shadow=None)

    def _draw_reward(self, screen):
        screen.fill(S.BG)
        st = self.game.state
        title = "JOURNAL PAGE RECOVERED"
        pixel.draw_text(screen, title,
                        ((W - pixel.text_size(title)[0]) // 2, 22), S.RUEN)
        pixel.draw_text(screen, self.stop["name"],
                        ((W - pixel.text_size(self.stop["name"])[0]) // 2, 40),
                        S.TEXT)
        y = 72
        pixel.draw_text(screen, "PAGE", (24, y), S.MUTED, shadow=None)
        pixel.draw_text(screen, self.stop["page"], (24, y + 12), S.TEXT, shadow=None)
        y += 40
        for card in self.stop.get("cards", []):
            pixel.draw_text(screen, "CULTURE CARD  %s" % card, (24, y),
                            (120, 226, 120), shadow=None)
            y += 14
        if self.stop.get("word"):
            w_ = self.stop["word"]
            pixel.draw_text(screen, "PAK TAI WORD", (24, y), S.MUTED, shadow=None)
            pixel.draw_text(screen, "%s (%s) — %s" % (w_["thai"], w_["roman"],
                                                      w_["meaning"]),
                            (24, y + 12), S.SPIRIT, shadow=None)
            y += 40
        pixel.draw_text(screen, "LEARN", (24, y), S.MUTED, shadow=None)
        self._draw_wrapped(screen, self.stop["learn"], 24, y + 12)
        y = H - 26
        hint = "confirm  continue" if self.phase == "reward" else "confirm  back to the map"
        pixel.draw_text(screen, hint, ((W - pixel.text_size(hint)[0]) // 2, y),
                        S.MUTED, shadow=None)

    @staticmethod
    def _draw_wrapped(screen, text, x, y):
        words = text.split()
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if pixel.text_size(trial)[0] > W - x - 16:
                pixel.draw_text(screen, line, (x, y), S.TEXT, shadow=None)
                y += 12
                line = word
            else:
                line = trial
        if line:
            pixel.draw_text(screen, line, (x, y), S.TEXT, shadow=None)
