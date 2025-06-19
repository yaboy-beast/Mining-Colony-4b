"""
Unit tests for the time system in Colony 4B.

This test suite verifies the functionality of the ``ColonyTime`` class
from the ``time_system`` module. It ensures that time is initialized
correctly, advances as expected, and that the 20-hour day cycle logic
is handled properly.
"""
import unittest
import sys
import os

# Add the parent directory to the sys.path to allow for package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from time_system import ColonyTime

class TestTimeSystem(unittest.TestCase):
    """
    Test cases for the ColonyTime class.
    
    This suite tests the time system's initialization, advancement,
    and day progression logic, ensuring all calculations are correct.
    """

    def setUp(self) -> None:
        """
        Set up a new ColonyTime instance before each test.
        """
        self.time = ColonyTime()

    def test_time_initialization(self) -> None:
        """
        Tests that time is initialized to hour 0 and day 0.
        """
        self.assertEqual(self.time.hours, 0)
        self.assertEqual(self.time.days, 0)

    def test_advance_time_default(self) -> None:
        """
        Tests the default time advancement of 0.25 hours.
        """
        self.time.advance_time()
        self.assertEqual(self.time.hours, 0.25)
        self.assertEqual(self.time.days, 0)
    
    def test_advance_time_custom(self) -> None:
        """
        Tests a custom time advancement that does not change the day.
        
        Also verifies that the method returns False when a new day does not
        occur.
        """
        self.time.hours = 5
        returned_val = self.time.advance_time(10)
        self.assertEqual(self.time.hours, 15)
        self.assertEqual(self.time.days, 0)
        self.assertFalse(returned_val)

    def test_advance_time_new_day(self) -> None:
        """
        Tests that advancing time past 20 hours starts a new day.
        
        Also verifies that the method returns True when a new day occurs.
        """
        self.time.hours = 19
        returned_val = self.time.advance_time(2)
        # Expected: 19 + 2 = 21. Rollover: 21 % 20 = 1. Day increments.
        self.assertEqual(self.time.hours, 1)
        self.assertEqual(self.time.days, 1)
        self.assertTrue(returned_val)

    def test_advance_time_exactly_one_day(self) -> None:
        """
        Tests that advancing time by exactly 20 hours starts a new day
        and keeps the hour the same.
        """
        self.time.hours = 5
        self.time.advance_time(20)
        # Expected: 5 + 20 = 25. Rollover: 25 % 20 = 5. Day increments.
        self.assertEqual(self.time.hours, 5)
        self.assertEqual(self.time.days, 1)

    def test_advance_time_multiple_days(self) -> None:
        """
        Tests that advancing time by multiple days' worth of hours is
        calculated correctly.
        """
        self.time.hours = 10
        # Advance by 45 hours (2 days and 5 hours).
        self.time.advance_time(45)
        # Expected: 10 + 45 = 55. Rollover: 55 % 20 = 15.
        # Days passed: 55 // 20 = 2.
        self.assertEqual(self.time.hours, 15)
        self.assertEqual(self.time.days, 2)

    def test_advance_time_zero(self) -> None:
        """
        Tests that advancing time by zero hours makes no changes.
        """
        original_hours = self.time.hours
        result = self.time.advance_time(0)
        self.assertEqual(self.time.hours, original_hours)
        self.assertFalse(result)

    def test_advance_time_negative_raises_error(self) -> None:
        """
        Tests that calling advance_time with a negative value raises a
        ValueError.
        """
        original_hours = self.time.hours
        with self.assertRaisesRegex(ValueError, "Cannot advance time backwards"):
            self.time.advance_time(-5)
        # Ensure time was not changed.
        self.assertEqual(self.time.hours, original_hours)

if __name__ == '__main__':
    unittest.main() 