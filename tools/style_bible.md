# The style bible — for generating art that belongs to this game

Everything here is free to use: any image generator, any source, your
own drawing. The pipeline (`tools/ai_unify.py`) fixes whatever comes
out, but starting from art that already agrees makes the job far easier.

---

## 1. The one-line style

> **Southern Thai pixel art, 3/4 top-down game asset, single object,
> centred, light from the upper left, flat plain background, muted
> jungle-and-sun colours, no text, no ground shadow.**

Append that to **every** prompt. Consistency comes from the shared tail,
not from the model's mood.

## 2. The rules that matter

| Rule | Why |
|---|---|
| 3/4 top-down view, camera slightly above and behind | The game is top-down. A front-on object will not sit in the world |
| Light from the **upper left**, always | Every sprite is rim-lit from the upper left in-game; art lit from the right will fight it |
| **No ground shadow** in the image | The engine draws its own contact shadow; a baked one doubles up |
| **Plain, flat background** (white or a single flat colour) | Anything else gets pasted into the world |
| **One object per image** (or a grid of objects, evenly spaced) | Slices cleanly and stays consistent within the sheet |
| Muted, warm, slightly desaturated | The game is lit by a colour grade per region; saturated art fights it |
| Silhouette first | It has to read at 48 px tall |

## 3. What to generate

### Landmarks (40 — one sheet of 8 per region is ideal)

Name them exactly, or the drop-in module will not find them:

```
thung_khao_hom   longtail_wreck      turtle_shadow      pilgrims_rock
the_four_winds   grandparents_rock   chak_phra_ground   the_mermaid_silt
five_rocks       the_salt_court     the_moving_tree    moken_camp
the_drowned_stupa the_boat_people_road the_standing_dead  the_wall
the_floating_school the_nine_stones  the_bats          the_low_tide_window
the_bell_tower   the_promthep_lovers the_phi_phi_crowds the_shrimp_paste_shed
the_lighthouse_steps the_waterfall_road the_cheow_lan_shore the_crocodile_pool
the_cave_mouth   the_rafia_field    the_smoke_rows    the_tin_scratch
the_night_market the_kradan_lighthouse the_letting_go_shore the_lake_mirror
the_nora_stage   the_khao_luang_mist the_painted_bow   the_wax_shed
```

Each one is a **place marker**, not a person: a cairn, a wreck, a rock
couple, a floating platform, a stupa, a bell tower, a stone, a shed.

### Region backgrounds (8)

`bg_gulf_shore` `bg_samui_sea` `bg_mangrove` `bg_karst`
`bg_pearl_coast` `bg_green_deep` `bg_sweet_islands` `bg_deep_south`

Wide, empty at the centre (the character stands there), no horizon
detail in the middle third.

### Texture and pattern (for shrine banners, cards, UI)

`pattern_batik` `pattern_songket` `pattern_nora` `pattern_khaek_feather`
`paper_old` `parchment_letter`

## 4. How to use it

1. Generate into `assets_ai/in/`.
   - A grid of N props: name it `name_xN.png` (e.g. `landmark_gulf_x8.png`)
     — the pipeline slices it into eight files.
   - A single object: `name.png`.
2. Run the pipeline:
   ```sh
   .venv/bin/python tools/ai_unify.py
   ```
3. It writes `assets_ai/out/*.png` and `game/art_ai.py`.
4. Look at the result in the gallery:
   ```sh
   .venv/bin/python tools/gallery.py
   ```

## 5. What the pipeline does to your art

| Pass | What it fixes |
|---|---|
| Slice | One sheet → many assets, so a sheet is internally consistent |
| Trim + centre | Consistent framing and base anchor |
| Pixel-size | Detail density matches the code-drawn sprites |
| **Palette lock** | Every pixel snapped to one 32-colour master palette, dithered — *this is what stops it looking stitched together* |
| Rim light | The same sun-side highlight the code art gets |
| Master palette | Shared with `game/palette.py`, so AI art and code art live in one colour world |

## 6. Licence notes

Use **CC0 / public domain** material only (museum scans from The Met
Open Access, the British Museum, Rijksmuseum, Wikimedia Commons) if you
ever want to sell the game. Generated images have no licence attached —
keep the prompts with the assets so you can prove they are yours.
