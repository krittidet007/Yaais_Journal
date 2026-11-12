"""The open world of the South — one big top-down peninsula.

The world is 240x320 tiles (3840x5120 px) but costs nothing to
draw, because ``tiles.draw_view`` only paints the tiles the camera
can see. The player walks, runs, and — the point of the journey —
**glides**: the spirit lifts you off the ground so you can float
across water to the islands. Forests still stop you; water does not.

Stops are pinned on the map. Press confirm beside one to play its
stop (dialogue -> local activity -> journal page). Collecting every
page and returning to Yaai's house unlocks the Wai Khru finale.
"""

import math
import random

import pygame

from .. import artgen as A
from .. import keymap
from .. import lighting
from .. import mouse
from .. import options as O
from .. import pixel
from .. import regions as RG
from .. import settings as S
from .. import story as ST
from .. import tablets as TB
from .. import tiles as T
from .. import weather as WX
from .. import views
from .. import world_map as WM

W, H = S.INTERNAL_W, S.INTERNAL_H
TILE = T.TILE

WALK = 74.0
RUN = 132.0
GLIDE = 196.0
SAIL = 210.0
REACH = 24.0
TOUCH = 22.0
DOCK_REACH = 30.0

# Danger mobs: they aggro on foot, chase, and catch you if they touch.
MOB_AGGRO = 82.0
MOB_LEASH = 300.0
MOB_CATCH = 15.0
MOB_COUNT = 18

# props are grouped into chunks of this many tiles for fast drawing
PROP_CHUNK = 16

# only the big things get a contact shadow (the little ones do not need one)
_SHADOWED = {"hut", "palm", "tree", "bigrock", "wat", "shophouse", "mangrove",
             "rubber", "spirit_house", "stilt", "well", "shrine", "stupa",
             "karst", "mosque", "lighthouse", "mountain", "ruin", "kiln",
             "puppet_stage", "banana", "rock"}

# Conversations never freeze you. Each dialogue is anchored to a place —
# the host's town, the sight, or wherever a voice on the wind found you.
# Walk out of earshot and it simply fades away. ``PINNED_KINDS`` are the
# story-critical beats that follow you instead (they cannot be walked
# away from), so the opening, the code lesson and the Wai Khru can't be
# lost by wandering off mid-sentence.
TALK_DRIFT = TILE * 11          # a memory / Lom's voice on the wind
SPOT_DRIFT = TILE * 8           # a host's welcome, a sight to look at
PINNED_KINDS = frozenset({"prologue", "tutorial", "finale_lines",
                           "finale_after"})

# keys that move you (usable even while someone is talking)
_MOVE_KEYS = frozenset({pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP,
                        pygame.K_DOWN, pygame.K_a, pygame.K_d,
                        pygame.K_w, pygame.K_s})

STOP_COLOR = {"province": (232, 96, 96), "secret": (244, 166, 188)}
HOME_COLOR = (255, 216, 150)


_landmark_art_cache = {}
_ai_prop_cache = {}


def _ai_asset(name):
    """A generated asset by name, if the AI pipeline produced one.

    The pipeline writes assets_ai/out/<name>.png. Anything the game asks
    for by that name is drawn instead of the code-drawn art, so a batch
    of generated Thai assets drops straight into the world.
    """
    if name in _ai_prop_cache:
        return _ai_prop_cache[name]
    art = None
    try:
        from .. import art_ai
        if art_ai.available(name):
            art = art_ai.get(name)
    except Exception:
        art = None
    _ai_prop_cache[name] = art
    return art


def _landmark_art(mark_id):
    """Generated art for a landmark, if the AI pipeline produced any.

    The pipeline writes assets_ai/out/<id>.png; when it is there the
    landmark wears it, and when it is not the code-drawn cairn is used.
    """
    return _ai_asset(mark_id)


