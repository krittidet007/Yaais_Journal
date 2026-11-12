"""Persistent state across scenes and sessions.

Region 1's village ward puzzle keeps its original fields; the Southern
Thailand adventure adds the four systems the journal design is built on:
journal pages, the Culture Codex, Pak Tai words, and the Spice/Respect
meters. Everything serialises so saves stay one file.
"""

from . import story as ST


class GameState:
    def __init__(self):
        # ---- Region 1 ward puzzle (kept)
        self.spirit_name = ""
        self.offering = ""
        self.named = False
        self.shrine_done = False
        self.well_done = False
        self.items = []
        # ---- Yaai's Journal
        self.pages = []          # stop ids whose journal page is recovered
        self.cards = []          # Culture Codex entries
        self.words = []          # {thai, roman, meaning}
        self.visited = []        # stop ids completed
        self.spice = 0            # 0..5 Spice Meter
        self.respect = 0         # Respect Meter
        self.noi_rank = 0        # Noi's Southern fluency, grows each stop
        self.finale_done = False
        self.pos = None          # [x, y] world px where you stand (no teleport)
        self.found = []          # stop ids whose hidden spark is found
        self.landmarks = []      # landmark ids you have walked to and heard
        self.fuel = 100.0        # glide fuel: sparks refill it, gliding burns it
        self.combo = 0           # clean tablet solves in a row (OROI combo)
        self.catches = []        # fishing log, oldest first
        self.play_t = 0.0        # seconds lived in the South (drives day/night)
        self.flags = []          # story milestones (forgery accused/solved...)
        self.failed = []         # stops whose tablet ever stumped you (hosts remember)
        self.khaek = 0           # times you caught the magpie spirit's tail
        self.act_seen = 0        # highest act reached (Lom taunts on change)
        self.quests = {}         # stop id -> beats done (meet 1, look 2, solve 3)
        self.caught = 0          # times the danger-mobs got their claws in you

    # ------------------------------------------------------------------ items
    def give_item(self, item_id):
        """Add an item once; returns True if it was newly collected."""
        if item_id in self.items:
            return False
        self.items.append(item_id)
        from . import audio
        audio.sfx("collect")
        return True

    def has_item(self, item_id):
        return item_id in self.items

    def display_spirit_name(self):
        return self.spirit_name if self.spirit_name else "SPIRIT"

    # ------------------------------------------------------------- the journal
    def stop_done(self, stop_id):
        return stop_id in self.visited

    def stop_known(self, stop_id):
        """A stop is known once its page is collected or it has been visited."""
        return stop_id in self.visited or stop_id in self.pages

    def add_page(self, stop_id):
        if stop_id in self.pages:
            return False
        self.pages.append(stop_id)
        return True

    def add_card(self, name):
        if name in self.cards:
            return False
        self.cards.append(name)
        return True

    def add_word(self, word):
        roman = (word or {}).get("roman", "")
        if not roman or any(w.get("roman") == roman for w in self.words):
            return False
        self.words.append(dict(word))
        return True

    def complete_stop(self, stop):
        """Record a finished stop's page, cards and word."""
        fresh = self.add_page(stop["id"])
        if stop["id"] not in self.visited:
            self.visited.append(stop["id"])
        gained = [c for c in stop.get("cards", []) if self.add_card(c)]
        if self.add_word(stop.get("word")) and "word" in stop:
            gained.append(stop["word"]["roman"])
        return fresh, gained

    def bump_spice(self, n):
        self.spice = max(0, min(5, self.spice + n))

    def bump_respect(self, n):
        self.respect = max(0, self.respect + n)

    def journal_count(self):
        return len(self.pages)

    def journal_total(self):
        return ST.TOTAL_PAGES

    def act_of(self):
        """The act the player is working on: the act of the first stop
        whose page is not yet collected (so finishing Act 1 rolls the
        HUD over to Act 2), or the last act once the journey is done."""
        for stop in ST.STOPS:
            if stop["id"] not in self.pages:
                return stop["act"]
        return ST.STOPS[-1]["act"]

    def journey_done(self):
        return all(s["id"] in self.pages for s in ST.STOPS)

    # --------------------------------------------------------------- sessions
    def reset(self):
        self.spirit_name = ""
        self.offering = ""
        self.named = False
        self.shrine_done = False
        self.well_done = False
        self.items = []
        self.pages = []
        self.cards = []
        self.words = []
        self.visited = []
        self.spice = 0
        self.respect = 0
        self.noi_rank = 0
        self.finale_done = False
        self.pos = None
        self.found = []
        self.landmarks = []
        self.fuel = 100.0
        self.combo = 0
        self.catches = []
        self.play_t = 0.0
        self.flags = []
        self.failed = []
        self.khaek = 0
        self.act_seen = 0
        self.quests = {}
        self.caught = 0

    def to_dict(self):
        return {
            "spirit_name": self.spirit_name,
            "offering": self.offering,
            "named": self.named,
            "shrine_done": self.shrine_done,
            "well_done": self.well_done,
            "items": list(self.items),
            "pages": list(self.pages),
            "cards": list(self.cards),
            "words": [dict(w) for w in self.words],
            "visited": list(self.visited),
            "spice": self.spice,
            "respect": self.respect,
            "noi_rank": self.noi_rank,
            "finale_done": self.finale_done,
            "pos": list(self.pos) if self.pos else None,
            "found": list(self.found),
            "landmarks": list(self.landmarks),
            "fuel": float(self.fuel),
            "combo": int(self.combo),
            "catches": list(self.catches),
            "play_t": float(self.play_t),
            "flags": list(self.flags),
            "failed": list(self.failed),
            "khaek": int(self.khaek),
            "act_seen": int(self.act_seen),
            "quests": dict(self.quests),
            "caught": int(self.caught),
        }

    def from_dict(self, data):
        self.reset()
        if not isinstance(data, dict):
            return
        self.spirit_name = str(data.get("spirit_name", ""))
        self.offering = str(data.get("offering", ""))
        self.named = bool(data.get("named", False))
        self.shrine_done = bool(data.get("shrine_done", False))
        self.well_done = bool(data.get("well_done", False))
        items = data.get("items", [])
        if isinstance(items, list):
            self.items = [str(item) for item in items]
        for key, dst in (("pages", "pages"), ("cards", "cards"),
                         ("visited", "visited")):
            val = data.get(key, [])
            if isinstance(val, list):
                setattr(self, dst, [str(v) for v in val])
        words = data.get("words", [])
        if isinstance(words, list):
            self.words = [dict(w) for w in words if isinstance(w, dict)]
        self.spice = int(data.get("spice", 0) or 0)
        self.respect = int(data.get("respect", 0) or 0)
        self.noi_rank = int(data.get("noi_rank", 0) or 0)
        self.finale_done = bool(data.get("finale_done", False))
        pos = data.get("pos")
        if (isinstance(pos, (list, tuple)) and len(pos) == 2
                and all(isinstance(v, (int, float)) for v in pos)):
            self.pos = [float(pos[0]), float(pos[1])]
        found = data.get("found", [])
        if isinstance(found, list):
            self.found = [str(v) for v in found]
        marks = data.get("landmarks", [])
        if isinstance(marks, list):
            self.landmarks = [str(v) for v in marks]
        try:
            self.fuel = max(0.0, min(100.0, float(data.get("fuel", 100.0))))
        except (TypeError, ValueError):
            self.fuel = 100.0
        try:
            self.combo = max(0, int(data.get("combo", 0) or 0))
        except (TypeError, ValueError):
            self.combo = 0
        catches = data.get("catches", [])
        if isinstance(catches, list):
            self.catches = [str(v) for v in catches]
        try:
            self.play_t = max(0.0, float(data.get("play_t", 0.0) or 0.0))
        except (TypeError, ValueError):
            self.play_t = 0.0
        flags = data.get("flags", [])
        if isinstance(flags, list):
            self.flags = [str(v) for v in flags]
        failed = data.get("failed", [])
        if isinstance(failed, list):
            self.failed = [str(v) for v in failed]
        try:
            self.khaek = max(0, int(data.get("khaek", 0) or 0))
        except (TypeError, ValueError):
            self.khaek = 0
        try:
            self.act_seen = max(1, int(data.get("act_seen", 1) or 1))
        except (TypeError, ValueError):
            self.act_seen = 1
        quests = data.get("quests", {})
        if isinstance(quests, dict):
            self.quests = {str(k): int(v) for k, v in quests.items()
                           if isinstance(v, int)}
        try:
            self.caught = max(0, int(data.get("caught", 0) or 0))
        except (TypeError, ValueError):
            self.caught = 0


state = GameState()
