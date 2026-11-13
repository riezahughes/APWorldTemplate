from typing import Any, Dict

from BaseClasses import Region, Tutorial
from worlds.AutoWorld import WebWorld, World

from .Items import FILLER_ITEM_NAME, MyGameImplementationItem, item_table
from .Locations import MyGameImplementationLocation, location_table
from .Options import MyGameImplementationOptions
from .Rules import set_location_rules
from .VictoryConditions import set_victory_condition


class MyGameImplementationWeb(WebWorld):
    theme = "stone"
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up MyGameImplementation for Archipelago.",
            "English",
            "setup_en.md",
            "setup/en",
            ["YourNameHere"],
        )
    ]


class MyGameImplementationWorld(World):
    """
    A tiny example fantasy game: find the Crystal Key, open the Dragon's Hoard, win.
    """

    game = "MyGameImplementation"  # Must match "game" in archipelago.json and the docs file name.
    web = MyGameImplementationWeb()
    options_dataclass = MyGameImplementationOptions
    options: MyGameImplementationOptions

    # Archipelago needs to know every item and location name up front, along with its ID.
    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_to_id = {name: data.code for name, data in location_table.items()}

    # Step 1: build the map. Regions are areas of the game; locations live inside them.
    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)  # Every world starts in "Menu".
        kingdom = Region("Fantasy Kingdom", self.player, self.multiworld)
        regions = {region.name: region for region in (menu, kingdom)}

        for name, data in location_table.items():
            region = regions[data.region]
            region.locations.append(MyGameImplementationLocation(self.player, name, data.code, region))

        self.multiworld.regions += [menu, kingdom]
        menu.connect(kingdom)  # The player can walk from the start into the kingdom.

    # Step 2: put exactly one item in the pool for every location.
    def create_items(self) -> None:
        for name in item_table:
            self.multiworld.itempool.append(self.create_item(name))

        # Pad with filler if there are more locations than items.
        missing = len(location_table) - len(item_table)
        for _ in range(missing):
            self.multiworld.itempool.append(self.create_item(FILLER_ITEM_NAME))

    def create_item(self, name: str) -> MyGameImplementationItem:
        data = item_table[name]
        return MyGameImplementationItem(name, data.classification, data.code, self.player)

    def get_filler_item_name(self) -> str:
        return FILLER_ITEM_NAME

    # Step 3: add the rules and the victory condition.
    def set_rules(self) -> None:
        set_location_rules(self)
        set_victory_condition(self)

    # Step 4: anything the game client needs to know about this seed (usually the options).
    def fill_slot_data(self) -> Dict[str, Any]:
        return self.options.as_dict("hard_mode", "starting_gold", "hero_class")
