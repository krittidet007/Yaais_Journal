"""The player UI: an Items screen and a Settings screen, drawn in the pixel style.

Both are modal overlays the Game swaps in on top of whatever scene is running.
They return the string "close" from ``handle_event`` when dismissed.
"""

import pygame

from . import keymap
from . import audio
from . import items
from . import mouse
from . import options as O
from . import pixel
from . import save
from . import settings as S
from .game_state import state

COLS, ROWS = 4, 3
SLOTS = COLS * ROWS
CELL, GAP = 26, 2

ROW_H = 16


def _dim(screen, alpha=184):
    layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    layer.fill((6, 7, 14, alpha))
    screen.blit(layer, (0, 0))


class Menu:
    """Shared chrome for the modal player menus."""

    def __init__(self):
        self.open_flag = False
        self.sel = 0
        self.t = 0.0

    @property
    def visible(self):
        return self.open_flag

    def open(self):
        self.open_flag = True
        self.sel = 0
        self.t = 0.0

    def close(self):
        self.open_flag = False

    def update(self, dt):
        self.t += dt

    def _header(self, screen, title, right=""):
        bar = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 15)
        pygame.draw.rect(screen, S.PANEL_BG_ALT, bar)
        pixel.draw_text(screen, title, (bar.x + 5, bar.y + 4), S.SPIRIT)
        if right:
            pixel.draw_text(screen, right,
                            (bar.right - pixel.text_size(right)[0] - 5, bar.y + 4),
                            S.MUTED, shadow=None)

    def _footer(self, screen, text):
        pixel.draw_text(screen, text, (self.rect.x + 6, self.rect.bottom - 12),
                        S.MUTED, shadow=None)


class InventoryMenu(Menu):
    """The Items section: a slot grid + the selected item's description."""

    def __init__(self):
        super().__init__()
        self.rect = pygame.Rect((S.INTERNAL_W - 280) // 2,
                                (S.INTERNAL_H - 130) // 2, 280, 130)

    def _slot_rect(self, index):
        row, col = divmod(index, COLS)
        x = self.rect.x + 8 + col * (CELL + GAP)
        y = self.rect.y + 22 + row * (CELL + GAP)
        return pygame.Rect(x, y, CELL, CELL)

    def handle_event(self, ev):
        if mouse.cancelled(ev):
            self.close()
            return "close"
        if mouse.clicked(ev):
            for i in range(SLOTS):
                if i < len(state.items) and self._slot_rect(i).collidepoint(ev.pos):
                    self.sel = i
                    return None
            return None
        if ev.type != pygame.KEYDOWN:
            return None
        if ev.key in (pygame.K_ESCAPE,) or keymap.pressed("items", ev):
            self.close()
            return "close"
        count = max(1, len(state.items))
        if ev.key in (pygame.K_LEFT, pygame.K_a):
            self.sel = (self.sel - 1) % count
        elif ev.key in (pygame.K_RIGHT, pygame.K_d):
            self.sel = (self.sel + 1) % count
        elif ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - COLS) % count
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + COLS) % count
        return None

    def draw(self, screen):
        _dim(screen)
        pixel.panel(screen, self.rect, S.PANEL_BG, S.PANEL_BORDER,
                    inner_highlight=S.PANEL_EDGE)
        self._header(screen, "ITEMS", "%d/%d" % (len(state.items), SLOTS))

        for i in range(SLOTS):
            rect = self._slot_rect(i)
            pygame.draw.rect(screen, S.PANEL_BG_ALT, rect)
            if i < len(state.items):
                screen.blit(items.icon(state.items[i]),
                            (rect.centerx - 8, rect.centery - 8))
            border = S.SPIRIT if i == self.sel and state.items else S.PANEL_EDGE
            pygame.draw.rect(screen, border, rect, 1)

        px = self.rect.x + 8 + COLS * (CELL + GAP) + 4
        pane = pygame.Rect(px, self.rect.y + 22, self.rect.right - px - 8, 92)
        pygame.draw.rect(screen, (16, 18, 30), pane)
        pygame.draw.rect(screen, S.PANEL_EDGE, pane, 1)

        if state.items:
            sel = min(self.sel, len(state.items) - 1)
            item_id = state.items[sel]
            big = pygame.transform.scale(items.icon(item_id), (32, 32))
            screen.blit(big, (pane.x + 6, pane.y + 6))
            pixel.draw_text(screen, items.name(item_id), (pane.x + 44, pane.y + 8), S.TEXT)
            body = pixel.wrap(items.description(item_id), pane.width - 12, 8)
            for i, line in enumerate(body[:5]):
                pixel.draw_text(screen, line, (pane.x + 6, pane.y + 30 + i * 10),
                                S.MUTED, shadow=None)
        else:
            for i, line in enumerate(("Your pack is empty.", "", "Help the village",
                                      "and you'll pick", "things up along", "the way.")):
                pixel.draw_text(screen, line, (pane.x + 6, pane.y + 8 + i * 10),
                                S.MUTED, shadow=None)

        self._footer(screen, "click/arrows select     [I / ESC] close")


