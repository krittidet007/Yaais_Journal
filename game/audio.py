"""Music and sound effects.

Two music layers:

- a **soundtrack** (optional): OGG files bundled under ``assets/music/`` stream
  through ``pygame.mixer.music`` — the "garden" track on menus, "dreamy" in
  the story scenes (see ``assets/music/CREDITS.md`` for the licences).
- a **procedural chiptune** loop, synthesised to 16-bit PCM, used as fallback
  when the files are missing, when the Music setting says so, or when the
  mixer cannot stream files.

SFX stay fully synthesised. If the mixer cannot start (headless / no audio
device) every function quietly becomes a no-op, so the rest of the game never
has to care.
"""

import array
import math
import os
import random

import pygame

from . import options as O

RATE = 22050
_ready = False
_chiptune = None
_sounds = {}
_last_scene = "cover"
_current_track = None
_chiptune_on = False

_MUSIC_DIR = os.path.join(os.path.dirname(__file__), "assets", "music")
# Licensed soundtrack: Kevin MacLeod (incompetech.com), CC BY 4.0.
TRACKS = (("garden", "Garden_Music.ogg"),      # cover / menus
          ("dreamy", "Dreamy_Flashback.ogg"),  # story scenes
          ("island", "Bumba_Crossing.ogg"),    # overworld by day
          ("night", "Meditation_Impromptu_01.ogg"),   # overworld by night
          ("sail", "Fluffing_a_Duck.ogg"),     # sailing the Andaman
          ("festival", "Monkeys_Spinning_Monkeys.ogg"),  # town festivals
          ("finale", "Meditation_Impromptu_02.ogg"))     # the Wai Khru

# scene -> track; moods set by gameplay override the scene track
SCENE_TRACK = {"cover": "garden", "splash": "garden",
               "overworld": "island", "finale": "finale"}
_mood = None


# --------------------------------------------------------------- audio bootstrap
def pre_init():
    """Call before pygame.init() so the mixer opens at our format."""
    try:
        pygame.mixer.pre_init(RATE, -16, 2, 512)
    except pygame.error:
        pass


def init():
    global _ready, _chiptune
    if _ready:
        return
    try:
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        pygame.mixer.init(RATE, -16, 2, 512)
        pygame.mixer.set_num_channels(16)
        _chiptune = _to_sound(_build_music())
        for name, fn in _SFX.items():
            _sounds[name] = _to_sound(fn())
        _ready = True
    except (pygame.error, ValueError):
        _ready = False
    apply_volumes()


def _to_sound(mono):
    channels = (pygame.mixer.get_init() or (RATE, -16, 2))[2]
    if channels >= 2:
        stereo = array.array("h")
        for sample in mono:
            stereo.append(sample)
            stereo.append(sample)
        return pygame.mixer.Sound(buffer=stereo.tobytes())
    return pygame.mixer.Sound(buffer=mono.tobytes())


# ------------------------------------------------------------------- synthesis
def _blank(seconds):
    return array.array("h", bytes(2 * int(RATE * seconds)))


def _finalize(samples):
    """Clamp a float sample list into a 16-bit PCM array."""
    out = array.array("h", bytes(2 * len(samples)))
    for i, value in enumerate(samples):
        out[i] = max(-32768, min(32767, int(value)))
    return out


def _mix(buf, start, samples, gain):
    for i, value in enumerate(samples):
        idx = start + i
        if idx >= len(buf):
            break
        total = buf[idx] + int(value * gain)
        buf[idx] = max(-32768, min(32767, total))


def _osc(freq, seconds, wave="tri"):
    n = int(RATE * seconds)
    out = [0.0] * n
    phase = 0.0
    step = freq / RATE
    for i in range(n):
        phase = (phase + step) % 1.0
        if wave == "square":
            out[i] = 1.0 if phase < 0.5 else -1.0
        elif wave == "saw":
            out[i] = 2.0 * phase - 1.0
        elif wave == "sine":
            out[i] = math.sin(2.0 * math.pi * phase)
        else:                                   # triangle
            out[i] = 4.0 * abs(phase - 0.5) - 1.0
    return out


def _note(freq, seconds, wave="tri", release=0.5, attack=0.01):
    osc = _osc(freq, seconds, wave)
    n = len(osc)
    for i in range(n):
        t = i / n
        env = min(1.0, t / attack) if attack > 0 else 1.0
        env *= min(1.0, (1.0 - t) / release) if release > 0 else 1.0
        osc[i] *= env * 9000
    return osc


def _midi(note):
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def _build_music():
    """An 8-second Am–F–C–G ambient loop: bass, arpeggio and pad."""
    seconds = 8.0
    buf = _blank(seconds)
    chords = (
        (57, 60, 64, 69),   # Am
        (53, 57, 60, 65),   # F
        (60, 64, 67, 72),   # C
        (55, 59, 62, 67),   # G
    )
    roots = (45, 41, 48, 43)
    arp_order = (0, 2, 1, 3, 2, 1, 3, 2)
    bar = 2.0
    step = bar / 8.0
    for b, chord in enumerate(chords):
        start = b * bar
        # pad
        for tone in (chord[0], chord[2]):
            _mix(buf, int(start * RATE), _note(_midi(tone) / 2.0, bar, "sine",
                                                release=0.2, attack=0.15), 0.5)
        # bass on the half-bars
        for half in range(2):
            _mix(buf, int((start + half * bar / 2) * RATE),
                 _note(_midi(roots[b]), bar / 2 - 0.05, "tri", release=0.25), 0.9)
        # arpeggio (eighth notes)
        for s in range(8):
            tone = chord[arp_order[s]]
            _mix(buf, int((start + s * step) * RATE),
                 _note(_midi(tone), step * 0.9, "square", release=0.4), 0.32)
    return buf


