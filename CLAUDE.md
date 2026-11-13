# CLAUDE.md

This repo is a template for building a first Archipelago (AP) world. It's a full copy of the
Archipelago source (version 0.6.8). The user's game lives in **one folder:
`worlds/MyGameImplementation`**. Everything else is Archipelago core.

The person using this is likely new to Archipelago and possibly to Python. Explain what you
change in plain terms, keep changes small, and test after each one.

## The task

Help the user turn `worlds/MyGameImplementation` into a working apworld for their chosen game:
a world that generates seeds without errors and passes the fuzzer.

The apworld is **only one part of the puzzle**. It runs at generation time and decides where
items go. To be playable the game also needs a **client** that, while playing, connects to the
server, sends checked locations (`LocationChecks`), applies received items (`ReceivedItems`) and
reports the goal (`StatusUpdate`). There are two ways to build it:

- **Inside the apworld**: ships in the same `.apworld` and opens from the Launcher. Use
  `BizHawkClient` (`worlds/_bizhawk`) for emulator games, or extend `CommonClient`
  (`CommonClient.py`) and register a Launcher `Component` in the world's `__init__.py`.
- **A separate client**: any program or game mod, in any language, that connects directly to
  the server's WebSocket and speaks the JSON protocol in `docs/network protocol.md`.

Either way, the client and apworld must agree on the game name, item/location IDs and slot data.
Mention the client when the user asks whether their world is "done". Only build it if asked.

## Core concepts

- **Item**: something the player receives (Final Fantasy: Mystic Key, Lute, Potion).
  Classified as `progression` (logic needs it), `useful`, `filler` or `trap`.
- **Location**: a check the player collects (Final Fantasy: a chest in Coneria Castle). Each
  location holds exactly one item. **Item pool size must equal the number of non-event locations.**
- **Region**: an area of the game that holds locations. Regions connect through entrances, and
  every world starts in the region `"Menu"`.
- **Rule**: a function `lambda state: ...` returning True when a location or entrance can be
  reached (Final Fantasy: locked doors need the Mystic Key). Use `state.has(name, player)`,
  `state.has_all(...)`, `state.has_any(...)`, `state.can_reach_location(...)`.
- **Victory condition**: `multiworld.completion_condition[player]`, what beating the game means.
- **Options**: settings in the player's YAML. `Toggle` (on/off), `Range` (number),
  `Choice` (pick one). Registered in the options dataclass.
- **Slot data**: `fill_slot_data()` returns what the game client needs to know (usually options).

## The example design: keys, a level select and a final door

The README has a worked example, **The Five Kingdoms** ("A good first design"). If the user
wants to use that model, asks how to structure their world, or asks questions about the
example, offer this way of working and adapt it to their game:

- **Custom key items** (progression), one per level. They don't exist in the original game;
  the client keeps a level locked in the game's **own level select** until its key is received.
- The **first level is open from the start**, with a couple of checks, so the player can begin.
- A **collection** of custom items (e.g. 3 `Crown Shard`, using a `count` field in the item
  table) opens the **final door**. The number needed is a `Range` option sent in slot data.
- **Regions**: `Menu` → `Level Select` → one region per level, connected by entrances named
  `Enter <level>`. Rules go on the **entrances**, so every location in a level inherits its key.
- **Locations**: a few per level (e.g. hidden chest, boss). The goal is an **event** location
  (code `None`, excluded from `location_name_to_id`) holding a locked `Victory` event item;
  `completion_condition` is `state.has("Victory", player)`.
- **Item pool** = keys + collection items, padded with filler up to the number of real
  (non-event) locations.
- In rule lambdas built in a loop, bind loop variables (`lambda state, key=key: ...`).
- **Client duties**: lock the level select by key/shard count, replace the game's own rewards
  with location checks (send the location ID), apply received items, report victory.

Build it up in small steps and run the tests, `Generate.py` and the fuzzer after each one. If
the game has no level select, the same pattern works with doors, warps or map areas.

## Files in the world folder