class OptionsMenu(Menu):
    """Settings: audio, video, gameplay and key bindings, with scrolling."""

    def __init__(self):
        super().__init__()
        height = S.INTERNAL_H - 20
        self.rect = pygame.Rect((S.INTERNAL_W - 268) // 2,
                                (S.INTERNAL_H - height) // 2, 268, height)
        self.mode = "main"
        self.scroll = 0
        self.capturing = False
        self.capture_action = None

    # ------------------------------------------------------------------ layout
    def _rows_top(self):
        return self.rect.y + 17

    def _visible_rows(self):
        return max(1, (self.rect.height - 17 - 16) // ROW_H)

    def _clamp_scroll(self):
        count = len(O.ROWS)
        visible = self._visible_rows()
        if self.sel < self.scroll:
            self.scroll = self.sel
        elif self.sel >= self.scroll + visible:
            self.scroll = self.sel - visible + 1
        self.scroll = max(0, min(self.scroll, max(0, count - visible)))

    # ------------------------------------------------------------------- events
    def open(self):
        super().open()
        self.mode = "main"
        self.scroll = 0
        self.capturing = False

    def handle_event(self, ev):
        if self.mode == "keys":
            return self._keys_event(ev)
        if mouse.cancelled(ev):
            self.close()
            return "close"
        if mouse.clicked(ev):
            return self._click_main(ev.pos)
        if ev.type == pygame.MOUSEWHEEL:
            self.sel = (self.sel - ev.y) % len(O.ROWS)
            self._clamp_scroll()
            return None
        if ev.type != pygame.KEYDOWN:
            return None

        if ev.key == pygame.K_ESCAPE or keymap.pressed("settings", ev):
            self.close()
            return "close"
        count = len(O.ROWS)
        result = None
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % count
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % count
        elif ev.key in (pygame.K_LEFT, pygame.K_a):
            self._adjust(-1)
        elif ev.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN, pygame.K_SPACE):
            result = self._adjust(1)
        self._clamp_scroll()
        return result

    def _adjust(self, direction):
        row = O.ROWS[self.sel]
        if row[0] == "action":
            if row[3] == "keys" and direction > 0:
                self.mode = "keys"
                self.sel = 0
                self.capturing = False
            elif row[3] == "save" and direction > 0:
                return "open:save"
            return None
        O.options.adjust(row[1], direction)
        if row[1] in ("master_volume", "music_volume", "sfx_volume"):
            audio.apply_volumes()
        elif row[1] == "music_source":
            audio.play_music()
        return None

    # ------------------------------------------------------------------ mouse
    def _row_at(self, pos, count):
        """Visible-row index under ``pos``, or None."""
        top = self._rows_top()
        if not (self.rect.x <= pos[0] <= self.rect.right):
            return None
        i = (pos[1] - top) // ROW_H + self.scroll
        if 0 <= i < count and self.scroll <= i < self.scroll + self._visible_rows():
            return i
        return None

    def _click_main(self, pos):
        i = self._row_at(pos, len(O.ROWS))
        if i is None:
            return None
        if i == self.sel:
            return self._adjust(1)      # second click = OK / change
        self.sel = i
        self._clamp_scroll()
        audio.sfx("click")
        return None

    # ------------------------------------------------------------- key bindings
    def _keys_event(self, ev):
        if self.capturing:
            if ev.type == pygame.KEYDOWN:
                if ev.key != pygame.K_ESCAPE:
                    O.options.set_key(self.capture_action, pygame.key.name(ev.key))
                self.capturing = False
            return None
        if mouse.cancelled(ev):
            self.mode = "main"
            self.sel = next(i for i, r in enumerate(O.ROWS)
                            if r[0] == "action" and r[3] == "keys")
            return None
        if mouse.clicked(ev):
            i = self._row_at(ev.pos, len(O.KEY_ACTIONS))
            if i is None:
                return None
            if i == self.sel:
                self.capturing = True
                self.capture_action = O.KEY_ACTIONS[self.sel][0]
            else:
                self.sel = i
                audio.sfx("click")
            return None
        if ev.type != pygame.KEYDOWN:
            return None
        count = len(O.KEY_ACTIONS)
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % count
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % count
        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.capturing = True
            self.capture_action = O.KEY_ACTIONS[self.sel][0]
        elif ev.key == pygame.K_ESCAPE or keymap.pressed("settings", ev):
            self.mode = "main"
            self.sel = next(i for i, r in enumerate(O.ROWS)
                            if r[0] == "action" and r[3] == "keys")
        return None

    # --------------------------------------------------------------------- draw
    def draw(self, screen):
        _dim(screen)
        pixel.panel(screen, self.rect, S.PANEL_BG, S.PANEL_BORDER,
                    inner_highlight=S.PANEL_EDGE)
        if self.mode == "keys":
            self._draw_keys(screen)
        else:
            self._draw_main(screen)

    def _draw_main(self, screen):
        self._header(screen, "SETTINGS", "\u2191\u2193 move")
        top = self._rows_top()
        visible = self._visible_rows()
        for i in range(visible):
            index = self.scroll + i
            if index >= len(O.ROWS):
                break
            row = O.ROWS[index]
            y = top + i * ROW_H
            selected = index == self.sel
            self._row_bg(screen, y, selected)
            pixel.draw_text(screen, row[2], (self.rect.x + 8, y + 4),
                            S.TEXT if selected else S.MUTED, shadow=None)
            self._draw_value(screen, row, y, selected)

        if len(O.ROWS) > visible:
            self._scrollbar(screen)
        self._footer(screen, "click row twice = ok   \u2190\u2192 change   O close")

    def _row_bg(self, screen, y, selected):
        if not selected:
            return
        row = pygame.Rect(self.rect.x + 4, y, self.rect.width - 8, ROW_H - 1)
        pygame.draw.rect(screen, S.PANEL_BG_ALT, row)
        pygame.draw.rect(screen, S.SPIRIT, row, 1)

    def _draw_value(self, screen, row, y, selected):
        color = S.SPIRIT if selected else S.MUTED
        if row[0] == "slider":
            _, key, _, lo, hi, _ = row
            value = int(O.options.get(key))
            frac = (value - lo) / float(hi - lo)
            bx = self.rect.right - 96
            bw = 56
            pygame.draw.rect(screen, S.PANEL_EDGE, pygame.Rect(bx, y + 5, bw, 6))
            pygame.draw.rect(screen, color, pygame.Rect(bx, y + 5, int(bw * frac), 6))
            label = str(value)
            pixel.draw_text(screen, label,
                            (self.rect.right - pixel.text_size(label)[0] - 7, y + 4),
                            S.TEXT if selected else S.MUTED, shadow=None)
        elif row[0] == "choice":
            text = "< %s >" % O.options.get(row[1])
            pixel.draw_text(screen, text,
                            (self.rect.right - pixel.text_size(text)[0] - 7, y + 4),
                            color, shadow=None)
        else:
            text = "enter >"
            pixel.draw_text(screen, text,
                            (self.rect.right - pixel.text_size(text)[0] - 7, y + 4),
                            color, shadow=None)

    def _scrollbar(self, screen):
        track = pygame.Rect(self.rect.right - 4, self._rows_top(), 2,
                            self._visible_rows() * ROW_H)
        pygame.draw.rect(screen, S.PANEL_EDGE, track)
        visible = self._visible_rows()
        thumb_h = max(8, int(track.height * visible / len(O.ROWS)))
        max_scroll = max(1, len(O.ROWS) - visible)
        ty = track.y + int((track.height - thumb_h) * self.scroll / max_scroll)
        pygame.draw.rect(screen, S.SPIRIT, pygame.Rect(track.x, ty, 2, thumb_h))

    def _draw_keys(self, screen):
        self._header(screen, "KEY BINDINGS", "")
        top = self._rows_top()
        for i, (action, label) in enumerate(O.KEY_ACTIONS):
            y = top + i * ROW_H
            selected = i == self.sel
            self._row_bg(screen, y, selected)
            pixel.draw_text(screen, label, (self.rect.x + 8, y + 4),
                            S.TEXT if selected else S.MUTED, shadow=None)
            name = keymap.label(action)
            pixel.draw_text(screen, name,
                            (self.rect.right - pixel.text_size(name)[0] - 7, y + 4),
                            S.SPIRIT if selected else S.MUTED, shadow=None)
        if self.capturing:
            self._footer(screen, "press a key\u2026  (esc cancels)")
        else:
            self._footer(screen, "enter rebind   ESC/o back")


SCENE_LABELS = {
    "washup": "Riverbank",
    "hub": "Village",
    "village_naming": "Naming",
    "shrine": "Shrine",
    "well": "Well",
    "epilogue": "Epilogue",
}


class SaveMenu(Menu):
    """Manual 3-slot save / load."""

    ROW_H = 24

    def __init__(self, game):
        super().__init__()
        self.game = game
        height = 15 + 3 * self.ROW_H + 16
        self.rect = pygame.Rect((S.INTERNAL_W - 284) // 2,
                                (S.INTERNAL_H - height) // 2, 284, height)
        self.mode = "load"
        self.save_allowed = True
        self.confirming = False
        self.flash_t = -10.0

    def open(self, mode="load", save_allowed=True):
        super().open()
        self.mode = "load" if not save_allowed else mode
        self.save_allowed = save_allowed
        self.confirming = False

    def _toggle_mode(self):
        if not self.save_allowed:
            return
        self.mode = "save" if self.mode == "load" else "load"
        self.confirming = False
        audio.sfx("click")

    # ------------------------------------------------------------------ mouse
    def _slot_rect(self, i):
        top = self.rect.y + 17
        return pygame.Rect(self.rect.x + 4, top + i * self.ROW_H,
                           self.rect.width - 8, self.ROW_H - 2)

    def _click(self, pos):
        if self.confirming:
            self._write_slot()          # click = yes, overwrite it
            self.confirming = False
            return None
        header = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 15)
        if header.collidepoint(pos):
            self._toggle_mode()
            return None
        for i in range(3):
            if self._slot_rect(i).collidepoint(pos):
                if i == self.sel:
                    return self._act()  # second click = load/save here
                self.sel = i
                audio.sfx("click")
                return None
        return None

    def _scene_name(self, index):
        info = save.slot_info(index)
        return info["scene"] if info else ""

    # ------------------------------------------------------------------- events
    def handle_event(self, ev):
        if mouse.cancelled(ev):
            if self.confirming:
                self.confirming = False
                return None
            self.close()
            return "close"
        if mouse.clicked(ev):
            return self._click(ev.pos)
        if ev.type != pygame.KEYDOWN:
            return None
        if self.confirming:
            if ev.key == pygame.K_ESCAPE or keymap.pressed("cancel", ev):
                self.confirming = False            # back out of the prompt
                return None
            if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE) \
                    or keymap.pressed("confirm", ev):
                self._write_slot()
            self.confirming = False
            return None
        if ev.key == pygame.K_ESCAPE or keymap.pressed("cancel", ev):
            self.close()
            return "close"
        if ev.key in (pygame.K_LEFT, pygame.K_a):
            self._toggle_mode()
        elif ev.key in (pygame.K_RIGHT, pygame.K_d):
            self._toggle_mode()
        elif ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % 3
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % 3
        elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE) \
                or keymap.pressed("confirm", ev):
            return self._act()
        self.flash_t = -10.0
        return None

    def _act(self):
        index = self.sel + 1
        if self.mode == "save":
            if save.slot_info(index) is not None:
                self.confirming = True          # occupied -> ask first
                audio.sfx("click")
            else:
                self._write_slot()
            return None
        # load
        data = save.read_slot(index)
        if data is None:
            audio.sfx("error")
            return None
        audio.sfx("collect")
        self.game.state.from_dict(data["state"])
        self.game.switch(data["scene"])         # also refreshes the autosave
        self.close()
        return "close"

    def _write_slot(self):
        scene = self.game.current.name
        if scene not in save.RESUMABLE:
            audio.sfx("error")
            return
        if save.write_slot(self.sel + 1, self.game.state, scene):
            self.flash_t = self.t
            audio.sfx("collect")

    # --------------------------------------------------------------------- draw
    def draw(self, screen):
        _dim(screen)
        pixel.panel(screen, self.rect, S.PANEL_BG, S.PANEL_BORDER,
                    inner_highlight=S.PANEL_EDGE)
        mode = "SAVE" if self.mode == "save" else "LOAD"
        self._header(screen, "SAVE / LOAD", "\u2039 %s \u203a" % mode)
        if not self.save_allowed:
            pixel.draw_text(screen, "start a game to save",
                            (self.rect.x + 8, self.rect.y + 17), S.MUTED, shadow=None)
        top = self.rect.y + 17
        for i in range(3):
            y = top + i * self.ROW_H
            selected = i == self.sel
            self._slot_row(screen, i, y, selected)
        if self.confirming:
            self._footer(screen, "overwrite slot?  click/enter yes  esc no")
        elif self.mode == "save":
            self._footer(screen, "click slot twice = save   esc close")
        else:
            self._footer(screen, "click slot twice = load   esc close")

    def _slot_row(self, screen, i, y, selected):
        info = save.slot_info(i + 1)
        row = pygame.Rect(self.rect.x + 4, y, self.rect.width - 8, self.ROW_H - 2)
        if selected:
            pygame.draw.rect(screen, S.PANEL_BG_ALT, row)
            pygame.draw.rect(screen, S.SPIRIT, row, 1)
        else:
            pygame.draw.rect(screen, S.PANEL_BG_ALT, row)
            pygame.draw.rect(screen, S.PANEL_EDGE, row, 1)
        if self.t - self.flash_t < 0.7 and i == self.sel:
            pygame.draw.rect(screen, S.SPIRIT, row, 2)    # freshly saved

        pixel.draw_text(screen, "SLOT %d" % (i + 1), (row.x + 6, row.y + 4), S.TEXT,
                        shadow=None)
        if info is None:
            pixel.draw_text(screen, "empty", (row.x + 78, row.y + 7), S.MUTED,
                            shadow=None)
            return
        scene = SCENE_LABELS.get(info["scene"], info["scene"])
        name = info["name"] or "?"
        line1 = "%s \u00b7 %s" % (scene, name)
        pixel.draw_text(screen, line1, (row.x + 78, row.y + 3), S.SPIRIT,
                        shadow=None)
        line2 = "%d items \u00b7 %s" % (info["items"], info["time"][-5:])
        pixel.draw_text(screen, line2, (row.x + 78, row.y + 14), S.MUTED,
                        shadow=None)


