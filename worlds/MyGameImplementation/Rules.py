from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from . import MyGameImplementationWorld


def set_location_rules(world: "MyGameImplementationWorld") -> None:
    player = world.player

    # The one rule: the Dragon's Hoard is locked until you have the Crystal Key.
    # "state" is everything the player has collected so far; the rule returns True when the
    # location can be reached. Locations without a rule are always reachable.
    set_rule(
        world.get_location("Dragon's Hoard"),
        lambda state: state.has("Crystal Key", player),
    )
