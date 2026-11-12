"""Autosave / load + manual 3-slot saves.

Autosave (used by the cover's Continue) lives in ``save.json``; manual slots live
in ``saves.json`` and are exposed through the Save/Load UI.
"""

import json
import os
import time

from . import options as O

RESUMABLE = ("washup", "hub", "overworld",
             "village_naming", "shrine", "well", "epilogue")

SLOTS_PATH = os.path.join(O.CONFIG_DIR, "saves.json")


# --------------------------------------------------------------- autosave file
def path():
    return O.SAVE_PATH


def has_save():
    return os.path.exists(path())


def write(state, scene_name):
    try:
        os.makedirs(O.CONFIG_DIR, exist_ok=True)
        payload = {"scene": scene_name, "state": state.to_dict()}
        with open(path(), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        return True
    except OSError:
        return False


def read():
    try:
        with open(path(), "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or "scene" not in data:
        return None
    if data["scene"] not in RESUMABLE:
        return None
    return data


def clear():
    try:
        os.remove(path())
    except OSError:
        pass


# ------------------------------------------------------------------- save slots
def _load_slots():
    try:
        with open(SLOTS_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _store_slots(slots):
    try:
        os.makedirs(O.CONFIG_DIR, exist_ok=True)
        with open(SLOTS_PATH, "w", encoding="utf-8") as fh:
            json.dump(slots, fh, indent=2)
        return True
    except OSError:
        return False


def write_slot(index, state, scene_name):
    """Write the current game into manual slot ``index`` (1..3)."""
    slots = _load_slots()
    slots[str(index)] = {
        "scene": scene_name,
        "state": state.to_dict(),
        "time": time.strftime("%y-%m-%d %H:%M"),
    }
    return _store_slots(slots)


def read_slot(index):
    """Validated save data for a slot, or None when empty/broken."""
    slots = _load_slots()
    data = slots.get(str(index))
    if not isinstance(data, dict) or data.get("scene") not in RESUMABLE:
        return None
    return data


def slot_info(index):
    """A small summary for the menu, or None when the slot is empty."""
    data = read_slot(index)
    if data is None:
        return None
    st = data.get("state") or {}
    items = st.get("items")
    return {
        "scene": data.get("scene", ""),
        "name": st.get("spirit_name") or "",
        "items": len(items) if isinstance(items, list) else 0,
        "time": data.get("time", ""),
    }


def has_slots():
    return any(read_slot(i) is not None for i in (1, 2, 3))