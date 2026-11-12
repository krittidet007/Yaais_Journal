"""Side quests — the errands that make a province more than a page.

Each is a small story with a place to go and something to bring back.
The host gives them once their page is yours; the target is usually a
landmark, so a quest is a reason to walk somewhere you would otherwise
only look at. Finishing one pays respect and a card.

``from``    the host town that gives the quest
``at``      the landmark id the errand is about (or "stop:<id>")
``ask``     what the host says when they hand it to you
``answer``  what they say when you come back with it
``reward``  respect and an optional culture card
"""

SIDE_QUESTS = {
    # ------------------------------------------------------- the Gulf Shore
    "chumphon_lens": {
        "from": "chumphon",
        "at": "longtail_wreck",
        "ask": "Bang Dot wants something from the wreck, and will not "
               "go himself. Go and stand at the wreck and tell me what "
               "you can see of the boat.",
        "answer": "You saw the name? Then she is still hers. My mother "
                  "painted that name under the gunwale in the year she "
                  "was born, and no one has taken it off. Take this — a "
                  "piece of the same paint, for the sea.",
        "reward": {"respect": 2, "card": "The Wreck's Name"},
    },
    "ko_tao_count": {
        "from": "ko_tao",
        "at": "turtle_shadow",
        "ask": "Ploy wants a count, and she cannot leave the boats. Go "
               "and stand at the shadow on the sand and count how many "
               "flippers it has.",
        "answer": "Five. Five, and a tail, and a shadow of a shell with "
                  "a hole in it. That is the count my grandmother kept "
                  "for forty years. We are not stopping now.",
        "reward": {"respect": 2, "card": "The Count of Five"},
    },
    # ------------------------------------------------------ the Samui Sea
    "samui_low_tide": {
        "from": "ko_samui",
        "at": "grandparents_rock",
        "ask": "The old singer will not go to the rocks alone, at low "
               "water, in the dark. Go and stand where the two stones "
               "lean and come back and tell me if they have moved.",
        "answer": "Then they have not moved. Good. When my time comes I "
                  "want them exactly where they are, leaning the same "
                  "way. You have brought me back a piece of my own life.",
        "reward": {"respect": 2, "card": "A Piece of the Low Tide"},
    },
    "surat_the_rope": {
        "from": "surat_thani",
        "at": "chak_phra_ground",
        "ask": "The monks will pull their boat up the river on the "
               "festival day. I am old and I would like to see it from "
               "the bank. Go and stand on the ground where they pull, "
               "and tell me how many ropes.",
        "answer": "Eleven ropes and a twelfth with nobody on it. That is "
                  "how we count the years now: how many of us can still "
                  "pull. Go and pull with them next time. You are young "
                  "enough to be the rope.",
        "reward": {"respect": 2, "card": "The Eleventh Rope"},
    },
    # -------------------------------------------------- the Mangrove Isthmus
    "ranong_the_song": {
        "from": "ranong",
        "at": "moken_camp",
        "ask": "The old man in the boat camp is the only one left who "
               "sings the sea songs. Go and stand at his camp and ask "
               "him for the one about the flood.",
        "answer": "He sang it to you? Then he heard it in your voice "
                  "first. That is how it is supposed to go: an old song "
                  "sings itself back out of a young throat. Now it is "
                  "yours, and he will not sing it again.",
        "reward": {"respect": 3, "card": "The Song About the Flood"},
    },
    "surin_the_names": {
        "from": "surin_islands",
        "at": "the_standing_dead",
        "ask": "We write the names of the lost on the dead trees. There "
               "is a name I cannot read. Go and stand among the standing "
               "dead and find me the one that is not finished.",
        "answer": "That is my brother. It has been waiting eleven years "
                  "for somebody to finish it. Finish it, and put him in "
                  "the water, and let the sea have the rest of him.",
        "reward": {"respect": 3, "card": "The Unfinished Name"},
    },
    # -------------------------------------------------------- the Karst Sea
    "phang_nga_the_school": {
        "from": "phang_nga",
        "at": "the_floating_school",
        "ask": "The school floats away with the tide and I am too old to "
               "wade after it. Go and stand at the school and find out "
               "how many children are on the platform.",
        "answer": "Thirty-one. Thirty-one, and one teacher, and the "
                  "teacher is the one who taught me to read. That is the "
                  "whole of it, isn't it. One teacher, and who the "
                  "teacher has.",
        "reward": {"respect": 2, "card": "Thirty-One Children"},
    },
    "khao_lak_the_window": {
        "from": "khao_lak",
        "at": "the_low_tide_window",
        "ask": "There is a square hole in the cliff that the sea made. "
               "At the lowest tide you can stand in front of it. Go and "
               "stand there and tell me what is behind it.",
        "answer": "A wall. Of course it is a wall. I told myself for "
                  "sixty years there was a room behind it. A room would "
                  "have been kinder. A wall is simply the end of "
                  "something.",
        "reward": {"respect": 2, "card": "Behind the Square Window"},
    },
    "similan_the_ninth": {
        "from": "similan",
        "at": "the_nine_stones",
        "ask": "Nine stones for nine years. There ought to be a tenth. "
               "Go and stand at the stones and count them again, "
               "properly, in the light.",
        "answer": "Ten. There are ten. Somebody added one — a woman, "
                  "from the carving. He did not know. He counted the "
                  "stones that were there when he came, and he never "
                  "looked twice.",
        "reward": {"respect": 3, "card": "The Tenth Stone"},
    },
    # ------------------------------------------------------ the Pearl Coast
    "phuket_the_bell": {
        "from": "phuket",
        "at": "the_bell_tower",
        "ask": "The bell tower has no one to ring it. Go and stand under "
               "it and tell me whether the rope is still there.",
        "answer": "The rope. Of course there is a rope. Somebody has "
                  "been keeping the bell. Then this whole town has been "
                  "wrong about being alone.",
        "reward": {"respect": 2, "card": "The Rope in the Bell Tower"},
    },
    "promthep_the_stone": {
        "from": "promthep",
        "at": "the_promthep_lovers",
        "ask": "There is a stone at the end of the headland where the "
               "bird always sits. Go and stand on the stone and tell me "
               "what is carved on the far side of it.",
        "answer": "A date. Someone carved a date where the bird stands, "
                  "and nobody knows who, and he has stood on it every "
                  "night to keep the carving clear of the salt.",
        "reward": {"respect": 2, "card": "The Date Under the Stone"},
    },
    # ------------------------------------------------------- the Green Deep
    "krabi_the_stones": {
        "from": "krabi",
        "at": "the_crocodile_pool",
        "ask": "Nobody has counted the crocodile pool stones in my "
               "lifetime. Go and stand where the old ones are and count "
               "them, and do not go in the water.",
        "answer": "Four hundred and six. And you did not go in. Good. "
                  "The old ones will let a careful person stand on the "
                  "bank. It is the careless ones they are teaching a "
                  "lesson to.",
        "reward": {"respect": 2, "card": "Four Hundred and Six"},
    },
    "krabi_the_mouth": {
        "from": "krabi",
        "at": "the_cave_mouth",
        "ask": "The water comes out of the mountain and nobody knows "
               "where it has been. Go and stand at the cave mouth and "
               "tell me if it is warm or cold.",
        "answer": "Cold. Of course cold. It has walked ten kilometres "
                  "under a mountain to get here and it has forgotten the "
                  "sun. ...He has been down there. He has been down "
                  "there and come up and the water is still cold.",
        "reward": {"respect": 3, "card": "The Cold Water"},
    },
    # ------------------------------------------- Rubber Country, the isles
    "trang_the_fire": {
        "from": "trang",
        "at": "the_smoke_rows",
        "ask": "The fires that keep the latex from setting have been "
               "burning since before I was born. Go and stand among the "
               "rows at dawn and tell me how many fires you can count.",
        "answer": "Nine. Nine fires and the whole valley full of haze. "
                  "That is not a forest, it is a shift. And someone has "
                  "to stand the shift. That is what he does not "
                  "understand: he thinks he is stealing. He is just "
                  "standing the shift.",
        "reward": {"respect": 2, "card": "The Nine Fires"},
    },
    "satun_the_smelter": {
        "from": "satun",
        "at": "the_tin_scratch",
        "ask": "The old smelter is up on the tin scratch. Go and stand "
               "where the smelter stood and tell me what is left of "
               "it.",
        "answer": "So it is all still there. They took the tin and "
                  "left the smelter. And now a man comes here for the "
                  "tin that is not there. He comes for the taking, not "
                  "the tin. I have been angry with him for thirty "
                  "years for stealing. He was only ever a smelter.",
        "reward": {"respect": 3, "card": "The Empty Smelter"},
    },
    "lipe_the_giving": {
        "from": "ko_lipe",
        "at": "the_letting_go_shore",
        "ask": "On the giving night, the sea people put their dead in "
               "the water. Go and stand on the giving shore and tell me "
               "what the tide leaves behind when it goes out.",
        "answer": "Nothing. Nothing at all. The tide took back "
                  "everything it was given, and it took back something "
                  "of ours too. ...Perhaps that is the answer. Perhaps "
                  "the sea does not keep what the land forgets. Perhaps "
                  "it gives it back, and we are the ones who forget.",
        "reward": {"respect": 3, "card": "What the Tide Gave Back"},
    },
    # ------------------------------------------------------ the Lake Kingdoms
    "songkhla_the_mirror": {
        "from": "songkhla",
        "at": "the_lake_mirror",
        "ask": "The lake is so still it holds the sky. Go and stand at "
               "the water and tell me what you can see in it that is "
               "not there.",
        "answer": "You saw the old town. In the water, upside down, and "
                  "burning. The lake keeps what the town threw away and "
                  "shows it to whoever stands still long enough. That is "
                  "what it is for. That is how it warns us.",
        "reward": {"respect": 2, "card": "The Upside-Down Town"},
    },
    "phatthalung_the_play": {
        "from": "phatthalung",
        "at": "the_nora_stage",
        "ask": "The shadow play tells the news and the gossip and the "
               "old stories. Go and stand by the lamp and listen to one "
               "whole play, and tell me which story they chose.",
        "answer": "The play about the binder's apprentice. Of course. "
                  "They always choose the one about him, and they always "
                  "choose it for the joke, and nobody in the audience "
                  "knows the joke is a confession.",
        "reward": {"respect": 3, "card": "The Binder's Apprentice"},
    },
    "yala_the_wax": {
        "from": "yala",
        "at": "the_wax_shed",
        "ask": "In batik the pattern is decided before the dye goes on. "
               "Go and stand in the wax shed and tell me which pattern "
               "they are filling today.",
        "answer": "The one with the bird in it, twice, facing each "
                  "other. That is not a pattern, that is a letter. "
                  "Somebody is sending a message to somebody, in wax, "
                  "and it has to be perfect, because wax does not take "
                  "back.",
        "reward": {"respect": 3, "card": "The Pattern With Two Birds"},
    },
}

# ---------------------------------------------------------------- more quests
# Written alongside the first batch; each one is a walk you would not
# otherwise take, and a small thing you learn on the way.
from . import _content_quests as _CQ  # noqa: E402

SIDE_QUESTS.update(_CQ.SIDE_QUESTS)
