# Consid AP World Template

A starter kit for building your first [Archipelago](https://archipelago.gg) world (an "apworld").

This repo is a full copy of the Archipelago source code, so you can generate and test seeds
locally. Your game lives in one folder: **`worlds/MyGameImplementation`**. It's cut down to the
bare minimum: 2 items, 2 locations, 1 rule and 1 victory condition, plus one example of each
of the three main option types.

> **The apworld is only one part of the puzzle.** It decides *where items go* and *what's
> needed to win*. To actually play, you also need a **client** that connects your game to the
> Archipelago server. See [The other half: the client](#the-other-half-the-client).

> The original Archipelago README is kept at [`docs/archipelago-README.md`](docs/archipelago-README.md).

---

## The three ideas you need

Archipelago shuffles a game's **items** into its **locations**, across several players' games
at once, while making sure the **rules** never leave anyone stuck. We'll use the original
**Final Fantasy** as an example.

### Item
Something the player *receives*. In Final Fantasy: the **Mystic Key**, the **Lute**, a
**Potion**, the **Airship**.

Each item has a classification:
- **progression**: the logic needs it (the Mystic Key opens locked doors).
- **useful**: helps, but is never required (a strong sword).
- **filler**: padding (a Potion, some gold).

### Location
A place the player *checks* to get something. In Final Fantasy: **a treasure chest in Coneria
Castle**, or **the King giving you the bridge**. In a randomizer, opening that chest might give
you someone else's item, from someone else's game.

Rule of thumb: **every location holds exactly one item**, so the number of items in the pool
must match the number of locations.

### Rule
A condition that says when a location (or area) can be reached. In Final Fantasy: *"the chests
behind the locked door in Coneria Castle need the **Mystic Key**"*. Archipelago reads your rules
to make sure the Mystic Key is never placed behind its own locked door.

### And two more
- **Victory condition**: what counts as beating the game. In Final Fantasy, *defeating Chaos*.
- **Options**: settings players choose in their YAML file (e.g. "shuffle the Airship?").

### How it fits in this template

| Concept           | In this template                                        | File                   |
|-------------------|---------------------------------------------------------|------------------------|
| Items             | `Crystal Key` (progression), `Healing Potion` (filler)  | `Items.py`             |
| Locations         | `Village Chest`, `Dragon's Hoard`                       | `Locations.py`         |
| Rule              | `Dragon's Hoard` needs the `Crystal Key`                | `Rules.py`             |
| Victory condition | Reach the `Dragon's Hoard`                              | `VictoryConditions.py` |
| Options           | `hard_mode` (Toggle), `starting_gold` (Range), `hero_class` (Choice) | `Options.py` |
| Wiring it all up  | Regions, item pool, slot data                           | `__init__.py`          |

---

## Step-by-step guide

### Step 1: Set up Python

You need Python 3.11, 3.12 or 3.13. From the repo folder:

```sh
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
python ModuleUpdate.py --yes    # installs everything Archipelago needs
pip install -r ci-requirements.txt  # installs pytest, for running tests
```

Check the template works before you change anything (see Step 6). It should already pass.

### Step 2: Rename everything to your game

Everything is called `MyGameImplementation` right now: the folder, the game name and every class
name. **Change all of them to match the game you've chosen.** For example, for Final Fantasy
you might use `FinalFantasyAP`:

| Change this                                 | Where                                                     | To (example)                 |
|---------------------------------------------|-----------------------------------------------------------|------------------------------|
| Folder `worlds/MyGameImplementation`        | the folder itself                                         | `worlds/finalfantasyap`      |
| `game = "MyGameImplementation"`             | `__init__.py`, `Items.py`, `Locations.py`, `test/__init__.py` | `"Final Fantasy AP"`     |
| `"game"` field                              | `archipelago.json`                                        | `"Final Fantasy AP"`         |
| `MyGameImplementationWorld`, `...Web`, `...Item`, `...ItemData`, `...Location`, `...LocationData`, `...Options`, `...TestBase` | all `.py` files | `FinalFantasyAPWorld`, `FinalFantasyAPItem`, ... |
| `docs/en_MyGameImplementation.md`           | docs folder; must be `en_<game name>.md`                  | `en_Final Fantasy AP.md`     |
| `apworld-path: worlds/MyGameImplementation` | `.github/workflows/*.yml`                                 | `worlds/finalfantasyap`      |
| `authors`, `"YourNameHere"`                 | `archipelago.json`, `__init__.py`                         | your name                    |

Rules:
- The **game name must be identical** everywhere it appears, and must not clash with an
  existing Archipelago game. It's what players type in their YAML.
- The **folder name** should be lowercase with no spaces (it becomes a Python module).

To find anything you missed:

```sh
grep -rn "MyGameImplementation" worlds/ .github/
```

### Step 3: Pick unique IDs

In `Items.py` and `Locations.py`, change `ITEM_BASE_ID` and `LOCATION_BASE_ID` to a big number of
your own. Each item and location adds 1, 2, 3... to it. Once people are playing, **never change
an ID**, or saved games and clients will break.

### Step 4: Fill in your game

Work through the files in this order, one small change at a time, running the checks in Step 6
after each change:

1. **`Locations.py`**: list your checks and which region each one is in.
2. **`Items.py`**: list your items and mark which ones are `progression`.
3. **`__init__.py` → `create_regions`**: create your regions and connect them.
4. **`Rules.py`**: add a rule for every location or connection that needs an item.
5. **`VictoryConditions.py`**: say what beating the game means.
6. **`Options.py`**: add the settings players can choose. Copy whichever of the three examples
   (`Toggle`, `Range`, `Choice`) fits, then add it to the `MyGameImplementationOptions` dataclass.
7. **`docs/`**: describe your game and how to set it up.

Keep the item pool the same size as the number of locations. `create_items` pads with filler
if you have more locations than items.

### Step 5: Generate a YAML template

Archipelago builds a player YAML from your options:

```sh
python Launcher.py "Generate Template Options" -- --skip_open_folder
```

Your template appears at `Players/Templates/MyGameImplementation.yaml`. Copy it into
`Players/` (one level up) and change the options if you want. This is the file players give
to the host.

```sh
cp "Players/Templates/MyGameImplementation.yaml" Players/
```

### Step 6: Test it

Run these after every change. All four should succeed.

**Generate a seed** (uses every YAML in `Players/`):

```sh
python Generate.py
```

It should end with `Done. Enjoy.` and put a `.zip` in `output/`. Add `--skip_output` for a
faster check that only tests the logic.

**Run your unit tests:**

```sh
python -m pytest worlds/MyGameImplementation/test
# or, without pytest installed:
python -m unittest discover -s worlds/MyGameImplementation/test -t .
```

**Run Archipelago's general tests** (they check every world, including yours):

```sh
python -m pytest test/general
```

**Run the fuzzer.** It generates hundreds of seeds with random options to find combinations
that break:

```sh
# 100 runs, 8 at a time, 1 player per seed
python fuzz.py -r 100 -j 8 -g MyGameImplementation -n 1

# 100 runs with 1 to 5 players per seed
python fuzz.py -r 100 -j 8 -g MyGameImplementation -n 1-5
```

`-g` is your world's **folder name**. A good run looks like this:

```
Success: 100
Failures: 0
Timeouts: 0
```

If anything fails, the failing YAMLs and errors are saved in `fuzz_output/`.

### Step 7: Build the .apworld

```sh
python Launcher.py "Build APWorlds" -- MyGameImplementation --skip_open_folder
```

This builds `build/apworlds/MyGameImplementation.apworld`. Players install it by double-clicking
it, or by copying it into the `custom_worlds` folder of their Archipelago install. Pushing a git
tag also builds it on GitHub using `.github/workflows/release.yml`.

---

## How do I know it's ready?

Your apworld is ready to use when all of these are true:

- [ ] There are no `MyGameImplementation` names left (`grep` from Step 2 finds nothing).
- [ ] Every item and location has a unique ID that you won't change again.
- [ ] Every progression item is used by at least one rule, and every locked location has a rule.
- [ ] `python Generate.py` ends with `Done. Enjoy.`
- [ ] Your unit tests and `test/general` pass.
- [ ] The fuzzer shows **0 failures and 0 timeouts** for both `-n 1` and `-n 1-5`.
- [ ] `docs/` explains what's shuffled and how to set the game up.
- [ ] The `.apworld` builds and generates a seed when installed in a normal Archipelago install.

This makes the apworld ready to **generate**. It isn't playable yet: for that you need a client.

---

## The other half: the client

The apworld only runs while the seed is being generated. Once the multiworld is hosted (on
[archipelago.gg](https://archipelago.gg) or your own server), something has to sit between your
game and the server while you play. That's the **client**. It needs to:

1. **Connect** to the server and log in as the player's slot.
2. **Send checks**: when the player opens the Village Chest, tell the server that location was
   checked (`LocationChecks`).
3. **Give items**: when the server says the player received the Crystal Key, put it in the
   game (`ReceivedItems`).
4. **Report victory**: tell the server when the goal is complete (`StatusUpdate`).

It uses the item and location **IDs** from `Items.py` and `Locations.py`, and the options you
sent in `fill_slot_data`. In Final Fantasy terms: the client notices you opened the Coneria
Castle chest, tells the server, and then hands you the Mystic Key someone else found.

There are two ways to build it:

### Option A: a client inside the apworld

The client ships in the same `.apworld` file and opens from the Archipelago Launcher, so players
only install one thing. Archipelago provides building blocks:

- **`BizHawkClient`** (`worlds/_bizhawk`): for games run in the BizHawk emulator. You write a
  class that reads and writes the game's memory, and Archipelago handles the server.
- **`CommonClient`** (`CommonClient.py`): a general client you can extend for PC games, e.g. by
  reading a save file or talking to a mod. Register it as a Launcher `Component` from your
  world's `__init__.py`.

Other worlds in `worlds/` show both approaches and are good examples to copy from.

### Option B: a separate client

If you prefer, build the client as its own program or game mod, in any language, and connect it
**directly to the server's WebSocket** (the address shown on the room page, e.g.
`archipelago.gg:38281`). The messages are plain JSON and are described in
[`docs/network protocol.md`](docs/network%20protocol.md). Ready-made libraries exist for
common languages (e.g. C# and JavaScript), which is handy if your game mod is already written
in one of them.

Either way, the apworld and the client must agree on the **game name, item IDs, location IDs and
slot data**. If you change one, update the other.

---

## Further reading

- [Adding a world](docs/world%20api.md): the full World API
- [Options API](docs/options%20api.md): every option type
- The Archipelago Discord (linked from [archipelago.gg](https://archipelago.gg)): the world-development channels are the place to ask
