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

## A good first design: keys, a level select and a final door

Not sure how to turn your game into an Archipelago world? This design works for almost any game
with **separate levels** and a **level select menu**, and it's a good place to start. You don't
have to understand or change the game's own progression: you add a few **custom items** and let
the client lock and unlock things.

Here's the idea, using an imaginary game called **The Five Kingdoms**:

- The game has a level select menu with five levels: **Whispering Woods**, **Goblin Caves**,
  **Frozen Peaks**, **Sunken Temple** and the final level, the **Dark Tower**.
- Each level except the first is locked behind a **key**. The keys are **custom items**: they
  don't exist in the original game. The client keeps a level greyed out in the level select
  until the player receives its key.
- The Dark Tower's door needs a **collection**: 3 **Crown Shards**, also custom items.
- Beating the **Dark Lord** at the top of the Dark Tower wins the game.

### Why this design works well

- **It doesn't touch the levels.** You only change what the level select allows, so you don't
  need to edit the game's maps or story.
- **It's easy to start.** The Whispering Woods is open from the beginning, so the player
  always has somewhere to go and something to check.
- **The keys make it a randomizer.** Your keys can turn up in other players' games, and theirs in
  yours, so everyone ends up helping each other.
- **The collection gives a clear goal.** "Find 3 Crown Shards" is easy to understand, and an
  option can change how many are needed.
- **It grows with you.** Get it working with chests and bosses first, then add more locations
  (collectables, NPCs, shops) once the basics are solid.

### Items

| Item                | Classification | How many | What it does                                 |
|---------------------|----------------|----------|----------------------------------------------|
| `Goblin Caves Key`  | progression    | 1        | Unlocks Goblin Caves in the level select     |
| `Frozen Peaks Key`  | progression    | 1        | Unlocks Frozen Peaks in the level select     |
| `Sunken Temple Key` | progression    | 1        | Unlocks Sunken Temple in the level select    |
| `Crown Shard`       | progression    | 3        | Collect enough to open the Dark Tower's door |
| `Healing Potion`    | filler         | 2        | Pads the pool so items = locations           |

### Locations

Two checks per level: a hidden chest and the boss. That makes 8 real locations, matching the 8
items above (3 keys + 3 shards + 2 potions).

| Region           | Locations                                       | Needs to enter            |
|------------------|-------------------------------------------------|---------------------------|
| Whispering Woods | `Hidden Chest`, `Defeat Giant Spider`           | nothing (open from start) |
| Goblin Caves     | `Hidden Chest`, `Defeat Goblin King`            | `Goblin Caves Key`        |
| Frozen Peaks     | `Hidden Chest`, `Defeat Ice Wyrm`               | `Frozen Peaks Key`        |
| Sunken Temple    | `Hidden Chest`, `Defeat Sea Serpent`            | `Sunken Temple Key`       |
| Dark Tower       | `Defeat the Dark Lord` (the goal, an **event**) | 3 `Crown Shard`           |

An **event** is a location with no ID. It never holds a real item and the client never sends
it. It exists so the logic can say "you've beaten the Dark Lord".

### The map

```
Menu ──► Level Select ──┬──► Whispering Woods                       (always open)
                        ├──► Goblin Caves       [Goblin Caves Key]
                        ├──► Frozen Peaks       [Frozen Peaks Key]
                        ├──► Sunken Temple      [Sunken Temple Key]
                        └──► Dark Tower         [3 × Crown Shard] ──► Victory
```

Each arrow is an **entrance**, and the rules go on the entrances. Every location inside a level
is then locked behind that level's key automatically, so you don't need a rule per location.

### How it looks in code

Below is how each template file would change. Rename the classes as described in Step 2.

**`Items.py`**: add a `count` so one item name can go into the pool more than once.

```python
class MyGameImplementationItemData(NamedTuple):
    code: Optional[int]
    classification: ItemClassification
    count: int = 1  # how many copies go into the item pool


item_table = {
    "Goblin Caves Key":  MyGameImplementationItemData(ITEM_BASE_ID + 1, ItemClassification.progression),
    "Frozen Peaks Key":  MyGameImplementationItemData(ITEM_BASE_ID + 2, ItemClassification.progression),
    "Sunken Temple Key": MyGameImplementationItemData(ITEM_BASE_ID + 3, ItemClassification.progression),
    "Crown Shard":       MyGameImplementationItemData(ITEM_BASE_ID + 4, ItemClassification.progression, count=3),
    "Healing Potion":    MyGameImplementationItemData(ITEM_BASE_ID + 5, ItemClassification.filler, count=0),  # added as padding
}
```

