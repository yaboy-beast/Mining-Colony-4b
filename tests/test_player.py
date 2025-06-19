"""
Unit tests for the Player class in Colony 4B.

This test suite covers the ``Player`` class from the ``player`` module. It
verifies the correct initialization of player attributes, the logic for
managing the player's inventory (adding and removing items, checking
capacity), and the behavior of quest flags and other status attributes.
"""
import unittest
import sys
import os

# Add the parent directory to the sys.path to allow for package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from player import Player
from items import Item, ItemType, ITEMS

class TestPlayer(unittest.TestCase):
    """
    Test cases for the Player class.
    
    This suite tests the initialization of a Player object, inventory
    management (adding, removing, and checking items), and the correctness
    of quest flags and other player stats.
    """

    def setUp(self) -> None:
        """
        Set up a new Player instance and some test items before each test.
        """
        self.player = Player("TestSubject")
        self.item1 = Item("Gadget", "A simple gadget.", ItemType.RESOURCE)
        self.item2 = Item("Widget", "A complex widget.", ItemType.RESOURCE)
        self.key_item = ITEMS["ID card"]
        self.consumable_key_item = ITEMS["Steamed Buns"]

    def test_player_initialization(self) -> None:
        """
        Tests that the player is initialized with correct default values.
        """
        self.assertEqual(self.player.name, "TestSubject")
        self.assertEqual(self.player.minshin, 50) # INITIAL_MINSHIN
        self.assertEqual(len(self.player.inventory), 0)
        self.assertEqual(self.player.max_inventory, 10) # MAX_INVENTORY_DEFAULT
        self.assertEqual(self.player.ambrosium_quota, 20) # WEEKLY_AMBROSIUM_QUOTA
        self.assertEqual(self.player.quota_fulfilled, 0)
        # Check a sample quest flag
        self.assertFalse(self.player.long_quest_complete)
        # Check a sample purchase flag
        self.assertFalse(self.player.bought_xl_backpack)

    def test_add_to_inventory_success(self) -> None:
        """
        Tests that an item can be successfully added to the inventory.
        """
        self.assertTrue(self.player.add_to_inventory(self.item1))
        self.assertEqual(len(self.player.inventory), 1)
        self.assertIn(self.item1, self.player.inventory)

    def test_add_to_inventory_full(self) -> None:
        """
        Tests that an item cannot be added when the inventory is full.
        """
        self.player.max_inventory = 1
        self.player.add_to_inventory(self.item1)
        self.assertFalse(self.player.add_to_inventory(self.item2))
        self.assertEqual(len(self.player.inventory), 1)
        self.assertNotIn(self.item2, self.player.inventory)

    def test_remove_from_inventory_success(self) -> None:
        """
        Tests that a standard item can be successfully removed from inventory.
        """
        self.player.add_to_inventory(self.item1)
        self.assertTrue(self.player.remove_from_inventory(self.item1))
        self.assertEqual(len(self.player.inventory), 0)

    def test_cannot_drop_essential_key_item(self) -> None:
        """
        Tests that an essential KEY_ITEM (like an ID card) cannot be removed.
        """
        self.player.add_to_inventory(self.key_item)
        self.assertFalse(self.player.remove_from_inventory(self.key_item))
        self.assertIn(self.key_item, self.player.inventory)
        
    def test_can_drop_consumable_key_item(self) -> None:
        """
        Tests that a consumable KEY_ITEM (like quest items) can be removed.
        """
        self.player.add_to_inventory(self.consumable_key_item)
        self.assertTrue(self.player.remove_from_inventory(self.consumable_key_item))
        self.assertNotIn(self.consumable_key_item, self.player.inventory)

    def test_is_inventory_full(self) -> None:
        """
        Tests the is_inventory_full check at various capacities.
        """
        self.player.max_inventory = 2
        self.player.add_to_inventory(self.item1)
        self.assertFalse(self.player.is_inventory_full())
        self.player.add_to_inventory(self.item2)
        self.assertTrue(self.player.is_inventory_full())

    def test_has_item(self) -> None:
        """
        Tests the has_item method for existing and non-existing items.
        """
        self.player.add_to_inventory(self.item1)
        self.assertTrue(self.player.has_item(self.item1))
        self.assertFalse(self.player.has_item(self.item2))

    def test_get_item_by_name(self) -> None:
        """
        Tests the get_item_by_name method for correctness and case-insensitivity.
        """
        self.player.add_to_inventory(self.item1)
        # Test exact match
        self.assertIs(self.player.get_item_by_name("Gadget"), self.item1)
        # Test case-insensitivity
        self.assertIs(self.player.get_item_by_name("gadget"), self.item1)
        # Test non-existent item
        self.assertIsNone(self.player.get_item_by_name("Widget"))

    def test_add_to_inventory_full_returns_false(self) -> None:
        """
        Tests that add_to_inventory returns False when inventory is full.
        """
        self.player.max_inventory = 2
        self.player.add_to_inventory(self.item1)
        self.player.add_to_inventory(self.item2)
        # Try to add a third item
        result = self.player.add_to_inventory(Item("Extra", "item", ItemType.RESOURCE))
        self.assertFalse(result)

    def test_has_item_not_in_inventory(self) -> None:
        """
        Tests that has_item returns False for an item not in inventory.
        """
        self.assertFalse(self.player.has_item(self.item1))

    def test_remove_item_not_in_inventory_returns_false(self) -> None:
        """
        Tests that removing an item that isn't in inventory returns False.
        """
        result = self.player.remove_from_inventory(self.item1)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main() 
