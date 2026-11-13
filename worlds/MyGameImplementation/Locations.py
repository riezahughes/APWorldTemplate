from typing import Dict, NamedTuple

from BaseClasses import Location


# Every location needs a unique number (an "ID"). The client tells the server which location
# was checked by sending this number, so the IDs here MUST match the IDs your client uses.
# The starting number is up to you: change LOCATION_BASE_ID to whatever you like, and each
# location adds 1, 2, 3... to it. Never change an ID once people are playing your world.
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
