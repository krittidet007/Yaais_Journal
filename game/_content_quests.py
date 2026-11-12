"""Errands and loose papers — the smaller commissions of the south.

The first dict holds the errands that hosts hand to a travelling
child: somewhere to stand, something to count or look at, and a
truth that is only true once it is reported back. The second is the
region's loose memory — letters, ledgers, songs and school books —
the paper trail of what the sea keeps and the land forgets.

``from``    the host town that gives the errand
``at``      the landmark id the errand is about
``ask``     what the host says when they send you
``answer``  what they say when you come back
``reward``  respect and a culture card for the journal
"""

SIDE_QUESTS = {
    # ------------------------------------------------------ the Samui Sea
    "ko_pha_ngan_side": {
        "from": "ko_pha_ngan",
        "at": "the_mermaid_silt",
        "ask": "Aunt Waan will not swim on the western side, and she "
               "will not say why twice. Go and stand where the water "
               "goes grey and tell me if the silt is still moving.",
        "answer": "Still moving. Then it is not finished settling, and "
                  "she is not finished combing. My brother's boat went "
                  "down on that side, and I have decided the grey is "
                  "her kindness, keeping his wood where the fish can "
                  "sit near it.",
        "reward": {"respect": 2, "card": "What the Silt Keeps"},
    },
    # ------------------------------------------------------ the Pearl Coast
    "ko_phi_phi_side": {
        "from": "ko_phi_phi",
        "at": "the_phi_phi_crowds",
        "ask": "Uncle Chalam cannot leave the scaffold in season. Go "
               "and stand where the boats crowd in and count how many "
               "of them are pointing at the same rock.",
        "answer": "All of them. Then the island has not changed. The "
                  "swiftlets gave up the open bay years before my "
                  "father did — a bird cannot sing over an engine — "
                  "and they keep to one cave, and we keep to one "
                  "cliff, and the visitors keep to everything else.",
        "reward": {"respect": 2, "card": "The Quiet End"},
    },
    # ------------------------------------------------------ the Lake Kingdoms
    "nakhon_side": {
        "from": "nakhon",
        "at": "the_khao_luang_mist",
        "ask": "Khru Lin's knees stopped climbing years before her "
               "eyes did. Go and stand at the shrine above the clouds "
               "and tell me whether the mist sits below it or above "
               "it this morning.",
        "answer": "Below it. Then we dance outside this year, in the "
                  "wet grass, the way it was done before there was a "
                  "hall. The mountain decides our calendar, child. It "
                  "decided mine before I was born — I was taught on "
                  "that path, and the mist was down that day too.",
        "reward": {"respect": 3, "card": "The Cloud's Calendar"},
    },
    # ------------------------------------------- Rubber Country, the isles
    "ko_kradan_side": {
        "from": "ko_kradan",
        "at": "the_kradan_lighthouse",
        "ask": "The warden cannot leave her boat this week. Go and "
               "stand under the old light and tell me whether the "
               "mirror on the gallery still turns in the wind.",
        "answer": "It turns. Then the reef is still minding itself. My "
                  "grandfather kept this light, and he said it never "
                  "needed a lamp at all — the danger here is a daytime "
                  "danger, and the sea only ever needed one honest "
                  "mirror to say so.",
        "reward": {"respect": 2, "card": "The Honest Mirror"},
    },
    # ------------------------------------------------------ the Lake Kingdoms
    "pattani_side": {
        "from": "pattani",
        "at": "the_painted_bow",
        "ask": "Uncle Bakri is painting three kolek bows before the "
               "monsoon and will not stop to walk. Go and stand where "
               "the old bows hang and tell me which of them the sea "
               "has not faded.",
        "answer": "The one with the eye, of course. Paint that bow "
                  "well and it looks back at you the whole way to the "
                  "fishing grounds; paint it badly and the sea looks "
                  "first. My grandmother painted it, and I have "
                  "re-lined the eye every year since, and my hand is "
                  "not as steady as hers was.",
        "reward": {"respect": 2, "card": "The Eye on the Bow"},
    },
    # ------------------------------------------------------ the Lake Kingdoms
    "narathiwat_side": {
        "from": "narathiwat",
        "at": "the_wax_shed",
        "ask": "Mak Su's chorus sings for the whole valley, but the "
               "dye is boiled in Yala, over the hills. Go and stand in "
               "the wax shed there and tell me which pattern they are "
               "filling, and whether the birds face each other.",
        "answer": "Two birds, still facing. Then she is still waiting, "
                  "whoever she is. Forty years that pattern has come "
                  "out of that shed, never twice the same, and my "
                  "mother said it was a letter long before I could "
                  "read it — she sang the answer into the last "
                  "chorus, and the valley has been singing her reply "
                  "ever since without knowing it.",
        "reward": {"respect": 3, "card": "The Answer in Wax"},
    },
}

# --------------------------------------------------------------------------
# Loose papers: the region's memory in its own hand. Letters, ledgers,
# songs and school books, each one a page of the hidden history.
# --------------------------------------------------------------------------

