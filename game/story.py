"""Yaai's Journal — the 24 stops of the Southern Thailand adventure.

Story data only: every stop carries its dialogue, its local activity, the
journal page it returns, the Culture Card it unlocks and the Pak Tai word Noi
teaches there. Rendering and minigame logic live in ``scenes/stop.py``; this
file stays a plain data table so the writing can be edited without touching
code.

Layout follows the real geography of the South: north is Chumphon and the
Kra Isthmus, the Gulf islands sit east, the Andaman coast runs down the west,
and the deep south tapers toward the Malaysian border.

``pos`` is (col, row) in ``world_map.WORLD_COLS/ROWS`` tile units.
"""

# speakers: (name, accent key in settings)
# keys are added in settings.py as ACCENTS so new speakers stay in one place.

PROLOGUE = {
    "id": "prologue",
    "name": "Yaai's House",
    "pos": (80, 35),
    "lines": [
        ("NARRATOR", "TEXT", "The school holiday. A boat, then a bus, then a songthaew up the hill."),
        ("NARRATOR", "TEXT", "Yaai's wooden house smells of smoke, coconut and old paper."),
        ("YAAI", "YAAI", "You came! Come, come — sit. The curry is still hot."),
        ("NARRATOR", "TEXT", "She says it the way she has said it every year of your life, and the house says it back: the low ceiling, the old fan, the dog asleep in the heat."),
        ("YOU", "PLAYER", "Yaai, where are all the pages?"),
        ("NARRATOR", "TEXT", "On the table lies her journal's cloth cover. Empty. The stitching is still holding, but the pages are gone from it like teeth from a comb."),
        ("YAAI", "YAAI", "Last night's storm took them out the window. Twenty-four of them, gone with the wind."),
        ("NOI", "NOI", "(a small cowhide puppet, voice like a rusty hinge)"),
        ("YAAI", "YAAI", "He is Noi. My teacher's puppet, and yours now. He knows the South better than any map."),
        ("NOI", "NOI", "I know it because I was CARRIED through it. Not walked. Carried, in a basket, for forty years."),
        ("YAAI", "YAAI", "He is rude because he is old, and old things are allowed to be rude in my house."),
        ("NOI", "NOI", "Wait. Wait. Yaai — the window was shut."),
        ("NARRATOR", "TEXT", "Noi lifts a single black-and-white feather off the sill. It is wet. It is fresh."),
        ("NOI", "NOI", "A storm does not leave feathers. A magpie leaves feathers. Something came in here and took them, one by one, by hand."),
        ("YAAI", "YAAI", "He was a good teacher and a worse student, and I have been paying for both for thirty years."),
        ("NOI", "NOI", "Yaai. Yaai. Who is HE?"),
        ("YAAI", "YAAI", "...Ah. You noticed that too. Good. Then you are old enough to carry it."),
        ("YAAI", "YAAI", "There was another one in my teacher's workshop. Louder than Noi. Brighter, and it never stopped raining inside him."),
        ("NOI", "NOI", "That is not an answer."),
        ("YAAI", "YAAI", "It is the only one I have, child. Find the pages. Find out who is holding them. And when you meet him — and you will — ask him whose handwriting he learned."),
        ("YAAI", "YAAI", "And do not go quietly. Take the journal. Write down what you find, and who you meet, and why each page mattered where it lived."),
        ("NOI", "NOI", "มา! ... ma. Come. Say it: ma."),
        ("YOU", "PLAYER", "Ma."),
        ("NOI", "NOI", "Ma means come. Some things come when called. Some things come when stolen. We start where the first page was taken — Chumphon."),
    ],
    "word": {"thai": "มา", "roman": "ma", "meaning": "come"},
    "cards": [],
}