class JournalMenu(Menu):
    """Yaai's journal, actually readable: pages, cards, words, catches."""

    ROW_H = 12

    def __init__(self, game):
        super().__init__()
        self.game = game
        height = S.INTERNAL_H - 16
        self.rect = pygame.Rect((S.INTERNAL_W - 288) // 2,
                                (S.INTERNAL_H - height) // 2, 288, height)
        self.tab = 0
        self.scroll = 0

    TABS = ("PAGES", "PLACES", "QUESTS", "CARDS", "WORDS", "CATCH", "SIGHTS",
            "STORY")

    def open(self):
        super().open()
        self.tab = 0
        self.scroll = 0

    def _entries(self):
        from . import story as ST
        if self.tab == 0:
            out = []
            for sid in state.pages:
                stop = ST.STOP_BY_ID.get(sid)
                if stop:
                    out.append((ST.chapter(stop), stop["page"]))
            return out
        if self.tab == 1:
            # the landmarks you have walked to: what each place was
            from . import landmarks as LM
            out = []
            for region, marks in LM.LANDMARKS.items():
                for mark in marks:
                    if mark["id"] not in state.landmarks:
                        continue
                    body = " ".join(line[-1] for line in mark["story"])
                    out.append((mark["name"], body))
            return out
        if self.tab == 2:
            # the quest log: what is on, what is ready, what is done
            from . import sidequests as SQ
            out = []
            for qid, quest in SQ.SIDE_QUESTS.items():
                done = "sq_%s_done" % qid in state.flags
                ready = "sq_%s_ready" % qid in state.flags
                given = "sq_%s_given" % qid in state.flags
                if done:
                    mark, body = "DONE", quest["answer"]
                elif ready:
                    mark, body = ("READY - go back to %s"
                                  % ST.STOP_BY_ID[quest["from"]]["name"]
                                  if quest["from"] in ST.STOP_BY_ID
                                  else "READY"), quest["ask"]
                elif given:
                    mark, body = ("ON - %s" % quest["at"].replace("_", " "),
                                  quest["ask"])
                else:
                    continue
                out.append((mark, body))
            return out
        if self.tab == 3:
            # culture cards — and the lore documents, which carry their
            # own text in the journal
            out = []
            for c in state.cards:
                body = ST.LORE.get(c, "")
                out.append((c, body))
            return out
        if self.tab == 4:
            return [("%s (%s)" % (w.get("thai", "?"), w.get("roman", "?")),
                     w.get("meaning", "")) for w in state.words]
        if self.tab == 5:
            return [(c, "") for c in state.catches]
        if self.tab == 6:
            out = []
            for sid in state.pages:
                stop = ST.STOP_BY_ID.get(sid)
                head = ST.chapter(stop) if stop else sid
                for sight in ST.icons_of(sid):
                    out.append(("%s: %s" % (head, sight), ""))
            return out
        # tab 7 — the story so far, so a player never loses the plot
        out = []
        act = state.act_of()
        act_name = {a: n for a, n, _lo, _hi in ST.ACTS}.get(act, "Prologue")
        out.append(("Chapter %d" % act, act_name))
        out.append(("Lom the Monsoon", "a thief of memory, one page per town"))
        for sid in state.visited:
            stop = ST.STOP_BY_ID.get(sid)
            if stop:
                out.append((ST.chapter(stop), stop["title"]))
        if state.journey_done():
            out.append(("THE WAI KHRU", "go home to Yaai's house"))
        return out

    def _visible(self):
        return max(1, (self.rect.height - 17 - 28 - 24) // self.ROW_H)

    def _clamp(self):
        entries = self._entries()
        visible = self._visible()
        self.sel = max(0, min(self.sel, max(0, len(entries) - 1)))
        if self.sel < self.scroll:
            self.scroll = self.sel
        elif self.sel >= self.scroll + visible:
            self.scroll = self.sel - visible + 1
        self.scroll = max(0, self.scroll)

    # ------------------------------------------------------------------ events
    def handle_event(self, ev):
        if mouse.cancelled(ev):
            self.close()
            return "close"
        if mouse.clicked(ev):
            header = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 15)
            if header.collidepoint(ev.pos):
                self.tab = (self.tab + 1) % len(self.TABS)
                self.sel = 0
                self.scroll = 0
                audio.sfx("click")
                return None
            top = self.rect.y + 17
            i = (ev.pos[1] - top) // self.ROW_H + self.scroll
            if 0 <= i < len(self._entries()):
                self.sel = i
                self._clamp()
            return None
        if ev.type == pygame.MOUSEWHEEL:
            self.sel = max(0, self.sel - ev.y)
            self._clamp()
            return None
        if ev.type != pygame.KEYDOWN:
            return None
        if ev.key == pygame.K_ESCAPE or keymap.pressed("cancel", ev) \
                or keymap.pressed("journal", ev):
            self.close()
            return "close"
        if ev.key in (pygame.K_LEFT, pygame.K_a):
            self.tab = (self.tab - 1) % len(self.TABS)
            self.sel = 0
            self.scroll = 0
        elif ev.key in (pygame.K_RIGHT, pygame.K_d):
            self.tab = (self.tab + 1) % len(self.TABS)
            self.sel = 0
            self.scroll = 0
        elif ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = max(0, self.sel - 1)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = self.sel + 1
        self._clamp()
        return None

    # --------------------------------------------------------------------- draw
    def draw(self, screen):
        from . import story as ST
        _dim(screen)
        pixel.panel(screen, self.rect, S.PANEL_BG, S.PANEL_BORDER,
                    inner_highlight=S.PANEL_EDGE)
        title = "JOURNAL  %d/%d" % (self.game.state.journal_count(),
                                    ST.TOTAL_STOPS)
        self._header(screen, title, "< %s >" % self.TABS[self.tab])
        entries = self._entries()
        top = self.rect.y + 17
        visible = self._visible()
        for i in range(visible):
            index = self.scroll + i
            if index >= len(entries):
                break
            head, tail = entries[index]
            y = top + i * self.ROW_H
            if index == self.sel and entries:
                row = pygame.Rect(self.rect.x + 4, y, self.rect.width - 8,
                                  self.ROW_H - 1)
                pygame.draw.rect(screen, S.PANEL_BG_ALT, row)
                pygame.draw.rect(screen, S.SPIRIT, row, 1)
            pixel.draw_text(screen, head[:40], (self.rect.x + 8, y + 2),
                            S.TEXT if index == self.sel else S.MUTED, shadow=None)
        if not entries:
            pixel.draw_text(screen, "empty — go find a page",
                            (self.rect.x + 8, top + 4), S.MUTED, shadow=None)
        elif entries[self.sel][1]:
            # the selected entry's detail gets its own strip, so rows
            # never overlap each other the way they used to. Lore
            # documents get a taller strip — they are worth reading.
            _head, tail = entries[self.sel]
            wrapped = pixel.wrap(tail, self.rect.width - 16, 8)
            rows = min(6, max(2, len(wrapped)))
            box = pygame.Rect(self.rect.x + 4, self.rect.bottom - 12 - rows * 10,
                              self.rect.width - 8, rows * 10 + 2)
            pygame.draw.rect(screen, S.PANEL_BG_ALT, box)
            pygame.draw.rect(screen, S.PANEL_BORDER, box, 1)
            for j, line in enumerate(wrapped[:rows]):
                pixel.draw_text(screen, line, (box.x + 4, box.y + 3 + j * 10),
                                S.SPIRIT, shadow=None)
        self._footer(screen, "click tab <>   arrows browse   J/esc close")


class MapView(Menu):
    """The full South on one screen: towns, storms, and you."""

    MW, MH = 280, 220

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.rect = pygame.Rect((S.INTERNAL_W - 420) // 2,
                                (S.INTERNAL_H - 320) // 2, 420, 320)
        self._base = None

    def open(self):
        super().open()
        self._base = None               # rebuilt fresh: towns change colour

    def _build_base(self):
        from . import world_map as WM
        tm = self.game.scenes["overworld"].tm
        base = pygame.Surface((self.MW, self.MH))
        sx, sy = self.MW / WM.WORLD_COLS, self.MH / WM.WORLD_ROWS
        step_x = max(1, WM.WORLD_COLS // self.MW)
        step_y = max(1, WM.WORLD_ROWS // self.MH)
        for r in range(0, WM.WORLD_ROWS, step_y):
            row = tm.grid[r]
            py = int(r * sy)
            h = max(1, int(step_y * sy) + 1)
            for c in range(0, WM.WORLD_COLS, step_x):
                k = row[c]
                col = (58, 116, 150) if k == "W" else (
                    (196, 176, 126) if k == "A" else
                    ((124, 128, 136) if k == "S" else
                     ((36, 88, 52) if k == "H" else
                      ((142, 106, 68) if k == "D" else (72, 138, 70)))))
                base.fill(col, pygame.Rect(int(c * sx), py,
                                           max(1, int(step_x * sx) + 1), h))
        self._base = base

    def _dot(self, screen, ox, oy, c, r, color, big=False):
        from . import world_map as WM
        sx = ox + int(c / WM.WORLD_COLS * self.MW)
        sy = oy + int(r / WM.WORLD_ROWS * self.MH)
        s = 2 if big else 1
        screen.fill(color, pygame.Rect(sx - s // 2, sy - s // 2, s + 1, s + 1))

    # ------------------------------------------------------------------ events
    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            self.close()
            return "close"
        if ev.type != pygame.KEYDOWN:
            return None
        self.close()
        return "close"

    # --------------------------------------------------------------------- draw
    def draw(self, screen):
        from . import story as ST
        _dim(screen)
        pixel.panel(screen, self.rect, S.PANEL_BG, S.PANEL_BORDER,
                    inner_highlight=S.PANEL_EDGE)
        self._header(screen, "THE SOUTH", "M close")
        if self._base is None:
            self._build_base()
        ox = self.rect.x + (self.rect.width - self.MW) // 2
        oy = self.rect.y + 18
        screen.blit(self._base, (ox, oy))
        st = self.game.state
        for stop in ST.STOPS:
            c, r = stop["pos"]
            if stop["id"] in st.pages:
                col = (120, 226, 120)
            else:
                col = (232, 96, 96) if stop["kind"] == "province" else (244, 166, 188)
            self._dot(screen, ox, oy, c, r, col)
        pc, pr = ST.PROLOGUE["pos"]
        self._dot(screen, ox, oy, pc, pr, (255, 216, 150), big=True)
        ow = self.game.scenes["overworld"]
        self._dot(screen, ox, oy, int(ow.player.x // 16), int(ow.player.y // 16),
                  (255, 255, 255), big=True)
        for s in ow.storms:
            self._dot(screen, ox, oy, int(s["x"] // 16), int(s["y"] // 16),
                      (150, 170, 210))
        tgt = ow._compass_target()
        if tgt is not None:
            from . import world_map as WM
            c, r = tgt["pos"]
            sx = ox + int(c / WM.WORLD_COLS * self.MW)
            sy = oy + int(r / WM.WORLD_ROWS * self.MH)
            pygame.draw.rect(screen, (255, 216, 150),
                             pygame.Rect(sx - 3, sy - 3, 7, 7), 1)
        self._footer(screen, "red town  pink secret  gold home  white you")