| File                   | Purpose                                                         |
|------------------------|-----------------------------------------------------------------|
| `__init__.py`          | The `World` class: regions, item pool, rules, slot data         |
| `Items.py`             | `item_table`: name → ID and classification                      |
| `Locations.py`         | `location_table`: name → ID and region                          |
| `Options.py`           | Option classes and the options dataclass                        |
| `Rules.py`             | Access rules for locations/entrances                            |
| `VictoryConditions.py` | The completion condition                                        |
| `archipelago.json`     | Manifest: game name, versions, authors                          |
| `docs/`                | `en_<game>.md` (game info page) and `setup_en.md`               |
| `test/`                | Unit tests built on `WorldTestBase`                             |

World generation calls these `World` methods in order: `generate_early` → `create_regions` →
`create_items` → `set_rules` → `generate_basic` → `fill_slot_data`.

## Renaming (do this first)

Every class name is prefixed `MyGameImplementation` (`MyGameImplementationWorld`,
`MyGameImplementationItem`, `MyGameImplementationLocation`, `MyGameImplementationOptions`,
`MyGameImplementationTestBase`, etc.). When the user picks their game, rename:

- the folder (lowercase, no spaces, it's a Python module),
- every class name prefix,
- the `game` string in `__init__.py`, `Items.py`, `Locations.py`, `test/__init__.py` and
  `archipelago.json`. These must be **identical** and not clash with an existing AP game,
- `docs/en_MyGameImplementation.md` → `docs/en_<game string>.md`,
- `apworld-path` in `.github/workflows/*.yml`.

Check with `grep -rn "MyGameImplementation" worlds/ .github/`. Nothing should remain.

## Rules for editing

- Only edit inside the world folder (plus `.github/workflows` and the README). Don't change
  Archipelago core files.
- Item and location IDs must be unique and stable. Never renumber existing IDs once released.
- The server and client only exchange IDs, never names, so the IDs in `Items.py` and
  `Locations.py` **must match how the items and locations are set up in the client**. When
  changing an ID, say the client needs the same change.
- `ITEM_BASE_ID` and `LOCATION_BASE_ID` are just starting numbers. The user can set them to
  anything they like; each entry adds 1, 2, 3... to them.
- Every `progression` item should matter to at least one rule; anything not needed by logic
  shouldn't be `progression`.
- Use `self.random` for randomness, never the global `random` module (seeds must be reproducible).
- Don't put the same item or location name in two places. Names are global within the world.
- When options make the location count change, make sure `create_items` still matches it.
- Raise `Options.OptionError` for option combinations that can't work.

## Commands (run from the repo root, inside the venv)

```sh
# setup
python -m venv venv && source venv/bin/activate
python ModuleUpdate.py --yes
pip install -r ci-requirements.txt

# YAML templates → Players/Templates/<game>.yaml (copy into Players/ to generate with it)
python Launcher.py "Generate Template Options" -- --skip_open_folder

# generate a seed from every YAML in Players/ (should end with "Done. Enjoy.")
python Generate.py
python Generate.py --skip_output        # logic only, faster

# tests
python -m pytest worlds/MyGameImplementation/test
python -m pytest test/general

# fuzzer (-g is the world FOLDER name); success = 0 failures, 0 timeouts
python fuzz.py -r 100 -j 8 -g MyGameImplementation -n 1
python fuzz.py -r 100 -j 8 -g MyGameImplementation -n 1-5

# build the .apworld → build/apworlds/
python Launcher.py "Build APWorlds" -- MyGameImplementation --skip_open_folder
```

After every change: run the world tests and `Generate.py`. Before calling it done: run the
fuzzer at `-n 1` and `-n 1-5` and `test/general`.

## Ready-for-use checklist

1. No `MyGameImplementation` names left.
2. Unique, stable IDs.
3. Rules cover every locked location, and every progression item is used.
4. `Generate.py` succeeds; world tests and `test/general` pass.
5. Fuzzer: 0 failures, 0 timeouts.
6. `docs/` filled in.
7. `.apworld` builds.

## Further reading

- `docs/world api.md`: full World API reference
- `docs/options api.md`: every option type
- Other worlds in `worlds/` are good references. `worlds/clique` and `worlds/apquest` are small.
