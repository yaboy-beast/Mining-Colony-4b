"""
Unit tests for the main Game class in Colony 4B.

This test suite verifies the core functionality of the ``Game`` class from
the ``game`` module. It covers the correct initialization of the game
state, creation of the game world (rooms and their connections), and the
behavior of key command handlers and game event triggers.
"""
import unittest
import sys
import os

# Add the parent directory to the sys.path for package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game import Game
from items import ITEMS
from game_constants import FOREMAN_SPAWN_DONATION_THRESHOLD

class TestGame(unittest.TestCase):
    """
    Test cases for the Game class.
    
    Tests basic game initialization and simple method functionality. Note
    that complex interactions involving the game loop and user input are
    difficult to test in a unit context and are largely omitted.
    """
    
    def setUp(self) -> None:
        """
        Set up a new Game instance before each test.
        """
        self.game = Game()
    
    def test_game_initialization(self) -> None:
        """
        Tests that the game initializes with the correct default state.
        """
        self.assertEqual(self.game.player.name, "Marmoris")
        self.assertEqual(self.game.mining_attempts, 0)
        self.assertEqual(self.game.total_donations, 0)
        self.assertFalse(self.game.debug_mode)
        # Player should start in 'Your Quarters'.
        self.assertEqual(self.game.current_room.name, "Your Quarters")
    
    def test_room_creation_and_connections(self) -> None:
        """
        Tests that all rooms are created and key connections exist.
        """
        # Test that a few key rooms exist.
        self.assertIsNotNone(self.game.player_home)
        self.assertIsNotNone(self.game.central_plaza)
        self.assertIsNotNone(self.game.mine_entrance)
        
        # Test a specific connection to ensure exits are wired up.
        exit_room = self.game.player_home.get_exit("residential corridor")
        self.assertIsNotNone(exit_room)
        self.assertEqual(exit_room.name, "Residential Corridor")
    
    def test_quit_game_returns_true(self) -> None:
        """
        Tests that the quit_game command handler returns True.
        
        This boolean return value is used to terminate the main game loop.
        """
        result = self.game.quit_game("")
        self.assertTrue(result)
    
    def test_check_for_foreman_spawn(self) -> None:
        """
        Tests that Foreman Long spawns correctly at the donation threshold.
        """
        # Ensure the foreman is not present initially.
        self.assertNotIn("Colony Foreman Long", self.game.memorial_pond.npcs)
        
        # Set donations to the required threshold.
        # The constant is imported from game_constants into the game module.
        self.game.total_donations = FOREMAN_SPAWN_DONATION_THRESHOLD
        self.game.check_for_foreman_spawn()
        
        # Verify that the foreman has been added to the correct room's NPC list.
        self.assertIn("Colony Foreman Long", self.game.memorial_pond.npcs)
    
    def test_take_item_with_empty_argument(self) -> None:
        """
        Tests that the take_item command with no argument adds the correct
        error message to the room's message queue.
        """
        # Ensure the message queue is empty before the test.
        self.game.current_room.messages.clear()
        
        self.game.take_item("")
        messages = self.game.current_room.get_messages()
        # Check that the expected error message was added.
        self.assertIn("Take what?", messages)
    
    def test_show_inventory_command_changes_state(self) -> None:
        """
        Tests that the show_inventory command correctly changes the
        room's interaction state to 'inventory'.
        """
        self.game.show_inventory("")
        self.assertEqual(
            self.game.current_room.current_interaction_state, 
            "inventory"
        )

if __name__ == '__main__':
    unittest.main()