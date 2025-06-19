"""
Manages the in-game time system for Colony 4B.

This module provides the ``ColonyTime`` class, which tracks the passage of
time in the game, measured in hours and days. A day in the colony is
defined as 20 hours.
"""

class ColonyTime:
    """
    Manages the in-game clock, tracking hours and days.

    A day in the colony is 20 hours long. This class handles time
    advancement and the rollover from one day to the next.

    Attributes:
        hours (float): The current hour of the day (from 0.0 to 19.9).
        days (int): The total number of full days that have passed.
    """
    def __init__(self) -> None:
        """
        Initializes the ColonyTime object.
        
        The game time starts at hour 0 on day 0.
        """
        self.hours = 0.0
        self.days = 0

    def advance_time(self, hours: float = 0.25) -> bool:
        """
        Advances the game time by a specified number of hours.

        If the total hours exceed the 20-hour day length, the time wraps
        around to the next day, and the day counter is incremented.

        :param hours: The number of hours to advance. Must be a non-
                      negative float or integer. Defaults to 0.25.
        :return: ``True`` if a new day has started, ``False`` otherwise.
        :raises ValueError: If the provided ``hours`` value is negative or
                            not a number.
        """
        if not isinstance(hours, (int, float)):
            raise ValueError("Hours must be a number")
        if hours < 0:
            raise ValueError("Cannot advance time backwards")

        self.hours += hours
        
        # A day in the colony is 20 hours long.
        if self.hours >= 20.0:
            days_passed = int(self.hours // 20)
            self.hours %= 20.0
            self.days += days_passed
            return True  # A new day has begun.
            
        return False  # The current day continues.
