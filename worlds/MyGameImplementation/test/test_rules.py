from . import MyGameImplementationTestBase


class TestDragonsHoard(MyGameImplementationTestBase):
    def test_village_chest_is_always_open(self) -> None:
        self.assertTrue(self.can_reach_location("Village Chest"))

    def test_hoard_needs_crystal_key(self) -> None:
        self.assertFalse(self.can_reach_location("Dragon's Hoard"))
        self.collect_by_name("Crystal Key")
        self.assertTrue(self.can_reach_location("Dragon's Hoard"))

    def test_victory_needs_crystal_key(self) -> None:
        self.assertBeatable(False)
        self.collect_by_name("Crystal Key")
        self.assertBeatable(True)
