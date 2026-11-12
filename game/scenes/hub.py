"""The walkable village hub, on the big tall valley world.

The world is much larger than the screen; ``Camera`` follows the player
(mostly along Y — north is the shrine terrace under the dusk sky, south is
the river and the wild lake). Movement has three paces: walk, run (hold the
run key) and glide (hold the glide key — a faster spirit-pace with a petal
trail). Water and the forest walls stop the player.
"""

import math

import pygame

from .. import keymap
from .. import mouse
from .. import options as O
from .. import pixel
from .. import settings as S
from .. import tiles as T
from .. import views

WALK = 62.0
RUN = 108.0
GLIDE = 148.0


class HubScene:
    name = "hub"
    REACH = 28.0

    def __init__(self, game):
        self.game = game
        self.t = 0.0
        self.player = pygame.Vector2(*views.VILLAGE["npc_child"])
        self.facing = "up"
        self.keys = set()
        self._run = False
        self._glide = False
        self.speed = WALK
        self.modal = None
        self.prompt = ""
        self._replay_child = 0
        self._steps = 0.0
        self.cam = views.Camera()
        self.tm = T.big_map()
        self.petals = []
        self._petal_age = 0.0

        v = views.VILLAGE
        self.ruen = pygame.Vector2(*v["npc_ruen"])
        self.nok = pygame.Vector2(*v["npc_nok"])
        self.shrine = pygame.Vector2(*v["shrine"])
        self.well = pygame.Vector2(*v["well"])
        self.child_home = pygame.Vector2(*v["npc_child"])

    # -------------------------------------------------------------- life cycle
    def on_enter(self):
        self.player = pygame.Vector2(self.child_home.x, self.child_home.y + 12)
        self.facing = "up"
        self.modal = None
        self.keys.clear()
        self.petals.clear()
        self.speed = WALK
        self.cam.snap_to(self.player.x, self.player.y)
        self.game.box.hide()
        self.game.state.give_item("river_stone")

    # ------------------------------------------------------------------- input
    def handle_event(self, ev):
        advance = (ev.type == pygame.KEYDOWN and (
            ev.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER)
            or keymap.pressed("confirm", ev)
        )) or mouse.clicked(ev)
        if self.modal is not None:
            if (ev.type == pygame.KEYDOWN and keymap.pressed("cancel", ev)) \
                    or mouse.cancelled(ev):
                self.modal = None
                self.game.box.hide()
            elif advance:
                self._advance_modal()
            return
        if ev.type == pygame.KEYDOWN:
            self.keys.add(ev.key)
            if keymap.pressed("run", ev):
                self._run = True
            if keymap.pressed("glide", ev):
                self._glide = True
            if advance:
                self._interact()
        elif ev.type == pygame.KEYUP:
            self.keys.discard(ev.key)
            if keymap.released("run", ev):
                self._run = False
            if keymap.released("glide", ev):
                self._glide = False

    def update(self, dt):
        self.t += dt
        if self.modal is not None:
            return
        direction = pygame.Vector2(0, 0)
        if self.keys & {pygame.K_LEFT, pygame.K_a}:
            direction.x -= 1
        if self.keys & {pygame.K_RIGHT, pygame.K_d}:
            direction.x += 1
        if self.keys & {pygame.K_UP, pygame.K_w}:
            direction.y -= 1
        if self.keys & {pygame.K_DOWN, pygame.K_s}:
            direction.y += 1

        run = self._run or keymap.held("run")
        glide = self._glide or keymap.held("glide")
        target = GLIDE if glide else (RUN if run else WALK)
        self.speed += (target - self.speed) * min(1.0, dt * 6.0)

        if direction.length_squared() > 0:
            step = direction.normalize() * self.speed * dt
            self._move(step.x, step.y)
            self._clamp_bounds()
            if abs(direction.x) > abs(direction.y):
                self.facing = "side"
            elif direction.y < 0:
                self.facing = "up"
            else:
                self.facing = "down"
            self._steps += dt * (self.speed / WALK)
            if glide:
                self._emit_petals(direction.normalize())
        else:
            self._steps = 0.0
        self._update_petals(dt)
        self.prompt = self._prompt()
        self.cam.follow(self.player.x, self.player.y, dt)

    # ---------------------------------------------------------------- movement
    def _feet_ok(self, x, y):
        """True when both feet-width samples sit on walkable ground."""
        return (T.walkable_at(self.tm, x + 3, y + 10)
                and T.walkable_at(self.tm, x + 13, y + 10))

    def _move(self, dx, dy):
        nx, ny = self.player.x + dx, self.player.y + dy
        if self._feet_ok(nx, self.player.y):
            self.player.x = nx
        if self._feet_ok(self.player.x, ny):
            self.player.y = ny

    def _clamp_bounds(self):
        self.player.x = max(6.0, min(views.WORLD_W - 8.0, self.player.x))
        self.player.y = max(views.GROUND_Y + 6.0, min(views.WORLD_H - 6.0, self.player.y))

    def walk_frame(self):
        return int(self._steps * 7) % 2 if self._steps else 0

    # ------------------------------------------------------------- glide trail
    def _emit_petals(self, d):
        p = self.player
        for i in range(2):
            jitter = (self._petal_age * 1.7 + i * 3.1) % (2 * math.pi)
            self.petals.append({
                "x": p.x + 16.0 - d.x * (8 + i * 5) + math.cos(jitter) * 3,
                "y": p.y + 8.0 - d.y * (8 + i * 5) + math.sin(jitter) * 2,
                "vx": -d.x * (20 + self.speed * 0.1) - 12.0,
                "vy": -d.y * (20 + self.speed * 0.1) - 12 * math.sin(jitter) - 4,
                "life": 0.75 + (i % 2) * 0.2,
                "max": 0.95,
                "hue": 0 if self._petal_age % 1.0 < 0.5 else 1,
            })
        if len(self.petals) > 64:
            del self.petals[:len(self.petals) - 64]

    def _update_petals(self, dt):
        for p in self.petals:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 16 * dt
            p["life"] -= dt
        self.petals = [p for p in self.petals if p["life"] > 0]

    def _draw_petals(self, screen, ox, oy):
        for p in self.petals:
            c = (246, 216, 180) if p["hue"] == 0 else (158, 226, 168)
            a = max(0.0, min(1.0, p["life"] / p["max"]))
            px, py = int(p["x"]) - ox, int(p["y"]) - oy
            if 0 <= px < S.INTERNAL_W - 1 and 0 <= py < S.INTERNAL_H - 1:
                screen.fill((c[0], c[1], c[2], int(230 * a)), pygame.Rect(px, py, 2, 2))

    # ------------------------------------------------------------- interactions
    def child_pos(self):
        return pygame.Vector2(self.child_home.x + math.sin(self.t * 0.6) * 16,
                              self.child_home.y)

    def _dist(self, point):
        return self.player.distance_to(point)

    def _prompt(self):
        st = self.game.state
        if not O.options.prompts_on():
            return ""
        act = keymap.label("confirm")
        if not st.named and self._dist(self.ruen) < self.REACH:
            return "%s  talk to Grandma Ruen" % act
        if st.named and not st.shrine_done and self._dist(self.shrine) < self.REACH:
            return "%s  inspect the shrine" % act
        if st.shrine_done and not st.well_done and self._dist(self.nok) < self.REACH:
            return "%s  talk to Nok" % act
        if self._dist(self.child_pos()) < self.REACH:
            return "%s  talk to the child" % act
        if self._dist(self.ruen) < self.REACH:
            return "%s  talk to Grandma Ruen" % act
        if self._dist(self.shrine) < self.REACH and not st.shrine_done:
            return "%s  inspect the shrine" % act
        if self._dist(self.nok) < self.REACH and not st.well_done:
            return "%s  talk to Nok" % act
        return ""

    def _interact(self):
        st = self.game.state
        if self._dist(self.ruen) < self.REACH:
            if not st.named:
                self.game.switch("village_naming")
            else:
                self._show([
                    ("GRANDMA RUEN", S.RUEN, "Spirit suits it. You did well."),
                    ("GRANDMA RUEN", S.RUEN, "Shrine's still quiet. Wake it, if you can."),
                ])
            return
        if self._dist(self.child_pos()) < self.REACH:
            st.give_item("gift_flower")
            lines = [
                ("CHILD", S.CHILD, "Did you really fall in the river? What did it feel like?"),
                ("CHILD", S.CHILD, "Grandma says you've got a ghost. I can't see it. Is it shy?"),
                ("CHILD", S.CHILD, "If you fix the well Nok will stop talking about it. Please."),
            ]
            self._show([lines[self._replay_child % len(lines)]])
            self._replay_child += 1
            return
        if self._dist(self.shrine) < self.REACH:
            if not st.named:
                self._show([("SPIRIT", S.SPIRIT, "Not for me yet. Grandma Ruen first.")])
            elif not st.shrine_done:
                self.game.switch("shrine")
            else:
                self._show([("SPIRIT", S.SPIRIT, "Warm again. It hums when you walk past.")])
            return
        if self._dist(self.nok) < self.REACH or self._dist(self.well) < self.REACH:
            if not st.named:
                self._show([("NOK", S.NOK, "Careful, the well's moody. Ruen'll sort you out.")])
            elif not st.shrine_done:
                self._show([("NOK", S.NOK, "Ward's out of sorts. Shrine has to wake first, Ruen says.")])
            elif not st.well_done:
                self.game.switch("well")
            else:
                self._show([("NOK", S.NOK, "Water's fine now. I keep lowering the bucket to watch.")])

    # ------------------------------------------------------------------- modal
    def _show(self, lines):
        prepared = [(self.game.state.display_spirit_name() if s == "SPIRIT" else s, a, t)
                    for s, a, t in lines]
        self.modal = {"lines": prepared, "index": -1}
        self._advance_modal()

    def _advance_modal(self):
        box = self.game.box
        if box.is_revealing():
            box.skip()
            return
        self.modal["index"] += 1
        index = self.modal["index"]
        if index < len(self.modal["lines"]):
            speaker, accent, text = self.modal["lines"][index]
            box.show(speaker, accent, text)
        else:
            self.modal = None
            box.hide()

    # -------------------------------------------------------------------- draw
    def draw(self, screen):
        st = self.game.state
        water = 0.9 if st.well_done else 0.0
        ox, oy = self.cam.offset()
        back_blit, lights = views.village_ground(screen, self.t, cam=(ox, oy),
                                                 lit_shrine=st.shrine_done, water=water)
        views.draw_back_layer(screen, back_blit, (ox, oy))

        child = self.child_pos()
        figures = [
            ("ruen", self.ruen, "down", 0),
            ("nok", self.nok, "down", int(self.t * 4) % 4),
            ("child", child, "side", int(self.t * 6) % 4),
        ]
        for who, pos, facing, frame in sorted(figures, key=lambda f: f[1].y):
            views.blit_character(screen, pos.x - ox, pos.y - oy, who, facing, frame)
        views.blit_spirit(screen, self.player.x + 9 - ox, self.player.y - 15 - oy, self.t)
        views.blit_character(screen, self.player.x - ox, self.player.y - oy, "player",
                             self.facing, self.walk_frame())
        lights.append((self.player.x + 9 - ox, self.player.y - 15 - oy, 22, 0.5))

        self._draw_petals(screen, ox, oy)
        views.draw_front_layer(screen, self.t, (ox, oy), water, lights)
        views.atmosphere(screen, lights, dark=56, tint=(96, 48, 32, 14))

        if self.prompt and self.modal is None:
            box = pygame.Rect(0, 0, pixel.text_size(self.prompt)[0] + 10, 14)
            box.center = (S.INTERNAL_W // 2, S.INTERNAL_H - 12)
            pixel.panel(screen, box, S.PANEL_BG, S.PANEL_BORDER)
            pixel.draw_text(screen, self.prompt, (box.x + 5, box.y + 3), S.TEXT, shadow=None)

        self._draw_hud(screen)
        self.game.box.draw(screen)

    def _draw_hud(self, screen):
        """Player UI: bound spirit + item count, and the controls hint."""
        st = self.game.state
        pixel.add_glow(screen, (9, 8), 6, (90, 235, 220), max_alpha=64)
        screen.fill((108, 240, 222), pygame.Rect(8, 7, 3, 3))
        pixel.draw_text(screen, st.display_spirit_name(), (15, 5), S.SPIRIT)

        label = "ITEMS %d" % len(st.items)
        pixel.draw_text(screen, label,
                        (S.INTERNAL_W - pixel.text_size(label)[0] - 6, 5),
                        S.MUTED, shadow=None)

        if self.modal is None and not self.prompt:
            run_label = "SHIFT" if keymap.code("run") in (pygame.K_LSHIFT, pygame.K_RSHIFT) \
                else keymap.label("run")
            hint = "[%s]items [%s]settings   %s run   %s glide" % (
                keymap.label("items"), keymap.label("settings"),
                run_label, "X" if keymap.code("glide") == pygame.K_x else keymap.label("glide"))
            pixel.draw_text(screen, hint, (5, S.INTERNAL_H - 11), S.MUTED, shadow=None)