from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range, Toggle


# The three option types you'll use most. Each class becomes a setting in the player's YAML file.
# The docstring is shown to players as the option's description, so write it for them.


class HardMode(Toggle):
    """Toggle: an on/off switch.
    When on, enemies hit twice as hard."""

    display_name = "Hard Mode"


class StartingGold(Range):
    """Range: a number between a minimum and a maximum.
    How much gold the hero starts the adventure with."""

    display_name = "Starting Gold"
    range_start = 0
    range_end = 999
    default = 100


class HeroClass(Choice):
    """Choice: pick one from a fixed list.
    Warrior - Strong in melee.
    Mage - Casts powerful spells.
    Thief - Fast and sneaky."""

    display_name = "Hero Class"
    option_warrior = 0
    option_mage = 1
    option_thief = 2
    default = option_warrior


# Register every option here. The field name (e.g. hard_mode) is the key used in the YAML file
# and how you read it in code: self.options.hard_mode.value
@dataclass
class MyGameImplementationOptions(PerGameCommonOptions):
    hard_mode: HardMode
    starting_gold: StartingGold
    hero_class: HeroClass