STOPS = [
    # ------------------------------------------------------------ Act 1: Gulf
    {
        "id": "chumphon",
        "name": "Chumphon",
        "title": "The Signal Hill",
        "kind": "province",
        "act": 1,
        "minutes": 8,
        "pos": (87, 32),
        "lines": [
            ("NARRATOR", "TEXT", "The Kra Isthmus — the narrowest part of Thailand. The Gulf and the Andaman are only a short walk apart here."),
            ("NARRATOR", "TEXT", "The smell arrives first: squid, diesel, wet rope, and the sweet rot of a harbour at low tide."),
            ("NOI", "NOI", "Yaai says page one is where the fleet comes in. Signal hill. Move fast, the light won't wait."),
            ("KEEPER", "YAAI", "Prince of Chumphon watches every hull that leaves. His page blew off with the rest — go on, earn it."),
            ("NOI", "NOI", "Bang Dot has been the keeper of that light for thirty-one years. He does not like strangers and he likes magpies less."),
            ("NOI", "NOI", "Ask him about the light. Not about the bird. If you say the word bird, he will shut like a tide gate."),
        ],
        "activity": {
            "type": "match",
            "prompt": "Match the harbour boats to their silhouettes",
            "options": ["longtail", "trawler", "ferry"],
            "decoys": ["tuk-tuk", "paraglider", "submarine"],
            "tries": 3,
        },
        "learn": "Prince of Chumphon, father of the Thai navy, is honoured on this hill. Signal flags still talk ship to shore.",
        "word": {"thai": "น้ำ", "roman": "nam", "meaning": "water"},
        "cards": ["Signal Hill", "Prince of Chumphon", "The First Page",
                  "The Keeper's Letter", "The Signal Code"],
        "page": "a sailor's knot, tied twice for luck.",
    },
    {
        "id": "ko_tao",
        "name": "Ko Tao",
        "title": "The Turtle Watch",
        "kind": "secret",
        "act": 1,
        "minutes": 6,
        "pos": (122, 56),
        "lines": [
            ("NARRATOR", "TEXT", "Turtle Island. The reef drops away in green steps."),
            ("NARRATOR", "TEXT", "On the shore a hundred small sand mounds wait like closed eyes. Nobody moves them."),
            ("NOI", "NOI", "Under the boat, over there. Follow her — she does not mind a quiet swimmer."),
            ("VOLUNTEER", "SPIRIT", "Watch from behind, never ahead. If she turns, you stop."),
            ("NOI", "NOI", "Ploy has watched turtles since she was tall enough to be told to watch them. She has counted four hundred and eleven hatchlings."),
            ("NOI", "NOI", "She also knows what the night boats sound like. We will want that later."),
        ],
        "activity": {
            "type": "calm",
            "prompt": "Snorkel out and follow the green turtle to the sunken boat",
            "steps": 4,
        },
        "learn": "Local volunteers protect turtles and coral. You must keep your distance and never touch the animals.",
        "word": {"thai": "เต่า", "roman": "tao", "meaning": "turtle"},
        "cards": ["Turtle Watch", "The Night Boat Song",
                  "The Turtle Master's Letter"],
        "page": "a song line: 'the reef remembers every hand that touched it.'",
    },
    {
        "id": "ko_pha_ngan",
        "name": "Ko Pha-ngan",
        "title": "The King's Initials",
        "kind": "secret",
        "act": 1,
        "minutes": 6,
        "pos": (134, 76),
        "lines": [
            ("NARRATOR", "TEXT", "Away from the party beaches, a waterfall path runs up into the rock."),
            ("NOI", "NOI", "Than Sadet. Kings walked this same path and left their initials in the stone."),
        ],
        "activity": {
            "type": "match",
            "prompt": "Match each set of royal initials to its king",
            "options": ["Vajiravudh", "Prajadhipok", "Bhumibol"],
            "decoys": ["Rama I", "Narai", "Taksin"],
            "tries": 3,
        },
        "learn": "Southern islands were once stops on royal journeys, and people still keep those memories alive.",
        "word": {"thai": "น้ำตก", "roman": "nam tok", "meaning": "waterfall"},
        "cards": ["Royal Initials"],
        "page": "a memory: 'the stones keep the kings' names wet.'",
    },
    {
        "id": "ko_samui",
        "name": "Ko Samui",
        "title": "The Stone Couple",
        "kind": "secret",
        "act": 1,
        "minutes": 7,
        "pos": (132, 93),
        "lines": [
            ("NARRATOR", "TEXT", "Two rocks by the sea that look like an old couple — Hin Ta and Hin Yai."),
            ("NOI", "NOI", "The page is fluttering at their feet. Grab it before the wind takes it again."),
            ("ELDER", "YAAI", "Hin Ta sailed to ask for her hand. The storm answered instead. They hold hands still."),
        ],
        "call": "Every act of the old dance ends with the teacher standing still. You are the standing still now. Go on. The next part is harder.",
        "activity": {
            "type": "timing",
            "prompt": "Catch the sunrise exactly between the old couple",
            "zone": 0.45,
            "tries": 3,
        },
        "learn": "The rocks are grandparents turned to stone: he sailed, she waited, the sea kept them both.",
        "word": {"thai": "หิน", "roman": "hin", "meaning": "stone"},
        "cards": ["Hin Ta & Hin Yai"],
        "page": "a legend: 'the grandparents hold hands still.'",
    },
    {
        "id": "surat_thani",
        "name": "Surat Thani · Chaiya",
        "title": "The Rope Pull",
        "kind": "province",
        "act": 2,
        "minutes": 14,
        "pos": (88, 98),
        "lines": [
            ("NARRATOR", "TEXT", "Chaiya. Wat Phra Boromathat Chaiya has stood here since Srivijaya made this a hub of the world."),
            ("NOI", "NOI", "It's Chak Phra week. The whole town pulls the Buddha together — you pull too."),
            ("MONK", "YAAI", "Chak Phra means pulling the Buddha. After Lent, on land and on water. Grip the rope, not the float."),
        ],
        "activity": {
            "type": "rhythm",
            "prompt": "Pull with the town: match the rhythm of the rope",
            "sequence": ["left", "right", "left", "right"],
            "tries": 3,
        },
        "learn": "Chaiya was a trade hub of the ancient Srivijaya world; Chak Phra ends Buddhist Lent with processions on land and water.",
        "word": {"thai": "แรง", "roman": "raeng", "meaning": "strength"},
        "cards": ["Chak Phra"],
        "page": "a memory: 'a dancer begins with her teacher.'",
        "call": "A dancer begins with her teacher. ... Keep going.",
    },
    # --------------------------------------------------- Act 2: Andaman coast
    {
        "id": "ranong",
        "name": "Ranong",
        "title": "The Tin Pan",
        "kind": "province",
        "act": 2,
        "minutes": 9,
        "pos": (58, 63),
        "lines": [
            ("NARRATOR", "TEXT", "The rainiest town in Thailand. Steam rises off the rocks at the hot springs."),
            ("NOI", "NOI", "Kaw Sim Bee's house is up the hill. The page is where the tin men rest."),
        ],
        "activity": {
            "type": "timing",
            "prompt": "Strike the mine bell when the cage reaches the top",
            "zone": 0.6,
            "tries": 3,
        },
        "learn": "Chinese immigrants shaped the South through tin mining and trade. Remember the name Kaw Sim Bee.",
        "word": {"thai": "แร่", "roman": "rae", "meaning": "ore"},
        "cards": ["Kaw Sim Bee"],
        "page": "a tin token, stamped with a dragon.",
    },
    {
        "id": "surin_islands",
        "name": "Surin Islands",
        "title": "Reading the Sky",
        "kind": "secret",
        "act": 2,
        "minutes": 6,
        "pos": (19, 95),
        "lines": [
            ("NARRATOR", "TEXT", "The Moken live between the sea and the land, and read both."),
            ("ELDER", "SPIRIT", "The wave that eats people — we sing it to our children. When the sea pulls back, we go up."),
        ],
        "activity": {
            "type": "choice",
            "prompt": "The elder asks how you will read the sky before the boat leaves",
            "options": [
                {"text": "The water just pulled back and the birds went inland", "respect": 2, "reply": "Good. You watched. Now you can go."},
                {"text": "It looks fine to me", "respect": 0, "reply": "It always looks fine first. Watch again."},
            ],
            "tries": 2,
        },
        "learn": "The Moken pass knowledge down by story and song; their legend of the wave that 'eats people' saved lives.",
        "word": {"thai": "ทะเล", "roman": "tha le", "meaning": "sea"},
        "cards": ["Moken"],
        "page": "a song line: 'the sea says it twice — believe the first.'",
    },
    {
        "id": "khao_lak",
        "name": "Khao Lak",
        "title": "The Lantern",
        "kind": "secret",
        "act": 2,
        "minutes": 6,
        "pos": (39, 140),
        "lines": [
            ("NARRATOR", "TEXT", "A police boat sits far from the shore, in a field. In 2004 the sea came all the way here."),
            ("NOI", "NOI", "No game here. Just walk, and light a lantern."),
            ("VILLAGER", "TEXT", "We light one every year. My brother is in that boat. Come — hold this with me."),
        ],
        "activity": {
            "type": "calm",
            "prompt": "Walk beside the boat and light a lantern",
            "steps": 3,
        },
        "learn": "Communities remember loss and prepare for the future. Early-warning towers now stand along the coast.",
        "word": {"thai": "รำลึก", "roman": "ram luek", "meaning": "remember"},
        "cards": ["Khao Lak Memorial"],
        "page": "a memory: 'the sea took; the town stayed.'",
    },
    {
        "id": "similan",
        "name": "Similan Islands",
        "title": "Nine Islands",
        "kind": "secret",
        "act": 2,
        "minutes": 6,
        "pos": (7, 145),
        "lines": [
            ("NARRATOR", "TEXT", "Similan is a Malay word for nine. The sailing rocks mark the group."),
            ("NOI", "NOI", "Count the islands. The balancing rock waits at the eighth."),
        ],
        "activity": {
            "type": "match",
            "prompt": "Sail between the islands and count what each one holds",
            "options": ["sailing rock", "white sand beach", "granite boulders"],
            "decoys": ["villages", "rubber plots", "mosques"],
            "tries": 3,
        },
        "learn": "Malay language and culture run deep through southern names. The park closes part of the year so coral can recover.",
        "word": {"thai": "เก้า", "roman": "kao", "meaning": "nine"},
        "cards": ["Similan Nine"],
        "page": "a song line: 'count to nine, then let the sea be.'",
    },
    {
        "id": "phang_nga",
        "name": "Phang Nga",
        "title": "The Floating School",
        "kind": "province",
        "act": 2,
        "minutes": 9,
        "pos": (52, 159),
        "lines": [
            ("NARRATOR", "TEXT", "Limestone cliffs rise straight out of the green water, and Ko Panyi's houses stand on stilts."),
            ("NOI", "NOI", "The page is in the floating school. Keep the ball dry — that is the whole game."),
            ("BOY", "CHILD", "We play football on the raft. You win, you keep the ball dry. Understand?"),
        ],
        "call": "The wall of Phang Nga is not a wall. It is a door, and it has been a door for a thousand years, and nobody has knocked. You have knocked. Keep knocking.",
        "activity": {
            "type": "rhythm",
            "prompt": "Pass the ball back dry: copy the raft rhythm",
            "sequence": ["up", "up", "down"],
            "tries": 3,
        },
        "learn": "Ko Panyi is a Muslim fishing village founded by seafarers more than two centuries ago.",
        "word": {"thai": "เกาะ", "roman": "ko", "meaning": "island"},
        "cards": ["Stilt Village"],
        "page": "a school bell that never rusts.",
    },
    {
        "id": "phuket",
        "name": "Phuket Old Town",
        "title": "The Beacon Chain",
        "kind": "province",
        "act": 3,
        "minutes": 14,
        "pos": (46, 186),
        "lines": [
            ("NARRATOR", "TEXT", "Sino-Portuguese shophouses on Thalang Road. The page is behind one of those doors."),
            ("AUNTIE", "YAAI", "The Sisters lit beacons ridge to ridge. When you see strange sails, you light. Quickly now."),
            ("NOI", "NOI", "After this we find the two sisters. They held this island with words and will."),
        ],
        "activity": {
            "type": "timing",
            "prompt": "Light each beacon as the fire reaches your ridge",
            "zone": 0.7,
            "tries": 3,
        },
        "learn": "Thao Thep Kasattri and Thao Si Sunthon rallied the island against a Burmese army in 1785. Peranakan culture mixes Chinese and Malay traditions.",
        "word": {"thai": "หญิง", "roman": "ying", "meaning": "woman"},
        "cards": ["Peranakan", "Vegetarian Festival"],
        "page": "a beacon order, signed by two sisters.",
    },
    {
        "id": "promthep",
        "name": "Promthep Cape",
        "title": "The Golden Hour",
        "kind": "secret",
        "act": 3,
        "minutes": 6,
        "pos": (42, 192),
        "lines": [
            ("NARRATOR", "TEXT", "The southern tip of the island. The light changes every few seconds."),
            ("NOI", "NOI", "The page blew to the cliff. Hold the shutter when the sun sits on the water."),
        ],
        "activity": {
            "type": "timing",
            "prompt": "Catch the sunset: shoot when the light lands on the cape",
            "zone": 0.85,
            "tries": 3,
        },
        "learn": "Long-tail boats and fishing families still shape life on the coast.",
        "word": {"thai": "ดวงอาทิตย์", "roman": "duang atit", "meaning": "sun"},
        "cards": ["Promthep Sunset"],
        "page": "a song line: 'sunset is a kind of storytelling too.'",
    },
    {
        "id": "ko_phi_phi",
        "name": "Ko Phi Phi",
        "title": "The Steady Lamp",
        "kind": "secret",
        "act": 3,
        "minutes": 7,
        "pos": (66, 194),
        "lines": [
            ("NARRATOR", "TEXT", "Maya Bay, and the swiftlet cave above it. The nests are called white gold."),
            ("COLLECTOR", "TEXT", "Hold the lamp steady. My father climbs that bamboo in the dark."),
        ],
        "call": "The island has two ends and only one of them has people on it. You have been walking towards the empty end your whole life. Good. That is where the stories are.",
        "activity": {
            "type": "calm",
            "prompt": "Keep the lamp lit on the scaffold — hold still",
            "steps": 5,
        },
        "learn": "Collectors perform a ritual before harvesting edible bird nests. Maya Bay was closed for years so nature could recover.",
        "word": {"thai": "ถ้ำ", "roman": "tham", "meaning": "cave"},
        "cards": ["Bird Nests"],
        "page": "a memory: 'climb slow, the nest is someone's year.'",
    },
    {
        "id": "krabi",
        "name": "Krabi",
        "title": "Twelve Hundred Steps",
        "kind": "province",
        "act": 4,
        "minutes": 10,
        "pos": (74, 172),
        "lines": [
            ("NARRATOR", "TEXT", "Twelve hundred steps up to Tiger Cave Temple, and Shell Cemetery below."),
            ("NOI", "NOI", "Breathe with the steps. Then read the fossils — the page hides in their pattern."),
            ("FISHER", "SPIRIT", "We tie ribbons to the bow for Mae Ya Nang. Without her, the engine is just metal."),
        ],
        "activity": {
            "type": "rhythm",
            "prompt": "Climb: breathe on every third step",
            "sequence": ["up", "up", "up"],
            "tries": 3,
        },
        "learn": "Fishermen tie colored ribbons to the bow of long-tail boats to honor Mae Ya Nang, the boat spirit. Shell Cemetery holds fossils tens of millions of years old.",
        "word": {"thai": "แม่", "roman": "mae", "meaning": "mother"},
        "cards": ["Mae Ya Nang"],
        "page": "a ribbon for the bow, salt-stiff and sun-faded.",
        "call": "The journal is my teacher's book. Every Nora dancer remembers who taught her. If the book is lost, they are lost too.",
    },
    # ------------------------------------------------------ Act 3: Deep South
    {
        "id": "nakhon",
        "name": "Nakhon Si Thammarat",
        "title": "The Dancing Hands",
        "kind": "province",
        "act": 4,
        "minutes": 12,
        "pos": (128, 153),
        "lines": [
            ("NARRATOR", "TEXT", "Tambralinga's old kingdom. Wat Phra Mahathat's great stupa shines above the city."),
            ("NOI", "NOI", "Sat Duean Sip — the tenth month. Arrange the tray for the ancestors, then watch the Nora."),
            ("DANCER", "YAAI", "Copy my hands. Long finger picks. The story is in the wrists."),
        ],
        "activity": {
            "type": "rhythm",
            "prompt": "Copy the Nora hand poses",
            "sequence": ["left", "down", "right", "up"],
            "tries": 3,
        },
        "learn": "Nora is the South's dance-drama with elegant hand movements and bright costumes. Sat Duean Sip honours ancestors with food offerings.",
        "word": {"thai": "ครู", "roman": "khru", "meaning": "teacher"},
        "cards": ["Sat Duean Sip", "Nora"],
        "page": "a song line: 'the melody you heard in Nakhon — keep it.'",
    },
    {
        "id": "phatthalung",
        "name": "Phatthalung",
        "title": "The Little Brother",
        "kind": "province",
        "act": 4,
        "minutes": 8,
        "pos": (134, 201),
        "lines": [
            ("NARRATOR", "TEXT", "A puppeteer's workshop. Leather hides hang from the ceiling like brown moons."),
            ("PUPPETEER", "NOI", "Noi! Little brother — you came home. Your Southern voice is still in the workshop."),
        ],
        "activity": {
            "type": "match",
            "prompt": "Carve the cowhide: pick the right cut for a movable arm",
            "options": ["front leg", "back leg", "torso"],
            "decoys": ["ear", "tail", "horn"],
            "tries": 3,
        },
        "learn": "Nang Talung is southern shadow puppetry with live music, jokes and local news; the puppeteer voices every character.",
        "word": {"thai": "หนัง", "roman": "nang", "meaning": "leather"},
        "cards": ["Nang Talung", "Yaai's Teacher's Note"],
        "page": "a memory: 'Noi got his full Southern voice here.'",
    },
    {
        "id": "trang",
        "name": "Trang",
        "title": "Rubber Dawn",
        "kind": "province",
        "act": 4,
        "minutes": 9,
        "pos": (110, 204),
        "lines": [
            ("NARRATOR", "TEXT", "Three in the morning. The rubber trees wait in the dark."),
            ("TAPPER", "TEXT", "Kaw Sim Bee brought rubber here from Ranong. Cut at an angle, shallow, and the tree gives."),
        ],
        "activity": {
            "type": "timing",
            "prompt": "Tap the rubber by headlamp: cut when the lamp is steady",
            "zone": 0.35,
            "tries": 3,
        },
        "learn": "Kaw Sim Bee, the governor from Ranong, introduced rubber to Trang and reshaped the South's economy.",
        "word": {"thai": "ยาง", "roman": "yang", "meaning": "rubber"},
        "cards": ["Rubber Dawn"],
        "page": "a latex tally: twelve cups before sunrise.",
    },
    {
        "id": "ko_kradan",
        "name": "Ko Kradan",
        "title": "The Gentle Hour",
        "kind": "secret",
        "act": 4,
        "minutes": 5,
        "pos": (91, 219),
        "lines": [
            ("NARRATOR", "TEXT", "A coral reef in shallow water, and seagrass beds offshore."),
            ("NOI", "NOI", "Float. The gentler you move, the more fish come. Never touch the coral."),
        ],
        "activity": {
            "type": "calm",
            "prompt": "Float without touching the coral — hold still",
            "steps": 4,
        },
        "learn": "Every February couples hold an underwater wedding here. Nearby seagrass beds are home to dugongs.",
        "word": {"thai": "ปะการัง", "roman": "pa ka rang", "meaning": "coral"},
        "cards": ["Underwater Wedding"],
        "page": "a song line: 'move slowly; the sea notices.'",
    },
    {
        "id": "satun",
        "name": "Satun · Pak Bara",
        "title": "The Torn Logbook",
        "kind": "province",
        "act": 4,
        "minutes": 8,
        "pos": (117, 245),
        "lines": [
            ("NARRATOR", "TEXT", "Pak Bara pier. Behind you the limestone hills of the geopark; ahead, Tarutao across the strait."),
            ("GUIDE", "SPIRIT", "The prison boats left from this pier. One logbook tore in 1940. Piece it back and the story reads itself."),
        ],
        "activity": {
            "type": "match",
            "prompt": "Piece the torn logbook together",
            "options": ["the timber yard", "the supply boat", "the rainy season"],
            "decoys": ["the railway", "the festival", "the market"],
            "tries": 3,
        },
        "learn": "Tarutao held prisoners in the 1930s and 40s; when supplies stopped during WWII some turned to piracy. Boats for the islands leave from Pak Bara, inside a UNESCO Global Geopark.",
        "word": {"thai": "เรือ", "roman": "ruea", "meaning": "boat"},
        "cards": ["Tarutao Geopark"],
        "page": "a salt-stained timetable: Tarutao, Lipe, home.",
    },
    {
        "id": "ko_lipe",
        "name": "Ko Lipe",
        "title": "Letting Go",
        "kind": "secret",
        "act": 4,
        "minutes": 6,
        "pos": (93, 266),
        "lines": [
            ("NARRATOR", "TEXT", "The Urak Lawoi build a small boat and let the tide carry bad luck away."),
            ("FAMILY", "YAAI", "Loy Reua. Place the offering, tie the ribbon, and send it. Do not look back."),
        ],
        "call": "Yaai wrote about the sea people last, and she wrote that they give their dead back to the water so the water will give them back to them. There is one page left and it is the page about that.",
        "activity": {
            "type": "calm",
            "prompt": "Assemble the boat and set it free at sunset",
            "steps": 4,
        },
        "learn": "The Urak Lawoi are sea people with their own language. In Loy Reua small items are placed in the boat and sent away with the tide.",
        "word": {"thai": "เรือไฟ", "roman": "ruea fai", "meaning": "floating boat"},
        "cards": ["Urak Lawoi"],
        "page": "a song line: 'the sea from Ko Lipe — let it go.'",
    },
    {
        "id": "songkhla",
        "name": "Songkhla",
        "title": "The Loom",
        "kind": "province",
        "act": 5,
        "minutes": 7,
        "pos": (161, 226),
        "lines": [
            ("NARRATOR", "TEXT", "Songkhla Old Town: painted walls, Chinese shophouses, sea air. The largest natural lake in Thailand sits behind it."),
            ("NOI", "NOI", "Finish the Ko Yo cloth. The page is pinned to the loom."),
        ],
        "activity": {
            "type": "match",
            "prompt": "Complete the Ko Yo cloth pattern",
            "options": ["indigo stripe", "silk weft", "temple border"],
            "decoys": ["plastic thread", "printed square", "leather patch"],
            "tries": 3,
        },
        "learn": "Songkhla sits between the sea and Thale Sap, the largest natural lake in Thailand. Its Old Town reflects centuries of Chinese, Malay and Thai trade.",
        "word": {"thai": "ท่าเรือ", "roman": "tha ruea", "meaning": "harbour"},
        "cards": ["Ko Yo Weaving"],
        "page": "a memory: 'between sea and lake, every road crosses.'",
    },
    {
        "id": "pattani",
        "name": "Pattani",
        "title": "The Painted Bow",
        "kind": "province",
        "act": 5,
        "minutes": 8,
        "pos": (197, 245),
        "lines": [
            ("NARRATOR", "TEXT", "Krue Se Mosque stands over the water, and the kolek boats are painted by hand."),
            ("NOI", "NOI", "Shoes off, shoulders covered, ask before photos. Respect gets you the story here."),
            ("PAINTER", "TEXT", "The bow takes the sea's eye. Paint it well and it will look back."),
        ],
        "activity": {
            "type": "choice",
            "prompt": "How do you enter the mosque ground?",
            "options": [
                {"text": "Take my shoes off, cover my shoulders, ask first", "respect": 3, "reply": "Thank you. Come in, and listen well."},
                {"text": "Walk straight in — it's just a look", "respect": 0, "reply": "Wait. Not like that. Come back when you understand."},
            ],
            "tries": 2,
        },
        "learn": "Pattani Malay (Yawi) is the local language. The Lim Ko Niao festival includes a famous fire-walking ceremony.",
        "word": {"thai": " masjid", "roman": "masjid", "meaning": "mosque"},
        "cards": ["Kolek Boat", "Lim Ko Niao"],
        "page": "a memory: 'one city, three faiths, one sea.'",
    },
    {
        "id": "yala",
        "name": "Yala",
        "title": "Wax and Colour",
        "kind": "province",
        "act": 5,
        "minutes": 7,
        "pos": (197, 264),
        "lines": [
            ("NARRATOR", "TEXT", "Wat Khuha Phimuk, a cave temple holding a reclining Buddha from the Srivijaya era."),
            ("NOI", "NOI", "Batik. Wax, colour, dye. The pattern is yours — hand-drawn, like Yaai's map."),
        ],
        "activity": {
            "type": "match",
            "prompt": "Draw the batik: choose the wax line for the border",
            "options": ["drawn line", "vines", "cloud band"],
            "decoys": ["printed dots", "glue", "staples"],
            "tries": 3,
        },
        "learn": "Yala is home to Buddhist, Muslim and Chinese communities, and its crafts and food reflect all of them.",
        "word": {"thai": "มลาย", "roman": "ma lai", "meaning": "Malay"},
        "cards": ["Batik"],
        "page": "a wax seal, pressed crooked and proud.",
    },
    {
        "id": "narathiwat",
        "name": "Narathiwat",
        "title": "The Last Chorus",
        "kind": "province",
        "act": 5,
        "minutes": 8,
        "pos": (225, 271),
        "lines": [
            ("NARRATOR", "TEXT", "The last page waits near the sea, close to Taksin Ratchaniwet Palace."),
            ("SINGER", "YAAI", "Dikir Hulu. You lead the chorus — we answer. Silat moves like a dance after it."),
        ],
        "call": "This is the last page. The one she wrote about him. Read it slowly, child. And when you have read it, do what she could not do for forty years.",
        "activity": {
            "type": "rhythm",
            "prompt": "Lead the chorus: call, and let the group answer",
            "sequence": ["left", "right", "left", "up", "up"],
            "tries": 3,
        },
        "learn": "Dikir Hulu is a sung performance blending rhythm, poetry and humour. Silat is a Malay martial art that moves like a dance.",
        "word": {"thai": "ร้อง", "roman": "rong", "meaning": "to sing"},
        "cards": ["Dikir Hulu", "Silat"],
        "page": "a song line: 'the last chorus is yours to lead.'",
        "call": "You have all my teachers now. Come home.",
    },
]