def _sfx_blip():
    return _finalize(_note(920, 0.05, "square", release=0.7, attack=0.0))


def _sfx_success():
    out = _blank(0.30)
    for i, note in enumerate((659, 880, 1319)):
        _mix(out, int(i * 0.07 * RATE), _note(note, 0.22, "tri", release=0.6), 1.0)
    return out


def _sfx_error():
    out = _note(150, 0.22, "saw", release=0.5, attack=0.0)
    rnd = random.Random(99)
    for i in range(len(out)):
        out[i] = int(out[i] * 0.7 + (rnd.random() * 2 - 1) * 4000 * (1 - i / len(out)))
    return _finalize(out)


def _sfx_collect():
    out = _blank(0.22)
    _mix(out, 0, _note(784, 0.10, "square", release=0.4), 1.0)
    _mix(out, int(0.08 * RATE), _note(1175, 0.14, "square", release=0.4), 1.0)
    return out


def _sfx_click():
    return _finalize(_note(440, 0.035, "square", release=0.5, attack=0.0))


def _sfx_splash():
    rnd = random.Random(7)
    out = _blank(0.35)
    for i in range(len(out)):
        env = (1 - i / len(out)) ** 2
        out[i] = int((rnd.random() * 2 - 1) * 9000 * env)
    return out


_SFX = {
    "blip": _sfx_blip,
    "success": _sfx_success,
    "error": _sfx_error,
    "collect": _sfx_collect,
    "click": _sfx_click,
    "splash": _sfx_splash,
}


# -------------------------------------------------------------------- playback
def _source():
    value = O.options.music_source()
    if value == "Auto":
        return "soundtrack" if any(_track_file(t) for t, _ in TRACKS) else "chiptune"
    return value.lower() if value in ("Soundtrack", "Chiptune", "Off") else "chiptune"


def _track_file(name):
    for track, filename in TRACKS:
        if track == name:
            path = os.path.join(_MUSIC_DIR, filename)
            return path if os.path.exists(path) else None
    return None


def _fallback_chiptune():
    global _chiptune_on
    if _chiptune is not None and not _chiptune_on:
        _chiptune.play(loops=-1, fade_ms=600)
        _chiptune_on = True


def set_mood(track):
    """Gameplay mood override (festival / night / sailing); None clears it."""
    global _mood
    if track is not None and _track_file(track) is None:
        track = None
    if track != _mood:
        _mood = track
        _retune()


def _wanted_track():
    if _mood is not None:
        return _mood
    return SCENE_TRACK.get(_last_scene, "dreamy")


def play_music(scene_name=None):
    """Make sure the right music is playing; call on every scene switch.

    Scene names map onto tracks (see SCENE_TRACK); a gameplay mood set
    with set_mood() overrides the scene track until the next switch.
    Missing files or a broken mixer channel fall back to procedural
    chiptune, and ``Off`` is silent.
    """
    global _last_scene, _current_track, _chiptune_on, _mood
    if not _ready:
        return
    if scene_name:
        _last_scene = scene_name
        _mood = None
    _retune()


def _retune():
    global _current_track, _chiptune_on
    source = _source()

    if source == "off":
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        if _chiptune is not None and _chiptune_on:
            _chiptune.stop()
        _current_track = None
        _chiptune_on = False
        return

    if source == "chiptune":
        if _current_track:
            pygame.mixer.music.stop()
            _current_track = None
        if not _chiptune_on:
            _fallback_chiptune()
        return

    # soundtrack
    if _chiptune_on:
        _chiptune.stop()
        _chiptune_on = False
    track = _wanted_track()
    path = _track_file(track)
    if path is None:                        # files not installed -> chiptune
        _fallback_chiptune()
        return
    if _current_track == track and pygame.mixer.music.get_busy():
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(loops=-1, fade_ms=600)
        _current_track = track
    except pygame.error:
        _current_track = None
        _fallback_chiptune()


def stop_music():
    global _current_track, _chiptune_on
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    if _chiptune is not None and _chiptune_on:
        _chiptune.stop()
    _current_track = None
    _chiptune_on = False


def apply_volumes():
    if not _ready:
        return
    if _chiptune is not None:
        _chiptune.set_volume(O.options.master() * O.options.music())
    try:
        pygame.mixer.music.set_volume(O.options.master() * O.options.music())
    except pygame.error:
        pass
    level = O.options.master() * O.options.sfx()
    for sound in _sounds.values():
        sound.set_volume(level)


def sfx(name):
    if not _ready:
        return
    sound = _sounds.get(name)
    if sound is not None:
        sound.play()
