"""Road encounters — what happens between one town and the next.

Walking is most of the game, so the walking has to have something in
it: a bird, a stranger, a change in the weather, a piece of the country
you would otherwise miss. These fire every so often while you are on
the move, and most of them are small.

``where`` restricts an encounter to a region (or "any").
"""

ENCOUNTERS = [
    # ---------------------------------------------------------- any region
    {
        "where": "any",
        "speaker": "NOI",
        "text": "A magpie flies across the road, low, and does not look back. "
                "Not once.",
    },
    {
        "where": "any",
        "speaker": "NOI",
        "text": "You have been walking for an hour without a single sound "
                "except your own feet. That is not quiet. That is "
                "somebody listening.",
    },
    {
        "where": "any",
        "speaker": "NARRATOR",
        "text": "A woman passes you on the path with a basket on her head "
                "and does not slow down, but she says something as she "
                "goes, and it sounds like your name.",
    },
    {
        "where": "any",
        "speaker": "NOI",
        "text": "Three shells on the path, in a row, each one the size of "
                "a coin. Somebody was here. Somebody was counting.",
    },
    {
        "where": "any",
        "speaker": "NOI",
        "text": "The wind turns. For about a minute it comes from the "
                "north, which is wrong, and then it goes back to being "
                "ordinary.",
    },
    {
        "where": "any",
        "speaker": "NARRATOR",
        "text": "A black feather, dry, lying in the dust by the side of "
                "the road. It has been stepped on twice and it is still "
                "whole.",
    },
    {
        "where": "any",
        "speaker": "NOI",
        "text": "You pass a shrine with no lamp in it and no name on it, "
                "and the cup in front of it is clean.",
    },
    {
        "where": "any",
        "speaker": "NARRATOR",
        "text": "Somebody has swept the road. The whole stretch of it, "
                "the dust banked neatly at the edges. Nobody has swept "
                "a road in this country in your lifetime.",
    },
    {
        "where": "any",
        "speaker": "NARRATOR",
        "text": "A shrine at the roadside, wrapped in a bright cloth, with a "
                "coke bottle full of flowers. Somebody stops here every day.",
    },
    {
        "where": "any",
        "speaker": "NOI",
        "text": "Somebody has tied strips of cloth to the branches. Red for "
                "safety, blue for the sea, yellow for the Buddha. Nobody "
                "remembers who taught them which is which.",
    },
    {
        "where": "any",
        "speaker": "NARRATOR",
        "text": "A boy is selling ice cream from a box on a bicycle, and the "
                "ice is already running down the sides of it.",
    },
    {
        "where": "any",
        "speaker": "NOI",
        "text": "The path here is worn in a curve. Every path in this "
                "country is worn in a curve, and every curve is somebody "
                "going the same way for years.",
    },
    {
        "where": "any",
        "speaker": "NARRATOR",
        "text": "A dog watches you from a step, with the perfect "
                "indifference of an animal that has never once been "
                "surprised by anybody.",
    },
    {
        "where": "any",
        "speaker": "NOI",
        "text": "There is a footprint in the mud going the other way, and "
                "it is not yours, and it is not going back.",
    },
    {
        "where": "any",
        "speaker": "NARRATOR",
        "text": "Somebody is burning leaves at the edge of the road, and "
                "the smoke goes straight up, which means the air is very "
                "still, which means the weather has not decided yet.",
    },
    {
        "where": "any",
        "speaker": "NOI",
        "text": "A kilometre marker, repainted so often the numbers have "
                "gone soft. It says how far from somewhere. It does not "
                "say where.",
    },
    {
        "where": "any",
        "speaker": "NARRATOR",
        "text": "A longtail boat goes by with a whole family in it, and a "
                "grandmother on the prow who raises one hand without "
                "looking at you.",
    },
    {
        "where": "any",
        "speaker": "NOI",
        "text": "The light has gone gold. Everything out here looks better "
                "when it is going gold, and I resent that.",
    },
    # ------------------------------------------------------- the Gulf Shore
    {
        "where": "gulf_shore",
        "speaker": "FISHER",
        "text": "A fisherman hauls a net and finds a page in it, holds it "
                "up, and shakes the water out of it. \"This yours?\" "
                "\"Good. It was in the net with the squid.\"",
    },
    {
        "where": "gulf_shore",
        "speaker": "NOI",
        "text": "The tide is out further than you have ever seen it. The "
                "boats are sitting on their keels in the mud like "
                "something that has been put away for the winter.",
    },
    # ------------------------------------------------------- the Samui Sea
    {
        "where": "samui_sea",
        "speaker": "SINGER",
        "text": "A woman on a porch is singing the same four notes over "
                "and over, and when she sees you she stops, and starts "
                "again a note lower.",
    },
    {
        "where": "samui_sea",
        "speaker": "NARRATOR",
        "text": "Salt-white ground, and the heat coming up off it in "
                "shimmer. Somewhere under the salt there is a town that "
                "was never moved.",
    },
    # -------------------------------------------------- the Mangrove Isthmus
    {
        "where": "mangrove",
        "speaker": "ELDER",
        "text": "A boat goes past with nobody waving, and the only sign "
                "there is a person aboard is that the lamp is lit.",
    },
    {
        "where": "mangrove",
        "speaker": "NOI",
        "text": "The mud here makes a sound like something drinking. "
                "Watch your footing. The ground is not finished deciding "
                "where it is.",
    },
    # ---------------------------------------------------------- the Karst Sea
    {
        "where": "karst",
        "speaker": "VOLUNTEER",
        "text": "A boy on the path is counting the limestone towers as he "
                "goes. He gets to nine, stops, counts again, and starts "
                "over from one.",
    },
    {
        "where": "karst",
        "speaker": "NOI",
        "text": "The rock here is full of holes and every one of them is "
                "a bird's house. The cliff is a town of birds, and they "
                "have been here longer than the sea.",
    },
    # ------------------------------------------------------- the Pearl Coast
    {
        "where": "pearl_coast",
        "speaker": "DANCER",
        "text": "Somebody is practising on a drum behind a wall. Badly, "
                "and then very well, and then badly again.",
    },
    {
        "where": "pearl_coast",
        "speaker": "NARRATOR",
        "text": "The road is walled on both sides with shuttered houses, "
                "and from every courtyard comes the sound of a business "
                "that nobody admits to running.",
    },
    # -------------------------------------------------------- the Green Deep
    {
        "where": "green_deep",
        "speaker": "GUIDE",
        "text": "A guide stops you at the treeline and makes you wait for "
                "the rain to pass through in one piece. \"It always "
                "comes in one piece. Like a story.\"",
    },
    {
        "where": "green_deep",
        "speaker": "NOI",
        "text": "The waterfall is louder than it was this morning, which "
                "means more water, which means it rained on the mountain "
                "while you were down here talking.",
    },
    # ------------------------------------------- Rubber Country, the isles
    {
        "where": "sweet_islands",
        "speaker": "TAPPER",
        "text": "A man is tapping a tree with a knife and singing. He "
                "stops the singing to count the cups and starts it "
                "again exactly where he was.",
    },
    {
        "where": "sweet_islands",
        "speaker": "NARRATOR",
        "text": "The haze is so thick that a house appears out of it a "
                "hundred metres before you can see it, like something "
                "being remembered rather than seen.",
    },
    # ------------------------------------------------------ the Lake Kingdoms
    {
        "where": "deep_south",
        "speaker": "PUPPETEER",
        "text": "From a house, a voice reciting. Then a second voice, "
                "and a third, and a whole cast of them arguing about "
                "something that happened four hundred years ago.",
    },
    {
        "where": "deep_south",
        "speaker": "PAINTER",
        "text": "A woman is painting a cloth with a brush in one hand "
                "and a hot wax pot in the other, and she does not look up "
                "when you pass, and she has not looked up once in years.",
    },
]


# ---------------------------------------------------------------- more moments
from . import _content_encounters as _CE  # noqa: E402

ENCOUNTERS.extend(_CE.ENCOUNTERS)
