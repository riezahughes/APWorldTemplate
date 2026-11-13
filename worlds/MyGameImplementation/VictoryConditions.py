from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import MyGameImplementationWorld


def set_victory_condition(world: "MyGameImplementationWorld") -> None:
    player = world.player

    # The one victory condition: the game is beaten once the Dragon's Hoard can be reached.
    # Archipelago uses this to check every seed can actually be finished.
    world.multiworld.completion_condition[player] = lambda state: state.can_reach_location("Dragon's Hoard", player)