FINALE = {
    "id": "finale",
    "name": "The Wai Khru",
    "lines": [
        ("NARRATOR", "TEXT", "Dusk at Yaai's village. A Nora stage stands under a canopy lit by lamps."),
        ("NOI", "NOI", "All twenty-four. Look at them rise."),
        ("LOM", "SPIRIT", "Little flame. Did you think I would miss the ending? One last spell, and the sky is yours."),
        ("YAAI", "YAAI", "Rong Khru is where a dancer honours her teachers and her ancestors. Calm him first. Then we dance."),
        ("NARRATOR", "TEXT", "The pages form a song and a map: the melody from Nakhon, the beacons from Phuket, the sea from Ko Lipe, the batik from Yala."),
        ("YAAI", "YAAI", "The last page is blank. Page twenty-five is yours. Write the story you loved most."),
    ],
    "code": {
        "title": "CALM THE WIND", "kind": "gauntlet", "fx": "festival",
        "parts": [
            {"kind": "set", "var": "knots", "expect": 3},
            {"kind": "lines", "expect": ["hush", "hush", "hush"]},
            {"kind": "func", "name": "release",
             "calls": [(("storm",), "sky: clear")]},
        ],
        "prefill": 'knots = 0\nprint("howl")\ndef release(wind):\n    return wind',
        "status": "Lom's last bargain: count his knots, hush him thrice, release the storm.",
        "broken": "the wind's own spell. It counts nothing and howls instead.",
        "hint": "knots is 3. Hush three times. Release any wind to 'sky: clear'.",
        "praise": "The wind sits down like a scolded dog. The lamps stop shaking.",
    },
    "after": [
        ("LOM", "SPIRIT", "...Hushed. Three times hushed. Keep your sky, little flame. I will borrow someone else's."),
        ("NOI", "NOI", "Did you see that? Did you SEE that?"),
        ("YAAI", "YAAI", "Rong Khru is where a dancer honours her teachers and her ancestors. We do it with you."),
    ],
}

# Lom speaks when the journey crosses into a new act.
LOM_TAUNTS = {
    2: "Little flame, little thief. I scattered them across two seas, and still you gather crumbs.",
    3: "Two coasts down. Come south, then. I am waiting with your last pages, and I am done being gentle.",
}

# Every recovered page restores one of Yaai's memories. Visions play
# with the reward, in her voice.
VISIONS = {
    "chumphon": "I shelled beans on this market floor. My mother counted my mistakes. There were many.",
    "ko_tao": "Your grandfather swam with turtles here. He came up crying — happy crying.",
    "ko_pha_ngan": "A king's boatman once shared his rice with me. I never learned his name.",
    "ko_samui": "Hin Ta proposed to Hin Yai at sunset. The whole beach cheered. Probably.",
    "surat_thani": "I pulled the Chak Phra rope at seven. My hands bled. I was so proud.",
    "ranong": "Kaw Sim Bee drank tea at my wedding. He pinched my cheek like kin.",
    "surin_islands": "A Moken grandmother taught me the wave song. Sing it and you will not drown.",
    "khao_lak": "I lit a lantern here every year since. Now you hold it with me.",
    "similan": "I counted nine islands with your mother. She always skipped eight, to tease me.",
    "phang_nga": "I learned to head a football on a raft. I was terrible. Gloriously terrible.",
    "phuket": "The two sisters drank my tea before the battle. I pretended not to shake.",
    "promthep": "Your grandfather proposed here. The sun agreed before I did.",
    "ko_phi_phi": "I climbed the bamboo once. Once. My knees still remember.",
    "krabi": "I tied my first ribbon for Mae Ya Nang with shaking hands.",
    "nakhon": "My teacher placed my fingers so. Long finger picks. Like this, child.",
    "phatthalung": "Noi was carved on a rainy night. He talked back before the paint dried.",
    "trang": "Dawn tapping, then the loudest songs. Your great-grandfather sang off-key on purpose.",
    "ko_kradan": "I floated here while the dugongs grazed below. Heaven is shallow.",
    "satun": "Prisoners carved hope into these walls. I read them all, once.",
    "ko_lipe": "I sent my griefs out on a little boat. The tide kept its promise.",
    "songkhla": "I wove one cloth in my life. It was crooked. I loved it fiercely.",
    "pattani": "Lim Ko Niao's sister walked the fire and laughed. So did I, watching.",
    "yala": "My first batik bled blue into everything. Including the cat.",
    "narathiwat": "I led the chorus once. My voice cracked. Everyone answered anyway.",
}

# ------------------------------------------------------------------- plot
# The spine of the story. Lom the Monsoon is not a weather event: he is
# a thief of memory, and a former student of Yaai's teacher. He appears
# between acts, and again at every stop through SCENES below. Nothing
# is teleported, nothing is a cutscene *away* from the map — he speaks
# on the wind, wherever you happen to be standing.
PLOT = {
    1: [
        ("NARRATOR", "TEXT", "The first night on the road, you sleep in a schoolroom with your sandals as a pillow, and somewhere south the storm is taking a page off a notice board."),
        ("NOI", "NOI", "Listen. That is the wind turning. It happens the same time every night now, and it happens a little further south each time."),
        ("NOI", "NOI", "Yaai's teacher used to say the wind goes round the south the way a hand goes round a bowl. I never understood it. I think I do now."),
        ("YOU", "PLAYER", "What is it doing?"),
        ("NOI", "NOI", "It is taking something, and it is taking it in order, and it is not in a hurry, and that is the worst of it. A thief in a hurry can be beaten."),
        ("NOI", "NOI", "One down, twenty-three to go. And the one thing I will not tell you, because you are young and there is no reason to carry it: I know whose hand it is."),
    ],
    2: [
        ("NARRATOR", "TEXT", "That night the wind changes. It smells of rain, and of someone else's handwriting."),
        ("LOM", "SPIRIT", "Little flame. You found five. I took five. Do you see yet how this ends?"),
        ("NOI", "NOI", "That voice — I know that voice. It used to sing me to sleep in the puppet workshop in Phatthalung."),
        ("LOM", "SPIRIT", "Stories are wasted on the places that make them. Told once at a wake, forgotten by the next monsoon. I keep them. I keep them ALL, forever, where nothing can rust them."),
        ("NOI", "NOI", "He keeps them where no one can HEAR them. That is not keeping. That is burying."),
        ("LOM", "SPIRIT", "Walk the coast, then. Every page you lift, I have already copied. Bring me the originals. The west coast is where I was made, and it is where I will be rich."),
    ],
    3: [
        ("NARRATOR", "TEXT", "On the road south a magpie drops a page at your feet. The ink is still wet. Yaai's hand never shook."),
        ("NOI", "NOI", "Hold it to the light. ...This is a COPY. He is not only taking the stories. He is writing new ones, and signing Yaai's name to them."),
        ("LOM", "SPIRIT", "You are slow, little flame, but you are thorough. Yes. I curate. The old versions are messy — full of grief and cheap rice and unpaid debts. Mine are clean."),
        ("YOU", "PLAYER", "You knew my grandmother."),
        ("LOM", "SPIRIT", "...I knew your grandmother's teacher. I was the better student. And when he died, everyone let him simply STOP. I refused. I will never let anyone simply stop."),
        ("NOI", "NOI", "The deep south, then. The last pages are the ones Yaai wrote about HIM. That is why he saved them till last."),
    ],
    4: [
        ("NARRATOR", "TEXT", "The rain comes down for nine days and the pages come with it. Not falling. Arriving \u2014 pinned to trees, tucked in doorways, laid out along the road like a welcome."),
        ("NOI", "NOI", "He is not hiding them any more. He is GIVING them out. Every page we lift now, he has put where we will find it, and he has put the next one closer to home."),
        ("LOM", "SPIRIT", "You are nearly there, little flame. I have been walking ahead of you for a year, and now I am walking beside you, and you still do not understand that we are going the same way."),
        ("LOM", "SPIRIT", "I kept them because they were being wasted. Stories told once at a wake, forgotten by the next monsoon. I kept them so they would last. What have you been doing for forty years, Yaai? TALKING."),
        ("NARRATOR", "TEXT", "And in the last town, a man who has been helping you since Phatthalung is standing at the pass with a bag of pages and a face you have never seen on anybody."),
        ("NOI", "NOI", "That is the face of a man who has been carrying something for someone else for a very long time, and has just been told that he no longer has to."),
        ("YOU", "PLAYER", "You gave him the pages."),
        ("LOM", "SPIRIT", "I gave him permission. There is a difference, and it is the only difference there is, and I am sorry \u2014 no. I am not sorry. Ask him what he did with them."),
    ],
    5: [
        ("NARRATOR", "TEXT", "The last pages are not in the deep south at all. They are up the pass, in the broken shrine, where the lamps have been broken one at a time by somebody keeping a promise to come back."),
        ("NOI", "NOI", "It is up there. The cup is up there. And the cup has been up there for a year, and he has been up there alone every time, waiting for somebody to sit down at it."),
        ("YOU", "PLAYER", "Why won't he just take it and go?"),
        ("NOI", "NOI", "Because he is not a thief, child. He is the boy in the puppet workshop who was the better student, and the better student was the one who would not STOP, and they all stopped him, and he has been trying to finish their stories ever since."),
        ("NOI", "NOI", "He took the pages so that they would not be forgotten. And he has been waiting at the top of a mountain for forty years for somebody to come and tell him it was all right."),
        ("LOM", "SPIRIT", "There is a cup at the shrine, and there is a cup at every place I stopped, and there is one more thing you have not noticed, and I will tell you because you have carried my letters a long way."),
        ("LOM", "SPIRIT", "There is only one cup at the shrine. For two. I have been setting it for two since the day Yaai took the boy out of the binding and did not put him back, because a binding with two in it belongs to nobody, and I have been nobody for forty years."),
        ("YOU", "PLAYER", "...Noi. What is a binding?"),
        ("NOI", "NOI", "A promise between a person and a spirit, to call each other back. Yaai broke one, and the spirit that came out has been walking the South, collecting everything it could, trying to become a person again."),
        ("NOI", "NOI", "He is not the monster in this story. He is what is left when a promise is broken, and nobody comes back for it."),
    ],
}

