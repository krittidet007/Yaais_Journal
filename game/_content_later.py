"""The trust-earned words — what each host says once the page is theirs.

Every stop's host has a public patter (``story.EXTRA``) and, behind it,
the things they could not say to a stranger. This dict holds those:
spoken after the town's page is recovered, when the child is no longer
a stranger but the one who pulled the rope, held the lamp, or counted
the cups.

Keys follow ``story.STOPS`` order, north to south; values are lists of
spoken lines (no names, no directions — the game supplies the speaker).
"""

LATER = {
    # ------------------------------------------------------- Act 1: the Gulf
    "chumphon": [
        "First fish of the season goes back over the side, alive and "
        "whole. The sea lends and does not sell, and every hull in this "
        "harbour was raised on that rule.",
        "My mother's longtail lies on her side in the shallows east of "
        "here, eleven years dry and never gone anywhere. I have not sold "
        "the timber — somebody has to keep her, and I am somebody.",
        "The ferries queue now like taxis, four deep at the pier, and "
        "the boys running them cannot tell a falling tide from a "
        "Tuesday. The Prince's fleet never queued.",
        "After you left I found a sheet under the fish baskets, neat as "
        "a ledger and damp at the crease — not Yaai's hand, whose never "
        "shook. This one never stops.",
    ],
    "ko_tao": [
        "You never kicked up sand once — you waited for her to pass like "
        "a boat in a narrow channel. My grandmother said a quiet guest "
        "is worth two loud helpers.",
        "Never count the hatchlings out loud before they reach the "
        "water. The sea counts over your shoulder and takes a tenth for "
        "listening.",
        "Four hundred and eleven is my count, and my grandmother's was "
        "three hundred and two, in the village book, in her own hand. I "
        "set my figures against hers whenever the season feels wrong.",
        "Then last Tuesday one walked the sandbar at dead low tide, heel "
        "to toe, counting our mounds. It did not leave like a bird; it "
        "left like a visitor who thinks he was not seen.",
    ],
    "ko_pha_ngan": [
        "Never whistle under the falls. The water throws your own "
        "whistle back half a beat late, and a man who answers it will "
        "take the wrong fork every time.",
        "My grandfather guided the king's boatman here — they waited at "
        "the river mouth for the tide to lift the boat, then walked up "
        "through the dark. He was paid in salt and one story, and we "
        "spent the salt years ago.",
        "Full-moon week the boats cross from Samui before dusk and the "
        "seaward path fills with torches at midnight. The kings walked "
        "it in the dark, quietly, the way you take your shoes off at a "
        "door.",
        "There is a new set of initials under the old kings', cut "
        "crooked and proud, and whoever cut it came back twice in one "
        "week. The kings took a day and a chisel and never signed the "
        "rock twice.",
    ],
    "ko_samui": [
        "Never point at a sea that is swelling wrong — point at the "
        "grandfather stone and say your thank-you instead. The boats "
        "cross kinder and the coconuts come down fuller.",
        "My husband proposed at the lowest tide of the year, standing "
        "where she leans into him, copying the rocks. Forty years "
        "married, and he still walks down to the water line to wait for "
        "me.",
        "The ring road jams from six in the morning now, and the tour "
        "vans idle at the grandparents' feet with their engines running. "
        "The rocks held hands a thousand years before anyone had a "
        "horn.",
        "Somebody tied one ribbon on every prayer at the old couple's "
        "feet — same colour, all of them, like a man buying the sea in "
        "bulk. I untied mine and let the tide have it; the rocks do not "
        "sell, and neither do I.",
    ],
    # -------------------------------------------------- Act 2: the Andaman
    "surat_thani": [
        "You pulled on the second beat, the way the old men do, without "
        "anyone telling you. The rope remembers hands, and so does the "
        "river.",
        "The salt farmers never sweep the court after dark — you would "
        "sweep the sun's share away with it — and the shrimp men of "
        "Bandon Bay never count their catch out loud, because a pond "
        "hears everything.",
        "I ordained the year my mother died. She raked salt beds here "
        "for forty years, and on quiet mornings I still hear the rake, "
        "so perhaps she is not finished with the court either.",
        "Half the rope pulled against us this year because a page told "
        "them to. The Buddha does not need a page pulled — the town "
        "does — so I read them the rope instead, and we finished "
        "together.",
    ],
    "ranong": [
        "Wash the pan before the bell, never after — tin that leaves the "
        "shed wet is tin the mountain counts as stolen. The mountain "
        "keeps a longer book than the company does.",
        "My father panned across the river and came home with a Burmese "
        "wife and a dragon-stamped token. I gave that token to a child "
        "with patient hands once — it was you.",
        "It rained forty days and the tide brought the river up into the "
        "streets, and the government sent a man to count the rain. "
        "Nobody came to count the potholes.",
        "There is a man who crosses from Kawthaung on the morning boat "
        "just for tea, and he always sets out a second cup, full, across "
        "from him. He leaves it steaming and goes back with the tide.",
    ],
    "surin_islands": [
        "Sing the wave song to the children before the tide ever pulls "
        "back. Afterward it is not a song any more, it is just running.",
        "My father's boat was called Standing Star, and when the sea "
        "kept her we carved her name into a dead tree in the shallows so "
        "the water could go on reading it. The sea has never once lost "
        "it.",
        "The park boat wants our names in a book now, every season, and "
        "the sea never asked for names because it knows all of ours. I "
        "sign anyway — paper is how you talk to people who cannot read "
        "water.",
        "Two nights back a boat sat beyond the reef with no lamp and no "
        "sound, and by dawn it was gone and the birds would not land on "
        "that water. The sea said it twice, so this week we keep our "
        "songs away from that spot.",
    ],
    "khao_lak": [
        "A lantern is lit from another lantern, never from a lighter — "
        "memory passes hand to hand or it does not pass at all. That is "
        "why we walk down to the water in a line.",
        "You held your lantern level the whole way, even when the wind "
        "came off the sea. The old woman behind you noticed, and by "
        "morning everyone will have heard about it.",
        "The warning towers test their sirens every month, and the boat "
        "in the field does not mind, and the dogs do. I do not mind, "
        "because the year they built them nobody had to be brave twice.",
        "My family lights first for my grandfather's brother, who the "
        "sea kept. Someone moved the lanterns one night — all in a row, "
        "facing the water, very tidy — and we put them back the way the "
        "village remembers, because tidy is not the same as true.",
    ],
    "similan": [
        "The first foot on an empty beach belongs to the sea — you "
        "splash a little water and say out loud that you are only "
        "visiting. The old boatmen taught me that, and I have had kind "
        "seasons ever since.",
        "My father counted these islands for the navy for twenty years, "
        "and on his last survey he counted ten. He laughed about it the "
        "whole way home, and I think of it every spring-tide run.",
        "The papers say we close in May, but the coral does not read "
        "papers, so I close the pier myself and collect the shouting. It "
        "comes with the uniform.",
        "Someone painted a new name on the eighth island's rock — "
        "English, in a font — and we scrubbed it before the paint "
        "cured. These islands were named by the sea and by sailors, "
        "slowly, and nothing that arrives by speedboat gets to rename "
        "one.",
    ],
    "phang_nga": [
        "You kept the ball dry and gave it back soft, underhand, like "
        "you had done it before. Last year it went in the sea and my "
        "cousin cried — not this year.",
        "On the water you never say lost, you say waiting — the tide "
        "brings back whatever it agrees to. So my ball is always "
        "waiting, never lost.",
        "My grandfather hung the school bell — it rang for his class, "
        "then my mother's, then mine, and it never once rang wrong until "
        "this month. I rang it back right the same day.",
        "The tide took the football raft again, and my uncle had to tow "
        "it home with his longtail, and the government still owes us a "
        "floating pitch. The tide answered before they did, as usual.",
    ],
    # ------------------------------------------------- Act 3: pearl coast
    "phuket": [
        "Nine days of the festival and the shop fire never goes out — "
        "the ancestors eat before the customers, and you keep their "
        "flame fed. My grandmother carried it through a war, and I will "
        "not be the one to let it gutter.",
        "My great-great-grandmother cooked for the two Sisters the night "
        "the beacons were lit, and the recipe is in my hand now. A war "
        "recipe does not go cold on my watch.",
        "They come by the coachload for the festival and photograph the "
        "fire-walking and never once ask why we do it. The road down to "
        "the shrine is still one lane, so you can imagine the horns.",
        "A page went round the shophouses with battle orders in the "
        "Sisters' voice. The Sisters never wrote orders — they wrote "
        "recipes and refused to run — and whoever wrote that knew our "
        "words and not our spines.",
    ],
    "promthep": [
        "Never take the last sliver of sun — you let the sea close its "
        "own eye, and you keep the second-to-last. Every boatman I know "
        "shoots it that way, and the boats come home.",
        "My father kept a longtail at Rawai for forty years and never "
        "once photographed the last sliver either. His boat's ribbon "
        "hangs on my wall — green, sun-faded, still his.",
        "You waited for the sun to sit. Ten thousand people and maybe "
        "forty wait, so you are one of my forty now.",
        "There is a stone below the rail that a black-and-white bird has "
        "used three nights running, always facing the water, always gone "
        "before full dark. I have watched ten thousand sunsets and never "
        "once seen a bird sit like a man.",
    ],
    "ko_phi_phi": [
        "You ask the swiftlets' leave before you climb — quietly, in the "
        "dark — and you never take the first nest or the last. My "
        "grandfather began every season with the same three words, and "
        "the cave let him climb for forty years.",
        "My father has climbed that bamboo for thirty years, and his "
        "knees are in the ledger now too. When he retires, the cave "
        "decides whether it trusts me — not the buyers in town.",
        "Six hundred boats before nine in the morning, every one of them "
        "pointing at the same rock, and the sea is a car park by ten. "
        "The birds came back to the dark, but the quiet never did.",
        "The lamp that vanished from our scaffold turned up on the empty "
        "end of the island, lit, set on a stone like an offering, and "
        "the tide has reached it twice a day without putting it out. Who "
        "lights a lamp for birds and takes no nests?",
    ],
    # ------------------------------------------------------- Act 4: green
    "krabi": [
        "Never buy a ribbon you will not tie yourself. The boat knows "
        "whose hand knotted it, and Mae Ya Nang knows the boat.",
        "My husband tied green ribbons for forty years, and the year he "
        "died I tied the bow myself and the engine started on the first "
        "pull. She knew his hand in mine.",
        "You tied one back in your own colour and you tied it crooked, "
        "like you meant it. Half the fleet went crooked by evening, on "
        "purpose, and the harbour looked like itself again.",
        "The tour boats wake at six and my nets come up smelling of "
        "diesel by seven, and that same morning every ribbon on the "
        "fleet was one colour, tied by a stranger's hand. Mae Ya Nang "
        "does not mind the colour; she minds being told.",
    ],
    "nakhon": [
        "Never dance the last pose without saying your teacher's name "
        "out loud. The wrists remember whose they are, even when the "
        "mouth forgets.",
        "My hands come from Khru Somjai, who took them from Khru "
        "Thanom, all the way back past the founding of the school. One "
        "day a student will say my name the same way, or I was never "
        "here.",
        "The stage lights cut off at ten now, city rule. Nora was born "
        "in lamplight long past midnight, and some rules snuff more than "
        "candles.",
        "In the teacher's book one name has been scraped off the founding "
        "page — you can still feel the ink underneath, like a bruise "
        "under paper. A name said out loud calls a person back, and "
        "whoever scraped it knew exactly that.",
    ],
    "phatthalung": [
        "Never hang a new puppet facing the wall — it learns to sulk, "
        "and a sulking puppet splits at the joints. Face the lamp, "
        "always the lamp.",
        "My father cut Noi from a hide the tannery had failed, one scar "
        "across the shoulder, and that shadow walks in every act. He "
        "kept the flaw in — leather without a story cracks.",
        "You should hear it here, in the lamplight, where the word was "
        "made: a binding is a promise between a person and a spirit to "
        "call each other back. There was a second puppet in this room "
        "once — brighter, louder — and the wall still shows where he "
        "hung.",
        "Leather is dearer every year, and the young ones want a "
        "punchline every thirty seconds. My father's plays breathed, and "
        "I refuse to choke them.",
    ],
    "trang": [
        "Never tap a tree with an empty cup waiting under the cut — the "
        "tree fills what it can see. My mother swore it, and her rows "
        "out-yielded the whole district.",
        "My mother tapped row three for forty-one years, and her tally "
        "books are still in the house — twelve cups before sunrise, "
        "every morning, in pencil. Pencil survives the rain better than "
        "pride does.",
        "You counted my cups with me before sunrise, and nobody does "
        "that; they think counting in the dark is silly. A tally and a "
        "rumour are different things, and now you know which one I "
        "keep.",
        "A page went round the camps telling tappers to cut deeper, and "
        "my mother's rule is the exact opposite, so I fed mine to the "
        "smoke pot. Whoever wrote it knew rubber and hated trees.",
    ],
    "ko_kradan": [
        "You call the fish with two slaps on the water, and you call the "
        "dugong with nothing at all. Know which day it is before you put "
        "your hands in the sea.",
        "You floated like a log, and the dugong came closer to you than "
        "to me, and I have been coming here since I could swim. I am "
        "pretending not to be jealous.",
        "In February the wedding boats come — forty couples in "
        "wetsuits, all so happy and so loud — and the dugongs give the "
        "whole month a wide berth. Who can blame them.",
        "The dugong tracks stop mid-bay, like something came through in "
        "a hurry, and the same morning the tide brought in a "
        "black-and-white feather. Dugongs do not hurry, and neither do "
        "we.",
    ],
    "satun": [
        "Mend a torn logbook with cloth, never glue. Glue lies flat, and "
        "a harbour trusts a scarred page — it should show where it "
        "hurt.",
        "My uncle ferried supplies to Tarutao the year the boats stopped "
        "coming, and I keep the pencil he counted the days with. It is "
        "shorter than hope and harder than iron.",
        "Geopark this, geopark that — signs everywhere, and the pier "
        "still floods at spring tide. Signs have never bailed water in "
        "their lives.",
        "The 1940 tear in the harbour log is knife-clean, and the "
        "missing years are the ugly ones — my pier master keeps the cut "
        "strip in a tin. Ugly and true beats pretty and blank.",
    ],
    "ko_lipe": [
        "Launch the little boats at slack tide, never at the turn — a "
        "turning tide takes back what it was given. My mother put forty "
        "boats out on the slack and outlived four storms.",
        "My mother built the letting-go boats with her own two hands, "
        "one nail and one coin in each so they would not drift back. I "
        "build them the same way, and the tide has kept its side of the "
        "bargain for sixty years.",
        "You put a nail and a coin in your little boat without being "
        "told, so it would carry weight and not drift back. The old ones "
        "noticed, and the old ones notice everything.",
        "Someone has been netting our little boats downstream and "
        "selling them to the tourists on the walking street — you may "
        "not sell what the sea was asked to keep. My mother's rule, and "
        "now mine.",
    ],
    # ------------------------------------------------ Act 5: the deep south
    "songkhla": [
        "Never weave a living person's name into cloth. Names in cloth "
        "belong to the gone, and the loom holds them longer than we hold "
        "anything.",
        "My grandmother wove the indigo stripe with wefts so tight the "
        "water stood on the cloth instead of soaking it — mine are "
        "close, not there yet. I keep her shuttle on the high shelf "
        "where I can see it lying.",
        "You lifted the shuttle for me when the cloth came up — a small "
        "thing for two hands, a large thing for one shoulder. You will "
        "be remembered at this loom.",
        "A page was pinned to my loom last month, smooth where an old "
        "woman's hand would waver — it read like Yaai, and it was not "
        "her. A copy is a picture of a person, not a person.",
    ],
    "pattani": [
        "Paint the eye before the boat touches the water, never after. "
        "An eye painted late watches the shore instead of the sea, and "
        "no crew will sail behind that.",
        "My father painted eyes on the kolek fleet for thirty years and "
        "never signed a boat — he said the eye was the signature. We "
        "keep his name at home, said after prayer, over rice.",
        "You gave the oldest boat her eye back, and that evening Uncle "
        "Din's stall by the pier put extra fish in the gravy for the "
        "whole crew — halal, hot, and on the house. One hand starts a "
        "harbour.",
        "Every eye in this harbour was shut one morning, painted over in "
        "the night, neat as a bank note — I opened the oldest boat's "
        "first. A coast that cannot see where it has been will believe "
        "anything about tomorrow.",
    ],
    "yala": [
        "Greet the cloth before the wax goes on — say something kind to "
        "it, out loud. The wax keeps whatever the room was feeling, and "
        "the dye announces it to everybody.",
        "My grandmother sold batik from a stall by the cave temple for "
        "fifty years and paid off the shop's debt one handkerchief at a "
        "time. My uncle closed the debt book the year she died and keeps "
        "it shut like a drawer.",
        "My stall sits between the mosque gate and the temple steps — "
        "prayer mats going one way at dawn, flower trays the other, my "
        "cloth drying across both. Nobody has ever complained, and the "
        "South is wider than people think.",
        "A cloth came back from the dye with our pattern on it and wax "
        "we never drew — like our hands, and not our hands. The wax is "
        "the memory, my grandmother said, so whose memory was that one?",
    ],
    "narathiwat": [
        "We sing after dawn prayer, while the pond is still holding the "
        "pink sky, and never after the night prayer — words sung cold "
        "come home heavy. The ducks answer first, then the chorus, and "
        "that is the correct order of the world.",
        "I lead the chorus my mother led, and she learned it from the "
        "pond-side women who sang the ducks in. When I call, I feel her "
        "breath under mine, one beat ahead, the way it always was.",
        "The verse the elders never wrote got answered from the back, in "
        "a voice like wet rope, and my mother's rule is to sing louder, "
        "not softer, when a stranger answers your chorus. We sang "
        "louder, and it has not answered since.",
        "The palm lorries start down the pond road before the birds do, "
        "and the whole dawn chorus has to sing over diesel. My mother "
        "sang over buffalo, and we are still singing.",
    ],
}