class OverworldScene:
    name = "overworld"

    def __init__(self, game):
        self.game = game
        self.t = 0.0
        self.tm = WM.south_map()
        self.player = pygame.Vector2(*self._px(*ST.PROLOGUE["pos"]))
        self.facing = "up"
        self.keys = set()
        self._run = False
        self._glide = False
        self._sail = False
        self.speed = WALK
        self._steps = 0.0
        self.cam = views.Camera(
            max_x=WM.WORLD_COLS * TILE - W,
            max_y=WM.WORLD_ROWS * TILE - H)
        self.petals = []
        self._petal_age = 0.0
        self.prompt = ""
        self._near = None
        self._dock = None
        self._target = None
        self._return_pt = None
        self.box = game.box
        self._modal = None
        self._modal_stop = None
        self.panel = None
        self._tablet_stop = None
        self._tablet_role = "main"
        self._tablet_spec = None
        self._finale_stage = None
        self._finale_open = False
        self._pending_tablet = None
        self._greeted = set()
        self._music_mood = None
        self._music_t = 0.0
        self.noi_bark = None
        self._bark_cool = {}
        self._night_was = False
        self._sailed_before = False
        self._region_id = None
        self._region_tick = 0
        self._look = pygame.Vector2(0.0, 0.0)
        self._last_step_frame = -1
        self._road_t = 0.0
        self._face_from = self.facing
        self._face_timer = 0.0
        self._squash = 0.0
        self._was_glide = False
        self.weather = WX.Weather("gulf_shore")
        # landmarks: the places that make a province a place
        self.landmarks = WM.landmark_spots(self.tm)
        self.fx = []
        self.fish = None               # None | {"x","y","wait","bite"}
        self.storms = []
        self.sprites = []
        self._storm_surf = None
        self._seed_sky()
        self.docks = WM.dock_spots(self.tm)
        self.props, self.blocked = WM.scenery(self.tm)
        self._prop_chunks = WM.chunk_props(self.props)
        self.sparks = {stop["id"]: pygame.Vector2(*self._px(*WM.hidden_spot(self.tm, stop)))
                       for stop in ST.STOPS}
        # danger: Lom's magpies and the wild boar roam the land between
        # the towns. They hunt on foot; the water and the granite are
        # your escape. Getting caught costs you marks and wind.
        self.mobs = self._spawn_mobs()
        self._stun = 0.0               # frozen after being caught
        self._shake = 0.0              # screen-shake seconds left
        self._danger = None            # nearest chasing mob (for the HUD)

    # ---------------------------------------------------------------- setup
    @staticmethod
    def _px(col, row):
        """Tile (col,row) -> world px (tile centre)."""
        return col * TILE + TILE // 2, row * TILE + TILE // 2

    def on_enter(self):
        self.facing = "up"
        self.keys.clear()
        self.petals.clear()
        self.speed = WALK
        self._glide = False
        self._sail = False
        self._modal = None
        # no teleport: resume exactly where you stood, else Yaai's house
        pos = self.game.state.pos
        if (isinstance(pos, (list, tuple)) and len(pos) == 2
                and 8.0 <= pos[0] <= WM.WORLD_COLS * TILE - 8.0
                and 8.0 <= pos[1] <= WM.WORLD_ROWS * TILE - 8.0):
            self.player = pygame.Vector2(float(pos[0]), float(pos[1]))
        else:
            self.player = pygame.Vector2(*self._px(*ST.PROLOGUE["pos"]))
        self.cam.snap_to(self.player.x, self.player.y)
        self.game.box.hide()
        self._return_pt = None
        self._music_mood = None
        self._music_t = 0.0
        self._finale_stage = None
        self._finale_open = False
        self._pending_tablet = None
        self._stun = 0.0
        self._shake = 0.0
        self._danger = None
        self.panel = self.game.make_panel(self._on_run)
        if not self.game.state.stop_done("prologue"):
            self._show(self._lines(ST.PROLOGUE), kind="prologue")
        self._mark_visited("prologue")
        # back from the town's activity: the reward lines are waiting
        if getattr(self.game, "pending_reward", None):
            self.game.pending_reward = None
            pending = getattr(self, "_pending_bonus", None)
            if pending is not None:
                stop, bonus, extra_card = pending
                self._show(self._reward_lines(stop, bonus, extra_card))

    def _after_the_storm(self):
        """The storm is past; now Yaai's house, and the puppet."""
        self._show(self._lines(ST.PROLOGUE), kind="prologue")

    def save_pos(self):
        """Remember where you stand so the journey never teleports."""
        self.game.state.pos = [float(self.player.x), float(self.player.y)]

    def leave(self):
        """Scene lifecycle hook: snapshot the spot before hopping scenes."""
        self.save_pos()

    def _mark_visited(self, stop_id):
        if stop_id not in self.game.state.visited:
            self.game.state.visited.append(stop_id)

    # ---------------------------------------------------------------- input
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
        if ev.type == pygame.KEYDOWN and keymap.pressed("fish", ev):
            if self._modal is None and not self._sail:
                self._cast_or_reel()
            return
        if self._modal is not None:
            # you keep your feet while someone talks: movement keys flow
            # through, the story keys still steer the conversation
            if ev.type == pygame.KEYDOWN:
                if ev.key in _MOVE_KEYS:
                    self.keys.add(ev.key)
                if keymap.pressed("run", ev):
                    self._run = True
                if keymap.pressed("glide", ev):
                    self._glide = True
            elif ev.type == pygame.KEYUP:
                self.keys.discard(ev.key)
                if keymap.released("run", ev):
                    self._run = False
                if keymap.released("glide", ev):
                    self._glide = False
            if (ev.type == pygame.KEYDOWN and keymap.pressed("cancel", ev)) \
                    or mouse.cancelled(ev):
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

    # ---------------------------------------------------------------- update
    def update(self, dt):
        if isinstance(self.player, (list, tuple)) and len(self.player) == 2:
            self.player = pygame.Vector2(float(self.player[0]), float(self.player[1]))
        self.t += dt
        self.game.state.play_t += dt
        self._update_fx(dt)
        self._update_music(dt)
        self._stun = max(0.0, self._stun - dt)
        self._shake = max(0.0, self._shake - dt)
        self._face_timer = max(0.0, self._face_timer - dt)
        self._squash = max(0.0, self._squash - dt * 4.0)
        if self.panel is not None and self.panel.visible:
            self.panel.update(dt)
            return
        if self._modal is not None:
            # talking is not paralysis: walk, run, glide — and if you
            # wander out of earshot the conversation fades on its own
            self._drift_check()
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
        want_glide = self._glide or keymap.held("glide")
        st = self.game.state
        glide = want_glide and st.fuel > 0 and not self._sail
        if want_glide and st.fuel <= 0 and not self._sail:
            st.fuel = 0.0
        if glide:
            st.fuel = max(0.0, st.fuel - 12.0 * dt)
            self._was_glide = True
        elif getattr(self, "_was_glide", False):
            self._was_glide = False
            self._squash = 1.0          # the landing
        elif not self._sail:
            st.fuel = min(100.0, st.fuel + 20.0 * dt)
        if self._sail:
            target = SAIL
        else:
            target = GLIDE if glide else (RUN if run else WALK)
            if self._feet_on("S"):        # scrambling over granite is slow
                target *= 0.55
        self.speed += (target - self.speed) * min(1.0, dt * 6.0)

        if direction.length_squared() > 0 and self._stun <= 0.0:
            step = direction.normalize() * self.speed * dt
            self._move(step.x, step.y)
            new_face = self.facing
            if abs(direction.x) > abs(direction.y):
                new_face = "side"
            elif direction.y < 0:
                new_face = "up"
            else:
                new_face = "down"
            if new_face != self.facing:
                # a body takes a moment to turn: the sprite keeps the old
                # facing for a beat, which reads as weight
                if self._face_from != new_face:
                    self._face_from = new_face
                    self._face_timer = 0.11
            self.facing = new_face
            self._steps += dt * (self.speed / WALK)
            # the camera looks a little where you are going
            self._look.x += (direction.x * 30.0 - self._look.x) * min(1.0, dt * 3.0)
            self._look.y += (direction.y * 24.0 - self._look.y) * min(1.0, dt * 3.0)
            # a puff of dust on every footfall
            frame = int(self._steps * 8)
            if frame != self._last_step_frame:
                self._last_step_frame = frame
                self._dust(step)
            if glide:
                self._emit_petals(direction.normalize())
        else:
            self._steps = 0.0
            self._look.x += (0.0 - self._look.x) * min(1.0, dt * 3.0)
            self._look.y += (0.0 - self._look.y) * min(1.0, dt * 3.0)
        self._update_petals(dt)
        self._update_sky(dt)
        self._update_fish(dt)
        self._update_barks(dt)
        self._update_mobs(dt)
        self._near = self._nearest_stop()
        self._dock = self._nearest_dock()
        self._target = self._compass_target()
        self.prompt = self._prompt()
        self.weather.set_region(self._region())
        self.weather.update(dt, self.player.x, self.player.y)
        self._check_road(dt)
        self._check_sparks()
        self._check_landmarks()
        self._check_greeting()
        self._check_act()
        self.cam.follow(self.player.x + self._look.x,
                        self.player.y + self._look.y, dt)

    def _dust(self, step):
        """A small puff where the foot lands — sells the weight of a step."""
        for _i in range(2):
            self.petals.append({
                "x": self.player.x + (4 if step.x >= 0 else -6),
                "y": self.player.y + 10,
                "vx": (step.x / 8.0) + (1 if step.x >= 0 else -1) * 6.0,
                "vy": -6.0 - (2 if step.y < 0 else 0),
                "life": 0.28, "max": 0.28, "hue": 2,
            })

    def _check_act(self):
        """Lom speaks on the wind each time the journey crosses an act."""
        st = self.game.state
        act = st.act_of()
        if act <= st.act_seen:
            return
        if act == 1 and "prologue_done" not in st.flags:
            return                      # the opening beat waits for the prologue
        plot = ST.PLOT.get(act)
        if plot:
            if self._modal is None:
                st.act_seen = act
                self._modal_stop = None
                self._show(list(plot), kind="talk")
            # else: a story is already playing — the act waits its turn
            return
        st.act_seen = act

    def _tile_at(self, x, y):
        c = int(x) // TILE
        r = int(y) // TILE
        return self.tm.cell(r, c)

    def _feet_on(self, kind):
        if isinstance(self.player, (list, tuple)) and len(self.player) == 2:
            self.player = pygame.Vector2(float(self.player[0]), float(self.player[1]))
        return (self._tile_at(self.player.x + 4, self.player.y + 10) == kind
                or self._tile_at(self.player.x + 12, self.player.y + 10) == kind)

    def _ok(self, x, y):
        """Walkable here. Gliding floats over water; sailing stays on it;
        forest always stops — and so do walls, trees and houses."""
        c = int(x) // TILE
        r = int(y) // TILE
        cell = self.tm.cell(r, c)
        if cell is None:
            return False
        if (c, r) in self.blocked:
            return False                    # houses and trees stop everyone
        if self._sail:
            return cell == "W"
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
        self.player.x = max(8.0, min(WM.WORLD_COLS * TILE - 8.0, self.player.x))
        self.player.y = max(8.0, min(WM.WORLD_ROWS * TILE - 8.0, self.player.y))

    def walk_frame(self):
        """A full four-frame cycle — the sprites are drawn for four poses,
        so use them all instead of alternating between two."""
        return int(self._steps * 8) % 4 if self._steps else 0

    # ------------------------------------------------------------ danger mobs
    # Lom's magpies and the wild boar. They hunt on foot, so the water
    # is your escape — glide, or hold SHIFT and run. Catch you, and they
    # take a mark of Respect and a lungful of Wind.
    def _pin_tiles(self):
        return [ST.PROLOGUE["pos"]] + [s["pos"] for s in ST.STOPS]

    def _mob_walkable(self, x, y):
        """Mobs only tread open land: not water, not forest, not granite."""
        c, r = int(x) // TILE, int(y) // TILE
        return self.tm.cell(r, c) in ("G", "A", "D")

    def _spawn_mobs(self):
        rng = random.Random(9091)
        pins = self._pin_tiles()
        mobs = []
        tries = 0
        while len(mobs) < MOB_COUNT and tries < 6000:
            tries += 1
            c = rng.randrange(20, WM.WORLD_COLS - 20)
            r = rng.randrange(20, WM.WORLD_ROWS - 20)
            x, y = c * TILE + 8.0, r * TILE + 8.0
            if not self._mob_walkable(x, y):
                continue
            if any(abs(c - pc) < 10 and abs(r - pr) < 10 for pc, pr in pins):
                continue
            fast = rng.random() < 0.55
            mobs.append({
                "kind": "magpie" if fast else "boar",
                "x": x, "y": y, "hx": x, "hy": y, "tx": x, "ty": y,
                "patrol": 34.0 if fast else 22.0,
                "chase": 106.0 if fast else 84.0,
                "state": "idle", "phase": rng.random() * 6.28,
            })
        return mobs

    def _mob_step(self, m, dx, dy):
        if self._mob_walkable(m["x"] + dx, m["y"]):
            m["x"] += dx
        if self._mob_walkable(m["x"], m["y"] + dy):
            m["y"] += dy

    def _update_mobs(self, dt):
        danger, near = None, 1e9
        for m in self.mobs:
            dx, dy = self.player.x - m["x"], self.player.y - m["y"]
            d = math.hypot(dx, dy)
            if d < MOB_AGGRO:
                m["state"] = "chase"
            elif d > MOB_LEASH or (m["state"] == "chase" and d > MOB_AGGRO * 1.6):
                m["state"] = "idle"
            if m["state"] == "chase":
                tx, ty, speed = self.player.x, self.player.y, m["chase"]
                if d < near:
                    near, danger = d, m
            else:
                if math.hypot(m["tx"] - m["x"], m["ty"] - m["y"]) < 6.0:
                    a = m["phase"] + self.t * 0.5
                    m["tx"] = m["hx"] + math.cos(a) * 34.0
                    m["ty"] = m["hy"] + math.sin(a * 1.3) * 34.0
                tx, ty, speed = m["tx"], m["ty"], m["patrol"]
            vx, vy = tx - m["x"], ty - m["y"]
            ln = math.hypot(vx, vy)
            if ln > 0.01:
                self._mob_step(m, vx / ln * speed * dt, vy / ln * speed * dt)
            m["phase"] += dt * 2.0
            if d < MOB_CATCH and self._stun <= 0.0:
                self._caught(m, dx, dy)
        self._danger = danger

    def _caught(self, m, dx, dy):
        st = self.game.state
        st.caught += 1
        st.combo = 0
        st.fuel = max(0.0, st.fuel - 30.0)
        took = st.respect > 0
        if took:
            st.respect -= 1
        self._shake = 0.7
        self._stun = 1.1
        ln = math.hypot(dx, dy) or 1.0
        for _ in range(30):                    # shove the player clear
            px, py = self.player.x + dx / ln * 3.0, self.player.y + dy / ln * 3.0
            if not self._feet_ok(px, py):
                break
            self.player.x, self.player.y = px, py
        m["state"] = "idle"
        self._burst(self.player.x, self.player.y, 14)
        if st.caught == 1:
            self._show([
                ("NOI", "NOI", "%s had you! It took %s." % (
                    "A magpie" if m["kind"] == "magpie" else "A boar",
                    "one of your marks of Respect" if took else "a lungful of Wind")),
                ("NOI", "NOI", "They hunt on foot. Hold SHIFT to RUN, or press X to GLIDE over the water — they will not follow you into the sea."),
            ])
        else:
            self._bark("Run! SHIFT to sprint, X to glide to the water!", ttl=2.6)

    # ------------------------------------------------------------ glide trail
    def _emit_petals(self, d):
        p = self.player
        for i in range(2):
            jitter = (self._petal_age * 1.7 + i * 3.1) % (2 * math.pi)
            self.petals.append({
                "x": p.x + 8.0 - d.x * (8 + i * 5) + math.cos(jitter) * 3,
                "y": p.y + 4.0 - d.y * (8 + i * 5) + math.sin(jitter) * 2,
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
            if p["hue"] == 2:
                c = (198, 190, 176)          # footfall dust
            else:
                c = (246, 216, 180) if p["hue"] == 0 else (158, 226, 168)
            a = max(0.0, min(1.0, p["life"] / p["max"]))
            px, py = int(p["x"]) - ox, int(p["y"]) - oy
            if 0 <= px < W - 1 and 0 <= py < H - 1:
                screen.fill((c[0], c[1], c[2], int(230 * a)),
                            pygame.Rect(px, py, 2, 2))

    def _sheltered(self):
        """Under a town's eaves: storms cannot take you here."""
        for stop in ST.STOPS + [ST.PROLOGUE]:
            c, r = stop["pos"]
            if self.player.distance_to(pygame.Vector2(*self._px(c, r))) < 70.0:
                return True
        return False

    def _update_sky(self, dt):
        from .. import audio
        ww, wh = WM.WORLD_COLS * TILE, WM.WORLD_ROWS * TILE
        sheltered = self._sheltered()
        for s in self.storms:
            s["x"] = (s["x"] + s["vx"] * dt) % ww
            s["y"] = (s["y"] + s["vy"] * dt) % wh
            d = self.player.distance_to(pygame.Vector2(s["x"], s["y"]))
            if d < s["r"] and not sheltered and self._modal is None:
                away = self.player - pygame.Vector2(s["x"], s["y"])
                if away.length_squared() < 1.0:
                    away = pygame.Vector2(1, 0)
                push = away.normalize() * 150.0 * dt
                nx, ny = self.player.x + push.x, self.player.y + push.y
                self.player.x = max(8.0, min(ww - 8.0, nx))
                self.player.y = max(8.0, min(wh - 8.0, ny))
                self._burst(self.player.x, self.player.y, 2)
                audio.sfx("splash")
        for sp in self.sprites:
            sp["ph"] += dt * 2.2
            sp["cool"] = max(0.0, sp["cool"] - dt)
            to_me = self.player - pygame.Vector2(sp["x"], sp["y"])
            d = to_me.length()
            vx = math.cos(sp["ph"]) * 24 + math.cos(sp["ph"] * 0.6) * 14
            vy = math.sin(sp["ph"] * 1.3) * 24
            if d < 220 and d > 1.0 and self._modal is None:
                vx += (to_me.x / d) * 46
                vy += (to_me.y / d) * 46
            sp["x"] = max(8.0, min(ww - 8.0, sp["x"] + vx * dt))
            sp["y"] = max(8.0, min(wh - 8.0, sp["y"] + vy * dt))
            if d < 13 and sp["cool"] <= 0.0 and self._modal is None:
                sp["cool"] = 2.0
                if d > 1.0:
                    shove = (to_me / d) * 42.0
                    self.player.x = max(8.0, min(ww - 8.0, self.player.x + shove.x))
                    self.player.y = max(8.0, min(wh - 8.0, self.player.y + shove.y))
                self._burst(self.player.x, self.player.y, 8)
                audio.sfx("blip")

    def _update_music(self, dt):
        """The soundtrack follows the moment: festivals, sailing, night."""
        from .. import audio
        self._music_t += dt
        if self._music_t < 0.5:
            return
        self._music_t = 0.0
        if any(f["kind"] == "festival" for f in self.fx):
            mood = "festival"
        elif self._sail:
            mood = "sail"
        elif self._night() >= 0.5:
            mood = "night"
        else:
            mood = None
        if mood != self._music_mood:
            self._music_mood = mood
            audio.set_mood(mood)

    # ------------------------------------------------------------- companion
    def _bark_ready(self, key, cool=20.0):
        left = self._bark_cool.get(key, 0.0)
        if left <= 0.0:
            self._bark_cool[key] = cool
            return True
        return False

    def _update_barks(self, dt):
        if self.noi_bark is not None:
            self.noi_bark["t"] += dt
            if self.noi_bark["t"] > self.noi_bark["ttl"]:
                self.noi_bark = None
        for key in list(self._bark_cool):
            self._bark_cool[key] = max(0.0, self._bark_cool[key] - dt)
        if self._modal is not None or not self.game.state.stop_done("prologue"):
            return
        night = self._night() >= 0.5
        if night and not self._night_was and self._bark_ready("night", 60.0):
            self._bark("Lamps out! Stay close.", ttl=3.5)
        self._night_was = night
        if self.game.state.fuel < 25.0 and self._bark_ready("fuel", 30.0):
            self._bark("Wind's thin! Find a spark!")
        if self._sail and not self._sailed_before:
            self._sailed_before = True
            self._bark("Wheee! ...I mean. Steady.", ttl=3.5)
        nearest_storm = min(
            (self.player.distance_to(pygame.Vector2(s["x"], s["y"]))
             for s in self.storms), default=9999.0)
        if nearest_storm < 170.0 and self._bark_ready("storm", 25.0):
            self._bark("Storm! To town, quick!")

    def _night(self):
        """0.0 at noon, 1.0 at midnight (4-minute days)."""
        phase = (self.game.state.play_t % 240.0) / 240.0
        if phase < 0.50:
            return 0.0
        if phase < 0.60:
            return (phase - 0.50) * 10.0
        if phase < 0.90:
            return 1.0
        return max(0.0, (1.0 - phase) * 10.0)

    # ----------------------------------------------------------------- fishing
    def _cast_or_reel(self):
        from .. import audio
        if self.fish is not None:
            if self.fish.get("bite", 0.0) > 0.0:
                self._catch()
            else:
                self.fish = None       # reeled in early, no harm
            return
        if self._dock is None:
            return
        import random
        c, r = self._dock["pos"]
        self.fish = {"x": c * TILE + TILE // 2.0, "y": r * TILE + TILE // 2.0,
                     "wait": 2.0 + random.Random().random() * 3.0, "bite": 0.0}

    def _fish_pool(self):
        rfrac = self.player.y / (WM.WORLD_ROWS * TILE)
        if rfrac > 0.75:
            pool = ST.FISH["south"]
        elif self.player.x > WM.WORLD_COLS * TILE / 2.0:
            pool = ST.FISH["gulf"]
        else:
            pool = ST.FISH["andaman"]
        if self._night() < 0.5:
            pool = [f for f in pool if f not in ST.NIGHT_FISH] or pool
        return pool

    def _update_fish(self, dt):
        from .. import audio
        if self.fish is None:
            return
        # wander off and the line snaps
        if self.player.distance_to(pygame.Vector2(self.fish["x"], self.fish["y"])) > 70.0:
            self.fish = None
            return
        if self.fish["bite"] > 0.0:
            self.fish["bite"] -= dt
            if self.fish["bite"] <= 0.0:
                self.fish = None
                audio.sfx("splash")    # ...it slipped away
            return
        self.fish["wait"] -= dt
        if self.fish["wait"] <= 0.0:
            self.fish["bite"] = 1.4
            audio.sfx("splash")

    def _catch(self):
        from .. import audio
        import random
        pool = self._fish_pool()
        fish = pool[random.Random().randrange(len(pool))]
        self.game.state.catches.append(fish)
        self.fish = None
        audio.sfx("collect")
        self._show([("NOI", "NOI", "Oroi! Caught a %s!" % fish),
                    ("NOI", "NOI", "The journal's catch log grows. Press J to admire it.")])

    # ------------------------------------------------------------- the stops
    def _nearest_stop(self):
        best, best_d = None, REACH
        for stop in ST.STOPS:
            c, r = stop["pos"]
            pos = pygame.Vector2(*self._px(c, r))
            d = self.player.distance_to(pos)
            if d < best_d:
                best, best_d = stop, d
        pc, pr = ST.PROLOGUE["pos"]
        d = self.player.distance_to(pygame.Vector2(*self._px(pc, pr)))
        if d < best_d:
            best = ST.PROLOGUE
        return best

    def _nearest_dock(self):
        best, best_d = None, DOCK_REACH
        for dock in self.docks:
            c, r = dock["pos"]
            pos = pygame.Vector2(*self._px(c, r))
            d = self.player.distance_to(pos)
            if d < best_d:
                best, best_d = dock, d
        return best

    def _compass_target(self):
        """The nearest stop whose page is still missing — or home, when
        the journal is full and the Wai Khru waits."""
        if self.game.state.journey_done():
            return ST.PROLOGUE
        best, best_d = None, None
        for stop in ST.STOPS:
            if self.game.state.stop_done(stop["id"]):
                continue
            c, r = stop["pos"]
            d = self.player.distance_to(pygame.Vector2(*self._px(c, r)))
            if best_d is None or d < best_d:
                best, best_d = stop, d
        return best

    def _check_sparks(self):
        """Step on a hidden page-spark and Noi pockets it: +1 Respect,
        and every sixth spark warms the Spice Meter too."""
        st = self.game.state
        for stop_id, pos in self.sparks.items():
            if stop_id in st.found:
                continue
            if self.player.distance_to(pos) < 10.0:
                st.found.append(stop_id)
                st.bump_respect(1)
                st.fuel = min(100.0, st.fuel + 25.0)
                st.noi_rank = len(st.found)
                st.quests[stop_id] = max(st.quests.get(stop_id, 0), 3)
                if len(st.found) % 6 == 0:
                    st.bump_spice(1)
                extra = ST.extra_of(stop_id)
                lines = [("NOI", "NOI", "Oroi! A hidden spark!"),
                         ("NOI", "NOI", extra.get(
                             "found", "A scrap of the lost page."))]
                lines += list(ST.scene_of(stop_id, "spark"))
                self._show(lines)
                return

    def _shore_near(self, radius=26.0):
        px, py = int(self.player.x), int(self.player.y)
        steps = int(radius) // 4
        for dy in range(-steps, steps + 1):
            for dx in range(-steps, steps + 1):
                x, y = px + dx * 4, py + dy * 4
                if math.hypot(dx * 4, dy * 4) > radius:
                    continue
                cell = self._tile_at(x, y)
                if cell is not None and cell not in ("W", "H"):
                    return True
        return False

    def _tablet_px(self, stop):
        c, r = stop["pos"]
        return pygame.Vector2(*self._px(c, r))

    def _host_px(self, stop):
        c, r = stop["pos"]
        ph = float(hash(stop["id"]) % 10)
        wx = 26 + math.sin(self.t * 0.4 + ph) * 8.0
        wy = 4 + math.cos(self.t * 0.33 + ph) * 6.0
        return pygame.Vector2(c * TILE + TILE // 2 + wx, r * TILE + TILE // 2 + wy)

    def _sight_px(self, stop):
        c, r = stop["pos"]
        sight = ST.extra_of(stop["id"]).get("sight", {})
        return pygame.Vector2(c * TILE + TILE // 2 + sight.get("dx", 0) * TILE,
                              r * TILE + TILE // 2 + sight.get("dy", 0) * TILE)

    def _near_what(self):
        """The tablet, host or sight the player can touch."""
        best, best_d, what = None, TOUCH + 8, None
        for stop in ST.STOPS:
            t_dist = self.player.distance_to(self._tablet_px(stop))
            h_dist = self.player.distance_to(self._host_px(stop))
            s_dist = self.player.distance_to(self._sight_px(stop))
            if t_dist < best_d and t_dist <= h_dist and t_dist <= s_dist:
                best, best_d, what = stop, t_dist, "tablet"
            elif h_dist < best_d and h_dist <= s_dist:
                best, best_d, what = stop, h_dist, "host"
            elif s_dist < best_d:
                best, best_d, what = stop, s_dist, "sight"
        return what, best

    def _check_greeting(self):
        """First arrival at an unsolved town: the host's welcome story."""
        if self._modal is not None or self._near is None:
            return
        if self._near is ST.PROLOGUE:
            return
        stop_id = self._near["id"]
        st = self.game.state
        if st.stop_done(stop_id) or st.quests.get(stop_id, 0) > 0:
            return
        if stop_id in self._greeted:
            return
        self._greeted.add(stop_id)
        lines = list(self._near["lines"]) + list(ST.scene_of(stop_id, "arrive"))
        self._show(lines, kind="greeting", stop_id=stop_id)

    def _prompt(self):
        if not O.options.prompts_on():
            return ""
        if self._modal is not None:
            return ""
        act = keymap.label("confirm")
        if self._sail:
            if self._shore_near():
                return "%s  step ashore" % act
            return "sail on, little flame"
        if self._near is None and self._dock is not None:
            fkey = keymap.label("fish")
            return "%s  board the boat   %s fish" % (act, fkey)
        what, touch = self._near_what()
        if what == "tablet":
            if self._beats(touch["id"]) < 3:
                return "%s  the tablet waits — %s" % (act, self._beat_text(touch)[0].lower())
            spec = ST.code_of(touch["id"])
            title = spec["title"] if spec else "RUNES"
            return "%s  read the %s tablet" % (act, title)
        if what == "host":
            extra = ST.extra_of(touch["id"])
            return "%s  talk to %s" % (act, extra.get("host", "local"))
        if what == "sight":
            label = ST.extra_of(touch["id"]).get("sight", {}).get("label", "the sight")
            return "%s  look at %s" % (act, label)
        if self._near is None:
            return ""
        if self._near is ST.PROLOGUE:
            if self.game.state.journey_done():
                return "%s  the Wai Khru (return home)" % act
            return "%s  Yaai's house" % act
        return "%s  %s" % (act, self._near.get("title", self._near.get("name", "home")))

    def _interact(self):
        if self._sail:
            self._dismount()
            return
        if self._near is None and self._dock is not None:
            self._sail = True
            self._glide = False
            return
        near = self._near
        if near is None and self._dock is None:
            what, touch = self._near_what()
            if what == "host":
                self._show(self._host_lines(touch), stop_id=touch["id"])
            elif what == "sight":
                extra = ST.extra_of(touch["id"])
                self._show([("NOI", "NOI", extra.get("sight", {}).get(
                    "text", "Look well. Remember it."))],
                    kind="sight", stop_id=touch["id"])
            elif what == "tablet":
                self._open_tablet(touch)
            return
        if near is None:
            return
        if near is ST.PROLOGUE:
            if self.game.state.journey_done():
                stage = getattr(self, "_finale_stage", None)
                if stage is None:
                    self._start_finale()
                elif stage == "tablet" and not self.panel.visible:
                    self._open_finale_tablet()
                return
            self._show(self._lines(ST.PROLOGUE), kind="prologue")
            return
        what, touch = self._near_what()
        if what == "host":
            self._show(self._host_lines(touch), stop_id=touch["id"])
            return
        if what == "sight":
            extra = ST.extra_of(touch["id"])
            self._show([("NOI", "NOI", extra.get("sight", {}).get(
                "text", "Look well. Remember it."))],
                kind="sight", stop_id=touch["id"])
            return
        self._open_tablet(touch or near)

    def _tablet_specs(self, stop):
        """The spell on the tablet: 'main', 'accuse' (a forged page whose
        first solve exposes the lie) or 'truth' (the follow-up spell)."""
        spec = ST.code_of(stop["id"])
        forg = (spec or {}).get("forgery")
        flags = self.game.state.flags
        if forg and "%s_truth" % stop["id"] not in flags:
            if "%s_accused" % stop["id"] not in flags:
                return spec, "accuse"
            return forg, "truth"
        return spec, "main"

    def _beat_text(self, stop):
        """What the current beat asks, and how to do it."""
        st = self.game.state
        extra = ST.extra_of(stop["id"])
        host = extra.get("host", "local")
        label = extra.get("sight", {}).get("label", "the sight")
        spec = ST.code_of(stop["id"])
        title = spec["title"] if spec else "RUNES"
        beats = self._beats(stop["id"])
        if beats < 1:
            return ("Hear the welcome", "stand by %s and listen" % host)
        if beats < 2:
            return ("Look at %s" % label, "walk to the glint, press %s" % keymap.label("confirm"))
        if beats < 3:
            return ("Find the hidden spark", "ask %s for the hint, then search" % host)
        return ("Solve the %s tablet" % title, "type the spell, Ctrl+Enter to run")

    def _open_tablet(self, stop):
        if self._beats(stop["id"]) < 3:
            self._show([("NOI", "NOI", "Not yet — %s." % self._beat_text(stop)[0].lower())])
            return
        st = self.game.state
        if "code_tutorial" not in st.flags:
            # never wrote a line of code? Noi teaches the three shapes first
            st.flags.append("code_tutorial")
            self._pending_tablet = stop
            self._show(list(ST.CODE_TUTORIAL), kind="tutorial")
            return
        spec, role = self._tablet_specs(stop)
        if spec is None:
            return
        self._tablet_stop = stop
        self._tablet_role = role
        self._tablet_spec = spec
        title = spec["title"]
        status = spec.get("status", "")
        if spec.get("broken"):
            title = "BROKEN " + title
            status = "BROKEN SPELL! " + spec["broken"] + "\n" + status
        self.panel.open(title, spec.get("prefill", ""), status,
                        teach=spec.get("teach") or spec.get("hint", ""))

    def _side_quest_for(self, stop_id):
        """The side quest this host can give, if any."""
        from .. import sidequests as SQ
        for qid, quest in SQ.SIDE_QUESTS.items():
            if quest["from"] == stop_id:
                return qid, quest
        return None, None

    def _side_quest_state(self, qid):
        """'none' | 'given' | 'ready' | 'done'."""
        st = self.game.state
        if "sq_%s_done" % qid in st.flags:
            return "done"
        if "sq_%s_ready" % qid in st.flags:
            return "ready"
        if "sq_%s_given" % qid in st.flags:
            return "given"
        return "none"

    def _host_lines(self, stop):
        """Chatting with the local character in their own town."""
        extra = ST.extra_of(stop["id"])
        host = extra.get("host", "Local")
        accent = ST.HOST_ACCENT.get(extra.get("look", "nok"), "NOK")
        lines = []
        if stop["id"] in self.game.state.failed and not self.game.state.stop_done(stop["id"]):
            lines.append((host, accent, "Back again? Good. The tablet remembers you too."))
        lines.extend((host, accent, text) for text in extra.get("lines", []))
        # once the town's page is yours, the host has more to say — the
        # things they could not tell a stranger
        if self.game.state.stop_done(stop["id"]):
            lines.extend((host, accent, text) for text in extra.get("later", []))
            # and one errand: the landmark in this district, to be walked
            # to and stood at. It is offered once.
            errand = extra.get("errand")
            flag = "errand_%s" % stop["id"]
            if errand and flag not in self.game.state.flags:
                lines.append((host, accent, errand))
                self.game.state.flags.append(flag)
            # and a side quest, once the errand is answered: something
            # only this person can ask you, with somewhere to go
            qid, quest = self._side_quest_for(stop["id"])
            if quest is not None:
                state = self._side_quest_state(qid)
                if state == "none":
                    lines.append((host, accent, quest["ask"]))
                    self.game.state.flags.append("sq_%s_given" % qid)
                elif state == "ready":
                    reward = quest.get("reward", {})
                    self.game.state.bump_respect(int(reward.get("respect", 1)))
                    if reward.get("card"):
                        self.game.state.add_card(reward["card"])
                    self.game.state.flags.append("sq_%s_done" % qid)
                    self.game.state.flags.remove("sq_%s_ready" % qid)
                    lines.append((host, accent, quest["answer"]))
                    lines.append(("NOI", "NOI", "Oroi! One errand done. "
                                  "The South counts these, not the "
                                  "tablets."))
        if stop["id"] not in self.game.state.found and extra.get("hint"):
            lines.append(("NOI", "NOI", extra["hint"]))
        return lines or self._lines(stop, replay=True)

    def _start_finale(self):
        """The Wai Khru, at home: no scene change, the ceremony comes here."""
        from .. import audio
        audio.set_mood("finale")
        self._finale_stage = "lines"
        # the cup at the pass comes first, as a scene rather than a page
        self.game.cutscene_id = "the_cup"
        self.game.cutscene_return = "overworld"
        self.game.cutscene_finished = self._after_the_cup
        self.game.switch("cutscene")

    def _after_the_cup(self):
        """The cutscene ends; the ceremony itself begins."""
        self._show(list(ST.FINALE["lines"]), kind="finale_lines")

    def _open_finale_tablet(self):
        self._finale_stage = "tablet"
        self._finale_open = True
        spec = ST.FINALE["code"]
        title = spec["title"]
        status = spec.get("status", "")
        if spec.get("broken"):
            title = "BROKEN " + title
            status = "BROKEN SPELL! " + spec["broken"] + "\n" + status
        self.panel.open(title, spec.get("prefill", ""), status,
                        teach=spec.get("hint", ""))

    # ------------------------------------------------------------------ tablet
    def _on_run(self, code):
        from .. import audio
        if getattr(self, "_finale_open", False):
            ok, console, status = TB.validate(ST.FINALE["code"], code)
            self.panel.set_console(console)
            self.panel.set_status(status, S.MUTED)
            if ok:
                audio.sfx("success")
                self.panel.close()
                self.game.box.hide()
                self.game.state.finale_done = True
                self._finale_open = False
                self._finale_stage = "after"
                for _i in range(3):
                    self._burst(self.player.x, self.player.y, 20)
                self._show(list(ST.FINALE.get("after", [])), kind="finale_after")
            else:
                audio.sfx("error")
            return
        stop = getattr(self, "_tablet_stop", None)
        spec = getattr(self, "_tablet_spec", None)
        if stop is None or spec is None:
            return
        role = getattr(self, "_tablet_role", "main")
        ok, console, status = TB.validate(spec, code)
        self.panel.set_console(console)
        self.panel.set_status(status, S.MUTED)
        if not ok:
            st = self.game.state
            st.combo = 0
            if stop["id"] not in st.failed:
                st.failed.append(stop["id"])
            audio.sfx("error")
            return
        if role == "accuse":
            audio.sfx("blip")
            self.panel.close()
            self.game.box.hide()
            self.game.state.flags.append("%s_accused" % stop["id"])
            forg = ST.code_of(stop["id"])["forgery"]
            self._show(list(forg["accuse"]))
            return
        audio.sfx("success")
        self.panel.close()
        self.game.box.hide()
        st = self.game.state
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
        self._spawn_fx(stop)
        # the code was only half of it: now the town's own activity —
        # matching boats, catching a sunrise, pulling a rope, following a
        # turtle — before the page is yours
        self._pending_bonus = (stop, bonus, extra_card)
        self.game.next_stop = stop["id"]
        self.game.pending_activity = stop["id"]
        self.game.switch("stop")

    def _reward_lines(self, stop, bonus="", extra_card=None):
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

    def _dismount(self):
        """Step ashore onto the nearest tile you can actually stand on."""
        best, best_d = None, 26.0
        px, py = int(self.player.x), int(self.player.y)
        for dy in range(-24, 25, 4):
            for dx in range(-24, 25, 4):
                x, y = px + dx, py + dy
                if math.hypot(dx, dy) > best_d:
                    continue
                if (self._tile_ok(x + 4, y + 10)
                        and self._tile_ok(x + 12, y + 10)):
                    best, best_d = (x, y), math.hypot(dx, dy)
        if best is not None:
            self.player = pygame.Vector2(*best)
            self._sail = False

    def _tile_ok(self, x, y):
        c, r = int(x) // TILE, int(y) // TILE
        cell = self.tm.cell(r, c)
        return cell is not None and cell not in ("W", "H")

    def _lines(self, stop, replay=False):
        """Dialogue for a stop, with Noi's line about the page."""
        lines = list(stop["lines"])
        if stop is not ST.PROLOGUE and not replay:
            if stop.get("call"):
                lines.append(("YAAI", "YAAI", stop["call"]))
        return lines

    # ---------------------------------------------------------------- modal
    def _dialogue_anchor(self, kind, stop_id):
        """Where a conversation lives, and how far it carries.

        Returns ``(anchor, drift)``; anchor ``None`` means the dialogue
        is pinned to the player and never fades with distance.
        """
        if kind in PINNED_KINDS:
            return None, 0.0
        if stop_id is not None:
            stop = ST.STOP_BY_ID.get(stop_id)
            if stop is not None:
                return pygame.Vector2(*self._px(*stop["pos"])), SPOT_DRIFT
        return pygame.Vector2(self.player.x, self.player.y), TALK_DRIFT

    def _show(self, lines, kind="talk", stop_id=None):
        if self._modal is not None:
            # a more urgent voice (a catch, a found spark) interrupts the
            # one playing: settle its bookkeeping so quest beats are never
            # lost, but don't chain follow-ups on top of the interruption
            self._close_modal(interrupt=True)
        # The box holds three wrapped lines; split anything longer into
        # as many spoken beats as it needs, so no plot line is ever cut.
        width = self.game.box.rect.width - 16
        out = []
        for speaker, accent, text in lines:
            wrapped = pixel.wrap(text, width) or [""]
            for i in range(0, len(wrapped), 3):
                out.append((speaker, accent, " ".join(wrapped[i:i + 3])))
        prepared = [(self.game.state.display_spirit_name() if s == "SPIRIT" else s, a, t)
                    for s, a, t in out]
        anchor, drift = self._dialogue_anchor(kind, stop_id)
        self._modal_stop = stop_id
        self._modal = {"lines": prepared, "index": -1, "kind": kind,
                       "stop_id": stop_id, "anchor": anchor, "drift": drift}
        self._advance_modal()

    def _drift_check(self):
        """Out of earshot, the conversation simply fades away."""
        modal = self._modal
        if modal is None:
            return
        anchor = modal.get("anchor")
        drift = modal.get("drift") or 0.0
        if anchor is None or drift <= 0.0:
            return
        if self.player.distance_to(anchor) > drift:
            self._close_modal()
            self._bark("...too far away to hear.", ttl=2.2)

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

    def _close_modal(self, interrupt=False):
        modal = self._modal or {}
        kind = modal.get("kind")
        stop_id = modal.get("stop_id")
        self._modal = None
        self._modal_stop = None
        self.game.box.hide()
        st = self.game.state
        # however the conversation ends, the town remembers you heard it
        if kind == "greeting" and stop_id:
            st.quests[stop_id] = max(st.quests.get(stop_id, 0), 1)
        if kind == "sight" and stop_id:
            st.quests[stop_id] = max(st.quests.get(stop_id, 0), 2)
        if kind == "prologue" and "prologue_done" not in st.flags:
            st.flags.append("prologue_done")
        if interrupt:
            return                      # something else is speaking already
        if kind == "sight" and stop_id:
            # the plot turns every time you look: what did Lom touch here?
            # (a narrated memory — it drifts along with you)
            scene = ST.scene_of(stop_id, "mid")
            if scene:
                self._show(list(scene), kind="plot")
        elif kind == "finale_lines":
            self._open_finale_tablet()
        elif kind == "tutorial":
            pending = getattr(self, "_pending_tablet", None)
            self._pending_tablet = None
            if pending is not None:
                self._open_tablet(pending)
        elif kind == "finale_after":
            self.game.finish_region()

    def _beats(self, stop_id):
        if self.game.state.stop_done(stop_id):
            return 3
        return self.game.state.quests.get(stop_id, 0)

    def _height_at(self, px, py):
        """How high the ground is here (terraces stand above the fields)."""
        cell = self.tm.cell(int(py) // TILE, int(px) // TILE)
        return T.HEIGHTS.get(cell, 0)

    # ------------------------------------------------------------------ region
    def _region(self):
        """Which part of the South the player is standing in (cheap lookup,
        refreshed a couple of times a second)."""
        self._region_tick += 1
        if self._region_id is None or self._region_tick > 30:
            self._region_tick = 0
            self._region_id = RG.region_for_position(
                self.player.x, self.player.y, ST.STOPS, TILE)
        return self._region_id

    def _draw_region_banner(self, screen, region):
        """When you cross into a new part of the South, say where you are."""
        if region != getattr(self, "_banner_region", None):
            self._banner_region = region
            self._banner_t = 4.0
        if getattr(self, "_banner_t", 0.0) <= 0.0:
            return
        self._banner_t = max(0.0, self._banner_t - 0.016)
        name = RG.region_name(region).upper()
        w = pixel.text_size(name)[0] + 24
        box = pygame.Rect((W - w) // 2, 26, w, 18)
        pixel.panel(screen, box, S.PANEL_BG, S.PANEL_BORDER)
        pixel.draw_text(screen, name, (box.x + 12, box.y + 5), S.AMBER,
                        shadow=None)
        if self._banner_t < 1.0:
            alpha = int(255 * self._banner_t)
            over = pygame.Surface(box.size, pygame.SRCALPHA)
            over.fill((0, 0, 0, 255 - alpha))
            screen.blit(over, box.topleft)

    def _region_lights(self, ox, oy):
        """Lamps, fires and the spirit, in screen space, for the light pass.

        Only the few nearest lamps are lit: they add up, and a village
        with forty lamps in view would burn out to white.
        """
        lights = []
        candidates = []
        size = PROP_CHUNK * 16
        c0 = (ox - 48) // size
        c1 = (ox + W + 48) // size
        r0 = (oy - 48) // size
        r1 = (oy + H + 48) // size
        px = self.player.x - ox
        py = self.player.y - oy
        for cc in range(int(c0), int(c1) + 1):
            for rr in range(int(r0), int(r1) + 1):
                for x, y, kind, _variant in self._prop_chunks.get((cc, rr), ()):
                    if kind != "lamp":
                        continue
                    sx, sy = x - ox, y - oy
                    if -40 <= sx <= W + 40 and -40 <= sy <= H + 40:
                        d = (sx - px) ** 2 + (sy - py) ** 2
                        candidates.append((d, sx, sy))
        candidates.sort()
        for _d, sx, sy in candidates[:5]:
            lights.append((sx, sy - 6, 17, 0.45))
        # the spirit always carries a little light with it
        lights.append((px + 8, py - 12, 16, 0.4))
        return lights

    def _check_landmarks(self):
        """Walk up to a landmark and its story finds you."""
        if self._modal is not None:
            return
        st = self.game.state
        for mark in self.landmarks:
            if mark["id"] in st.landmarks:
                continue
            c, r = mark["pos"]
            x, y = c * TILE + TILE // 2, r * TILE + TILE // 2
            if self.player.distance_to(pygame.Vector2(x, y)) > 18.0:
                continue
            st.landmarks.append(mark["id"])
            st.add_card(mark["card"])
            st.bump_respect(1)
            # a side quest may have been waiting for exactly this place
            from .. import sidequests as SQ
            for qid, quest in SQ.SIDE_QUESTS.items():
                if quest.get("at") == mark["id"] \
                        and "sq_%s_done" % qid not in st.flags \
                        and "sq_%s_ready" % qid not in st.flags:
                    st.flags.append("sq_%s_ready" % qid)
            self._modal_stop = None
            self._show(list(mark["story"]), kind="landmark")
            return

    def _draw_landmarks(self, screen, ox, oy):
        """Carved stone markers for the landmarks — a cairn with a flame.

        If generated art exists for a landmark (the AI pipeline writes
        assets_ai/out/<id>.png), that is used instead, so the world can
        carry real illustrations without the code art changing at all.
        """
        found = self.game.state.landmarks
        for mark in self.landmarks:
            c, r = mark["pos"]
            x = c * TILE + TILE // 2 - ox
            y = r * TILE + TILE // 2 - oy
            if not (-16 <= x <= W + 16 and -16 <= y <= H + 16):
                continue
            seen = mark["id"] in found
            col = (236, 198, 120) if seen else (250, 214, 150)
            art = _landmark_art(mark["id"])
            if art is not None:
                views.blit_base(screen, art, x, y)
            else:
                # a small cairn: three stones, widest at the bottom
                screen.fill((92, 84, 76), pygame.Rect(int(x) - 4, int(y) - 9, 8, 9))
                screen.fill((120, 110, 100), pygame.Rect(int(x) - 3, int(y) - 8, 6, 8))
                screen.fill((150, 138, 124), pygame.Rect(int(x) - 2, int(y) - 7, 4, 3))
                screen.fill((70, 64, 58), pygame.Rect(int(x) - 5, int(y) - 1, 10, 2))
            # the flame on top
            flick = int(math.sin(self.t * 5.0 + c) * 1.5)
            pixel.add_glow(screen, (int(x), int(y) - 11), 9, col,
                           max_alpha=110 if not seen else 70)
            screen.fill((255, 226, 150),
                        pygame.Rect(int(x) - 1, int(y) - 12 + flick, 3, 4))
            screen.fill((255, 250, 210),
                        pygame.Rect(int(x), int(y) - 13 + flick, 1, 3))
            # the name, once you are close enough to read it
            if not seen and self.player.distance_to(
                    pygame.Vector2(c * TILE + 8, r * TILE + 8)) < 70.0:
                name = mark["name"].upper()[:18]
                nw = pixel.text_size(name)[0]
                pixel.draw_text(screen, name, (int(x) - nw // 2, int(y) - 26),
                                (250, 224, 170), shadow=None)

    def _check_road(self, dt):
        """Something happens on the road now and then.

        The walk between towns is most of the game, so it gets small
        moments: a bird, a stranger, a change in the weather.
        """
        if self._modal is not None:
            return
        if self.panel is not None and self.panel.visible:
            return
        if self._near is not None:
            return                      # not on the road
        moved = abs(self.speed) > 1.0
        self._road_t = (self._road_t or 0.0) + (dt if moved else 0.0)
        if self._road_t < 28.0:
            return
        self._road_t = 0.0
        from .. import encounters as EN
        region = self._region()
        pool = [e for e in EN.ENCOUNTERS
                if e.get("where") in ("any", region)]
        if not pool:
            return
        pick = pool[int(self.t * 7.0) % len(pool)]
        self._bark(pick["text"], ttl=5.0)

    # ------------------------------------------------------------------ draw
    def draw(self, screen, cinematic=False):
        st = self.game.state
        ox, oy = self.cam.offset()
        if self._shake > 0.0:                  # caught: the world jolts
            s = min(5.0, self._shake * 9.0)
            ox += int(math.sin(self.t * 72.0) * s)
            oy += int(math.cos(self.t * 64.0) * s)
        T.draw_view(screen, self.tm, (ox, oy), phase=T.phase_for(self.t))
        self._draw_markers(screen, ox, oy)
        self._draw_docks(screen, ox, oy)
        self._draw_sparks(screen, ox, oy)
        self._draw_landmarks(screen, ox, oy)
        self._draw_hosts(screen, ox, oy)
        self._draw_tablets(screen, ox, oy)
        base_y = self.player.y - oy
        self._draw_props(screen, ox, oy, behind=base_y)

        # Noi, the cowhide puppet, hops along behind
        self._draw_noi(screen, ox, oy)
        if self._sail:
            self._draw_boat(screen, self.player.x - ox, self.player.y - oy + 6)
        views.blit_spirit(screen, self.player.x + 8 - ox,
                          self.player.y - 14 - oy, self.t)
        face = self.facing
        if self._face_timer > 0.0 and self._face_from in ("up", "down", "side"):
            face = self._face_from
        bob = 0
        if not self._steps:
            bob = int(math.sin(self.t * 1.8) * 0.6)   # breathing when still
        py = (self.player.y - oy + bob
              - self._height_at(self.player.x, self.player.y))
        if self._squash > 0.0:
            # landing squash: a moment of stretch, then settle
            k = self._squash
            surf = A.character("player", face, self.walk_frame())
            w = max(6, int(surf.get_width() * (1.0 + 0.12 * k)))
            h = max(6, int(surf.get_height() * (1.0 - 0.14 * k)))
            surf = pygame.transform.scale(surf, (w, h))
            screen.blit(surf, (int(self.player.x - ox - w / 2), int(py - h)))
        else:
            views.blit_character(screen, self.player.x - ox, py,
                                 "player", face, self.walk_frame())
        self._draw_props(screen, ox, oy, before=base_y)
        self._draw_mobs(screen, ox, oy)
        self._draw_sky(screen, ox, oy)
        self._draw_fx(screen, ox, oy)
        self.weather.draw(screen, ox, oy, self._night())
        self._draw_fish_line(screen, ox, oy)
        self._draw_petals(screen, ox, oy)

        # the light pass decides the mood of the place: ambient tint,
        # light pools, haze and the colour grade
        night = self._night()
        lighting.apply(screen, self._region(),
                       self._region_lights(ox, oy), night)
        if night > 0.5:
            self._glow_lamps(screen, ox, oy)

        if self.prompt and self._modal is None:
            self._draw_banner(screen, self.prompt, S.TEXT)
        elif self.fish is not None and self._modal is None:
            msg = "NOW! reel it in!" if self.fish.get("bite", 0.0) > 0.0 else "waiting for a bite..."
            self._draw_banner(screen, msg,
                              S.CHILD if self.fish.get("bite", 0.0) > 0.0 else S.MUTED)

        if not cinematic:
            self._draw_hud(screen)
            self._draw_objective(screen)
            if self._modal is None:
                self._draw_compass(screen)
                self._draw_quest_arrow(screen)
        if self.panel is not None and self.panel.visible:
            self.panel.draw(screen)
        if not cinematic:
            # in a cutscene the scene draws the dialogue itself, so that it
            # can be lifted above the letterbox
            self.game.box.draw(screen)

    # ---------------------------------------------------------------- scenery
    _PROP_FNS = None

    def _draw_props(self, screen, ox, oy, behind=None, before=None):
        if OverworldScene._PROP_FNS is None:
            OverworldScene._PROP_FNS = {
                "hut": A.hut, "palm": A.palm, "banana": A.banana,
                "well": A.well, "shrine": A.shrine, "boat": A.boat,
                "lamp": A.lamp, "fence": A.fence, "fishtrap": A.fishtrap,
                "dryingrack": A.dryingrack, "flags": A.flags,
                "rock": A.rock, "bush": A.bush, "stump": A.stump,
                "tree": A.tree, "bigrock": A.bigrock, "flowers": A.flowers,
                "stupa": A.stupa, "karst": A.karst, "mosque": A.mosque,
                "lighthouse": A.lighthouse, "mountain": A.mountain,
                # region-specific plants and buildings
                "mangrove": A.mangrove, "rubber": A.rubber,
                "spirit_house": A.spirit_house, "shophouse": A.shophouse,
                "fern": A.fern, "stilt": A.stilt,
                "market_stall": A.market_stall, "windmill": A.windmill,
                # the heritage of the South
                "wat": A.wat, "buddha": A.buddha, "ruin": A.ruin,
                "puppet_stage": A.puppet_stage, "carving": A.carving,
                "kiln": A.kiln,
            }
        # only the chunks under the camera — the world holds tens of
        # thousands of props and touching them all every frame stutters
        size = PROP_CHUNK * 16
        c0 = (ox - 64) // size
        c1 = (ox + W + 64) // size
        r0 = (oy - 64) // size
        r1 = (oy + H + 64) // size
        visible = []
        chunks = self._prop_chunks
        for cc in range(int(c0), int(c1) + 1):
            for rr in range(int(r0), int(r1) + 1):
                bucket = chunks.get((cc, rr))
                if bucket:
                    visible.extend(bucket)
        visible.sort(key=lambda p: p[1])
        for x, y, kind, variant in visible:
            sx, sy = x - ox, y - oy
            if not (-24 <= sx <= W + 24 and -32 <= sy <= H + 24):
                continue
            if behind is not None and sy >= behind:
                continue
            if before is not None and sy < before:
                continue
            fn = OverworldScene._PROP_FNS.get(kind)
            if fn is None:
                continue
            try:
                surf = fn(variant) if kind not in ("hut", "well", "shrine", "boat", "stupa", "karst", "mosque", "lighthouse", "mountain") else fn()
            except TypeError:
                surf = fn()
            # generated art wins, when there is any: a batch of AI assets
            # drops straight into the world and replaces the code-drawn one
            gen = _ai_asset("%s_%s" % (kind, self._region()))
            if gen is None:
                gen = _ai_asset(kind)
            if gen is not None:
                surf = gen
            # a contact shadow so the prop stands on the ground instead of
            # floating over it (and it stands on the terrace, if it is on one)
            lift = self._height_at(x, y)
            if kind in _SHADOWED:
                views.shadow(screen, sx, sy - lift, max(8, surf.get_width() - 4))
            views.blit_base(screen, surf, sx, sy - lift)

    def _draw_tablets(self, screen, ox, oy):
        for stop in ST.STOPS:
            pos = self._tablet_px(stop)
            x, y = pos.x - ox, pos.y - oy
            if -16 <= x <= W + 16 and -16 <= y <= H + 16:
                done = self.game.state.stop_done(stop["id"])
                col = (120, 226, 120) if done else S.SPIRIT
                pixel.add_glow(screen, (x, y - 6), 9, col, max_alpha=80)
                screen.fill((60, 62, 92), pygame.Rect(int(x) - 5, int(y) - 12, 11, 9))
                screen.fill(col, pygame.Rect(int(x) - 5, int(y) - 12, 11, 1))
                screen.fill(col, pygame.Rect(int(x) - 5, int(y) - 4, 11, 1))

    def _draw_markers(self, screen, ox, oy):
        """Region gates: arches you walk into (gold for home)."""
        t = self.t
        for stop in ST.STOPS + [ST.PROLOGUE]:
            c, r = stop["pos"]
            x = c * TILE + TILE // 2 - ox
            y = r * TILE + TILE // 2 - oy
            if -16 <= x <= W + 16 and -16 <= y <= H + 16:
                done = self.game.state.stop_done(stop["id"])
                if stop is ST.PROLOGUE:
                    col = HOME_COLOR
                    bob = 2
                else:
                    col = STOP_COLOR.get(stop.get("kind", "province"), (232, 96, 96))
                    bob = 0
                # pulse for unvisited stops so the map feels alive
                pulse = 0 if done else int(2 * (0.5 + 0.5 * math.sin(t * 3 + c)))
                pixel.add_glow(screen, (x, y - 3), 5 + pulse, col, max_alpha=70)
                # an arch: two posts and a lintel, the way into the region
                x, y = int(x), int(y)
                screen.fill(col, pygame.Rect(x - 5, y - 8 - bob, 2, 9))
                screen.fill(col, pygame.Rect(x + 3, y - 8 - bob, 2, 9))
                screen.fill(col, pygame.Rect(x - 5, y - 9 - bob, 10, 2))
                if done:
                    screen.fill((120, 226, 120), pygame.Rect(x - 2, y - 3 - bob, 5, 2))
                name = "YAAI'S" if stop is ST.PROLOGUE else stop["title"].upper()[:20]
                nw = pixel.text_size(name)[0]
                pixel.draw_text(screen, name, (x - nw // 2, y - 20 - bob),
                                (250, 224, 140) if stop is ST.PROLOGUE else S.MUTED,
                                shadow=None)

    def _draw_noi(self, screen, ox, oy):
        """Noi scouts ahead toward the quest target, or trails behind."""
        if not self.game.state.stop_done("prologue"):
            return
        x, y = self._noi_pos()
        x, y = int(x - ox), int(y - oy)
        y += int(math.sin(self.t * 4.0) * 1.5)
        # cowhide body, dark rim, two eyes
        pixel.add_glow(screen, (x, y), 4, (196, 150, 96), max_alpha=60)
        screen.fill((90, 58, 40), pygame.Rect(x - 4, y - 3, 9, 7))
        screen.fill((150, 100, 62), pygame.Rect(x - 3, y - 2, 7, 5))
        screen.fill((240, 232, 214), pygame.Rect(x - 2, y - 1, 2, 2))
        screen.fill((240, 232, 214), pygame.Rect(x + 1, y - 1, 2, 2))
        self._draw_bark(screen, x, y)

    def _noi_pos(self):
        """Ahead toward the quest when it is far, at your heels at home."""
        tgt = self._target
        if tgt is not None:
            c, r = tgt["pos"]
            dest = pygame.Vector2(*self._px(c, r))
            away = dest - self.player
            if away.length() > 200.0:
                return self.player + away.normalize() * 22.0
        dx, dy = {"up": (0, 8), "down": (0, -8), "side": (10, 0)}[self.facing]
        return pygame.Vector2(self.player.x - dx, self.player.y - dy)

    def _bark(self, text, ttl=3.0):
        self.noi_bark = {"text": text, "t": 0.0, "ttl": ttl}

    def _draw_bark(self, screen, x, y):
        bark = getattr(self, "noi_bark", None)
        if not bark:
            return
        w = pixel.text_size(bark["text"])[0]
        bx = max(2, min(W - w - 12, x - w // 2))
        box = pygame.Rect(0, 0, w + 10, 13)
        box.topleft = (bx, max(2, y - 24))
        pixel.panel(screen, box, S.PANEL_BG, S.PANEL_BORDER)
        pixel.draw_text(screen, bark["text"], (box.x + 5, box.y + 3),
                        S.CHILD, shadow=None)

    def _draw_mobs(self, screen, ox, oy):
        """Lom's magpies and the wild boar, jittering as they hunt."""
        for m in self.mobs:
            x, y = int(m["x"] - ox), int(m["y"] - oy)
            if x < -24 or x > W + 24 or y < -24 or y > H + 24:
                continue
            chasing = m["state"] == "chase"
            j = int(math.sin(self.t * 32.0 + m["phase"]) * (2 if chasing else 0.7))
            if m["kind"] == "magpie":
                screen.fill((24, 24, 32), pygame.Rect(x - 5 + j, y - 9, 10, 6))
                screen.fill((238, 238, 244), pygame.Rect(x - 3 + j, y - 4, 6, 3))
                screen.fill((226, 176, 58), pygame.Rect(x + 3 + j, y - 8, 3, 2))
                screen.fill((24, 24, 32), pygame.Rect(x - 8 + j, y - 7, 3, 2))
            else:
                screen.fill((78, 54, 40), pygame.Rect(x - 7 + j, y - 6, 14, 8))
                screen.fill((54, 36, 28), pygame.Rect(x + 5 + j, y - 4, 4, 5))
                screen.fill((240, 240, 230), pygame.Rect(x + 8 + j, y - 3, 2, 2))
                screen.fill((28, 22, 18), pygame.Rect(x - 6 + j, y + 2, 3, 3))
                screen.fill((28, 22, 18), pygame.Rect(x + 2 + j, y + 2, 3, 3))
                screen.fill((210, 200, 180), pygame.Rect(x + 6 + j, y - 5, 2, 2))
            if chasing:
                pygame.draw.circle(screen, (236, 72, 72), (x, y - 13), 2)

    @staticmethod
    def _fit(text, max_px):
        """Trim a single line so it never runs past its panel."""
        if pixel.text_size(text)[0] <= max_px:
            return text
        while text and pixel.text_size(text + "..")[0] > max_px:
            text = text[:-1]
        return text + ".."

    def _draw_banner(self, screen, text, color):
        """A centered prompt that wraps instead of running off-screen."""
        lines = pixel.wrap(text, W - 20)[:2] or [""]
        h = 6 + 9 * len(lines)
        wpx = max(pixel.text_size(ln)[0] for ln in lines) + 10
        box = pygame.Rect(0, 0, min(W - 2, wpx), h)
        box.center = (W // 2, H - 6 - h // 2)
        pixel.panel(screen, box, S.PANEL_BG, S.PANEL_BORDER)
        y = box.y + 4
        for ln in lines:
            pixel.draw_text(screen, ln, (box.x + 5, y), color, shadow=None)
            y += 9

    def _draw_hud(self, screen):
        st = self.game.state
        # journal
        label = "JOURNAL %d/%d" % (st.journal_count(), ST.TOTAL_STOPS)
        pixel.draw_text(screen, label, (5, 4), S.TEXT, shadow=None)
        act = self.game.state.act_of()
        act_name = {a: n for a, n, _lo, _hi in ST.ACTS}.get(act, "Prologue")
        pixel.draw_text(screen, act_name, (5, 13), S.MUTED, shadow=None)
        self._draw_quest_line(screen)
        # meters, right side
        spice = "SPICE" + "*" * st.spice + "." * (5 - st.spice)
        respect = "RESPECT" + "*" * st.respect
        w = pixel.text_size(spice)[0]
        pixel.draw_text(screen, spice, (W - w - 5, 4), S.AMBER, shadow=None)
        w = pixel.text_size(respect)[0]
        pixel.draw_text(screen, respect, (W - w - 5, 13), S.SPIRIT, shadow=None)
        # Noi's words
        if st.words:
            words = " / ".join(w_["roman"] for w_ in st.words[-3:])
            pixel.draw_text(screen, self._fit(words, W - 10), (5, H - 11),
                            S.MUTED, shadow=None)
        # danger: pulsing warning the moment a mob starts the hunt
        if getattr(self, "_danger", None) is not None:
            pulse = 0.5 + 0.5 * abs((self.t * 6.0) % 2.0 - 1.0)
            col = (238, int(50 + 80 * pulse), 50)
            text = "!!  THEY SEE YOU - RUN (SHIFT) or GLIDE (X)  !!"
            pixel.draw_text(screen, self._fit(text, W - 8),
                            ((W - pixel.text_size(self._fit(text, W - 8))[0]) // 2,
                             H - 36), col, shadow=None)

    # ------------------------------------------------------- storm and sprites
    def _seed_sky(self):
        """Three wandering storm cells and five teasing wind sprites."""
        import random
        rng = random.Random(4242)
        ww, wh = WM.WORLD_COLS * TILE, WM.WORLD_ROWS * TILE
        self.storms = []
        for _i in range(3):
            ang = rng.random() * 2 * math.pi
            self.storms.append({
                "x": rng.random() * ww, "y": rng.random() * wh,
                "vx": math.cos(ang) * 26, "vy": math.sin(ang) * 18,
                "r": 70,
            })
        self.sprites = []
        for _i in range(5):
            self.sprites.append({
                "hx": rng.random() * ww, "hy": rng.random() * wh,
                "x": 0.0, "y": 0.0, "ph": rng.random() * 6.28, "cool": 0.0,
            })
            self.sprites[-1]["x"] = self.sprites[-1]["hx"]
            self.sprites[-1]["y"] = self.sprites[-1]["hy"]
        self._storm_surf = None

    def _storm_surface(self):
        if self._storm_surf is None:
            surf = pygame.Surface((160, 160), pygame.SRCALPHA)
            for r, alpha in ((78, 60), (64, 70), (50, 80), (36, 90), (22, 110)):
                pygame.draw.circle(surf, (24, 26, 48, alpha), (80, 80), r)
            for i in range(3):
                pygame.draw.arc(surf, (150, 170, 210, 130),
                                pygame.Rect(30 + i * 12, 30 + i * 12,
                                            100 - i * 24, 100 - i * 24),
                                0.4 + i, 2.4 + i, 3)
            self._storm_surf = surf
        return self._storm_surf
    # ------------------------------------------------------------ spell effects
    FX_TTL = {"burst": 1.5, "rise": 7.0, "swim": 6.0, "pull": 6.0,
              "bloom": 5.0, "rain": 6.0, "dance": 9.0, "festival": 25.0}

    def _spawn_fx(self, stop):
        import random
        spec = ST.code_of(stop["id"])
        kind = (spec or {}).get("fx", "burst")
        pos = self._tablet_px(stop)
        rng = random.Random(stop["id"])
        self.fx.append({"kind": kind, "x": pos.x, "y": pos.y, "t": 0.0,
                        "ttl": self.FX_TTL.get(kind, 2.0),
                        "seed": [rng.random() for _ in range(16)]})
        if kind in ("burst", "festival"):
            self._burst(pos.x, pos.y, 26 if kind == "festival" else 14)
        if kind == "festival":
            self._bark("Dance! No excuses!", ttl=4.0)

    def _burst(self, x, y, n):
        import random
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

    def _glow_lamps(self, screen, ox, oy):
        for x, y, kind, _variant in self.props:
            if kind != "lamp":
                continue
            sx, sy = x - ox, y - oy
            if -8 <= sx <= W + 8 and -8 <= sy <= H + 8:
                pixel.add_glow(screen, (sx, sy - 6), 7, (255, 200, 120),
                               max_alpha=110)

    def _draw_fish_line(self, screen, ox, oy):
        if self.fish is None:
            return
        fx, fy = self.fish["x"] - ox, self.fish["y"] - oy
        px, py = self.player.x - ox, self.player.y - oy
        if -8 <= fx <= W + 8 and -8 <= fy <= H + 8:
            pygame.draw.line(screen, (200, 200, 210),
                             (int(px), int(py) - 8), (int(fx), int(fy)), 1)
            bite = self.fish.get("bite", 0.0) > 0.0
            dip = 2 if bite else 0
            screen.fill((232, 96, 96), pygame.Rect(int(fx) - 1, int(fy) - 1 + dip, 3, 3))
            screen.fill((240, 240, 240), pygame.Rect(int(fx) - 1, int(fy) - 3 + dip, 3, 2))
            if bite:
                pixel.draw_text(screen, "!", (int(fx) + 4, int(fy) - 10),
                                S.CHILD, shadow=None)

    def _draw_sky(self, screen, ox, oy):
        surf = self._storm_surface()
        for s in self.storms:
            x, y = s["x"] - ox, s["y"] - oy
            if -90 <= x <= W + 90 and -90 <= y <= H + 90:
                screen.blit(surf, (int(x) - 80, int(y) - 80))
        for sp in self.sprites:
            x, y = sp["x"] - ox, sp["y"] - oy
            if -8 <= x <= W + 8 and -8 <= y <= H + 8:
                wob = math.sin(self.t * 7 + sp["ph"]) * 2
                screen.fill((235, 240, 250), pygame.Rect(int(x) - 2, int(y) - 1, 5, 3))
                screen.fill((190, 200, 225), pygame.Rect(int(x) - 4 + int(wob), int(y) + 1, 3, 2))

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
        # bunting overhead
        for i in range(5):
            fx = x - 30 + i * 15
            fy = y - 26 + int(3 * math.sin(f["t"] * 4 + i))
            screen.fill((232, 96, 96) if i % 2 else (255, 216, 150),
                        pygame.Rect(int(fx), int(fy), 4, 3))

    def _draw_quest_line(self, screen):
        """The quest compass readout: where next, and how far."""
        tgt = self._target
        if tgt is None:
            text = "NEXT > home"
        else:
            c, r = tgt["pos"]
            d = int(self.player.distance_to(pygame.Vector2(*self._px(c, r))) // TILE)
            label = tgt.get("title", tgt.get("name", "home"))
            text = "NEXT > %s %dm" % (label.upper()[:18], d)
        pixel.draw_text(screen, self._fit(text, W // 2), (5, 22), S.AMBER, shadow=None)
        self._draw_fuel(screen)
        self._draw_combo(screen)

    def _draw_fuel(self, screen):
        st = self.game.state
        pixel.draw_text(screen, "WIND", (5, 31), S.MUTED, shadow=None)
        bar = pygame.Rect(32, 32, 44, 5)
        screen.fill((30, 32, 48), bar)
        fill = int(44 * max(0.0, min(1.0, st.fuel / 100.0)))
        col = S.SPIRIT if st.fuel > 25 else S.RED
        if fill:
            screen.fill(col, pygame.Rect(32, 32, fill, 5))

    def _draw_objective(self, screen):
        """Side tab: what to do now, and how to do it — never off-screen."""
        st = self.game.state
        if st.journey_done() and getattr(self, "_finale_stage", None) is None:
            head, what, how = ("THE WAI KHRU", "Go home to Yaai's house",
                               "follow the gold arrow")
        else:
            tgt = self._target
            if tgt is None or tgt is ST.PROLOGUE:
                return
            what, how = self._beat_text(tgt)
            head = ST.chapter(tgt)
        box = pygame.Rect(W - 150, 30, 145, 70)
        pixel.panel(screen, box, S.PANEL_BG, S.PANEL_BORDER)
        inner = box.w - 10
        pixel.draw_text(screen, "OBJECTIVE", (box.x + 5, box.y + 4),
                        S.AMBER, shadow=None)
        lines = (pixel.wrap(head, inner)[:1]
                 + pixel.wrap("> " + what, inner)[:2]
                 + pixel.wrap(how, inner)[:3])
        y = box.y + 15
        for i, line in enumerate(lines[:6]):
            col = S.TEXT if i == 0 else (S.SPIRIT if i < 3 else S.MUTED)
            pixel.draw_text(screen, self._fit(line, inner), (box.x + 5, y),
                            col, shadow=None)
            y += 9

    def _draw_combo(self, screen):
        combo = self.game.state.combo
        if combo >= 2:
            text = "OROI x%d" % combo
            w = pixel.text_size(text)[0]
            pixel.draw_text(screen, text, (W - w - 5, 25), S.CHILD, shadow=None)
        night = self._night()
        col = (250, 230, 150) if night < 0.5 else (200, 210, 240)
        pygame.draw.circle(screen, col, (W - 8, 38), 3)
        if night >= 0.5:
            pygame.draw.circle(screen, S.BG, (W - 7, 37), 2)

    def _draw_quest_arrow(self, screen):
        """A gold arrow over your head, pointing at the quest target —
        pinned to the screen edge when the target is far away."""
        tgt = self._target
        if tgt is None:
            return
        c, r = tgt["pos"]
        dest = pygame.Vector2(*self._px(c, r))
        if self.player.distance_to(dest) < REACH * 2:
            return                      # you're here; no arrow needed
        ang = math.atan2(dest.y - self.player.y, dest.x - self.player.x)
        ox, oy = self.cam.offset()
        dx, dy = dest.x - ox, dest.y - oy
        if 0 <= dx <= W and 0 <= dy <= H:
            cx = self.player.x - ox + math.cos(ang) * 14.0
            cy = self.player.y - oy - 20 + math.sin(ang) * 14.0
        else:
            cx = max(10.0, min(W - 10.0, self.player.x - ox + math.cos(ang) * 200.0))
            cy = max(10.0, min(H - 10.0, self.player.y - oy + math.sin(ang) * 200.0))
        pts = []
        for a, length in ((0.0, 7.0), (2.5, 4.0), (-2.5, 4.0)):
            pts.append((cx + math.cos(ang + a) * length,
                        cy + math.sin(ang + a) * length))
        pygame.draw.polygon(screen, (255, 216, 150), pts)

    def _draw_docks(self, screen, ox, oy):
        for dock in self.docks:
            c, r = dock["pos"]
            x = c * TILE + TILE // 2 - ox
            y = r * TILE + TILE // 2 - oy
            if -16 <= x <= W + 16 and -16 <= y <= H + 16:
                self._draw_boat(screen, x, y)

    @staticmethod
    def _draw_boat(screen, x, y):
        """A little long-tail boat: dark hull, white trim, ribbon."""
        screen.fill((90, 58, 40), pygame.Rect(int(x) - 7, int(y) - 2, 15, 5))
        screen.fill((150, 100, 62), pygame.Rect(int(x) - 7, int(y) - 2, 15, 1))
        screen.fill((240, 232, 214), pygame.Rect(int(x) - 1, int(y) - 5, 2, 3))
        screen.fill((232, 96, 96), pygame.Rect(int(x) + 4, int(y) - 4, 3, 1))

    def _draw_sparks(self, screen, ox, oy):
        found = self.game.state.found
        for stop_id, pos in self.sparks.items():
            if stop_id in found:
                continue
            x, y = pos.x - ox, pos.y - oy
            if -8 <= x <= W + 8 and -8 <= y <= H + 8:
                if (self.t * 1.5 + hash(stop_id) % 10) % 2.0 < 1.2:
                    pixel.add_glow(screen, (x, y), 4, (255, 240, 180),
                                   max_alpha=90)
                    screen.fill((255, 246, 210), pygame.Rect(int(x), int(y), 2, 2))

    def _draw_hosts(self, screen, ox, oy):
        for stop in ST.STOPS:
            extra = ST.extra_of(stop["id"])
            if not extra:
                continue
            pos = self._host_px(stop)
            x, y = pos.x - ox, pos.y - oy
            if -16 <= x <= W + 16 and -16 <= y <= H + 16:
                views.blit_character(screen, x, y, extra.get("look", "nok"),
                                     "down", 0)

    def _draw_compass(self, screen):
        """A small north marker in the corner so the big world orients you."""
        pixel.draw_text(screen, "N", (W - 14, H - 11), S.MUTED, shadow=None)
        screen.fill((144, 152, 176), pygame.Rect(W - 8, H - 10, 2, 5))