# Three story beats per stop. The page is never simply lying there —
# Lom's magpies (khaek) are always one step ahead, hiding, renaming,
# replacing. Beat by beat:
#   arrive : what is wrong the moment you walk in
#   mid    : the plot turn, spoken when you stop and look at the sight
#   spark  : what you read once the hidden page is in your hand
SCENES = {
    "chumphon": {
        "arrive": [
            ("KEEPER", "YAAI", "Yaai's province, and mine. Page one was written in that market, before you were born — she wrote down everything the old people said, and did not trust her memory to keep it."),
            ("KEEPER", "YAAI", "But page one is not in the market any more. Something walked in last night and lifted it off the notice board. Come — look at the mast, and tell me what you see."),
            ("NOI", "NOI", "Look how the board is nailed. One nail, middle, then the rest. That is not a storm. Storms do not carry a hammer."),
        ],
        "mid": [
            ("NOI", "NOI", "Look at the mast — black feathers. The same as Yaai's windowsill."),
            ("KEEPER", "YAAI", "A bird sat up there all night, watching the harbour like it was taking notes. It flew the moment I said the Prince's name aloud. Whatever it is, it fears being NAMED."),
            ("NOI", "NOI", "Then we name everything we find. Starting with that page."),
            ("KEEPER", "YAAI", "Name it, then — but name it PROPERLY. Write it down. A thing written down is a thing that cannot be shuffled into another story."),
        ],
        "spark": [
            ("NOI", "NOI", "Here it is — behind the fish baskets, still damp. He read it here, in the open, where anyone could see him. He is not hiding. He is daring us."),
            ("NOI", "NOI", "And look — under it, a second sheet. He left us the clean copy."),
            ("NOI", "NOI", "The clean one is not Yaai's handwriting. It is neater. It is a person's handwriting pretending to be hers."),
            ("NOI", "NOI", "Keep it dry. One down, twenty-three to go."),
        ],
    },
    "ko_tao": {
        "arrive": [
            ("VOLUNTEER", "SPIRIT", "You are late for the hatch — but so are the turtles, and that has never happened in my eleven years here."),
            ("NOI", "NOI", "They will not come ashore while that bird sits on the sandbar. If the turtles do not nest, the village has nothing to count and nothing to sing about. He attacks the story by attacking the thing it is about."),
            ("VOLUNTEER", "SPIRIT", "My grandmother counted the turtles before me. Her grandmother before her. The count is not a number. It is a promise."),
        ],
        "mid": [
            ("NOI", "NOI", "The turtles came up early today. They do that when the water tastes wrong. Or when something black is standing on the reef."),
            ("VOLUNTEER", "SPIRIT", "A magpie has paced the sandbar for two days. Every time a swimmer surfaces it cocks its head, as if comparing us to something it remembers."),
            ("NOI", "NOI", "It is not hunting us. It is CHECKING us. Looking for one of us in this crowd."),
        ],
        "spark": [
            ("NOI", "NOI", "Wedged in the reef, half under coral. Mind the ledge — the colony spent sixty years growing it."),
            ("NOI", "NOI", "The page is wet, but the ink held. Yaai wrote in rain-proof ink. She always expected to be ambushed."),
            ("NOI", "NOI", "There is a note folded inside it, in a hand neither of us knows. Small words. It says: the sea keeps what the land forgets."),
        ],
    },
    "ko_pha_ngan": {
        "arrive": [
            ("NOI", "NOI", "The stone with the kings' initials — this is where people come to prove the story is real. So of course he came here first, like a man signing a wall he did not build."),
            ("NOI", "NOI", "A new set of initials, cut last week. Go and look. Tell me if the hand is steady."),
        ],
        "mid": [
            ("NOI", "NOI", "Someone carved a NEW set of initials under the old kings'. Sloppy. Left-handed. Yaai is right-handed."),
            ("NOI", "NOI", "He is writing his own history over ours. Even the stone is not safe."),
        ],
        "spark": [
            ("NOI", "NOI", "In a hollow under the western rock, folded small and left with a magpie feather on top."),
            ("NOI", "NOI", "A calling card. He wants us to know he is ahead of us. Good. A proud thief makes mistakes."),
        ],
    },
    "ko_samui": {
        "arrive": [
            ("ELDER", "YAAI", "Welcome. You will have heard about the ribbon. A tourist, I thought at first — but no. A bird cannot tie a ribbon. A bird with hands can."),
            ("NOI", "NOI", "The grandmother and grandfather stones. Every boat blesses here before the crossing, and every ribbon is a different prayer. Someone has tied the SAME colour on all of them, as if we all pray the same word."),
        ],
        "mid": [
            ("NOI", "NOI", "The old couple — someone tied a black-and-white ribbon round them and left it there like a fence post."),
            ("ELDER", "YAAI", "Whoever it is believes that if you rename a thing you own it. The rocks will outlast his ribbon."),
        ],
        "spark": [
            ("NOI", "NOI", "Tucked behind the grandfather stone, where the fishermen leave their coins."),
            ("NOI", "NOI", "Three pages now. Yaai would say: do not run. Read as you walk. A hurry is a kind of blindness."),
        ],
    },
    "surat_thani": {
        "arrive": [
            ("MONK", "YAAI", "Come, come — the rope is heavy and the day is short. Chak Phra needs hands, not questions. ...Though you do look like a person with questions."),
            ("NOI", "NOI", "Watch them pull. Half of them are pulling against the others, all perfectly certain they are right. That is what a false page does to a town."),
        ],
        "mid": [
            ("NOI", "NOI", "Half the town is pulling the wrong way today. They say a page told them to. A PAGE told them to."),
            ("MONK", "YAAI", "He is not only taking stories, child. He is giving them back, changed. That is worse."),
            ("NOI", "NOI", "Chak Phra works because everyone pulls the same way. Break the story, break the rope."),
        ],
        "spark": [
            ("NOI", "NOI", "Under the temple step, wrapped in banana leaf — hidden for a person who was LOOKING, not a person who was told."),
            ("NOI", "NOI", "That is the whole difference between a story and a rumour: a story survives you coming to it."),
        ],
    },
    "ranong": {
        "arrive": [
            ("NOI", "NOI", "The tin sheds, on the Andaman side, where it rains nine months and nobody comes for the sun. Yaai loved it here because it was honest about being hard."),
            ("NOI", "NOI", "The mine bell rang two hours early this morning. The whole shift walked out to a sea that was still dark."),
        ],
        "mid": [
            ("NOI", "NOI", "The tin pans came up empty — someone stamped the mine bell early and the whole shift walked off."),
            ("NOI", "NOI", "A false signal. A false page. Same trick, different town."),
        ],
        "spark": [
            ("NOI", "NOI", "In the empty ore cart, under the rain. The miners will be back by noon — take it before they do."),
            ("NOI", "NOI", "He used the bell they trust the most. That is how we will find him: he always uses the thing you trust."),
        ],
    },
    "surin_islands": {
        "arrive": [
            ("ELDER", "SPIRIT", "The Moken do not count time by clocks. We read the water. Tonight the water says a stranger stood here."),
            ("NOI", "NOI", "These islands are their home and the sea is their road, and he walked both in one night. He left a mark on the reef."),
        ],
        "mid": [
            ("NOI", "NOI", "The Moken read the sky, not the radio. Yesterday a magpie flew inland at dusk. The elders noticed."),
            ("ELDER", "SPIRIT", "A bird that leaves the sea to hide in the trees is carrying something it should not have. Watch the horizon, child."),
        ],
        "spark": [
            ("NOI", "NOI", "In the floating basket under the stilt house. The Moken keep their most careful things above the water."),
            ("NOI", "NOI", "They say a story told at sea belongs to the sea. He is trying to make it belong to one man."),
        ],
    },
    "khao_lak": {
        "arrive": [
            ("VILLAGER", "TEXT", "You are the one Noi sent for. Good. Look at the memorial — the lanterns. Tell me what is wrong."),
            ("NOI", "NOI", "This place remembers a wave. The lanterns are the remembering made visible. He came at night and MOVED them — not broke, moved. So the shrine tells the wrong story now."),
        ],
        "mid": [
            ("NOI", "NOI", "Someone moved the lanterns. Not knocked over — MOVED, in a row, facing the water."),
            ("VILLAGER", "TEXT", "That is not how we remember them. Whoever did it tidied my brother into a story that never happened."),
            ("NOI", "NOI", "Gentle hands, wrong hands. We put the lanterns back the way the village keeps them, before we leave."),
        ],
        "spark": [
            ("NOI", "NOI", "On the wall behind the shrine, folded inside the khom flag."),
            ("NOI", "NOI", "Memory is a doing, not a thing, child. If nobody moves the lanterns back, there is no memory — only lanterns."),
        ],
    },
    "similan": {
        "arrive": [
            ("NOI", "NOI", "Nine islands, and a name on a rock. Sailors named these before anyone drew a map — the names are how a sailor finds his way home in the dark."),
            ("NOI", "NOI", "The eighth island has a new name now. Painted on the rock, in English, in a font. That is the worst part. A font."),
        ],
        "mid": [
            ("NOI", "NOI", "The eighth island has a new name painted on the rock. In English. In a font."),
            ("NOI", "NOI", "Sailor's names are given, not pasted. Scrub it before we sail. The sea already knows this island."),
        ],
        "spark": [
            ("NOI", "NOI", "In the tidal pool at low water, pinned under a smooth stone."),
            ("NOI", "NOI", "One more page. A name is a promise you make to a place. He has been breaking promises all week."),
        ],
    },
    "phang_nga": {
        "arrive": [
            ("BOY", "CHILD", "You came for the page! But first — our bell. It rang at the wrong time and everyone went home. Everyone but me."),
            ("NOI", "NOI", "A floating school. Classes travel by boat, and the bell is how children know when to come back. He has started ringing it himself."),
        ],
        "mid": [
            ("NOI", "NOI", "The floating school's bell rang by itself and half the children rowed home. He is playing with the schedule now."),
            ("BOY", "CHILD", "It wasn't time! I know our own bell!"),
            ("NOI", "NOI", "Small cruelty. Little falsehoods. That is how a place forgets itself — one wrong bell at a time."),
        ],
        "spark": [
            ("NOI", "NOI", "Under the hull of the school boat, where the tide will not reach it."),
            ("NOI", "NOI", "Small cruelties are how big silences get made. Remember that. It is the whole of his method."),
        ],
    },
    "phuket": {
        "arrive": [
            ("AUNTIE", "YAAI", "The Sisters. Two women who sat down in the road in 1785 and would not move, and stopped an army with nothing but staying."),
            ("NOI", "NOI", "And there, pinned to the shrine — orders. Battle orders, in the Sisters' voice. But the Sisters never wrote orders. They wrote recipes and refused to run."),
        ],
        "mid": [
            ("NOI", "NOI", "Wet ink. On the Sisters' own orders. Hold on — this page is a forgery."),
            ("AUNTIE", "YAAI", "Those are not the Sisters' words. Those are MINE, and I am no general."),
            ("NOI", "NOI", "He is not stealing the story any more. He is rewriting it. Page by page we take it back."),
        ],
        "spark": [
            ("NOI", "NOI", "Behind the incense shelf — the real page, the old one."),
            ("NOI", "NOI", "Compare the ink. The old page is brown at the edges. His forgery is still wet. That changes everything we thought we knew."),
        ],
    },
    "promthep": {
        "arrive": [
            ("NOI", "NOI", "The last cape of the peninsula. People come here to watch the sun leave for the day. Yaai brought you here once, when you were small. You will not remember it. She did."),
            ("NOI", "NOI", "Look west. The sun is early today — by eleven minutes. He is buying pieces of the sky now."),
        ],
        "mid": [
            ("NOI", "NOI", "The sunset is early. By eleven minutes. He is moving the light, or buying the sky something to say."),
            ("NOI", "NOI", "Photograph it true, child. A remembered sunset is a kind of evidence."),
        ],
        "spark": [
            ("NOI", "NOI", "Under the lookout rail, where children leave shells for the next children."),
            ("NOI", "NOI", "Eleven minutes. He moved the sun eleven minutes and thought nobody would notice. Somebody always notices."),
        ],
    },
    "ko_phi_phi": {
        "arrive": [
            ("COLLECTOR", "TEXT", "You want the cave? The swiftlets want the cave too, and they have not come home."),
            ("NOI", "NOI", "The nests are worth more than gold, and the birds will only return to a dark that feels right. Someone took a lamp. That is all it takes to empty a cave."),
        ],
        "mid": [
            ("NOI", "NOI", "The swiftlet cave is quiet. Too quiet — a lamp is missing and the birds will not come home to a dark that feels wrong."),
            ("COLLECTOR", "TEXT", "Whatever took it did not take it for money. It took it so that the story would have a hole in it."),
        ],
        "spark": [
            ("NOI", "NOI", "On the cave ledge, in the nest the birds abandoned."),
            ("NOI", "NOI", "He did not steal the nests. He stole the DARK. He is teaching the birds to distrust their own home."),
        ],
    },
    "krabi": {
        "arrive": [
            ("FISHER", "SPIRIT", "Welcome aboard. Do not mind the ribbons — they are all the same colour today. The gremlin's work, not ours."),
            ("NOI", "NOI", "Every long-tail boat carries ribbons for Mae Ya Nang, the spirit of the boat. Each owner picks their own colour. One colour for all means one owner for all."),
        ],
        "mid": [
            ("NOI", "NOI", "The ribbons on the long-tail bows are all the same colour today. Someone standardised them."),
            ("FISHER", "SPIRIT", "Mae Ya Nang does not care what colour. But SHE chose hers, and we chose ours. That is the whole point of a ribbon."),
            ("NOI", "NOI", "Take one back. One is enough to remember how choice works."),
        ],
        "spark": [
            ("NOI", "NOI", "Tangled in the trawler net, dry as a bone."),
            ("NOI", "NOI", "Tie one ribbon your own colour before we leave. Not for the spirit — for the crew, so they remember they are allowed to choose."),
        ],
    },
    "nakhon": {
        "arrive": [
            ("DANCER", "YAAI", "You have come for the Nora. Wait — watch my hands. No, really watch them."),
            ("NOI", "NOI", "Nora is older than the kingdom. Every dancer inherits her hands from a teacher, hand to hand, and remembers the teacher's name out loud."),
        ],
        "mid": [
            ("NOI", "NOI", "The Nora dancer's hands are wrong. The teacher placed them. Someone moved them."),
            ("DANCER", "YAAI", "Every Nora remembers who taught her. If the book of teachers is lost, we are all just moving our arms."),
            ("NOI", "NOI", "I was carved in Phatthalung, three provinces from here. I am somebody's memory too. So are you."),
        ],
        "spark": [
            ("NOI", "NOI", "In the teacher's book, between the pages about the founding of the school."),
            ("NOI", "NOI", "If the book is lost, then nobody's hands are wrong and nobody's are right — and that suits him exactly."),
        ],
    },
    "phatthalung": {
        "arrive": [
            ("PUPPETEER", "NOI", "Little brother! You came home. ...And you brought the child. Good. Sit down — this workshop made you both."),
            ("NOI", "NOI", "Nang Talung shadow puppets. Cut from cowhide, held up to a lamp, every voice made by one throat. This is where I was made."),
        ],
        "mid": [
            ("NOI", "NOI", "This is the workshop. This is where I was cut from cowhide and given a voice."),
            ("PUPPETEER", "NOI", "Little brother! ...You are shaking. Look — his hands. Lom carved me once, before you. He was always the better carver and the worse listener."),
            ("NOI", "NOI", "I remember him now. He never let a story end. Not even mine. He would re-run the same act until the puppets tore."),
        ],
        "spark": [
            ("NOI", "NOI", "In the puppet trunk, under the spare faces. Faces I have worn."),
            ("NOI", "NOI", "...He carved me, child. Before I was Yaai's, I was his. Do not tell me that means nothing. It means everything, and it changes nothing."),
        ],
    },
    "trang": {
        "arrive": [
            ("TAPPER", "TEXT", "You picked a wet night for the grove. Mind your footing — the cups are full and the rain makes the latex run."),
            ("NOI", "NOI", "Rubber. Kaw Sim Bee brought it from Ranong and the whole South changed in one generation. Cut shallow and the tree gives for fifty years. Cut deep and it gives once."),
        ],
        "mid": [
            ("NOI", "NOI", "The tappers all received the same page: cut deeper. If they cut deeper, the trees bleed out."),
            ("TAPPER", "TEXT", "Kaw Sim Bee taught us shallow cuts, patient cuts. This page is trying to empty the forest."),
            ("NOI", "NOI", "A story that kills the thing it comes from is a bad story. That is the first rule Yaai ever taught me."),
        ],
        "spark": [
            ("NOI", "NOI", "In the collection cup on the oldest tree. He would not touch the oldest tree — he knows it is watching."),
            ("NOI", "NOI", "He wrote them a page that would kill the forest, and dressed it as advice. That is what he does with everything."),
        ],
    },
    "ko_kradan": {
        "arrive": [
            ("NOI", "NOI", "Quiet today. The dugong grass should be full of them, and it is empty. Something has scared them off the shallows."),
            ("NOI", "NOI", "A dugong cannot be chased. You float, you wait, and it decides you are a rock. Someone here did not wait."),
        ],
        "mid": [
            ("NOI", "NOI", "Dugong tracks, and then no more tracks. Something chased them off the seagrass."),
            ("NOI", "NOI", "Whoever it was, he was in a hurry. Hurry is how you can tell he is lying."),
        ],
        "spark": [
            ("NOI", "NOI", "In the seagrass bed, weighted down with a coral stone."),
            ("NOI", "NOI", "Nobody in a hurry has ever listened to anything. That is why the sea will not keep his secrets."),
        ],
    },
    "satun": {
        "arrive": [
            ("GUIDE", "SPIRIT", "The logbook of the old harbour. Read it and you will see that the page is torn."),
            ("NOI", "NOI", "Satun sat on the pirates' road. Some of the town's history is ugly. It is still history."),
        ],
        "mid": [
            ("NOI", "NOI", "The logbook is torn at 1940 — but the tear is clean. A knife, not a war."),
            ("GUIDE", "SPIRIT", "Someone wanted the pirates edited out. Some stories are inconvenient to a man who sells only pleasant ones."),
            ("NOI", "NOI", "Yes. Put the pirates back. Everyone should see the whole page."),
        ],
        "spark": [
            ("NOI", "NOI", "Folded into the back cover of the ledger, where the missing years should be."),
            ("NOI", "NOI", "He cuts out the ugly parts so the pretty parts can be sold. The whole page or nothing — that is the deal."),
        ],
    },
    "ko_lipe": {
        "arrive": [
            ("FAMILY", "YAAI", "You are just in time for Loy Reua. Make a boat, put your troubles in it, and let the water keep them."),
            ("NOI", "NOI", "Watch the children — they put a nail and a coin in theirs, so the little boat carries weight, so it does not drift back."),
        ],
        "mid": [
            ("NOI", "NOI", "The little boats they send off — someone has been collecting them downstream and selling them back."),
            ("FAMILY", "YAAI", "Loy Reua is for letting go. You may not sell what you were asked to release."),
            ("NOI", "NOI", "Let it go, then. All the way to the horizon, where nobody's fingers can reach it."),
        ],
        "spark": [
            ("NOI", "NOI", "Caught in the mangrove roots where the tide left it."),
            ("NOI", "NOI", "He cannot let anything go either. Not a boat, not a page, not a story. That is not love, child. That is a fist."),
        ],
    },
    "songkhla": {
        "arrive": [
            ("NOI", "NOI", "Ko Yo, where the cloth is woven. Feel this. The loom's pattern stops halfway and a machine finished it."),
            ("NOI", "NOI", "Hand-woven cloth is slow on purpose. The slowness IS the pattern. You can see exactly where a person stopped and a printer began."),
        ],
        "mid": [
            ("NOI", "NOI", "The loom's pattern stops halfway. A machine finished it — you can see where the hand stopped and the printer began."),
            ("NOI", "NOI", "Ko Yo cloth is slow on purpose. The slowness IS the pattern. He cannot copy that, however hard he tries."),
        ],
        "spark": [
            ("NOI", "NOI", "Wrapped in a bolt of cloth that was never finished."),
            ("NOI", "NOI", "He cannot copy slowness. That is how we will find him out — he is always, somewhere, in a hurry."),
        ],
    },
    "pattani": {
        "arrive": [
            ("PAINTER", "TEXT", "Stand clear — I am painting the eye. ...I WAS painting the eye. Every boat in this harbour has a closed one now."),
            ("NOI", "NOI", "A kolek boat carries a painted eye on its bow, to watch over the crew on the water. Every eye here is shut."),
        ],
        "mid": [
            ("NOI", "NOI", "The kolek boat's painted bow — the eye is closed. On every boat in the harbour. Shut. Who shuts an eye?"),
            ("PAINTER", "TEXT", "A bow eye is for looking after you. Whoever closed them does not want these boats to see where they have been."),
            ("NOI", "NOI", "Open one. Give the boats their eyes back."),
        ],
        "spark": [
            ("NOI", "NOI", "In the fish hold of the oldest boat, under the brine."),
            ("NOI", "NOI", "A coast that cannot see where it has been can be told anything at all. Remember that."),
        ],
    },
    "yala": {
        "arrive": [
            ("NOI", "NOI", "The batik workshop runs all night. The wax resists the dye — the pattern IS the wax's refusal. That is the whole art."),
            ("NOI", "NOI", "Someone drew the pattern wrong and let the wax run, so the cloth looks ruined. As if the hands here had gone careless."),
        ],
        "mid": [
            ("NOI", "NOI", "The batik wax is running. Someone drew the pattern wrong and let it bleed, to look accidental."),
            ("NOI", "NOI", "Nothing here is accidental. He wants the cloth to look ruined, so that we stop making it."),
        ],
        "spark": [
            ("NOI", "NOI", "Under the wax pot, wrapped in a batik that never made it to the dye."),
            ("NOI", "NOI", "If the pattern looks ruined, the pattern dies with us. We will not let that happen. Not here, not anywhere."),
        ],
    },
    "narathiwat": {
        "arrive": [
            ("SINGER", "YAAI", "You hear that? Dikir Hulu. One voice calls and the group answers. It is a conversation, not a concert."),
            ("NOI", "NOI", "Listen to what the group is answering. That verse was never written by these elders. He answered for the whole town."),
        ],
        "mid": [
            ("NOI", "NOI", "The chorus is on the wrong verse. The call went up and everyone answered — but they answered a verse the elders never wrote."),
            ("SINGER", "YAAI", "Dikir Hulu is a conversation. He answered for us. That is the rudest thing one voice can do to another."),
            ("NOI", "NOI", "This is the last page, child. After this he has nothing left to answer with. Come — lead."),
        ],
        "spark": [
            ("NOI", "NOI", "Here. The youngest singer was hiding it for you, under her seat."),
            ("NOI", "NOI", "After this he has nothing left to answer with. Come. Lead the chorus yourself. He will hear it, wherever he is standing."),
        ],
    },
}


