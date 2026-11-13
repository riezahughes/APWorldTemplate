from typing import Dict, NamedTuple, Optional

from BaseClasses import Item, ItemClassification


# Every item needs a unique number (an "ID"). The server and client only ever exchange these
# numbers, never the names, so the IDs here MUST match the IDs your client uses for each item.
# The starting number is up to you: change ITEM_BASE_ID to whatever you like, and each item
# adds 1, 2, 3... to it. Never change an ID once people are playing your world.
ITEM_BASE_ID = 8_675_000


class MyGameImplementationItemData(NamedTuple):
    code: Optional[int]  # The ID the game client will receive. None = event item (logic only).
    classification: ItemClassification


# The list of every item in the game.
#   progression - something the logic needs (opens doors, beats bosses).
#   filler      - nice to have, never required (potions, gold, ammo).
item_table: Dict[str, MyGameImplementationItemData] = {
    "Crystal Key": MyGameImplementationItemData(ITEM_BASE_ID + 1, ItemClassification.progression),
    "Healing Potion": MyGameImplementationItemData(ITEM_BASE_ID + 2, ItemClassification.filler),
}

# The item used to pad out the pool if there are more locations than items.
FILLER_ITEM_NAME = "Healing Potion"


class MyGameImplementationItem(Item):
    game: str = "MyGameImplementation"
