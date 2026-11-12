"""A province you actually walk into: its own map, its own story.

Sailing, gliding or hiking through a gate on the big map brings you
here — a full local map cut from the real South around the town, with
the host in the plaza, the sight worth seeing, the rune tablet on its
dais, and the south road back out. Nothing is free: hear the welcome
(meet), look at the sight (look), then solve the tablet (solve) to
win the page. Walk out and you stand exactly where you entered.
"""

import math
import random

import pygame

from .. import keymap
from .. import mouse
from .. import options as O
from .. import pixel
from .. import settings as S
from .. import story as ST
from .. import tablets as TB
from .. import tiles as T
from .. import views
from .. import world_map as WM

W, H = S.INTERNAL_W, S.INTERNAL_H
TILE = T.TILE

WALK = 62.0
RUN = 108.0
GLIDE = 176.0
TOUCH = 24.0

CROP_W, CROP_H = 64, 48


class RegionScene:
    name = "region"

    def __init__(self, game):
        self.game = game
        self.t = 0.0
        self.stop = None
        self.tm = None
        self.ox = 0
        self.oy = 0
        self.player = pygame.Vector2(0, 0)
        self.spawn = pygame.Vector2(0, 0)
        self.tablet = pygame.Vector2(0, 0)
        self.host = pygame.Vector2(0, 0)
        self.sight = pygame.Vector2(0, 0)
        self.facing = "up"
        self.keys = set()
        self._run = False
        self._glide = False
        self.speed = WALK
        self._steps = 0.0
        self.cam = views.Camera()
        self.petals = []
        self.fx = []
        self.prompt = ""
        self.box = game.box
        self._modal = None
        self.panel = None
        self._tablet_stop = None
        self._tablet_role = "main"
        self._tablet_spec = None
        self._fade = 1.0              # 1 = black, 0 = clear
        self._leaving = False

    # -------------------------------------------------------------- life cycle
    def on_enter(self):
        self.t = 0.0
        self.stop = ST.STOP_BY_ID.get(self.game.next_stop) or ST.STOPS[0]
        world = self.game.scenes["overworld"].tm
        self.tm, self.ox, self.oy = WM.region_crop(world, self.stop,
                                                   w=CROP_W, h=CROP_H)
        self.cam = views.Camera(
            max_x=self.tm.cols * TILE - W, max_y=self.tm.rows * TILE - H)
        c, r = self.stop["pos"]
        lx = (c - self.ox) * TILE + TILE // 2
        ly = (r - self.oy) * TILE + TILE // 2
        self.tablet = pygame.Vector2(lx, ly)
        self.host = pygame.Vector2(lx + 26, ly + 4)
        extra = ST.extra_of(self.stop["id"])
        sight = extra.get("sight", {})
        self.sight = pygame.Vector2(
            lx + sight.get("dx", 0) * TILE, ly + sight.get("dy", 0) * TILE)
        self.spawn = pygame.Vector2(*self._find_spawn())
        self.player = self.spawn.copy()
        self.cam.snap_to(self.player.x, self.player.y)
        self.facing = "up"
        self.keys.clear()
        self.petals.clear()
        self.fx.clear()
        self.speed = WALK
        self._glide = False
        self._fade = 1.0
        self._leaving = False
        self._modal = None
        self.panel = self.game.make_panel(self._on_run)
        self.game.box.hide()
        if (not self.game.state.stop_done(self.stop["id"])
                and self.game.state.quests.get(self.stop["id"], 0) == 0):
            self._show(list(self.stop["lines"]), kind="greeting")

    def _find_spawn(self):
        """A walkable tile near the bottom middle: the south road in."""
        w, h = self.tm.cols, self.tm.rows
        for r in range(h - 2, 0, -1):
            for k in range(w):
                for c in (w // 2 + k, w // 2 - k):
                    if 0 <= c < w and self.tm.grid[r][c] not in ("W", "H"):
                        return (c * TILE + TILE // 2, r * TILE + TILE // 2)
        return (w * TILE // 2, h * TILE // 2)

    # ------------------------------------------------------------------ quests
    def _beats(self):
        return self.game.state.quests.get(self.stop["id"], 0)

    def _meet_done(self):
        return self._beats() >= 1 or self.game.state.stop_done(self.stop["id"])

    def _look_done(self):
        return self._beats() >= 2 or self.game.state.stop_done(self.stop["id"])

    def _spark_done(self):
        return self._beats() >= 3 or self.game.state.stop_done(self.stop["id"])

    def _objective(self):
        if self.game.state.stop_done(self.stop["id"]):
            return "south road to leave"
        if not self._meet_done():
            return "hear the welcome"
        if not self._look_done():
            extra = ST.extra_of(self.stop["id"])
            label = extra.get("sight", {}).get("label", "the sight")
            return "look at %s" % label
        if not self._spark_done():
            extra = ST.extra_of(self.stop["id"])
            return "find the hidden spark — ask %s" % extra.get("host", "the host")
        spec = ST.code_of(self.stop["id"])
        title = spec["title"] if spec else "RUNES"
        return "solve the %s tablet" % title

    def _objective_pos(self):
        if self.game.state.stop_done(self.stop["id"]):
            return self.spawn
        if not self._meet_done():
            return self.host
        if not self._look_done():
            return self.sight
        if not self._spark_done():
            return self.spawn          # out the gate, into the wild
        return self.tablet

    # ------------------------------------------------------------------- input
    def handle_event(self, ev):
        advance = (ev.type == pygame.KEYDOWN and (
            ev.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER)
            or keymap.pressed("confirm", ev)
        )) or mouse.clicked(ev)
        if self.panel is not None and self.panel.visible:
            result = self.panel.handle_event(ev)
            if result == "close":
                self.panel.close()
            return
        if self._modal is not None:
            cancel = (ev.type == pygame.KEYDOWN and keymap.pressed("cancel", ev)) \
                or mouse.cancelled(ev)
            if cancel:
                self._close_modal()
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
        elif mouse.clicked(ev):
            self._interact()

    # ------------------------------------------------------------------ update
    def update(self, dt):
        self.t += dt
        self._update_fx(dt)
        if self._fade > 0.0 and not self._leaving:
            self._fade = max(0.0, self._fade - dt * 2.2)
        if self._leaving:
            self._fade = min(1.0, self._fade + dt * 2.6)
            if self._fade >= 1.0:
                self.game.switch("overworld")
            return
        if self.panel is not None and self.panel.visible:
            self.panel.update(dt)
            return
        if self._modal is not None:
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
            if abs(direction.x) > abs(direction.y):
                self.facing = "side"
            elif direction.y < 0:
                self.facing = "up"
            else:
                self.facing = "down"
            self._steps += dt * (self.speed / WALK)
        else:
            self._steps = 0.0
        self._update_petals(dt)
        self.prompt = self._prompt()
        self.cam.follow(self.player.x, self.player.y, dt)

    def _ok(self, x, y):
        c, r = int(x) // TILE, int(y) // TILE
        cell = self.tm.cell(r, c)
        if cell is None:
            return False
        if cell in ("W", "H"):
            return self._glide and cell == "W"
        return True

    def _feet_ok(self, x, y):
        return self._ok(x + 4, y + 10) and self._ok(x + 12, y + 10)

    def _move(self, dx, dy):
        nx, ny = self.player.x + dx, self.player.y + dy
        if self._feet_ok(nx, self.player.y):
            self.player.x = nx
        if self._feet_ok(self.player.x, ny):
            self.player.y = ny
        self.player.x = max(8.0, min(self.tm.cols * TILE - 8.0, self.player.x))
        self.player.y = max(8.0, min(self.tm.rows * TILE - 8.0, self.player.y))

    def walk_frame(self):
        return int(self._steps * 7) % 2 if self._steps else 0

    def _update_petals(self, dt):
        for p in self.petals:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 16 * dt
            p["life"] -= dt
        self.petals = [p for p in self.petals if p["life"] > 0]

    # ---------------------------------------------------------------- interact
    def _near_what(self):
        best, best_d, what = None, TOUCH + 8, None
        for name, pos in (("tablet", self.tablet), ("host", self.host),
                          ("sight", self.sight), ("gate", self.spawn)):
            d = self.player.distance_to(pos)
            if d < best_d:
                best, best_d, what = pos, d, name
        return what

    def _prompt(self):
        if not O.options.prompts_on() or self._modal is not None:
            return ""
        act = keymap.label("confirm")
        what = self._near_what()
        if what == "tablet":
            spec = ST.code_of(self.stop["id"])
            title = spec["title"] if spec else "RUNES"
            if self._look_done():
                return "%s  read the %s tablet" % (act, title)
            return "the tablet waits — %s first" % self._objective()
        if what == "host":
            extra = ST.extra_of(self.stop["id"])
            return "%s  talk to %s" % (act, extra.get("host", "local"))
        if what == "sight":
            label = ST.extra_of(self.stop["id"]).get("sight", {}).get("label", "the sight")
            return "%s  look at %s" % (act, label)
        if what == "gate":
            return "%s  south road, back to the map" % act
        return ""

    def _interact(self):
        what = self._near_what()
        if what == "host":
            self._show(self._host_lines(), kind="host")
        elif what == "sight":
            extra = ST.extra_of(self.stop["id"])
            sight = extra.get("sight", {})
            self._show([("NOI", "NOI", sight.get("text", "Look well. Remember it."))],
                       kind="sight")
        elif what == "tablet":
            if not self._spark_done():
                extra = ST.extra_of(self.stop["id"])
                host = extra.get("host", "local")
                if not self._meet_done():
                    need = "meet " + host
                elif not self._look_done():
                    need = "look at " + extra.get("sight", {}).get("label", "the sight")
                else:
                    need = "find the hidden spark (ask %s for the hint)" % host
                self._show([("NOI", "NOI", "Not yet — %s first." % need)],
                           kind="locked")
                return
            self._open_tablet()
        elif what == "gate":
            self._leaving = True

    def _host_lines(self):
        extra = ST.extra_of(self.stop["id"])
        host = extra.get("host", "Local")
        accent = ST.HOST_ACCENT.get(extra.get("look", "nok"), "NOK")
        lines = []
        if self.stop["id"] in self.game.state.failed and not self.game.state.stop_done(self.stop["id"]):
            lines.append((host, accent, "Back again? Good. The tablet remembers you too."))
        lines.extend((host, accent, text) for text in extra.get("lines", []))
        if self.stop["id"] not in self.game.state.found and extra.get("hint"):
            lines.append(("NOI", "NOI", extra["hint"]))
        return lines or list(self.stop["lines"])

    # ------------------------------------------------------------------ tablet
    def _tablet_specs(self):
        spec = ST.code_of(self.stop["id"])
        forg = (spec or {}).get("forgery")
        flags = self.game.state.flags
        if forg and "%s_truth" % self.stop["id"] not in flags:
            if "%s_accused" % self.stop["id"] not in flags:
                return spec, "accuse"
            return forg, "truth"
        return spec, "main"

    def _open_tablet(self):
        spec, role = self._tablet_specs()
        if spec is None:
            return
        self._tablet_stop = self.stop
        self._tablet_role = role
        self._tablet_spec = spec
        title = spec["title"]
        status = spec.get("status", "")
        if spec.get("broken"):
            title = "BROKEN " + title
            status = "BROKEN SPELL! " + spec["broken"] + "\n" + status
        self.panel.open(title, spec.get("prefill", ""), status)

    def _on_run(self, code):
        from .. import audio
        stop = self._tablet_stop
        spec = self._tablet_spec
        if stop is None or spec is None:
            return
        role = self._tablet_role
        ok, console, status = TB.validate(spec, code)
        self.panel.set_console(console)
        self.panel.set_status(status, S.MUTED)
        st = self.game.state
        if not ok:
            st.combo = 0
            if stop["id"] not in st.failed:
                st.failed.append(stop["id"])
            audio.sfx("error")
            return
        if role == "accuse":
            audio.sfx("blip")
            self.panel.close()
            self.game.box.hide()
            st.flags.append("%s_accused" % stop["id"])
            forg = ST.code_of(stop["id"])["forgery"]
            self._show(list(forg["accuse"]), kind="accuse")
            return
        audio.sfx("success")
        self.panel.close()
        self.game.box.hide()
        fresh, _gained = st.complete_stop(stop)
        if fresh:
            st.bump_spice(1 if stop["kind"] == "province" else 0)
        extra_card = None
        if role == "truth":
            st.flags.append("%s_truth" % stop["id"])
            extra_card = spec.get("card")
            if extra_card:
                st.add_card(extra_card)
        st.combo += 1
        bonus = ""
        if st.combo % 3 == 0:
            st.bump_respect(1)
            bonus = " OROI COMBO x%d! The South applauds." % st.combo
        self._spawn_fx()
        self._show(self._reward_lines(bonus, extra_card), kind="reward")

    def _reward_lines(self, bonus="", extra_card=None):
        stop = self.stop
        lines = []
        if stop["id"] in ST.VISIONS:
            lines.append(("YAAI", "YAAI", "That page... oh. Oh, I remember. " +
                          ST.VISIONS[stop["id"]]))
        lines.append(("NOI", "NOI", "Oroi! The page is ours!" + bonus))
        lines.append(("YAAI", "YAAI", ST.chapter(stop)))
        lines.append(("NOI", "NOI", "Page: %s" % stop["page"]))
        for card in stop.get("cards", []):
            lines.append(("YAAI", "YAAI", "Culture card: %s." % card))
        if extra_card:
            lines.append(("YAAI", "YAAI", "A bonus card, in her own hand: %s." % extra_card))
        word = stop.get("word")
        if word:
            lines.append(("NOI", "NOI", "Pak Tai: %s (%s) — %s."
                          % (word["thai"], word["roman"], word["meaning"])))
        lines.append(("NARRATOR", "TEXT", stop["learn"]))
        if stop.get("call"):
            lines.append(("YAAI", "YAAI", stop["call"]))
        return lines

    # ------------------------------------------------------------------- modal
    def _show(self, lines, kind="talk"):
        prepared = [(self.game.state.display_spirit_name() if s == "SPIRIT" else s, a, t)
                    for s, a, t in lines]
        self._modal = {"lines": prepared, "index": -1, "kind": kind}
        self._advance_modal()

    def _advance_modal(self):
        box = self.game.box
        if box.is_revealing():
            box.skip()
            return
        self._modal["index"] += 1
        index = self._modal["index"]
        if index < len(self._modal["lines"]):
            speaker, accent, text = self._modal["lines"][index]
            box.show(speaker, accent, text)
        else:
            self._close_modal()

    def _close_modal(self):
        kind = (self._modal or {}).get("kind")
        self._modal = None
        self.game.box.hide()
        if kind == "greeting":
            st = self.game.state
            st.quests[self.stop["id"]] = max(st.quests.get(self.stop["id"], 0), 1)
        elif kind == "sight":
            st = self.game.state
            st.quests[self.stop["id"]] = max(st.quests.get(self.stop["id"], 0), 2)

    # ------------------------------------------------------------ spell effects
    FX_TTL = {"burst": 1.5, "rise": 7.0, "swim": 6.0, "pull": 6.0,
              "bloom": 5.0, "rain": 6.0, "dance": 9.0, "festival": 25.0}

    def _spawn_fx(self):
        spec = ST.code_of(self.stop["id"])
        kind = (spec or {}).get("fx", "burst")
        rng = random.Random(self.stop["id"])
        self.fx.append({"kind": kind, "x": self.tablet.x, "y": self.tablet.y,
                        "t": 0.0, "ttl": self.FX_TTL.get(kind, 2.0),
                        "seed": [rng.random() for _ in range(16)]})
        if kind in ("burst", "festival"):
            self._burst(self.tablet.x, self.tablet.y, 26 if kind == "festival" else 14)

    def _burst(self, x, y, n):
        rng = random.Random()
        for _i in range(n):
            ang = rng.random() * 2 * math.pi
            sp = 30 + rng.random() * 60
            self.petals.append({
                "x": x, "y": y - 6,
                "vx": math.cos(ang) * sp, "vy": math.sin(ang) * sp - 30,
                "life": 0.8 + rng.random() * 0.4, "max": 1.2,
                "hue": rng.randrange(2),
            })

    def _update_fx(self, dt):
        for f in self.fx:
            f["t"] += dt
        self.fx = [f for f in self.fx if f["t"] < f["ttl"]]

    def _draw_fx(self, screen, ox, oy):
        for f in self.fx:
            x, y = f["x"] - ox, f["y"] - oy
            if not (-40 <= x <= W + 40 and -40 <= y <= H + 40):
                continue
            kind, t = f["kind"], f["t"]
            if kind == "rise":
                self._draw_rise(screen, x, y, f)
            elif kind == "swim":
                self._draw_swim(screen, x, y, f)
            elif kind == "pull":
                self._draw_pull(screen, x, y, t)
            elif kind == "bloom":
                self._draw_bloom(screen, x, y, t)
            elif kind == "rain":
                self._draw_rain(screen, x, y, t)
            elif kind in ("dance", "festival"):
                self._draw_dance(screen, x, y, f)

    def _draw_rise(self, screen, x, y, f):
        for i in range(5):
            s = f["seed"][i]
            lx = x + (s - 0.5) * 60
            ly = y - 10 - ((f["t"] * 22 + s * 60) % 90)
            pixel.add_glow(screen, (lx, ly), 5, (255, 190, 110), max_alpha=90)
            screen.fill((255, 214, 140), pygame.Rect(int(lx) - 1, int(ly) - 2, 3, 4))

    def _draw_swim(self, screen, x, y, f):
        for i in range(3):
            s = f["seed"][i]
            ang = s * 2 * math.pi
            d = min(f["t"] * 26, 70)
            tx, ty = x + math.cos(ang) * d, y + math.sin(ang) * d * 0.5
            screen.fill((70, 140, 90), pygame.Rect(int(tx) - 3, int(ty) - 1, 7, 3))
            screen.fill((120, 190, 120), pygame.Rect(int(tx) + 3, int(ty) - 1, 2, 2))

    def _draw_pull(self, screen, x, y, t):
        bob = int(2 * math.sin(t * 9))
        screen.fill((150, 110, 70), pygame.Rect(int(x) - 34, int(y) - 4 + bob, 68, 2))
        for i, dx in enumerate((-28, -12, 4)):
            lean = int(2 * math.sin(t * 9 + i))
            views.blit_character(screen, x + dx, y + 8, "child", "side", (i + int(t * 6)) % 2)
            screen.fill((150, 110, 70), pygame.Rect(int(x) + dx, int(y) - 4 + bob + lean, 8, 1))

    def _draw_bloom(self, screen, x, y, t):
        for i in range(8):
            ang = i * math.pi / 4 + t * 0.6
            d = min(t * 14, 26)
            fx, fy = x + math.cos(ang) * d, y + math.sin(ang) * d * 0.6
            col = (240, 150, 180) if i % 2 else (250, 230, 150)
            screen.fill(col, pygame.Rect(int(fx), int(fy), 2, 2))
        pixel.add_glow(screen, (x, y - 6), 8, (250, 220, 150), max_alpha=70)

    def _draw_rain(self, screen, x, y, t):
        for i in range(14):
            s = (i * 0.37) % 1.0
            rx = x + ((i * 53 + t * 40) % 80) - 40
            ry = y - 30 + ((s * 60 + t * 90) % 60)
            screen.fill((140, 180, 220), pygame.Rect(int(rx), int(ry), 1, 4))

    def _draw_dance(self, screen, x, y, f):
        n = 8 if f["kind"] == "festival" else 4
        frame = int(f["t"] * 6) % 2
        for i in range(n):
            s = f["seed"][i % 16]
            ang = i * 2 * math.pi / n + f["t"] * 0.8
            dx = x + math.cos(ang) * (16 + 4 * math.sin(f["t"] * 3 + i))
            dy = y + math.sin(ang) * 8
            views.blit_character(screen, dx, dy,
                                 ("child", "nok", "ruen")[i % 3], "down", frame)
        for i in range(5):
            fx = x - 30 + i * 15
            fy = y - 26 + int(3 * math.sin(f["t"] * 4 + i))
            screen.fill((232, 96, 96) if i % 2 else (255, 216, 150),
                        pygame.Rect(int(fx), int(fy), 4, 3))

    # -------------------------------------------------------------------- draw
    def draw(self, screen):
        ox, oy = self.cam.offset()
        T.draw_view(screen, self.tm, (ox, oy), phase=T.phase_for(self.t))
        self._draw_tablet(screen, ox, oy)
        extra = ST.extra_of(self.stop["id"])
        if extra:
            views.blit_character(screen, self.host.x - ox, self.host.y - oy,
                                 extra.get("look", "nok"), "down", 0)
        self._draw_sight_marker(screen, ox, oy)
        pixel.add_glow(screen, (self.spawn.x - ox, self.spawn.y - oy),
                       6, (255, 216, 150), max_alpha=60)
        screen.fill((255, 216, 150),
                    pygame.Rect(int(self.spawn.x - ox) - 4, int(self.spawn.y - oy) - 1, 9, 3))
        views.blit_spirit(screen, self.player.x + 8 - ox,
                          self.player.y - 14 - oy, self.t)
        views.blit_character(screen, self.player.x - ox, self.player.y - oy,
                             "player", self.facing, self.walk_frame())
        self._draw_petals(screen, ox, oy)
        self._draw_fx(screen, ox, oy)
        views.atmosphere(screen, [], dark=44, tint=(96, 48, 32, 10))

        if self.prompt and self._modal is None and not self._panel_up():
            box = pygame.Rect(0, 0, pixel.text_size(self.prompt)[0] + 10, 14)
            box.center = (W // 2, H - 12)
            pixel.panel(screen, box, S.PANEL_BG, S.PANEL_BORDER)
            pixel.draw_text(screen, self.prompt, (box.x + 5, box.y + 3),
                            S.TEXT, shadow=None)

        self._draw_hud(screen)
        if self.panel is not None and self.panel.visible:
            self.panel.draw(screen)
        self.game.box.draw(screen)
        if self._fade > 0.0:
            fade = pygame.Surface((W, H))
            fade.set_alpha(int(255 * self._fade))
            fade.fill((8, 8, 14))
            screen.blit(fade, (0, 0))

    def _panel_up(self):
        return self.panel is not None and self.panel.visible

    def _draw_tablet(self, screen, ox, oy):
        x, y = self.tablet.x - ox, self.tablet.y - oy
        done = self.game.state.stop_done(self.stop["id"])
        locked = not self._spark_done()
        col = (120, 226, 120) if done else (S.SPIRIT if not locked else (110, 110, 130))
        if not locked or done:
            pixel.add_glow(screen, (x, y - 6), 9, col, max_alpha=80)
        screen.fill((60, 62, 92), pygame.Rect(int(x) - 5, int(y) - 12, 11, 9))
        screen.fill(col, pygame.Rect(int(x) - 5, int(y) - 12, 11, 1))
        screen.fill(col, pygame.Rect(int(x) - 5, int(y) - 4, 11, 1))
        pixel.draw_text(screen, "≡", (int(x) - 2, int(y) - 11), col, shadow=None)

    def _draw_sight_marker(self, screen, ox, oy):
        if self.game.state.stop_done(self.stop["id"]):
            return
        if self._meet_done() and not self._look_done():
            pos = self.sight
        elif self._look_done() and not self._spark_done():
            pos = self.spawn
        elif self._spark_done():
            pos = self.tablet
        else:
            pos = self.host
        x, y = pos.x - ox, pos.y - oy + int(3 * math.sin(self.t * 3))
        pixel.add_glow(screen, (x, y - 8), 6, (255, 240, 180), max_alpha=110)
        screen.fill((255, 246, 210), pygame.Rect(int(x), int(y) - 10, 2, 2))

    def _draw_petals(self, screen, ox, oy):
        for p in self.petals:
            c = (246, 216, 180) if p["hue"] == 0 else (158, 226, 168)
            a = max(0.0, min(1.0, p["life"] / p["max"]))
            px, py = int(p["x"]) - ox, int(p["y"]) - oy
            if 0 <= px < W - 1 and 0 <= py < H - 1:
                screen.fill((c[0], c[1], c[2], int(230 * a)),
                            pygame.Rect(px, py, 2, 2))

    def _draw_hud(self, screen):
        st = self.game.state
        label = "%s   PAGE %d/%d" % (ST.chapter(self.stop).upper()[:28],
                                     st.journal_count(), ST.TOTAL_STOPS)
        pixel.draw_text(screen, label, (5, 5), S.TEXT, shadow=None)
        pixel.draw_text(screen, "☆ " + self._objective(), (5, 15), S.AMBER, shadow=None)