def scene_of(stop_id, key):
    """One story beat for a stop: ``arrive``, ``mid`` or ``spark``."""
    return SCENES.get(stop_id, {}).get(key, [])

# ------------------------------------------------------------------- indexes
STOP_BY_ID = {s["id"]: s for s in STOPS}
TOTAL_STOPS = len(STOPS)
TOTAL_PAGES = 1 + TOTAL_STOPS + 1      # cover + stops + finale page


def chapter(stop):
    """The journal name of a stop: 'Chapter N · Title'."""
    return "Chapter %d · %s" % (STOPS.index(stop) + 1, stop["title"])

# Lore documents — letters, journals, murals and songs that the journal
# collects alongside the pages. Each is unlocked as a Culture Card, and
# its text is readable in the journal (CARDS tab). They are the slow
# reveal: the more you read, the more Yaai's teacher and the puppet
# workshop make sense.
LORE = {
    "The First Page": (
        "Chumphon Market, the first week of the cool season. Yaai, aged nine, "
        "with her grandmother's squid stall. The page records what she was "
        "told about the light: that it was not built to send ships away, "
        "but to bring one home. Bang Dot's grandfather lit the lamp by hand "
        "for thirty years and never once missed a night."),
    "The Keeper's Letter": (
        "Unsent, in Bang Dot's hand, folded into a signal-flag case: "
        "'To whoever is looking for the pages — the bird does not take things. "
        "It RETURNS things. Every page it carried, it carried back to the "
        "same house it was written in. I have watched it for three nights. "
        "It comes back empty every time, and it comes back angry.'"),
    "The Signal Code": (
        "Signal Hill keeps a code of flags for hulls that cannot speak. "
        "One flag means: I have lost a thing and cannot say so. Two flags "
        "mean: send help, but not the kind that counts. Bang Dot has not "
        "needed it since 1992, and keeps the flags anyway."),
    "The Night Boat Song": (
        "A song the boats sing on the water at night, in the old sea-tongue "
        "the people of the isles use. The tune is called 'the sea keeps what "
        "the land forgets'. Ploy says it is a blessing. Yaai's note in the "
        "margin says: 'it is a warning, and someone has been rewriting it.'"),
    "The Turtle Master's Letter": (
        "From the turtle master of Ko Tao to the volunteer who counts the "
        "hatchlings: 'Count them in ones, and write down the number, and the "
        "number will hold. If you count them in thousands, the sea hears you "
        "and takes one for itself. In this year the sand mounds are late, "
        "and I have seen a bird that walks like a man.'"),
    "Yaai's Teacher's Note": (
        "In the puppet workshop in Phatthalung, on the back of a pattern for "
        "a cowhide bird: 'Two students again this year. One will stay. One "
        "will not. I have told them both the same thing, and the one who "
        "leaves will remember it longest, and that will be the cruelty of it. "
        "The binding holds only while someone calls it back.'"),
}

