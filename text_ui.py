"""
Defines the text-based user interface for the Colony 4B game.

This module contains the ``TextUI`` class, which is exclusively responsible
for managing the presentation layer of the application. It handles all
input from and output to the terminal, acting as the bridge between
the player and the game's core logic.
"""
import os
import logging
from typing import List, Tuple, Optional, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from player import Player
    from time_system import ColonyTime
    from room import Room

class TextUI:
    """
    Handles all text-based input and output for the game.

    This class is responsible for clearing the screen, drawing the game
    interface (including room info, stats, and messages), displaying the
    map, and parsing raw command strings from the player. It is designed
    as a pure presentation layer, with no knowledge of game logic.

    Attributes:
        last_command (any): Stores the last command entered. Currently unused.
        main_width (int): The character width for the main content panel.
        stats_width (int): The character width for the side statistics panel.
    """
    def __init__(self) -> None:
        """
        Initializes the TextUI object.
        """
        self.last_command = None
        self.main_width = 70  # Width for main content
        self.stats_width = 28  # Width for stats display

    def clear_screen(self) -> None:
        """
        Clears the terminal screen.
        
        Uses 'cls' for Windows and 'clear' for other operating systems.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_room(self, room: 'Room', player: 'Player', time: 'ColonyTime') -> None:
        """
        Draws the main game interface on the screen.

        This method clears the screen and then prints a formatted layout
        containing the room description, available actions, messages, and a
        side panel with player and time stats.

        :param room: The current Room object the player is in.
        :param player: The active Player object.
        :param time: The game's ColonyTime object.
        """
        self.clear_screen()
        
        # Print top border
        print("=" * (self.main_width + self.stats_width + 2))
        
        # Prepare main content
        main_content = []
        
        # Add room description
        desc_lines = self.format_main_content(room.get_description())
        main_content.extend(desc_lines)
        
        # Add available actions
        actions = room.get_available_interactions()
        if actions:
            main_content.extend(["", "Available actions:"])
            for i, action in enumerate(actions, 1):
                main_content.append(f"{i}. {action}")
        
        # Add messages
        messages = room.get_messages()
        if messages:
            main_content.extend(["", "Messages:"])
            for msg in messages:
                wrapped_lines = self.format_main_content(msg)
                main_content.extend(wrapped_lines)
        
        # Create stats display
        stats = self.create_stats_box(player, time)
        
        # Print main content and stats side by side
        max_lines = max(len(main_content), len(stats))
        for i in range(max_lines):
            main_line = main_content[i] if i < len(main_content) else ""
            stats_line = stats[i] if i < len(stats) else ""
            # Pad main line to create consistent spacing
            main_line = f"{main_line:<{self.main_width}}"
            print(f"{main_line}  {stats_line}")
        
        # Print bottom border
        print("\n" + "=" * (self.main_width + self.stats_width + 2))

    def display_map(self, current_room_name: str) -> None:
        """
        Clears the screen and displays a visual map of the colony.

        The player's current location flashes for a few seconds to provide a
        clear visual indicator of their position.

        :param current_room_name: The name of the room the player is in.
        """
        map_layout = [
            "                                    +----------------------+",
            "                                    | Residential District |",
            "                                    +----------+-----------+",
            "                                               |            ",
            "+------------------------+     +---------------+------+     "
            "+-----------------+",
            "| Memorial Pond          |-----|  Central Plaza      |-----| "
            "Colony Market   |",
            "+------------------------+     +-------+--------------+     "
            "+-----------------+",
            "                                       |                    ",
            "                   +-------------------+-------------------+",
            "                   |                                       |",
            "         +---------+------------+                +---------+------------+",
            "         | Communications Tower |                | Sec. Checkpoint(Res) |",
            "         +----------------------+                +----------------------+",
            "                                                         |               ",
            "                                               +---------+------------+",
            "                                               | Sec. Checkpoint(Ind) |",
            "                                               +----------------------+",
            "                                                         |               ",
            "+------------------------+     +-------------------------+      "
            "+-----------------+",
            "| Deposit Station        |-----|    Industrial Plaza     |------| "
            "Refinery        |",
            "+------------------------+     +-------------------------+      "
            "+-----------------+",
            "                                             |                  ",
            "                                    +--------+---------+        ",
            "                                    |  Mine Entrance  |        ",
            "                                    +-----------------+        "
        ]

        # Coords are (line_idx, char_idx, length) for placing marker *under* room name
        room_name_locations = {
            "Your Quarters":                (2, 36, 22), # Line below Res District
            "Residential Corridor":         (2, 36, 22),
            "Residential Entrance":         (2, 36, 22),
            "Central Plaza":                (7, 36, 22),
            "Colony Market":                (7, 66, 17),
            "Memorial Pond":                (7, 0, 24),
            "Communications Tower Entrance": (13, 9, 22),
            "Security Checkpoint (Residential)": (13, 47, 22),
            "Security Checkpoint (Industrial)":  (17, 47, 22),
            "Industrial Plaza":             (21, 36, 25),
            "Refinery":                     (21, 68, 17),
            "Mine Entrance":                (25, 36, 17),
            "Deposit Station":              (21, 0, 24),
        }
        
        # Security gates are not distinct locations on the map, point to parent
        room_name_locations["Residential Checkpoint Gate"] = room_name_locations[
            "Security Checkpoint (Residential)"
        ]
        room_name_locations["Industrial Checkpoint Gate"] = room_name_locations[
            "Security Checkpoint (Industrial)"
        ]

        coords = room_name_locations.get(current_room_name)
        if not coords:
            # Fallback for rooms not on the map
            self.clear_screen()
            print("\nYou are in a location not marked on the map.")
            time.sleep(2)
            return

        line_idx, char_idx, length = coords

        # Blinking animation
        animation_duration = 3  # seconds
        start_time = time.time()
        blink_on = True
        while time.time() - start_time < animation_duration:
            self.clear_screen()
            
            # Create a mutable copy of the map layout
            temp_map_lines = list(map_layout)
            
            if blink_on:
                # Create the indicator line and insert it into the map
                indicator_text = "vvv YOU ARE HERE vvv".center(length)
                indicator_line = " " * char_idx + indicator_text
                temp_map_lines.insert(line_idx + 1, indicator_line)

            for line in temp_map_lines:
                print("".join(line))
            
            print("\n" + "Scanning location...".center(80))
            
            blink_on = not blink_on
            time.sleep(0.4)

        # Final static map display
        self.clear_screen()
        final_map_lines = list(map_layout)
        indicator_text = ">>> YOU ARE HERE <<<".center(length)
        indicator_line = " " * char_idx + indicator_text
        final_map_lines.insert(line_idx + 1, indicator_line)

        for line in final_map_lines:
            print("".join(line))
        
        input("\n" + "Post-scan map. Press Enter to close.".center(80))

    def get_command(self, room: 'Room') -> Tuple[Optional[str], Optional[str]]:
        """
        Gets and parses a command from the user.

        This method reads player input from the terminal and handles the
        logic for resolving numbered choices into full command strings. It
        then splits the command into a primary verb and a secondary argument.

        :param room: The current Room object, used to get the list of
                     available numbered interactions.
        :return: A tuple containing the command word and the rest of the
                 string, or (None, None) for empty or invalid input.
        """
        try:
            # Get all available interactions from the current room state.
            interactions = room.get_available_interactions()
            
            # Display the prompt. create_prompt is not defined, so building it here.
            prompt_lines = ["\nEnter command: "]
            prompt = "".join(prompt_lines)
            
            raw_input = input(prompt).strip()
            logging.info(f"Raw user input: '{raw_input}'")

            # If in the donating state, don't treat numbers as action choices.
            if room.current_interaction_state == "donating":
                if raw_input.lower() == "go back":
                    return "go", "back"
                elif raw_input.isdigit():
                    return raw_input, None # Return the number as the command word
                else:
                    # For any other text, parse as usual
                    parts = raw_input.upper().split()
                    command_word = parts[0]
                    second_word = " ".join(parts[1:]) if len(parts) > 1 else None
                    logging.info(
                        f"Parsed command: command_word='{command_word}', "
                        f"second_word='{second_word}'"
                    )
                    return command_word, second_word

            # Check if the input is a number.
            if raw_input.isdigit():
                try:
                    choice_index = int(raw_input) - 1
                    if 0 <= choice_index < len(interactions):
                        chosen_action = interactions[choice_index].lower()
                        logging.info(
                            f"User chose number {raw_input}, mapped to action: "
                            f"'{chosen_action}'"
                        )
                        
                        parts = chosen_action.split()
                        verb = parts[0]
                        # This logic handles multi-word actions from the numbered list
                        noun = " ".join(parts[1:]) if len(parts) > 1 else None
                        
                        # Return the parsed verb and noun from the resolved action
                        logging.info(
                            f"Parsed command from number: "
                            f"command_word='{verb.upper()}', second_word='{noun}'"
                        )
                        return verb.upper(), noun

                    else:
                        logging.warning(f"Invalid number choice: {raw_input}")
                        room.add_message(f"Invalid action number: {raw_input}")
                        return None, None # Invalid number

                except (ValueError, IndexError):
                    logging.warning(f"Error processing number choice: {raw_input}")
                    room.add_message(f"Invalid command: {raw_input}")
                    return None, None
            
            # If not a number, parse as a text command.
            else:
                if not raw_input:
                    return None, None
                parts = raw_input.upper().split()
                command_word = parts[0]
                second_word = " ".join(parts[1:]) if len(parts) > 1 else None
                logging.info(
                    f"Parsed command: command_word='{command_word}', "
                    f"second_word='{second_word}'"
                )
                return command_word, second_word
            
            logging.info(
                f"Final Parsed command: command_word='{command_word}', "
                f"second_word='{second_word}'"
            )
            return command_word, second_word

        except Exception as e:
            logging.error(f"Error processing input: {e}", exc_info=True) 
            print("An error occurred processing your input. Please try again.") 
            return None, None

    def create_stats_box(self, player: 'Player', time: 'ColonyTime') -> List[str]:
        """
        Creates a formatted list of strings for the stats display box.

        This box shows key information like game time, player currency,
        quota progress, and a high-level tracker for quest completion.

        :param player: The active Player object.
        :param time: The game's ColonyTime object.
        :return: A list of strings that form the visual stats box.
        """
        width = self.stats_width
        box = [
            "+" + "-" * (width - 2) + "+",
            "|" + "STATS".center(width - 2) + "|",
            "+" + "-" * (width - 2) + "+",
            f"| Time: {time.hours:02.1f}:00".ljust(width - 1) + "|",
            f"| Day: {time.days}".ljust(width - 1) + "|",
            f"| Minshin: {player.minshin}".ljust(width - 1) + "|",
            f"| Quota: {player.quota_fulfilled}/{player.ambrosium_quota}".ljust(width - 1) + "|",
            "+" + "-" * (width - 2) + "+",
        ]
        
        quests = [
            player.cecil_quest_complete,
            player.creedal_quest_complete,
            player.ephsus_quest_complete,
            player.long_quest_complete,
            player.weatherbee_quest_complete
        ]
        progress_str = " ".join(["[✓]" if q else "[ ]" for q in quests])
        box.append("|" + progress_str.center(width - 2) + "|")

        box.append("+" + "-" * (width - 2) + "+")
        box.append("")  # Empty line for spacing
        box.append("Type 'help' for commands".center(width))
        return box

    def format_main_content(self, content: str) -> List[str]:
        """
        Formats and wraps a string to fit within the main content panel.

        This method correctly handles multi-line strings and preserves the
        formatting of any text that appears to be pre-formatted (e.g.,
        ASCII art), while wrapping standard paragraphs to prevent them from
        breaking the UI layout.

        :param content: The string content to format.
        :return: A list of strings, where each string is a formatted line.
        """
        # If the content is a multi-line block that looks like ASCII art, don't wrap it.
        if '\n' in content and content.strip().startswith(
            ('+', '|', '/', '\\', '*')
        ):
            return content.split('\n')

        lines = []
        for line in content.split('\n'):
            if not line.strip():
                lines.append("")
                continue

            current_line = ""
            words = line.split()
            
            for word in words:
                if len(current_line) + len(word) + 1 <= self.main_width:
                    current_line += (word + " ")
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            
            if current_line:
                lines.append(current_line.strip())
            
        return lines if lines else [""]  # Return at least one empty line for empty content