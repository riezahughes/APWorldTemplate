from typing import Dict, NamedTuple

from BaseClasses import Location


# Locations need their own unique IDs too. Never change one once people are playing your world.
LOCATION_BASE_ID = 8_675_000


class MyGameImplementationLocationData(NamedTuple):
    code: int     # The ID the game client sends when this check is collected.
    region: str   # The region (area of the game) this location lives in.


# The list of every location ("check") in the game.
location_table: Dict[str, MyGameImplementationLocationData] = {
    "Village Chest": MyGameImplementationLocationData(LOCATION_BASE_ID + 1, "Fantasy Kingdom"),
    "Dragon's Hoard": MyGameImplementationLocationData(LOCATION_BASE_ID + 2, "Fantasy Kingdom"),
}


class MyGameImplementationLocation(Location):
    game: str = "MyGameImplementation"