ACTS = [
    (1, "The Stolen Sea", 0, 3),
    (2, "The Wind That Answers", 4, 9),
    (3, "The Pearl Coast", 10, 12),
    (4, "What the Rain Remembers", 13, 19),
    (5, "The Wai Khru", 20, 23),
]

# ------------------------------------------------------------------ the hosts
# Every stop has a local character standing by its pin, plus one hidden
# page-spark tucked somewhere nearby. ``look`` is one of the NPC sprites
# (ruen / nok / child). The host chats after the stop is done; the spark
# is found by exploring and pays +1 Respect.
EXTRA = {
    "chumphon": {
        "host": "Bang Dot", "look": "nok",
        "lines": ["Tides wait for no one — not even lost pages.",
                  "The Prince's shrine first, questions later.",
                  "Thirty-one years I have trimmed that lamp. It has outlived four boats, two storms and my wife.",
                  "Your grandmother wrote that page in my mother's stall. She bought squid. She always bought too much squid."],
        "later": ["Now that you have it, I will say the thing I could not say to a stranger.",
                  "The magpie did not take the page off the board. It took the page OFF THE BOARD — the nails are still in the wood.",
                  "Yaai came through here every year. Every year she asked me the same question: is the lamp lit? I always said yes.",
                  "This year I could not say it. That is why she lost them all."],
        "hint": "Noi: something shiny behind the fish baskets, east side.",
        "found": "A fish-scale bookmark. The market gives what the sea lent.",
        "sight": {"label": "the drying racks", "dx": -3, "dy": 1, "text": "Fish dry in silver rows, salted for monsoon months."},
    },
    "ko_tao": {
        "host": "Ploy", "look": "child",
        "lines": ["Shhh. She hears fins before voices.",
                  "Count turtles, not minutes.",
                  "If you splash, you are asking the sea to talk over you. It will.",
                  "My grandmother said the night boats carry songs to people who cannot leave."],
        "later": ["You found the note. Then you know about the songs.",
                  "The night boats come from the isles west of here. People who live on the sea. They do not land.",
                  "They said they saw a man in the water, taking pages from a wreck. A man who did not swim like a man.",
                  "I did not believe them. I am beginning to."],
        "hint": "Noi: check the tide pool, under the longtail's shadow.",
        "found": "A turtle-shell button. Ploy says the sea dropped it for you.",
        "sight": {"label": "the fish trap", "dx": -2, "dy": 0, "text": "A fish trap, empty by law. The turtles come first here."},
    },
    "ko_pha_ngan": {
        "host": "Lung Khob", "look": "nok",
        "lines": ["Kings carved their names here. Sign the guestbook, not the rock.",
                  "Waterfall's loud today. Means rain up the hill."],
        "hint": "Noi: where the mist is thickest, behind the falling water.",
        "found": "A waterproof page corner. Even kings lost things here.",
        "sight": {"label": "the King's rock", "dx": -2, "dy": -2, "text": "Initials a century deep. Touch gently."},
    },
    "ko_samui": {
        "host": "Pa Nim", "look": "ruen",
        "lines": ["He sailed for her hand, and the sea said no.",
                  "They hold hands still. Look at low tide."],
        "hint": "Noi: where the grandparents' offerings pile, at their feet.",
        "found": "A pebble worn smooth as an elder's hand.",
        "sight": {"label": "the grandparents", "dx": -1, "dy": -3, "text": "Two grandparents, holding hands against the tide."},
    },
    "surat_thani": {
        "host": "Luang Phi Ek", "look": "ruen",
        "lines": ["Grip the rope, not the float.",
                  "Pull together, or don't pull at all."],
        "hint": "Noi: tap the temple drum. Something rattles inside.",
        "found": "A drumstick splinter. It kept the beat so you don't have to.",
        "sight": {"label": "the old chedi", "dx": 0, "dy": -3, "text": "A Srivijaya chedi. A thousand years of mornings."},
    },
    "ranong": {
        "host": "Ah Ma", "look": "ruen",
        "lines": ["Tin built this town. Steam warms it.",
                  "Kaw Sim Bee built half this town. The other half is steam."],
        "hint": "Noi: behind the spring rocks, where the steam hides you.",
        "found": "A tin token stamped with a dragon. Ah Ma winks: souvenir.",
        "sight": {"label": "the hot well", "dx": 2, "dy": -2, "text": "The spring breathes steam. Tin men soaked their bones here."},
    },
    "surin_islands": {
        "host": "Toh Ja", "look": "nok",
        "lines": ["The sea says it twice. Believe the first.",
                  "Count the birds before you count the waves."],
        "hint": "Noi: tied to the tallest stilt pole, above the tide.",
        "found": "A carved fishhook. Toh Ja nods: the sea provides.",
        "sight": {"label": "the stilt hut", "dx": 2, "dy": 0, "text": "A hut over clear water. Home is where the boat floats."},
    },
    "khao_lak": {
        "host": "Nong Fon", "look": "child",
        "lines": ["We light one every year. Hold this with me?",
                  "The boat stays. So do we."],
        "hint": "Noi: by the memorial flowers. Step softly.",
        "found": "A folded paper lantern. Light it in your heart, Noi whispers.",
        "sight": {"label": "the memorial lamp", "dx": -1, "dy": -2, "text": "A lamp that never goes out. Hold still a moment."},
    },
    "similan": {
        "host": "Ranger Khwan", "look": "nok",
        "lines": ["Nine islands. Count them yourself, I won't tell.",
                  "Coral sleeps half the year. Tiptoe."],
        "hint": "Noi: at the foot of the balancing rock. Look up.",
        "found": "A granite pebble, perfectly round. The eighth island approves.",
        "sight": {"label": "the sailing rock", "dx": -3, "dy": -1, "text": "Balanced since before maps. Count to nine below it."},
    },
    "phang_nga": {
        "host": "Dek Chai", "look": "child",
        "lines": ["Keep the ball dry! That is the whole game!",
                  "Stilts, sea, football. Best school ever."],
        "hint": "Noi: under the school floorboard. Lift, don't break.",
        "found": "A wooden whistle. Blow softly — the fish like it.",
        "sight": {"label": "the karsts", "dx": -3, "dy": -2, "text": "Limestone teeth. Painted ships, three thousand years old, hide in their caves."},
    },
    "phuket": {
        "host": "Auntie Sim", "look": "ruen",
        "lines": ["Beacons ridge to ridge. Light when you see strange sails.",
                  "Two sisters saved this island. Eat — no, listen, then I'll tell you."],
        "hint": "Noi: behind the blue shophouse shutter, top hinge.",
        "found": "A Peranakan bead. Auntie Sim: for luck, for courage.",
        "sight": {"label": "the old lamp", "dx": 0, "dy": -3, "text": "Lit the night the beacons burned. It remembers."},
    },
    "promthep": {
        "host": "Lung Det", "look": "nok",
        "lines": ["Sun sits on water, you press shutter. Not before.",
                  "I've watched ten thousand sunsets. This one is yours."],
        "hint": "Noi: at the little cliff shrine, under the garland.",
        "found": "An elephant coin, green with age. For the keeper of the cape.",
        "sight": {"label": "the cape lamp", "dx": -2, "dy": 0, "text": "Every sunset in history passed this lamp."},
    },
    "ko_phi_phi": {
        "host": "Bang Chai", "look": "nok",
        "lines": ["Lamp steady. My father climbs in the dark.",
                  "Nests are a year's work. Tread like a cat."],
        "hint": "Noi: in the scaffold knot, where the rope wears thin.",
        "found": "A swiftlet feather. Lighter than the page, almost.",
        "sight": {"label": "Maya's walls", "dx": -2, "dy": -1, "text": "Closed for years so the reef could breathe. Tread like a cat."},
    },
    "krabi": {
        "host": "Yai Nom", "look": "ruen",
        "lines": ["Ribbon on the bow, or the engine is just metal.",
                  "Twelve hundred steps. Breathe every third."],
        "hint": "Noi: in the Shell Cemetery, the biggest flat slab.",
        "found": "A fossil shell, forty million years old. Older than every secret.",
        "sight": {"label": "the cliffs", "dx": -4, "dy": -1, "text": "Tiger Cave cliffs, ribbons fluttering at their feet."},
    },
    "nakhon": {
        "host": "Khru Mew", "look": "ruen",
        "lines": ["Wrists, not arms. The story lives in the wrists.",
                  "Sat Duean Sip: feed the ancestors first, dance after."],
        "hint": "Noi: in the costume chest, under the gold belt.",
        "found": "A sequin shaped like a star. The stage misses you already.",
        "sight": {"label": "the great stupa", "dx": 0, "dy": -3, "text": "They say it casts no shadow at noon. Check."},
    },
    "phatthalung": {
        "host": "Lung Sorn", "look": "nok",
        "lines": ["Noi! Little brother came home!",
                  "Leather remembers every hand. Carve kindly."],
        "hint": "Noi: on the hide rack, behind the third moon.",
        "found": "A leather offcut with two eyes. A puppet, unborn.",
        "sight": {"label": "the workshop lamp", "dx": -1, "dy": -3, "text": "Leather learns to talk under this light."},
    },
    "trang": {
        "host": "Bang Rit", "look": "nok",
        "lines": ["Angle shallow, cut at night, thank the tree.",
                  "Rubber built this town. Songs built me."],
        "hint": "Noi: inside an old latex cup, third row of trees.",
        "found": "A rubber seed. Plant it anywhere. It will wait.",
        "sight": {"label": "the lighthouse", "dx": -4, "dy": -2, "text": "The seal come to life: a light over trading waves."},
    },
    "ko_kradan": {
        "host": "Nong Nam", "look": "child",
        "lines": ["Float. Fish come to the gentle.",
                  "Dugongs eat here. So no touching, okay?"],
        "hint": "Noi: in the seagrass, where the sand ripples.",
        "found": "Smooth sea glass. The sea tumbling its losses into treasure.",
        "sight": {"label": "the dive boat", "dx": 3, "dy": 0, "text": "Glass-bottomed. The coral does the talking."},
    },
    "satun": {
        "host": "Bang Mat", "look": "nok",
        "lines": ["Tarutao boats that way. Geopark this way. History both ways.",
                  "Logbooks tear. Stories tear too. We piece them."],
        "hint": "Noi: under the pier master's stool, behind the loose board.",
        "found": "A slate pencil stub. Somebody counted days with this.",
        "sight": {"label": "the old stone", "dx": -3, "dy": 0, "text": "Geopark rock, folded before dinosaurs."},
    },
    "ko_lipe": {
        "host": "Nek Yam", "look": "ruen",
        "lines": ["Ribbon tight, wish tighter. Don't look back.",
                  "Tide takes the bad luck. You keep the good."],
        "hint": "Noi: at the pandanus roots, where the boat was built.",
        "found": "A tiny sail cloth. For boats that carry worries away.",
        "sight": {"label": "the spirit boat", "dx": 3, "dy": 0, "text": "Small, ribboned, waiting for sunset and bad luck."},
    },
    "songkhla": {
        "host": "Pa Sri", "look": "ruen",
        "lines": ["Indigo stripe, silk weft. The loom doesn't hurry.",
                  "Sea one side, lake other. Weave both."],
        "hint": "Noi: in the loom shuttle, when the cloth is lifted.",
        "found": "A brass bobbin. It hummed while you worked.",
        "sight": {"label": "the cape light", "dx": 3, "dy": -2, "text": "Sweeping sea and lake both, all night."},
    },
    "pattani": {
        "host": "Bang Su", "look": "nok",
        "lines": ["Bow takes the sea's eye. Paint it well.",
                  "Shoes off, shoulders covered, camera asked. Then welcome."],
        "hint": "Noi: in the oldest paint pot, under the blue lid.",
        "found": "A brush worn to a nub. It painted a hundred watchful eyes.",
        "sight": {"label": "Krue Se", "dx": 0, "dy": 3, "text": "Old as empires, watching the water."},
    },
    "yala": {
        "host": "Che Nah", "look": "ruen",
        "lines": ["Wax first, then colour. Patience is the pattern.",
                  "Three faiths, one market. Try everything."],
        "hint": "Noi: by the dye vat, where the cloth drips.",
        "found": "A wax stamp of a cloud. Stamp it on your map.",
        "sight": {"label": "the cave stone", "dx": 0, "dy": -3, "text": "A reclining Buddha sleeps inside this hill."},
    },
    "narathiwat": {
        "host": "Mak Dik", "look": "ruen",
        "lines": ["You lead, we answer. Loudly!",
                  "Last chorus is yours. Make it count."],
        "hint": "Noi: inside the spare drum, under the skin.",
        "found": "A spare drum lace. Tie your song together.",
        "sight": {"label": "the festival flags", "dx": -2, "dy": 0, "text": "Bright as a sung chorus. Follow them to the stage."},
    },
}

