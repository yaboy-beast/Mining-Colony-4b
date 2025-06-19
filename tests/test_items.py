"""
Unit tests for the item system in Colony 4B.

This test suite verifies the functionality of the ``Item`` class and the
``ItemType`` enumeration from the ``items`` module. It ensures that
items are created correctly with valid properties and that the expected
exceptions are raised when invalid data is provided.
"""
import unittest
import sys
import os

# Add the parent directory to the sys.path to allow for package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from items import Item, ItemType, _key_item, _resource

class TestItems(unittest.TestCase):
    """
    Test cases for the Item class and its helper functions.
    
    This suite tests the creation and validation of Item objects, ensuring
    that the constructor correctly assigns properties and raises
    appropriate errors for invalid input.
    """

    def test_item_creation_success(self):
        """
        Tests that a valid Item can be created successfully.
        
        This test checks that the name, description, and type are correctly
        assigned during object instantiation.
        """
        item = Item("Test Item", "A description.", ItemType.RESOURCE)
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.description, "A description.")
        self.assertEqual(item.type, ItemType.RESOURCE)

    def test_item_creation_invalid_name(self):
        """
        Tests that creating an item with an invalid name raises a ValueError.
        
        This test case checks for both empty string and None as invalid names.
        """
        with self.assertRaisesRegex(ValueError, "Item name must be a non-empty string"):
            Item("", "A description.", ItemType.RESOURCE)
        with self.assertRaisesRegex(ValueError, "Item name must be a non-empty string"):
            Item(None, "A description.", ItemType.RESOURCE)

    def test_item_creation_invalid_description(self):
        """
        Tests that creating an item with a non-string description raises a ValueError.
        """
        with self.assertRaisesRegex(ValueError, "Item description must be a string"):
            Item("Test Item", None, ItemType.RESOURCE)

    def test_item_creation_invalid_type(self):
        """
        Tests that creating an item with an invalid type raises a ValueError.

        This checks both incorrect string values and non-enum types.
        """
        with self.assertRaisesRegex(ValueError, "Invalid item type"):
            Item("Test Item", "A description.", "not_an_item_type")
        with self.assertRaisesRegex(ValueError, "Invalid item type"):
            Item("Test Item", "A description.", 123)

    def test_key_item_factory_function(self):
        """
        Tests that the _key_item factory function creates a KEY_ITEM correctly.
        """
        key_item = _key_item("Key", "A key item.")
        self.assertEqual(key_item.name, "Key")
        self.assertEqual(key_item.description, "A key item.")
        self.assertEqual(key_item.type, ItemType.KEY_ITEM)
        
    def test_resource_factory_function(self):
        """
        Tests that the _resource factory function creates a RESOURCE correctly.
        """
        resource_item = _resource("Ore", "Some ore.")
        self.assertEqual(resource_item.name, "Ore")
        self.assertEqual(resource_item.description, "Some ore.")
        self.assertEqual(resource_item.type, ItemType.RESOURCE)

if __name__ == '__main__':
    unittest.main() 
