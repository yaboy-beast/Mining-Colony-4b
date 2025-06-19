"""
Unit tests for the Room and RoomFactory classes in Colony 4B.

This test suite covers the ``Room`` and ``RoomFactory`` classes from the
``room`` module. It verifies the correct initialization of rooms, the
management of exits, items, and NPCs, and the handling of interaction
states. It also includes tests for the factory methods to ensure they
construct rooms as expected.
"""
import unittest
import sys
import os

# Add the parent directory to the sys.path to allow for package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from room import Room, RoomFactory
from items import Item, ItemType, ITEMS

class TestRoom(unittest.TestCase):
    """
    Test cases for the Room class.

    This suite tests the core functionality of a Room, including initialization,
    management of exits, items, NPCs, and interaction states.
    """

    def setUp(self) -> None:
        """
        Set up a new Room instance and test data before each test.
        """
        self.room = Room("Test Chamber", "A room for testing.")
        self.other_room = Room("Exit Room", "A room connected to the test chamber.")
        self.item = ITEMS["lucky coin"]

    def test_room_initialization(self) -> None:
        """
        Tests that a room is initialized with correct default values.
        """
        self.assertEqual(self.room.name, "Test Chamber")
        self.assertEqual(self.room.description, "A room for testing.")
        self.assertEqual(len(self.room.exits), 0)
        self.assertEqual(len(self.room.items), 0)
        self.assertEqual(len(self.room.npcs), 0)
        self.assertEqual(self.room.current_interaction_state, "main")

    def test_add_and_get_exit(self) -> None:
        """
        Tests that an exit can be added to a room and retrieved correctly.
        """
        self.room.add_exit("north", self.other_room)
        self.assertIn("north", self.room.exits)
        self.assertIs(self.room.get_exit("north"), self.other_room)
        # Check that a 'go' command was added to the main interaction state.
        self.assertIn("go north", self.room.interaction_states["main"].interactions)

    def test_get_nonexistent_exit(self) -> None:
        """
        Tests that trying to get a non-existent exit returns None.
        """
        self.assertIsNone(self.room.get_exit("south"))

    def test_add_and_remove_item(self) -> None:
        """
        Tests that an item can be added to and removed from a room.
        
        This also verifies that the corresponding 'take' interaction is
        added and removed from the room's main state.
        """
        # Note: The 'add_item' method takes an item's name (key), not an object.
        self.room.add_item("lucky coin")
        self.assertIn(self.item, self.room.items)
        self.assertIn("take lucky coin", self.room.interaction_states["main"].interactions)

        self.room.remove_item(self.item)
        self.assertNotIn(self.item, self.room.items)
        self.assertNotIn("take lucky coin", self.room.interaction_states["main"].interactions)

    def test_add_npc(self) -> None:
        """
        Tests that an NPC can be added to a room correctly.
        
        Also ensures the 'talk to' interaction is created.
        """
        self.room.add_npc("Dr. Test")
        self.assertIn("Dr. Test", self.room.npcs)
        self.assertIn("talk to Dr. Test", self.room.interaction_states["main"].interactions)

    def test_add_duplicate_npc(self) -> None:
        """
        Tests that adding the same NPC twice does not create duplicate entries
        or interactions.
        """
        self.room.add_npc("Dr. Test")
        self.room.add_npc("Dr. Test")
        self.assertEqual(self.room.npcs.count("Dr. Test"), 1)
        self.assertEqual(self.room.interaction_states["main"].interactions.count("talk to Dr. Test"), 1)

    def test_add_and_set_interaction_state(self) -> None:
        """
        Tests that a new interaction state can be added and set as current.
        """
        self.room.add_interaction_state("testing", ["action1", "action2"], parent="main")
        self.room.set_interaction_state("testing")
        self.assertEqual(self.room.current_interaction_state, "testing")
        self.assertEqual(self.room.get_available_interactions(), ["action1", "action2"])

    def test_get_parent_state(self) -> None:
        """
        Tests that the parent of the current state can be correctly retrieved.
        """
        self.room.add_interaction_state("child", [], parent="parent_state")
        self.room.add_interaction_state("parent_state", [], parent="main")
        self.room.set_interaction_state("child")
        self.assertEqual(self.room.get_parent_state(), "parent_state")
        self.room.set_interaction_state("parent_state")
        self.assertEqual(self.room.get_parent_state(), "main")

    def test_message_queue(self) -> None:
        """
        Tests the functionality of the room's message queue.
        
        This test verifies that messages are added, retrieved in the correct
        order, and that the queue is cleared after retrieval.
        """
        self.room.add_message("Hello")
        self.room.add_message("World")
        messages = self.room.get_messages()
        self.assertEqual(messages, ["Hello", "World"])
        # Test that the queue is cleared after getting messages.
        self.assertEqual(self.room.get_messages(), [])

    def test_add_invalid_exit_raises_error(self) -> None:
        """
        Tests that add_exit raises ValueError for invalid parameters.
        """
        with self.assertRaises(ValueError):
            self.room.add_exit(None, self.other_room)
        with self.assertRaises(ValueError):
            self.room.add_exit("north", "not a room object")

    def test_room_factory_player_home(self) -> None:
        """
        Tests that the RoomFactory correctly creates the player's home.
        """
        home = RoomFactory.create_player_home()
        self.assertEqual(home.name, "Your Quarters")
        # Check for the hidden items in the cupboard.
        self.assertIn("cupboard", home.hidden_items)
        self.assertTrue(any(item.name == "ID card" for item in home.hidden_items["cupboard"]))
        # Check for the terminal interaction.
        self.assertIn("check terminal", home.interaction_states["main"].interactions)

if __name__ == '__main__':
    unittest.main() 