HOST_ACCENT = {"ruen": "YAAI", "nok": "NOK", "child": "CHILD"}


def extra_of(stop_id):
    """Host + hidden spark writing for a stop (empty when unknown)."""
    return EXTRA.get(stop_id, {})


# ------------------------------------------------------------- the tablets
# One coding puzzle per stop: the game is a coding game, so the page is
# won at the rune tablet, not in a minigame. The arc runs from Act 1's
# first print() to Act 3's little functions. Validators live in
# ``tablets.py``; each spec carries its own teaching words.
CODE = {
    # ---------------------------------------------------------- Act 1: first spells
    "chumphon": {
        "title": "SIGNAL HILL", "fx": "burst", "kind": "say", "expect": "hold fast",
        "prefill": 'print("drift")',
        "status": "The signal hill answers only ships that hold fast.",
        "hint": "Change what is printed. The fleet holds fast.",
        "praise": "Hold fast. The harbour reads you.",
    },
    "ko_tao": {
        "title": "TURTLE COUNT", "fx": "swim", "kind": "set", "var": "turtles", "expect": 4,
        "prefill": "turtles = 0",
        "status": "Four green turtles rest by the sunken boat.",
        "hint": "Put the number 4 into turtles with = .",
        "praise": "Four turtles. Counted, and true.",
    },
    "ko_pha_ngan": {
        "title": "ROYAL INITIALS", "fx": "burst", "kind": "say", "expect": "VPB",
        "prefill": 'print("V")',
        "status": "Three kings walked here. Join their initials with join.",
        "hint": "Build one line from a list: \",\".join is for commas — plain join uses \"\".",
        "praise": "Three kings, one stone, one line.",
    },
    "ko_samui": {
        "title": "STONE COUPLE", "fx": "bloom", "kind": "lines",
        "expect": ["grandfather", "grandmother", "stone"],
        "prefill": 'print("stone")',
        "status": "Tell the legend in order: who sailed, who waited, what remains.",
        "hint": "Three prints, in order. Or a loop over a list.",
        "praise": "The rocks remember. So will you.",
    },
    "surat_thani": {
        "title": "PULL TOGETHER", "kind": "gauntlet", "fx": "festival",
        "parts": [
            {"kind": "set", "var": "rope", "expect": 4},
            {"kind": "lines", "expect": ["pull", "pull", "pull", "pull"]},
        ],
        "prefill": 'rope = 0\nprint("pull")',
        "status": "BOSS TABLET. The Chak Phra rope needs its number AND its pulls, in one script.",
        "broken": "last year's pull spell. It shouts once and forgets to count.",
        "hint": "Set rope to 4, then loop range(rope) printing pull.",
        "praise": "Four pulls, one town, one Buddha. The crowd roars.",
    },
    # ------------------------------------------------------- Act 2: choosing
    "ranong": {
        "title": "TIN PAN", "fx": "bloom", "kind": "table", "var": "water",
        "cases": [("muddy", "swirl"), ("clear", "keep")],
        "prefill": 'print("swirl")',
        "status": "Muddy water: swirl. Clear water: keep the tin.",
        "hint": "If the water is clear, keep. Else, swirl.",
        "praise": "Tin in the pan. Kaw Sim Bee nods.",
    },
    "surin_islands": {
        "title": "READ THE SKY", "fx": "swim", "kind": "table", "var": "sea_pulls_back",
        "cases": [(True, "go up"), (False, "sail")],
        "prefill": 'print("sail")',
        "status": "When the sea pulls back, the boats stay in.",
        "hint": "If the sea pulls back, print go up. Else, sail.",
        "praise": "You watched. Now you can go.",
    },
    "khao_lak": {
        "title": "LANTERN LINE", "fx": "rise", "kind": "say", "expect": "we remember",
        "prefill": 'print("we")',
        "status": "One lantern, one line. Finish it gently.",
        "hint": "Finish the line: we remember.",
        "praise": "...thank you for being gentle.",
    },
    "similan": {
        "title": "COUNT NINE", "fx": "burst", "kind": "lines",
        "expect": ["island 1", "island 2", "island 3", "island 4", "island 5",
                   "island 6", "island 7", "island 8", "island 9"],
        "prefill": "for i in range(9):\n    print(i)",
        "status": "Name all nine islands: 'island 1' through 'island 9'.",
        "broken": "a crab's counting spell. It counts from zero and names nothing.",
        "hint": "f-strings name things: print(f\"island {i}\") counts 1 to 9.",
        "praise": "Nine islands, named true.",
    },
    "phang_nga": {
        "title": "KEEP DRY", "fx": "pull", "kind": "table", "var": "ball_dry",
        "cases": [(True, "pass"), (False, "fetch")],
        "prefill": 'print("pass")',
        "status": "Dry ball: pass. Wet ball: fetch it from the sea.",
        "hint": "If the ball is dry, pass. Else, fetch.",
        "praise": "Dry ball, good pass.",
    },
    "phuket": {
        "title": "BEACON ORDERS", "fx": "burst", "kind": "table", "var": "sails",
        "cases": [("none", "wait"), ("ships", "light")],
        "prefill": 'print("wait")',
        "status": "Empty sea: wait. Strange sails: light the beacons.",
        "hint": "If the sails are ships, light. Else, wait.",
        "praise": "Ridge to ridge, the fire runs.",
        "forgery": {
            "title": "TRUE ORDERS", "kind": "lines",
            "expect": ["light", "hold", "stand"],
            "prefill": 'print("light")',
            "status": "The beacon keeper dictates, you write. Three words, in order.",
            "hint": "Light, then hold, then stand — one print per line, or a loop.",
            "praise": "The true orders, in the Sisters' own words.",
            "card": "True Beacon Orders",
            "accuse": [
                ("NOI", "NOI", "Hold on... this ink is still wet. These orders are a COPY!"),
                ("AUNTIE", "YAAI", "...Caught. Those aren't the Sisters' words. Those are mine, and I am no general."),
                ("AUNTIE", "YAAI", "The true orders never left the beacon keeper's mouth. Write them true and I'll sign them myself."),
                ("NOI", "NOI", "The tablet changed! Light, hold, stand — in order."),
            ],
        },
    },
    "promthep": {
        "title": "GOLDEN HOUR", "fx": "burst", "kind": "table", "var": "sun",
        "cases": [("high", "wait"), ("low", "click")],
        "prefill": 'print("wait")',
        "status": "Press the shutter only when the sun sits on the water.",
        "hint": "If the sun is low, click. Else, wait.",
        "praise": "The sunset is yours.",
    },
    "ko_phi_phi": {
        "title": "STEADY LAMP", "fx": "rise", "kind": "lines",
        "expect": ["steady", "steady", "steady"],
        "prefill": 'lamp = 0\nwhile lamp < 3:\n    print("steady")',
        "status": "Hold the lamp steady: three breaths, three lines.",
        "broken": "a lamp spell that never ends. It forgot to count.",
        "hint": "A while loop needs its count to grow, or it burns forever.",
        "praise": "Three breaths. The lamp settles.",
    },
    "krabi": {
        "title": "TWELVE HUNDRED STEPS", "kind": "gauntlet", "fx": "festival",
        "parts": [
            {"kind": "set", "var": "steps", "expect": 9},
            {"kind": "lines",
             "expect": ["step", "step", "breathe"] * 3},
        ],
        "prefill": 'steps = 0\nfor i in range(9):\n    print("step")',
        "status": "BOSS TABLET. Count the climb AND breathe every third step, in one script.",
        "broken": "a tired climber's spell. It counts nothing and never breathes.",
        "hint": "Set steps to 9. Count 1..steps; breathe when the count divides by 3.",
        "praise": "Breathed with the steps. The summit bows, and the town cheers.",
    },
    # ----------------------------------------------------- Act 3: real spells
    "nakhon": {
        "title": "NORA HANDS", "fx": "dance", "kind": "set", "var": "calls",
        "expect": ["LEFT", "DOWN", "RIGHT", "UP"],
        "prefill": "calls = []",
        "status": "Shout every pose to the back row: uppercase them all, at once.",
        "hint": "One comprehension shouts a whole list: [p.upper() for p in ...].",
        "praise": "The back row heard every wrist.",
    },
    "phatthalung": {
        "title": "PUPPET VOICE", "fx": "dance", "kind": "set", "var": "voices",
        "expect": 5,
        "prefill": 'troupe = {"hero": 1, "clown": 3, "demon": 1}\nvoices = 0',
        "status": "Count every voice in the troupe.",
        "hint": "Add up everything the dict holds: sum(troupe.values()).",
        "praise": "Five voices. Noi's little brother wakes.",
    },
    "trang": {
        "title": "RUBBER COUNT", "fx": "rain", "kind": "lines",
        "expect": ["cup %d" % n for n in range(1, 13)],
        "prefill": 'for n in range(12):\n    print("cup")',
        "status": "Number all twelve cups for the dawn tally.",
        "broken": "a tally spell that cannot count past 'cup'.",
        "hint": "Number them: range(1, 13), and f-strings name things.",
        "praise": "Twelve cups, tallied before sunrise.",
    },
    "ko_kradan": {
        "title": "FLOAT", "fx": "swim", "kind": "say", "expect": "float",
        "prefill": 'print("splash")',
        "status": "No splashing. One word, gently.",
        "hint": "Print float, and mean it.",
        "praise": "The sea notices. It approves.",
    },
    "satun": {
        "title": "LOGBOOK", "fx": "burst", "kind": "safe", "name": "mend",
        "calls": [(("supply boat",), "supply boat (mended)"),
                  (("rainy season",), "rainy season (mended)")],
        "traps": [((None,), "unknown (mended)")],
        "prefill": "def mend(page):\n    return page + \" (mended)\"",
        "status": "Torn pages come back mended — even pages of nothing.",
        "broken": "a fair-weather spell. It mends paper but drowns on rot.",
        "hint": "Catch the rot with try/except. Nothing mends to 'unknown (mended)'.",
        "praise": "Fair weather or foul, the story reads itself again.",
    },
    "ko_lipe": {
        "title": "SEND AWAY", "fx": "rise", "kind": "func", "name": "send",
        "calls": [(("storm",), "gone: storm")],
        "prefill": "def send(worry):\n    return worry",
        "status": "Worries go out with the tide, marked gone.",
        "hint": "Return 'gone: ' plus the worry.",
        "praise": "Let it go. The tide takes it.",
    },
    "songkhla": {
        "title": "WEAVE", "fx": "bloom", "kind": "set", "var": "pattern",
        "expect": ["indigo", "silk", "temple"],
        "prefill": 'pattern = "indigo,silk,temple".split(" ")',
        "status": "The thread names arrive in one tangled string. Split them.",
        "broken": "a weaver's spell that cuts in all the wrong places.",
        "hint": "Split on what separates them: commas, not spaces.",
        "praise": "Three threads, cleanly cut.",
    },
    "pattani": {
        "title": "WELCOME", "fx": "burst", "kind": "table", "var": "shoes_off",
        "cases": [(True, "welcome"), (False, "wait")],
        "prefill": 'print("welcome")',
        "status": "Shoes off, shoulders covered — then welcome.",
        "hint": "If the shoes are off, welcome. Else, wait.",
        "praise": "Come in, and listen well.",
    },
    "yala": {
        "title": "BATIK STAMP", "fx": "bloom", "kind": "class", "name": "Stamp",
        "make": [],
        "checks": [("attr", "color", "blue"),
                   ("call", "press", ("cloth",), "cloth batik")],
        "prefill": 'class Stamp:\n    color = "red"\n    def press(self, cloth):\n        return cloth',
        "status": "Carve the stamp: blue wax, and a press that batiks cloth.",
        "broken": "a stamp carved backwards. Wrong wax, and it presses nothing.",
        "hint": "Blue the wax. Then press should return the cloth plus ' batik'.",
        "praise": "Stamped true. The wax is the memory.",
    },
    "narathiwat": {
        "title": "CHORUS", "fx": "festival", "kind": "gauntlet", "fx": "festival",
        "parts": [
            {"kind": "func", "name": "chorus",
             "calls": [(("sail",), "sail!"), (("home",), "home!")]},
            {"kind": "say", "expect": "home!"},
        ],
        "prefill": 'def chorus(call):\n    return call\nprint("home")',
        "status": "BOSS TABLET. Teach the chorus AND sing the last line home, in one script.",
        "broken": "a shy singer's spell. It answers flat and never finishes.",
        "hint": "Chorus adds '!' to the call. Then print(chorus(\"home\")).",
        "praise": "The last chorus is yours. You led it, and the South answers.",
    },
}


def code_of(stop_id):
    """The coding puzzle for a stop (None when unknown)."""
    return CODE.get(stop_id)


