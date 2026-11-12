"""Regions of the South — light, colour, weather and mood per area.

Every stop belongs to a region. The region decides how the world looks:
the ambient tint multiplied over the frame, the colour of lamps and
beacons, the haze in the air, and the weather that hangs over it.

This is what makes the peninsula feel like eight different places
instead of one long green field — and it costs one lookup per frame.
"""

# ambient   : multiplied over the whole frame (the colour of the light)
# light     : the colour lamps, fires and beacons cast
# fog       : (colour, alpha) haze layered over the frame
# grade     : (saturation, temperature) final colour grade, -1 = unused
# weather   : "clear" | "rain" | "mist" | "haze" | "squall"
REGIONS = {
    "gulf_shore": {
        "name": "The Gulf Shore",
        "biome": "fishing village, beach",
        "stops": ["chumphon", "ko_tao"],
        "ambient": (255, 236, 206),
        "light": (255, 206, 138),
        "fog": ((250, 214, 170), 16),
        "grade": (1.04, 0.10),
        "weather": "clear",
    },
    "samui_sea": {
        "name": "The Samui Sea",
        "biome": "islands, festival town",
        "stops": ["ko_pha_ngan", "ko_samui", "surat_thani"],
        "ambient": (255, 240, 224),
        "light": (255, 214, 156),
        "fog": ((255, 226, 190), 12),
        "grade": (1.10, 0.14),
        "weather": "clear",
    },
    "mangrove": {
        "name": "The Mangrove Isthmus",
        "biome": "tidal swamp, stilt paths",
        "stops": ["ranong", "surin_islands"],
        "ambient": (206, 226, 198),
        "light": (222, 240, 168),
        "fog": ((150, 186, 140), 34),
        "grade": (0.92, -0.08),
        "weather": "mist",
    },
    "karst": {
        "name": "The Karst Sea",
        "biome": "limestone islands, sea caves",
        "stops": ["khao_lak", "similan", "phang_nga"],
        "ambient": (212, 234, 246),
        "light": (186, 224, 255),
        "fog": ((176, 214, 240), 22),
        "grade": (0.96, -0.12),
        "weather": "clear",
    },
    "pearl_coast": {
        "name": "The Pearl Coast",
        "biome": "old town, market, beacon cliffs",
        "stops": ["phuket", "promthep", "ko_phi_phi"],
        "ambient": (252, 230, 236),
        "light": (255, 198, 168),
        "fog": ((246, 200, 214), 14),
        "grade": (1.06, 0.12),
        "weather": "clear",
    },
    "green_deep": {
        "name": "The Green Deep",
        "biome": "rainforest, river, falls",
        "stops": ["krabi"],
        "ambient": (184, 222, 186),
        "light": (186, 240, 150),
        "fog": ((126, 176, 130), 40),
        "grade": (0.94, -0.10),
        "weather": "rain",
    },
    "sweet_islands": {
        "name": "Rubber Country & the Sweet Islands",
        "biome": "plantations, clear water",
        "stops": ["trang", "ko_kradan", "satun", "ko_lipe"],
        "ambient": (216, 238, 232),
        "light": (232, 244, 190),
        "fog": ((198, 226, 216), 18),
        "grade": (1.02, 0.04),
        "weather": "haze",
    },
    "deep_south": {
        "name": "The Lake Kingdoms & the Last Mountains",
        "biome": "lake, mist highlands, ruins",
        "stops": ["nakhon", "phatthalung", "songkhla", "pattani",
                  "yala", "narathiwat"],
        "ambient": (206, 206, 236),
        "light": (206, 214, 255),
        "fog": ((168, 176, 226), 38),
        "grade": (0.90, -0.06),
        "weather": "mist",
    },
}

# the village you start in belongs to the Gulf Shore
REGIONS["gulf_shore"]["stops"].insert(0, "prologue")

DEFAULT_REGION = "gulf_shore"


def region_of_stop(stop_id):
    """The region a stop sits in."""
    for rid, reg in REGIONS.items():
        if stop_id in reg["stops"]:
            return rid
    return DEFAULT_REGION


def region_name(rid):
    reg = REGIONS.get(rid)
    return reg["name"] if reg else ""


def region_for_position(x, y, stops, tile=16):
    """Nearest region to a world position (by its stops' positions)."""
    best = None
    best_d = 1e18
    for stop in stops:
        cx, cy = stop["pos"]
        d = (cx * tile - x) ** 2 + (cy * tile - y) ** 2
        if d < best_d:
            best_d, best = d, stop["id"]
    if best is None:
        return DEFAULT_REGION
    return region_of_stop(best)