LORE = {
    "The Flood Song of the Boat People":
        "The old woman sang it flat, without mourning, the way you "
        "recite a list. Two boats went up the mountain in the song. "
        "One came down. The sea rose in one breath, she said, before "
        "any bird moved, and the ancestors knew to read the water "
        "going backwards, quiet, the colour of an old coin. We do not "
        "sing it to remember drowning. We sing it so the children "
        "keep the reading of it.",

    "A Tin Merchant's Letter":
        "Brother, the dredges chew the river and the mud goes out red "
        "as temple lacquer. I have paid the coolies in opium and "
        "promises, both cheaper than coin. Today I watched the monks "
        "wade out to a drowned chedi and hang a cloth on what "
        "remained of it. They billed us nothing for the blessing. "
        "Write to mother that I am rich, and let her keep the letter, "
        "since I cannot keep anything here.",

    "The Naming of the Light":
        "The keeper's widow told it this way: the light was never "
        "named for anyone. The surveyors asked the islanders what the "
        "tower should be called, and the islanders said the name of "
        "the reef, and the reef's name was already the reef's, so the "
        "tower took a borrowed word and never gave it back. She kept "
        "the spare wick in a tea tin forty years after the light went "
        "dark. Ask before you open it.",

    "The Boat-Builder's Rule of Thumb":
        "He measured everything against his own body: the beam was "
        "his arm-span, the keel his own height less a hand. Three "
        "woods in one hull, cut in the waning moon, or they will "
        "argue. He wrote nothing down. His son remembers the sayings "
        "but not the numbers, and his grandson buys his boats from "
        "another province. The sea keeps the measurements, which is "
        "why every hull in the south is a cousin.",

    "The Binder's Apprentice, As First Told":
        "Before the joke was a joke, the play ran long. The "
        "apprentice was sent to bind a journal and fell in love with "
        "the hand that wrote it, and the master cut a puppet of him "
        "from poor hide, so the audiences would laugh and never ask "
        "why the bird could not fly straight. The lamp-keeper's "
        "grandfather altered the middle. What he cut out was the "
        "apprentice going home. Nobody has played that scene since.",

    "The Tide Ledger":
        "In the back of the almanac the headman copied the sayings "
        "his father kept: never say a drowned name on the water; the "
        "sea hears its own. Give the first fish to the grandmother at "
        "the head of the beach, even if she is a stranger. When the "
        "tide goes out farther than it has ever gone, walk uphill and "
        "do not look back until the sound behind you stops being one "
        "sound.",

    "The Schoolmistress's Roll Book":
        "She ruled each page into three columns: present, absent, "
        "gone to sea. Under 'gone to sea' she never wrote 'lost'. She "
        "wrote the year the family left, the name of the uncle in "
        "Trang, and whether the child could already read. For sixty "
        "years she taught the south its letters and then recorded "
        "where the letters went. The book ends mid-column, in a hand "
        "suddenly unsteady, with one name written and no mark beside "
        "it.",

    "The Salt-Farm Lease":
        "The lease is written in two hands. The company's clerk set "
        "down the rent and the seasons. Then the grandfather added a "
        "line underneath in soft pencil, and every heir has traced "
        "over it so the pencil never fades: the salt is sold, but the "
        "first crop of every year is poured back into the sea, "
        "because the sea lent the water in the first place. The "
        "clerk's ink never mentions this. The lease holds.",

    "The Railway Survey, 1909":
        "The surveyor's notebook is mostly figures, then this, "
        "undated: the embankment will stand where the fishermen "
        "spread their nets, and they know it, and they have asked for "
        "nothing. One old man walked the whole route with me and said "
        "at the end: you are building a road for the tin to leave by. "
        "Nobody has ever built one for it to come home. I gave him my "
        "pencil. He has it still, I think.",

    "The Monk's Chronicle":
        "Year of the great rain: the river took the granaries and the "
        "monastery gave away its roof. Year of the tin fleet: forty "
        "ships, and the town quieter than before. Year of the fever: "
        "no bell was rung for the children; the ringing was "
        "continuous. In the last hand, in different ink: a traveller "
        "left a book here for mending. He said he would return for "
        "it. The book is whole. The shelf waits.",

    "The Bird-Trapper's Diary":
        "Fog the bamboo, oil the pole, climb before the moon is down. "
        "The male sings hardest at first light; take nothing then, "
        "the village rule, though buyers pay double. Twenty-two years "
        "in this book and every page the same lesson: a bird kept in "
        "a cage sings half a song, and half a song will not teach the "
        "young ones. Last year I let the red-throat go from my own "
        "hand. The diary stops there.",

    "The Rubber Planter's Account":
        "Seed from Kew, round the Cape: nine hundred, and six lived. "
        "The boys from the north did not believe the trees wept until "
        "they saw the cup under the cut. Twelve years before the "
        "first harvest; the company's letters grew short and then "
        "stopped. The ledger does not say: every tapper learned the "
        "cut from a neighbour, and the neighbour from another, and "
        "the knowledge arrived the way rain does, hand passing to "
        "hand.",
}