# ------------------------------------------------- ten iconic things
# Ten iconic things per province, mined from Wikipedia's province
# articles (parks, landmarks, festivals, crafts, history). The journal's
# SIGHTS tab shows the ones you have walked to.
ICONS = {
    "chumphon": [
        "Shrine of Prince Abhakara, Father of the Royal Thai Navy",
        "Hat Thung Wua Laen, voted the country's cleanest beach",
        "Hat Sai Ri's white sand and clear water",
        "Khao Sam Kaeo digs: 2,000-year-old pottery and beads",
        "The Kra Isthmus, narrow land bridge of the peninsula",
        "Mu Ko Chumphon National Park's island chain",
        "Ko Ngam's twin bays, big and little",
        "Khao Chao Mueang viewpoint over two seas",
        "Pathio's mangrove channels",
        "Lang Suan's traditional long-boat races",
    ],
    "ranong": [
        "Raksawarin Hot Springs, the town's famous soak",
        "Ratana Rangsan Palace, the tin governor's gift to kings",
        "Niveshkiri Hill and the city pillar view",
        "Namtok Ngao National Park's forest waterfalls",
        "Laem Son's casuarina beaches and mangroves",
        "Phu Khao Ya, the bald grass mountain",
        "The Kra Buri River border with Myanmar",
        "Victoria Point across the water in Kawthaung",
        "Mangrove channels you sail standing up",
        "Tin-mining heritage: pans, picks and company rows",
    ],
    "surat_thani": [
        "Khao Sok, rainforest older than the Amazon",
        "Cheow Lan Lake under limestone teeth",
        "The giant Rafflesia bloom of Khao Sok",
        "The Tapi and Phum Duang meeting at Tha Kham",
        "Wat Phra Boromathat Chaiya, Srivijaya chedi",
        "The city pillar shrine in the old hall grounds",
        "Mu Ko Ang Thong's forty-two islands",
        "Khlong Sok's raft houses on green water",
        "Bandon Bay's oyster rafts and fishing stakes",
        "Don Sak pier, gateway to the Gulf islands",
    ],
    "phang_nga": [
        "Ko Ta Pu, the needle from The Man with the Golden Gun",
        "Ao Phang Nga National Park's drowned karsts",
        "Nakha cave's 3,000-year-old painted ships",
        "Takua Pa old town, tin port of two centuries",
        "Thai Mueang beach and its sea-turtle festival",
        "Lampi's six tiers falling all year",
        "Ton Chong Fa in Khao Lak-Lam Ru",
        "Laem Pakarang's pine groves for camping",
        "Si Phang Nga's untouched interior forest",
        "Sarasin Bridge joining the road to Phuket",
    ],
    "phuket": [
        "The Two Sisters who dressed women as soldiers, 1785",
        "The Big Buddha in Burmese marble over Chalong Bay",
        "Wat Chalong, the island's most-visited temple",
        "Thalang Museum of the 200-year war",
        "The Vegetarian Festival's fire-walking and blade ladders",
        "The Chao Le boat-floating festival at Rawai",
        "December's King's Cup Regatta at Kata",
        "Old Town's Sino-Portuguese rows and the On On Hotel",
        "Promthep, Brahma's Cape at the island's tip",
        "Sirinat's turtle-nesting beaches in the northwest",
    ],
    "krabi": [
        "Railay and Ton Sai, the world's climbing walls",
        "Maya Bay's silver screen fame",
        "Lang Rong Rien cave: 40,000 years of people",
        "Khao Phanom Bencha, highest in the province",
        "Four national parks, sea and stone",
        "The crossed swords on the provincial seal",
        "Shell Cemetery's forty-million-year fossils",
        "Mae Ya Nang, spirit of every bow",
        "Ko Lanta's long beaches to the south",
        "Krabi town's riverfront and morning market",
    ],
    "nakhon": [
        "Wat Phra Mahathat's shadowless chedi",
        "Tambralinga, the old kingdom of the ligor",
        "Sat Duean Sip and its trays for the dead",
        "Nora dance-drama's wrists and wings",
        "Khanom's pink dolphins",
        "Khao Luang, roof of the South",
        "Sichon's quiet surf coast",
        "The old city wall and its northern gate",
        "Shadow-play heritage in village halls",
        "The tenth-month long drums",
    ],
    "phatthalung": [
        "Nang Talung shadow puppetry, jokes and news",
        "Phu Khao Ok Thalu on the provincial seal",
        "Songkhla Lake's Lam-pam waters",
        "Khao Pu–Khao Ya on the Trang border",
        "The Banthat mountain wall",
        "Ok Phansa candle parades and lake sports",
        "Pla lam-pam, the tinfoil barb",
        "Thale Noi's lotus and a thousand herons",
        "Krajood reed weaving",
        "Cave temples with rows of old Buddhas",
    ],
    "trang": [
        "The underwater wedding off Ko Kradan",
        "The Peranakan vegetarian festival",
        "The lighthouse on the provincial seal",
        "Four piers for the islands: Pak Meng and friends",
        "Ramsar wetlands at the river mouth",
        "The dugongs grazing off Ko Libong",
        "Kaw Sim Bee's first rubber trees",
        "Kantang's old railway terminus",
        "Morakot Cave's emerald room on Ko Muk",
        "Ko Libong's bird marshes at dawn",
    ],
    "satun": [
        "Tarutao, the prison island turned paradise",
        "Mu Ko Phetra's thirty Strait islands",
        "Thale Ban's freshwater swamp on the border",
        "Satun Geopark's fossils and caves",
        "Pak Bara pier for every island boat",
        "Ko Lipe's walking street of sand",
        "Ko Adang's viewpoint ridge",
        "Ko Bulon's cashew and clear bays",
        "Ku-Den Mansion, the Chinese merchant's house",
        "Tanyong Po's long low-tide beach",
    ],
    "songkhla": [
        "Songkhla Lake, the largest natural lake in the land",
        "Tinsulanond Bridge, longest concrete bridge around",
        "Sathing Phra's buried 10th-century cities",
        "The National Museum in the Chinese mansion",
        "Cape Samila and her bronze mermaid",
        "Hat Yai's hilltop park and cable car",
        "Ton Nga Chang's seven falling tiers",
        "Ko Yo weaving in indigo and silk",
        "The old town walls by the sea",
        "The hilltop zoo looking over the lake",
    ],
    "pattani": [
        "Krue Se, the famous old mosque by the water",
        "Lim Ko Niao shrine and its fire-walking",
        "Wat Chang Hai, 300 years and Luang Pu Thuat",
        "Yaring's hand-painted kolek boats",
        "Patani Malay, the local Yawi tongue",
        "The Sankalakhiri mountain wall",
        "Budo-Su-ngai Padi's deep forest",
        "The mouse-deer that named the town",
        "The Central Mosque on Friday noon",
        "Pattani Bay's cockle beds at low tide",
    ],
    "yala": [
        "Wat Khuha Phimuk's cave reclining Buddha",
        "Betong's hot springs in the hills",
        "Piyamit's jungle tunnels",
        "The winter flower garden above the mist",
        "Iyerweng's sea of morning mist",
        "Bang Lang's long reservoir",
        "Hand-drawn batik in every market",
        "Hornbills over the Bala forest",
        "Betong's car tunnel through the hill",
        "Yala's old town circle and pillar shrine",
    ],
    "narathiwat": [
        "Taksin Ratchaniwet, the palace by the sea",
        "Ao Manao and Khao Tanyong's bay",
        "Narathat Beach at the river mouth",
        "Pacho Waterfall in Budo-Su-ngai Padi",
        "The Central Mosque on Pitchitbamrung Road",
        "Dikir Hulu sung choruses",
        "Silat that moves like dance",
        "Su-ngai Kolok's border market",
        "Tak Bai's quiet fishing beach",
        "The Bang Nara river road at dusk",
    ],
}


def icons_of(stop_id):
    """Ten iconic things for a province stop (empty elsewhere)."""
    return ICONS.get(stop_id, [])


# ------------------------------------------------------------------- fishing
# What bites depends on the water: Gulf east, Andaman west, deep south.
# The last two only come out at night.
FISH = {
    "gulf": ["mackerel", "squid", "crab", "sea bass"],
    "andaman": ["grouper", "snapper", "squid", "parrotfish"],
    "south": ["catfish", "prawn", "moonfish", "lanternfish"],
}
NIGHT_FISH = {"lanternfish", "squid"}


# ----------------------------------------------------- learning to code
# Shown the first time you touch a rune tablet, and again under F1.
# Plain language, no jargon: the player has never written code before.
PY_PRIMER = (
    "print(x)       show something",
    "x = 5          store a value",
    "x == 5         is it equal?",
    "if cond:       do this when true",
    "    print(x)   (indent 4 spaces)",
    "for i in range(3):   repeat 3x",
    "    print(i)   the repeated line",
    "while x > 0:   repeat while true",
    "    x = x - 1  so it can stop",
    "",
    "CAST with CTRL+ENTER, or RUN >",
    "F1 shows this page in any tablet.",
)

CODE_TUTORIAL = [
    ("NOI", "NOI", "Wait. Before the tablet — a word. You have never cast a spell before. Neither had I, once."),
    ("NOI", "NOI", "A spell here is Python, a real language. Three shapes solve nearly everything you will meet."),
    ("NOI", "NOI", "ONE: print(...) shows something. print(\"hello\") shows the word hello."),
    ("NOI", "NOI", "TWO: name = value stores something. turtles = 4 remembers the number four under the name turtles."),
    ("NOI", "NOI", "THREE: for repeats, if chooses. Put the repeated lines below, indented by four spaces."),
    ("NOI", "NOI", "The task is written at the bottom of the tablet. Rewrite the spell until the world changes. A wrong spell never hurts you — you simply try again."),
    ("NOI", "NOI", "Press F1 inside any tablet for this page again. CTRL+ENTER, or the RUN button, casts it. Go on. I am watching."),
]


# --------------------------------------------------------------------- pins
# Every ``pos`` above is authored in the 240x320 GADM mask frame — the
# same frame the coastline was rasterized in, so a pin can be checked
# against the real map by eye. The playable world is finer
# (world_map.MAP_SCALE). Scaling here keeps one source of truth.
from . import world_map as _WM       # noqa: E402  (constants only, no cycle)


def _grow(pos):
    return (pos[0] * _WM.MAP_SCALE, pos[1] * _WM.MAP_SCALE)


PROLOGUE["pos"] = _grow(PROLOGUE["pos"])
for _stop in STOPS:
    _stop["pos"] = _grow(_stop["pos"])
del _grow, _stop


def _add_landmark_errands():
    """Every host sends you to the landmark in their district.

    The code buys the page; the walk to the landmark is the errand
    that comes after it — the reason to keep moving once the tablet
    is done.
    """
    from . import landmarks as LM
    for _region, marks in LM.LANDMARKS.items():
        for mark in marks:
            extra = EXTRA.get(mark["stop"])
            if extra is None:
                continue
            extra["errand"] = (
                "One more thing before you go. There is a place in this "
                "district you should stand at: %s. Out past the last house, "
                "where the road turns. Go and stand there, and listen."
                % mark["name"])


_add_landmark_errands()


def _apply_deepening():
    """Fold the deeper beats into the stops and scenes.

    Added, never replaced: every line written before is still there,
    and the new beats continue it.
    """
    from . import deepening as D
    for sid, extra in D.DEEPENING.items():
        stop = STOP_BY_ID.get(sid)
        if stop is not None and extra.get("lines"):
            stop["lines"] = list(stop["lines"]) + list(extra["lines"])
        scene = SCENES.setdefault(sid, {})
        for beat in ("arrive", "mid", "spark"):
            if extra.get(beat):
                scene[beat] = list(scene.get(beat, [])) + list(extra[beat])


_apply_deepening()


# ------------------------------------------------- the hosts open up
# Once the page is yours, the hosts tell you the things they could not
# tell a stranger. Written as a batch and folded in here.
from . import _content_later as _CL  # noqa: E402
from . import _content_quests as _CQ2  # noqa: E402

for _sid, _lines in _CL.LATER.items():
    _extra = EXTRA.get(_sid)
    if _extra is None:
        continue
    _extra.setdefault("later", [])
    for _line in _lines:
        if _line not in _extra["later"]:
            _extra["later"].append(_line)

LORE.update(_CQ2.LORE)


# The lore documents found in the field, and the towns they are found in.
_LORE_HOME = {
    "The Flood Song of the Boat People": "surin_islands",
    "A Tin Merchant's Letter": "ranong",
    "The Naming of the Light": "khao_lak",
    "The Boat-Builder's Rule of Thumb": "surat_thani",
    "The Binder's Apprentice, As First Told": "phatthalung",
    "The Tide Ledger": "songkhla",
    "The Schoolmistress's Roll Book": "phang_nga",
    "The Salt-Farm Lease": "satun",
    "The Railway Survey, 1909": "trang",
    "The Monk's Chronicle": "nakhon",
    "The Bird-Trapper's Diary": "ko_pha_ngan",
    "The Rubber Planter's Account": "ko_kradan",
}

for _doc, _stop in _LORE_HOME.items():
    _sp = STOP_BY_ID.get(_stop)
    if _sp is not None and _doc not in _sp["cards"]:
        _sp["cards"].append(_doc)