**`Locations.py`**: each location says which level it's in. The goal has no ID (`None`).

```python
class MyGameImplementationLocationData(NamedTuple):
    code: Optional[int]  # None = event
    region: str


location_table = {
    "Whispering Woods: Hidden Chest":        MyGameImplementationLocationData(LOCATION_BASE_ID + 1, "Whispering Woods"),
    "Whispering Woods: Defeat Giant Spider": MyGameImplementationLocationData(LOCATION_BASE_ID + 2, "Whispering Woods"),
    "Goblin Caves: Hidden Chest":            MyGameImplementationLocationData(LOCATION_BASE_ID + 3, "Goblin Caves"),
    "Goblin Caves: Defeat Goblin King":      MyGameImplementationLocationData(LOCATION_BASE_ID + 4, "Goblin Caves"),
    "Frozen Peaks: Hidden Chest":            MyGameImplementationLocationData(LOCATION_BASE_ID + 5, "Frozen Peaks"),
    "Frozen Peaks: Defeat Ice Wyrm":         MyGameImplementationLocationData(LOCATION_BASE_ID + 6, "Frozen Peaks"),
    "Sunken Temple: Hidden Chest":           MyGameImplementationLocationData(LOCATION_BASE_ID + 7, "Sunken Temple"),
    "Sunken Temple: Defeat Sea Serpent":     MyGameImplementationLocationData(LOCATION_BASE_ID + 8, "Sunken Temple"),
    "Dark Tower: Defeat the Dark Lord":      MyGameImplementationLocationData(None, "Dark Tower"),
}
```

**`Options.py`**: let players choose how many shards they need.

```python
class CrownShardsRequired(Range):
    """How many Crown Shards you need to open the door to the Dark Tower."""

    display_name = "Crown Shards Required"
    range_start = 1
    range_end = 3
    default = 3


@dataclass
class MyGameImplementationOptions(PerGameCommonOptions):
    crown_shards_required: CrownShardsRequired
```

**`__init__.py`**: build the level select, then fill the item pool.

```python
    # Only real locations get an ID; the event (code None) is left out.
    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_to_id = {name: data.code for name, data in location_table.items() if data.code is not None}

    LEVELS = ["Whispering Woods", "Goblin Caves", "Frozen Peaks", "Sunken Temple", "Dark Tower"]

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        level_select = Region("Level Select", self.player, self.multiworld)
        menu.connect(level_select)
        regions = {"Menu": menu, "Level Select": level_select}

        # One region per level, each reached from the level select through "Enter <level>".
        for level in self.LEVELS:
            regions[level] = Region(level, self.player, self.multiworld)
            level_select.connect(regions[level], f"Enter {level}")

        for name, data in location_table.items():
            region = regions[data.region]
            region.locations.append(MyGameImplementationLocation(self.player, name, data.code, region))

        self.multiworld.regions += regions.values()

    def create_items(self) -> None:
        pool = []
        for name, data in item_table.items():
            pool += [self.create_item(name) for _ in range(data.count)]

        # Pad with filler until there's one item per real location.
        real_locations = len(self.location_name_to_id)
        pool += [self.create_item(FILLER_ITEM_NAME) for _ in range(real_locations - len(pool))]
        self.multiworld.itempool += pool

    def fill_slot_data(self) -> Dict[str, Any]:
        return self.options.as_dict("crown_shards_required")  # the client needs this for the door
```

**`Rules.py`**: two rules cover the whole game.

```python
LEVEL_KEYS = {
    "Goblin Caves": "Goblin Caves Key",
    "Frozen Peaks": "Frozen Peaks Key",
    "Sunken Temple": "Sunken Temple Key",
}


def set_location_rules(world) -> None:
    player = world.player

    # Rule 1: each level in the level select needs its key.
    for level, key in LEVEL_KEYS.items():
        set_rule(world.get_entrance(f"Enter {level}"), lambda state, key=key: state.has(key, player))

    # Rule 2: the Dark Tower's door needs enough Crown Shards.
    shards = world.options.crown_shards_required.value
    set_rule(world.get_entrance("Enter Dark Tower"), lambda state: state.has("Crown Shard", player, shards))
```

