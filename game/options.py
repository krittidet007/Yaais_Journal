"""Player-facing options with disk persistence.

Deliberately has **no pygame dependency** so it can be imported from anywhere
(the renderer, the atmosphere pass, the scene code) without cycles. Key names
are stored as strings; use ``game.keymap`` to turn them into pygame key codes.
"""

import json
import os

if os.name == "nt":
    # Windows: keep settings and saves in %APPDATA%, not a Unix-style ~/.config
    _BASE = os.environ.get("APPDATA") or os.path.expanduser("~")
else:
    _BASE = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
CONFIG_DIR = os.path.join(_BASE, "wicha")
CONFIG_PATH = os.path.join(CONFIG_DIR, "options.json")
SAVE_PATH = os.path.join(CONFIG_DIR, "save.json")

# Row descriptors, in the order shown in the settings menu:
#   ("slider", key, label, lo, hi, step)
#   ("choice", key, label, (choices...))
#   ("action", key, label, action_id)
ROWS = (
    ("slider", "master_volume", "Master Volume", 0, 100, 5),
    ("slider", "music_volume", "Music Volume", 0, 100, 5),
    ("slider", "sfx_volume", "SFX Volume", 0, 100, 5),
    ("choice", "music_source", "Music", ("Auto", "Soundtrack", "Chiptune", "Off")),
    ("slider", "brightness", "Brightness", 0, 200, 5),
    ("slider", "contrast", "Contrast", 0, 200, 5),
    ("choice", "display_mode", "Display", ("Windowed", "Borderless", "Fullscreen")),
    ("choice", "vsync", "V-Sync", ("On", "Off")),
    ("choice", "supersample", "Super-sampling", ("On", "Off")),
    ("choice", "scale", "Screen Scale", ("Auto", "1x", "2x", "3x", "4x")),
    ("choice", "text_speed", "Text Speed", ("Slow", "Normal", "Fast", "Instant")),
    ("choice", "particles", "Particles", ("On", "Off")),
    ("choice", "prompts", "Prompt Hints", ("On", "Off")),
    ("choice", "vignette", "Vignette", ("On", "Off")),
    ("choice", "fps", "Show FPS", ("On", "Off")),
    ("choice", "skip_splash", "Skip Splash", ("Off", "On")),
    ("choice", "autosave", "Autosave", ("On", "Off")),
    ("action", "keybinds", "Key Bindings", "keys"),
    ("action", "save", "Save / Load", "save"),
)

DEFAULTS = {
    "master_volume": 80,
    "music_volume": 55,
    "sfx_volume": 80,
    "music_source": "Auto",
    "brightness": 100,
    "contrast": 100,
    "display_mode": "Windowed",
    "vsync": "Off",
    "supersample": "Off",
    "scale": "Auto",
    "text_speed": "Normal",
    "particles": "On",
    "prompts": "On",
    "vignette": "On",
    "fps": "Off",
    "skip_splash": "Off",
    "autosave": "On",
}

# Rebindable actions (movement stays on arrows/WASD, the editor needs its keys).
KEY_ACTIONS = (
    ("confirm", "Confirm / Interact"),
    ("items", "Open Items"),
    ("journal", "Open Journal"),
    ("fish", "Cast Line / Reel In"),
    ("map", "Open Map"),
    ("settings", "Open Settings"),
    ("save", "Save / Load Menu"),
    ("run", "Run (hold)"),
    ("glide", "Glide (hold)"),
    ("cancel", "Cancel / Back"),
)
KEY_DEFAULTS = {"confirm": "e", "items": "i", "journal": "j", "fish": "f",
                "map": "m", "settings": "o",
                "save": "f5", "run": "left shift", "glide": "x", "cancel": "escape"}

TEXT_CPS = {"Slow": 16.0, "Normal": 42.0, "Fast": 82.0, "Instant": 1_000_000.0}

_row_by_key = {row[1]: row for row in ROWS}


class Options:
    def __init__(self):
        self.values = dict(DEFAULTS)
        self.keys = dict(KEY_DEFAULTS)
        self.load()

    # ------------------------------------------------------------- persistence
    def load(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return
        if not isinstance(data, dict):
            return
        values = data.get("values", data)      # accept the old flat format too
        keys = data.get("keys", {})
        if isinstance(values, dict):
            for key, value in values.items():
                if key in self.values:
                    self.values[key] = value
        if isinstance(keys, dict):
            for action, name in keys.items():
                if action in KEY_DEFAULTS and isinstance(name, str):
                    self.keys[action] = name
        self._clamp()

    def _clamp(self):
        for row in ROWS:
            if row[0] == "slider":
                _, key, _, lo, hi, _step = row
                try:
                    self.values[key] = max(lo, min(hi, int(self.values[key])))
                except (TypeError, ValueError):
                    self.values[key] = DEFAULTS[key]
            elif row[0] == "choice":
                _, key, _, choices = row
                if self.values.get(key) not in choices:
                    self.values[key] = DEFAULTS[key]
        # keep the old single value for backward compatibility if present
        self.values.pop("fullscreen", None)

    def save(self):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
                json.dump({"values": self.values, "keys": self.keys}, fh, indent=2)
        except OSError:
            pass

    # ------------------------------------------------------------------ access
    def get(self, key):
        return self.values.get(key, DEFAULTS.get(key))

    def set(self, key, value):
        self.values[key] = value
        self._clamp()
        self.save()

    def adjust(self, key, direction):
        row = _row_by_key.get(key)
        if row is None:
            return
        if row[0] == "slider":
            _, _, _, lo, hi, step = row
            value = int(self.values[key]) + direction * step
            self.set(key, max(lo, min(hi, value)))
        elif row[0] == "choice":
            choices = row[3]
            index = (choices.index(self.values[key]) + direction) % len(choices)
            self.set(key, choices[index])

    def key_name(self, action):
        return self.keys.get(action, KEY_DEFAULTS.get(action, ""))

    def set_key(self, action, name):
        self.keys[action] = name
        self.save()

    # ----------------------------------------------------------------- helpers
    def master(self):
        return self.values["master_volume"] / 100.0

    def music(self):
        return self.values["music_volume"] / 100.0

    def sfx(self):
        return self.values["sfx_volume"] / 100.0

    def music_source(self):
        value = self.get("music_source")
        return value if value in ("Auto", "Soundtrack", "Chiptune", "Off") else "Auto"

    def text_cps(self):
        return TEXT_CPS[self.get("text_speed")]

    def particles_on(self):
        return self.get("particles") == "On"

    def prompts_on(self):
        return self.get("prompts") == "On"

    def vignette_on(self):
        return self.get("vignette") == "On"

    def fps_on(self):
        return self.get("fps") == "On"

    def vsync_on(self):
        return self.get("vsync") == "On"

    def supersample_on(self):
        return self.get("supersample") == "On"

    def skip_splash_on(self):
        return self.get("skip_splash") == "On"

    def autosave_on(self):
        return self.get("autosave") == "On"

    def display_mode(self):
        return self.get("display_mode")

    def scale_override(self):
        value = self.get("scale")
        return None if value == "Auto" else int(value[0])

    def brightness(self):
        return int(self.get("brightness"))

    def contrast(self):
        return int(self.get("contrast"))


options = Options()
