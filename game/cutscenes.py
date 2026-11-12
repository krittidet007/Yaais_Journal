"""Cutscene data — the shots, and what is said in them.

Focus is written as ("stop", <stop id>, dx, dy) in tile units, so a
cutscene keeps working when the world is rebuilt at a new size.
"""

CUTSCENES = {
    # ------------------------------------------------------------ the storm
    "the_storm": {
        "music": "finale",
        "shots": [
            {
                "focus": ("stop", "prologue", 0, 0),
                "zoom": 1.35,
                "hold": 1.6,
                "fade": 0.35,
                "lines": [
                    ("NARRATOR", "TEXT",
                     "The night the pages went. It did not begin as weather."),
                    ("NARRATOR", "TEXT",
                     "It began as a knocking. Not on the door. In the walls, "
                     "the way a boat knocks in a harbour."),
                ],
            },
            {
                "focus": ("stop", "prologue", -3, -2),
                "zoom": 1.8,
                "hold": 1.4,
                "fade": 0.55,
                "lines": [
                    ("NOI", "NOI",
                     "That is the wind, in a house with a good roof. "
                     "You do not knock in a good roof. You go round."),
                ],
            },
            {
                "focus": ("stop", "prologue", 0, 0),
                "zoom": 1.2,
                "hold": 2.2,
                "lines": [
                    ("NARRATOR", "TEXT",
                     "The window was shut. The latch was tied with a strip "
                     "of cloth, the way Yaai ties it every night."),
                    ("NOI", "NOI",
                     "And on the sill, one black-and-white feather, wet, "
                     "and warm, and not from any bird that nests here."),
                ],
            },
        ],
    },

    # ------------------------------------------------------------- the cup
    "the_cup": {
        "music": "finale",
        "shots": [
            {
                "focus": ("stop", "narathiwat", 0, -6),
                "zoom": 1.25,
                "hold": 1.8,
                "lines": [
                    ("NARRATOR", "TEXT",
                     "The pass at last. The lamps in the shrine are all "
                     "broken, one at a time, neatly, by somebody keeping a "
                     "promise to come back."),
                ],
            },
            {
                "focus": ("stop", "narathiwat", 0, -6),
                "zoom": 1.9,
                "hold": 2.0,
                "lines": [
                    ("NARRATOR", "TEXT",
                     "Inside, on the stone floor, two cups. Both clean. "
                     "Both full."),
                    ("NOI", "NOI",
                     "Two. Not one. Forty years I have been told there was "
                     "one, and there are two, and I do not know which of "
                     "those is worse."),
                ],
            },
            {
                "focus": ("stop", "narathiwat", 0, -6),
                "zoom": 1.45,
                "hold": 2.4,
                "lines": [
                    ("LOM", "SPIRIT",
                     "Sit down, little flame. You have carried my letters "
                     "a long way and you never once opened them."),
                    ("NOI", "NOI",
                     "Lom. He has been waiting to be asked. That is the "
                     "whole crime. Not the pages. The waiting."),
                ],
            },
            {
                "focus": ("stop", "narathiwat", 0, -6),
                "zoom": 1.1,
                "hold": 3.0,
                "lines": [
                    ("LOM", "SPIRIT",
                     "Yaai took a boy out of a binding and did not put him "
                     "back. A binding with two in it belongs to nobody, and "
                     "I have been nobody for forty years."),
                    ("NOI", "NOI",
                     "So he collected the stories to make himself heavy "
                     "enough to be somebody again."),
                    ("LOM", "SPIRIT",
                     "I collected the stories so that nobody could be "
                     "forgotten. There is a difference. You are old enough "
                     "to know which of us is lying."),
                ],
            },
        ],
    },
}