> **Watch out:** the `key=key` in the first lambda matters. Without it, every level would check
> for the *last* key in the loop (`Sunken Temple Key`), because Python looks up `key` when the
> rule runs, not when it's written.

**`VictoryConditions.py`**: put a `Victory` event on the Dark Lord and win when you have it.

```python
from BaseClasses import ItemClassification

from .Items import MyGameImplementationItem


def set_victory_condition(world) -> None:
    player = world.player
    victory = MyGameImplementationItem("Victory", ItemClassification.progression, None, player)  # None = event
    world.get_location("Dark Tower: Defeat the Dark Lord").place_locked_item(victory)
    world.multiworld.completion_condition[player] = lambda state: state.has("Victory", player)
```

**`test/test_rules.py`**: check the rules do what you expect.

```python
class TestLevelKeys(MyGameImplementationTestBase):
    def test_woods_open_from_start(self) -> None:
        self.assertTrue(self.can_reach_region("Whispering Woods"))

    def test_caves_need_key(self) -> None:
        self.assertFalse(self.can_reach_region("Goblin Caves"))
        self.collect_by_name("Goblin Caves Key")
        self.assertTrue(self.can_reach_region("Goblin Caves"))

    def test_dark_tower_needs_shards(self) -> None:
        self.assertFalse(self.can_reach_region("Dark Tower"))
        self.collect_by_name("Crown Shard")  # collects all 3
        self.assertTrue(self.can_reach_region("Dark Tower"))
        self.assertBeatable(True)
```

### What the client does for this design

The apworld only decides where things go. While playing, the client:

1. **Locks the level select.** Goblin Caves, Frozen Peaks and Sunken Temple can't be picked
   until their key has been received. The Dark Tower can't be picked until the player has
   `crown_shards_required` Crown Shards (from slot data).
2. **Swaps out the game's own rewards.** When a chest is opened or a boss is beaten, the original
   item isn't given. Instead the client sends that location's ID to the server (e.g.
   `8675003` for `Goblin Caves: Hidden Chest`).
3. **Gives received items.** A key unlocks its level, a Crown Shard adds to the count, a Healing
   Potion heals the player.
4. **Reports victory** when the Dark Lord is defeated.

The client doesn't need to know the rules: the server and the apworld have already made sure
the seed can be finished.

### Making it fit your game

- Swap the five levels for your game's levels, and the chest/boss checks for whatever your
  game has (collectables, NPC rewards, shops...).
- Keep at least one level open at the start with a couple of checks in it, so the player can
  always begin.
- Pick a collection that suits your game: shards, medals, stars, souls. Make "how many are
  needed" an option.
- If your game has no level select, the same idea works with doors, warps or areas of a map.

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

### Step 3: Pick your IDs

Every item and location has a number, its **ID**. The server never sends names, only IDs:
when the player opens the Village Chest, the client sends the server `8675001`. When the player
receives the Crystal Key, the server sends the client `8675001` (items and locations have
separate lists, so the same number can appear in both).

**The IDs are important: they have to match however you set up the items and locations in your
client.** If the apworld says the Dragon's Hoard is `8675002` but the client sends `8675003`,
the check goes to the wrong place or doesn't count at all. Keep one list of IDs and use it in
both the apworld and the client.

The starting number is up to you. In `Items.py` and `Locations.py`, change `ITEM_BASE_ID` and
`LOCATION_BASE_ID` to whatever you like (they can be the same or different). Each item and
location then adds 1, 2, 3... to it. A big number makes it less likely to look like another
game's IDs, which helps when debugging.

Once people are playing, **never change an ID**, or saved games and clients will break.

### Step 4: Fill in your game

Need an idea for how to lay it out? Start from
[A good first design](#a-good-first-design-keys-a-level-select-and-a-final-door).

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
- [ ] Every item and location has a unique ID that you won't change again, and the same IDs are used in your client.
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
