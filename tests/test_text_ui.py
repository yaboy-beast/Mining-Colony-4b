"""
Unit tests for the text-based UI in Colony 4B.

This test suite focuses on the ``TextUI`` class from the ``text_ui``
module. Due to the difficulty of testing terminal output directly, these
tests primarily verify the correctness of data-driven UI components, such
as the stats box, to ensure they accurately reflect the current game state.
"""
import unittest
import sys
import os

# Add the parent directory to the sys.path to allow for package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from text_ui import TextUI
from player import Player
from time_system import ColonyTime
from room import Room

class TestTextUI(unittest.TestCase):
    """
    Test cases for the TextUI class.

    This suite primarily tests the generation of UI components, like the
    stats box, to ensure they correctly reflect the current game state.
    Direct testing of command parsing and screen drawing is omitted due to
    its complexity.
    """

    def setUp(self) -> None:
        """
        Set up instances needed for UI testing before each test.
        """
        self.ui = TextUI()
        self.player = Player("TestPlayer")
        self.time = ColonyTime()
        self.room = Room("Test Room", "A room for testing UI.")

    def test_create_stats_box_quest_tracker(self) -> None:
        """
        Tests that the quest tracker in the stats box displays correctly.
        
        This test checks the visual representation of quest progress at
        different stages of completion: no quests done, some quests done,
        and all quests done.
        """
        # Case 1: No quests complete.
        # The expected string shows 5 empty brackets.
        stats_box = self.ui.create_stats_box(self.player, self.time)
        progress_line = next(
            (line for line in stats_box if "[ ]" in line or "[✓]" in line), None
        )
        self.assertIn("[ ] [ ] [ ] [ ] [ ]", progress_line)

        # Case 2: Some quests complete.
        self.player.cecil_quest_complete = True
        self.player.ephsus_quest_complete = True
        self.player.weatherbee_quest_complete = True
        stats_box = self.ui.create_stats_box(self.player, self.time)
        progress_line = next(
            (line for line in stats_box if "[ ]" in line or "[✓]" in line), None
        )
        # Player quest flags are checked in a specific order in the UI method.
        # This test verifies that the checkmarks appear in the correct slots.
        # Order: cecil, creedal, ephsus, long, weatherbee
        self.assertIn("[✓] [ ] [✓] [ ] [✓]", progress_line)

        # Case 3: All quests complete.
        self.player.creedal_quest_complete = True
        self.player.long_quest_complete = True
        stats_box = self.ui.create_stats_box(self.player, self.time)
        progress_line = next(
            (line for line in stats_box if "[ ]" in line or "[✓]" in line), None
        )
        self.assertIn("[✓] [✓] [✓] [✓] [✓]", progress_line)


if __name__ == '__main__':
    unittest.main() 
