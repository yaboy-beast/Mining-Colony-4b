# Colony 4B

## Overview

Colony 4B is a text-based adventure game where you take on the role of Marmoris Gold, a miner working in a corporate-owned colony. Your primary goal is to meet a strict mining quota while navigating the social and political environment of the underground facility.

## Requirements

- Python 3.7 or higher.
- The game uses only the Python standard library; no external packages are required for it to run.

## How to Play

This game is designed to be run from a command-line interface. You can use the built-in terminal in an IDE (like PyCharm or VS Code) or your operating system's standard terminal (e.g., Command Prompt, PowerShell, or Terminal).

1.  Navigate to the root directory where the game files are located.
2.  Execute the following command to start the game:

    ```bash
    python game.py
    ```

## Game Objective

The primary objective is to mine and deposit **20 Ambrosium crystals** at the Deposit Station before the quota deadline of **3 Thebian days**.

## Key Features

-   **Multiple Endings:** The outcome of the game changes based on your actions, choices, and success in completing side quests for other characters in the colony.

## Basic Commands

Player actions are performed by typing commands, which are not case-sensitive.
The game also frequently presents numbered options for specific interactions.
You can type the number to perform the corresponding action.

-   `go <location>`: Move to another location (e.g., `go central plaza`).
-   `take <item>`: Pick up an item (e.g., `take ID card`).
-   `drop <item>`: Drop an item from your inventory.
-   `inventory`: Check your inventory and item descriptions.
-   `open <container>`: Open a container like a cupboard.
-   `look at <object>`: Examine an object more closely (e.g., `look at bulletin board`).
-   `talk to <person>`: Speak with an NPC (e.g., `talk to Greyman Cecil`).
-   `read <item>`: Read an item like a plaque or a notice on a bulletin board.
-   `check <object>`: Interact with an object like a terminal.
-   `insert <item>`: Insert an item into a slot (e.g., `insert id card`).
-   `map`: Display the colony map with your current location.
-   `help`: Show a list of primary commands.
-   `quit`: Exit the game.

## File Structure

-   `game.py`: Main game engine, containing the game loop and command handling.
-   `game_interactions.py`: Handles all NPC quest logic and special interactions.
-   `game_ui_helpers.py`: Contains helper methods for animations and UI display.
-   `player.py`: Defines the `Player` class, which manages inventory, stats, and quest progress.
-   `room.py`: Contains the `Room` and `RoomFactory` classes for building the game world.
-   `items.py`: Defines all in-game `Item`s and the `ItemType` enumeration.
-   `text_ui.py`: Handles all text-based input and output.
-   `time_system.py`: Manages the in-game clock and day/night cycle.
-   `game_constants.py`: A collection of global constants for game balance (e.g., prices, quotas).
-   `game.log`: A log file for debugging purposes.
-   `README.md`: This file.
-   `tests/`: A directory containing unit tests for the game logic.

## Running Tests

The project includes a suite of unit tests. If the `tests/` directory is present, the tests can be run from the project's root directory with the following command:

```bash
python tests/run_all_tests.py
```

<details>
  <summary>Debug Commands (for testing)</summary>

  The game includes a debug mode for testing purposes. To activate it, type `debugmode`. Once active, the following commands are available:

  - `debug goto <room_name>`: Teleport to any room in the game.
  - `debug give <item_name>`: Add any item to your inventory.
  - `debug set <stat> <value>`: Change a player or game stat.
    - `time <hour>`: Sets the current hour.
    - `day <day>`: Sets the current day.
    - `minshin <amount>`: Sets your Minshin balance.
    - `quota <amount>`: Sets your quota fulfilled count.

  To disable debug mode, type `debugmode` again.
</details> 