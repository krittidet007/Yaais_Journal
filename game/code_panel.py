"""The diegetic rune-tablet code editor, drawn in the pixel UI style."""

import pygame

from . import pixel
from . import settings as S

CTRL = pygame.KMOD_CTRL | pygame.KMOD_LCTRL | pygame.KMOD_RCTRL
LINE_H = 10


class CodePanel:
    def __init__(self, on_run):
        self.on_run = on_run
        self.rect = pygame.Rect(10, 8, 300, S.INTERNAL_H - 16)
        x, y, w = self.rect.x, self.rect.y, self.rect.width
        self.title_rect = pygame.Rect(x, y, w, 15)
        # console + status anchored to the bottom of the tablet, editor fills the rest
        self.console_rect = pygame.Rect(x + 6, self.rect.bottom - 21 - 34 - 26, w - 12, 26)
        self.status_rect = pygame.Rect(x + 6, self.rect.bottom - 21 - 34, w - 12, 34)
        editor_top = y + 18
        self.editor_rect = pygame.Rect(x + 6, editor_top, w - 12,
                                       self.console_rect.y - 4 - editor_top)
        self.gutter_w = 20
        self.visible_lines = self.editor_rect.height // LINE_H

        self.visible = False
        self.title = "RUNE TABLET"
        self.lines = [""]
        self.row = 0
        self.col = 0
        self.scroll = 0
        self.console = []
        self.status = ""
        self._status_color = S.MUTED
        self.run_rect = None
        self._blink = 0.0
        self.teach = ""           # plain-language help for this spell
        self.help = False         # F1 cheat-sheet overlay
        self._help_scroll = 0

    # ---------------------------------------------------------------- control
    def open(self, title, prefill, status="", teach=""):
        self.title = title
        self.lines = prefill.split("\n") if prefill else [""]
        self.row = 0
        self.col = len(self.lines[0])
        self.scroll = 0
        self.console = []
        self.status = status
        self._status_color = S.MUTED
        self.teach = teach
        self.help = False
        self.visible = True

    def close(self):
        self.visible = False

    def reopen(self):
        self.visible = True

    def set_console(self, text, color=None):
        self.console = [(line, color or S.TEXT) for line in str(text).split("\n")]

    def set_status(self, text, color=None):
        self.status = text
        self._status_color = color or S.MUTED

    def code(self):
        return "\n".join(self.lines)

    def update(self, dt):
        self._blink += dt

    # ------------------------------------------------------------------ input
    def handle_event(self, ev):
        if not self.visible:
            return None
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.run_rect and self.run_rect.collidepoint(ev.pos):
                self._run()
            return None
        if ev.type != pygame.KEYDOWN:
            return None

        if ev.key == pygame.K_ESCAPE:
            if self.help:
                self.help = False
                return None
            return "close"
        if ev.key in (pygame.K_F1, pygame.K_SLASH) and not (getattr(ev, "mod", 0) & CTRL):
            self.help = not self.help
            return None
        if self.help:
            return None
        if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if ev.mod & CTRL:
                self._run()
            else:
                self._newline()
            return None
        if ev.key == pygame.K_TAB:
            self._insert("    ")
            return None
        if ev.key == pygame.K_BACKSPACE:
            self._backspace()
            return None
        if ev.key == pygame.K_DELETE:
            self._delete()
            return None
        if ev.key == pygame.K_LEFT:
            self._move(-1)
            return None
        if ev.key == pygame.K_RIGHT:
            self._move(1)
            return None
        if ev.key == pygame.K_UP:
            self._move_vertical(-1)
            return None
        if ev.key == pygame.K_DOWN:
            self._move_vertical(1)
            return None
        if ev.key == pygame.K_HOME:
            self.col = 0
            return None
        if ev.key == pygame.K_END:
            self.col = len(self.lines[self.row])
            return None
        if ev.key == pygame.K_PAGEUP:
            self.row = max(0, self.row - self.visible_lines)
            self.col = min(self.col, len(self.lines[self.row]))
            self._keep_visible()
            return None
        if ev.key == pygame.K_PAGEDOWN:
            self.row = min(len(self.lines) - 1, self.row + self.visible_lines)
            self.col = min(self.col, len(self.lines[self.row]))
            self._keep_visible()
            return None

        if not (getattr(ev, "mod", 0) & CTRL) and getattr(ev, "unicode", "") and ev.unicode.isprintable():
            self._insert(ev.unicode)
        return None

    # ------------------------------------------------------------- editing
    def _insert(self, text):
        line = self.lines[self.row]
        self.lines[self.row] = line[: self.col] + text + line[self.col :]
        self.col += len(text)

    def _newline(self):
        line = self.lines[self.row]
        indent = line[: len(line) - len(line.lstrip(" "))]
        before, after = line[: self.col], line[self.col :]
        self.lines[self.row] = before
        self.lines.insert(self.row + 1, indent + after)
        self.row += 1
        self.col = len(indent)
        self._keep_visible()

    def _backspace(self):
        if self.col > 0:
            line = self.lines[self.row]
            self.lines[self.row] = line[: self.col - 1] + line[self.col :]
            self.col -= 1
        elif self.row > 0:
            prev = self.lines[self.row - 1]
            self.col = len(prev)
            self.lines[self.row - 1] = prev + self.lines[self.row]
            del self.lines[self.row]
            self.row -= 1
            self._keep_visible()

    def _delete(self):
        line = self.lines[self.row]
        if self.col < len(line):
            self.lines[self.row] = line[: self.col] + line[self.col + 1 :]
        elif self.row < len(self.lines) - 1:
            self.lines[self.row] = line + self.lines[self.row + 1]
            del self.lines[self.row + 1]

    def _move(self, delta):
        target = self.col + delta
        if 0 <= target <= len(self.lines[self.row]):
            self.col = target
        elif delta < 0 and self.row > 0:
            self.row -= 1
            self.col = len(self.lines[self.row])
            self._keep_visible()
        elif delta > 0 and self.row < len(self.lines) - 1:
            self.row += 1
            self.col = 0
            self._keep_visible()

    def _move_vertical(self, delta):
        self.row = max(0, min(len(self.lines) - 1, self.row + delta))
        self.col = min(self.col, len(self.lines[self.row]))
        self._keep_visible()

    def _keep_visible(self):
        if self.row < self.scroll:
            self.scroll = self.row
        elif self.row >= self.scroll + self.visible_lines:
            self.scroll = self.row - self.visible_lines + 1

    def _run(self):
        self.on_run(self.code())

    # ------------------------------------------------------------------- draw
    def draw(self, screen):
        if not self.visible:
            return

        pixel.panel(screen, self.rect, S.PANEL_BG, S.PANEL_BORDER, inner_highlight=S.PANEL_EDGE)
        pygame.draw.rect(screen, S.PANEL_BG_ALT, self.title_rect)
        pixel.draw_text(screen, self.title[:22], (self.title_rect.x + 5, self.title_rect.y + 4), S.SPIRIT)
        hint = "F1 help"
        pixel.draw_text(screen, hint, (self.title_rect.right - pixel.text_size(hint)[0] - 5,
                                       self.title_rect.y + 4), S.MUTED, shadow=None)

        # editor well
        pygame.draw.rect(screen, (14, 16, 26), self.editor_rect)
        screen.set_clip(self.editor_rect)
        for i in range(self.visible_lines):
            index = self.scroll + i
            if index >= len(self.lines):
                break
            y = self.editor_rect.y + 2 + i * LINE_H
            pixel.draw_text(screen, str(index + 1).rjust(2), (self.editor_rect.x + 2, y), (86, 94, 120), shadow=None)
            pixel.draw_text(screen, self.lines[index][:34], (self.editor_rect.x + self.gutter_w, y), S.TEXT, shadow=None)

        if int(self._blink * 2) % 2 == 0:
            line = self.lines[self.row]
            cx = self.editor_rect.x + self.gutter_w + pixel.text_size(line[: self.col])[0]
            cy = self.editor_rect.y + 2 + (self.row - self.scroll) * LINE_H
            if self.editor_rect.collidepoint(cx, cy):
                pygame.draw.rect(screen, S.SPIRIT, pygame.Rect(cx, cy, 1, 8))
        screen.set_clip(None)

        # console
        y = self.console_rect.y + 2
        for text, color in self.console[-2:]:
            pixel.draw_text(screen, text[:36], (self.console_rect.x + 2, y), color, shadow=None)
            y += LINE_H

        # status
        status_lines = []
        for line in self.status.split("\n"):
            status_lines.extend(pixel.wrap(line, self.status_rect.width, 8))
        for i, line in enumerate(status_lines[:3]):
            pixel.draw_text(screen, line, (self.status_rect.x + 2, self.status_rect.y + i * LINE_H),
                            self._status_color, shadow=None)

        # bottom bar
        pixel.draw_text(screen, "ESC - step back", (self.rect.x + 6, self.rect.bottom - 13), S.MUTED, shadow=None)
        self.run_rect = pygame.Rect(self.rect.right - 52, self.rect.bottom - 15, 46, 13)
        pygame.draw.rect(screen, (28, 68, 60), self.run_rect)
        pygame.draw.rect(screen, S.SPIRIT, self.run_rect, 1)
        label = "RUN >"
        pixel.draw_text(screen, label, (self.run_rect.centerx - pixel.text_size(label)[0] // 2,
                                        self.run_rect.y + 3), S.SPIRIT, shadow=None)

        if self.help:
            self._draw_help(screen)

    def _draw_help(self, screen):
        """A beginner's cheat-sheet, over everything, one keypress away."""
        from . import story as ST
        veil = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        veil.fill((8, 10, 20, 250))
        screen.blit(veil, self.rect.topleft)
        screen.set_clip(self.rect)
        x, y = self.rect.x + 8, self.rect.y + 8
        pixel.draw_text(screen, "FIRST TIME CODING? START HERE", (x, y),
                        S.AMBER, shadow=None)
        y += 12
        for line in ST.PY_PRIMER:
            pixel.draw_text(screen, line, (x, y), S.TEXT, shadow=None)
            y += 9
        if self.teach:
            y += 4
            pixel.draw_text(screen, "THIS TABLET WANTS", (x, y), S.SPIRIT, shadow=None)
            y += 9
            for line in pixel.wrap(self.teach, self.rect.w - 16)[:4]:
                pixel.draw_text(screen, line, (x, y), S.MUTED, shadow=None)
                y += 9
        pixel.draw_text(screen, "F1 or ESC closes this page",
                        (x, self.rect.bottom - 22), S.MUTED, shadow=None)
        screen.set_clip(None)
