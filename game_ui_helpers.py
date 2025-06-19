"""
Defines UI helper methods for the Colony 4B game.

This module provides the ``GameUIHelpers`` mixin class, which contains
a collection of utility methods for creating terminal-based animations
and formatted display elements. These helpers are used to enhance the
player's experience with dynamic and visually appealing feedback.
"""
import time
import sys
import textwrap
import shutil
from typing import List, Tuple, Optional
from game_constants import MINSHIN_PER_AMBROSIUM_POST_QUOTA

class GameUIHelpers:
    """
    A mixin class containing helper methods for UI display.

    This class is intended to be inherited by the main ``Game`` class to
    provide a separation of concerns, keeping UI-specific presentation
    logic apart from the core game logic.
    """

    def _run_animation(
        self,
        steps: List[Tuple[str, float]],
        padding: int,
        clear_screen: bool = False,
        final_pause: float = 0.0,
        end_message: Optional[str] = None
    ) -> None:
        """
        Displays a generic, multi-step animation with a spinner.

        This is a versatile base function for creating terminal animations.
        Each step consists of a message and a duration.

        :param steps: A list of tuples, where each tuple contains a
                      message (str) and a duration (float).
        :param padding: The character padding to apply for alignment.
        :param clear_screen: If True, the screen will be cleared before
                             the animation starts.
        :param final_pause: An optional pause duration after the
                            animation completes.
        :param end_message: An optional message to display after the
                            animation finishes.
        """
        if clear_screen:
            self.ui.clear_screen()

        animation_chars = ['|', '/', '-', '\\']
        print()

        for message, duration in steps:
            start_time = time.time()
            while time.time() - start_time < duration:
                for char in animation_chars:
                    padded_message = message.ljust(padding)
                    sys.stdout.write(f"\r{padded_message} [{char}]")
                    sys.stdout.flush()
                    time.sleep(0.1)
                    if time.time() - start_time > duration:
                        break
            sys.stdout.write(f"\r{message.ljust(padding)} [✓]\n")
            time.sleep(0.5)

        if end_message:
            print(end_message)

        if final_pause > 0:
            sys.stdout.flush()
            time.sleep(final_pause)

    def _run_travel_animation(self, steps: List[Tuple[str, float]]) -> None:
        """
        Displays a standardized travel animation.
        
        :param steps: A list of (message, duration) tuples for the
                      animation.
        """
        self._run_animation(steps, padding=50, clear_screen=True, final_pause=1.0)

    def _run_fireworks_animation(self) -> None:
        """
        Displays a simple ASCII firework animation in the terminal.
        """
        self.ui.clear_screen()
        width = shutil.get_terminal_size().columns
        
        firework_frames = [
            (r"      .      ", r"     ,O,     "),
            (r"      *      ", r"   \ `O` /   "),
            (r"    \ | /    ", r"   -- * --   "),
            (r"    . | .    ", r"   .  *  .   ")
        ]

        start_time = time.time()
        frame_index = 0
        while time.time() - start_time < 3:
            self.ui.clear_screen()
            fw_top, fw_bottom = firework_frames[frame_index % len(firework_frames)]
            pad = " " * ((width - len(fw_top)) // 2)
            
            print("\n\n\n\n\n")
            print(pad + fw_top)
            print(pad + fw_bottom)
            
            time.sleep(0.2)
            frame_index += 1
        
        self.ui.clear_screen()

    def _run_terminal_animation(self, steps: List[Tuple[str, float]]) -> None:
        """
        Runs a terminal-style animation, ideal for processing messages.
        
        :param steps: A list of (message, duration) tuples.
        """
        self._run_animation(steps, padding=70)

    def _run_deposit_terminal_animation(
        self, animation_steps: List[Tuple[str, float]]
    ) -> None:
        """
        Runs a deposit terminal animation with a standard ending message.
        
        :param animation_steps: A list of (message, duration) tuples for
                                the animation.
        """
        self.suppress_next_room_display = True
        end_msg = "Thank you for your service - Olympus Resources\n" + ("-" * 30)
        self._run_animation(animation_steps, padding=70, end_message=end_msg)

    def _display_dramatic_discovery(
        self, line1: str, line2: str, char_delay: float = 0.1,
        pause_duration: float = 4.0
    ) -> None:
        """
        Displays a two-part message dramatically in the center of the screen.

        Each character is printed sequentially to create a "typing" effect,
        enhancing the dramatic impact of the message.

        :param line1: The first line of the message.
        :param line2: The second line of the message.
        :param char_delay: The delay between each character print.
        :param pause_duration: The pause after the message is fully displayed.
        """
        self.ui.clear_screen()
        width, height = shutil.get_terminal_size()
        v_padding = (height // 2) - 1
        print("\n" * v_padding)

        # Print the first line character by character.
        h_padding1 = " " * ((width - len(line1)) // 2)
        sys.stdout.write(h_padding1)
        for char in line1:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(char_delay)
        
        print()

        # Print the second line character by character.
        h_padding2 = " " * ((width - len(line2)) // 2)
        sys.stdout.write(h_padding2)
        for char in line2:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(char_delay)

        time.sleep(pause_duration)

    def _display_ending_text(
        self, paragraphs: List[str], final_message: str
    ) -> None:
        """
        Handles the paragraph-by-paragraph display for an ending sequence.

        This function displays long-form text one paragraph at a time,
        requiring the user to press Enter to continue. This is used for
        all game endings.

        :param paragraphs: A list of strings, where each is a paragraph.
        :param final_message: The final message to display (e.g., "GAME OVER").
        """
        self.ui.clear_screen()
        width = shutil.get_terminal_size().columns

        for i, paragraph in enumerate(paragraphs):
            # Handle empty strings used for spacing.
            if not paragraph.strip():
                print()
                continue

            wrapped_lines = textwrap.fill(paragraph, width)
            print(wrapped_lines)
            print()

            # Prompt for user input to continue, except after the last paragraph.
            if i < len(paragraphs) - 1:
                prompt = "Press enter to continue..."
                print(prompt.center(width))
                input()
                # Use ANSI escape codes to move cursor up and clear lines.
                sys.stdout.write("\033[F\033[K")  # Move up one line and clear it.
                sys.stdout.write("\033[F\033[K")  # Move up again for the blank line.
                print()

        print("\n" * 2)
        print(final_message.center(width))
        print("\n" * 2)
        input("Press enter to exit.".center(width))
        sys.exit()

    def display_quota_celebration(self) -> None:
        """
        Displays a celebratory message when the player meets their quota.
        """
        self._run_fireworks_animation()
        width = shutil.get_terminal_size().columns
        
        base_lines = [
            "|----------------------------------------------------|",
            "|                                                    |",
            "|               QUOTA OBLIGATION FULFILLED           |",
            "|                                                    |",
            "|----------------------------------------------------|",
            "",
            ("Congratulations Miner, your quota for this cycle has been met. "
             "Your service to Olympus Resources is noted and appreciated."),
            (f"As a reward, any further Ambrosium deposited this cycle will "
             f"yield a bonus of {MINSHIN_PER_AMBROSIUM_POST_QUOTA} Minshin "
             "per crystal."),
            ("You may continue to contribute to the company's prosperity "
             "until the next cycle."),
            ""
        ]
        
        print("\n\n")
        for line in base_lines:
            # Wrap long lines while keeping the box centered.
            if len(line) > 54: # Width of the box content area
                 wrapped = textwrap.fill(line, width=width-4)
                 for sub_line in wrapped.split('\n'):
                     print(sub_line.center(width))
            else:
                print(line.center(width))

        input("\n" + "Press Enter to continue...".center(width))
        
        self.current_room.add_message(
            "A confirmation chime echoes from the deposit station. You have "
            "met your quota for this cycle."
        )

    def _display_appreciation_animation(
        self, npc_name: str, message: str
    ) -> None:
        """
        A base method to display a standardized quest completion screen.

        This combines the fireworks animation with a formatted message box
        to provide rewarding feedback to the player.

        :param npc_name: The name of the NPC showing appreciation.
        :param message: The message from the NPC.
        """
        self._run_fireworks_animation()
        width = shutil.get_terminal_size().columns
        box_width = 52 # Fixed width for the box
        
        lines = [
            f"+{'='*box_width}+",
            f"|{' ' * box_width}|",
            f"|{'You gained appreciation from:'.center(box_width)}|",
            f"|{npc_name.center(box_width)}|",
            f"|{' ' * box_width}|",
            f"+{'='*box_width}+",
        ]
        
        print("\n\n")
        # Center the entire box.
        box_padding = " " * ((width - box_width - 2) // 2)
        for line in lines:
            print(box_padding + line)
        print()

        # Wrap and center the message below the box.
        wrapped_message = textwrap.fill(message, width=width-4)
        for msg_line in wrapped_message.split('\n'):
            print(msg_line.center(width))
            
        time.sleep(2)
        input("\n" + "Press Enter to continue...".center(width))