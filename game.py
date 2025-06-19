"""
Main game class and entry point for the Colony 4B adventure game.

This module contains the ``Game`` class, which serves as the central engine
for the entire application. It orchestrates the game loop, manages the
player's state, handles command parsing and delegation, and ties together
all other components, including the UI, rooms, items, and time system.
The main game execution starts from the ``main()`` function at the end
of this file.
"""
from room import Room, RoomFactory, InteractionState
from text_ui import TextUI
from time_system import ColonyTime
from player import Player
from items import ItemType, ITEMS
import random
import time
import sys
import logging
from typing import Optional, List, Tuple
import textwrap
import shutil
from game_constants import *
from game_interactions import GameInteractions
from game_ui_helpers import GameUIHelpers

# Setup logging
logging.basicConfig(
    filename='game.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Game(GameInteractions, GameUIHelpers):
    """
    The main class for the Colony 4B game, orchestrating all game components.

    This class initializes the game world, including the player, rooms, and
    time system. It contains the main game loop, which continuously prompts
    the player for input, processes commands, and updates the game state.
    It inherits functionality from two mixin classes:
    - ``GameInteractions``: Handles the logic for all specific NPC quests
      and special location-based interactions.
    - ``GameUIHelpers``: Provides methods for displaying animations and
      other complex UI elements, separating presentation from core logic.

    Attributes:
        ui (TextUI): The text-based user interface for handling input and output.
        player (Player): The player character object.
        time (ColonyTime): The in-game time system.
        current_room (Room): The room the player is currently in.
        mining_attempts (int): A counter for how many times the player has mined,
                               used for triggering special events.
        total_donations (int): The total amount of Minshin donated by the player.
        intended_destination (Optional[str]): Used for multi-step travel.
        debug_mode (bool): A flag to enable or disable debug commands.
        suppress_next_room_display (bool): A flag to prevent the room description
                                           from being displayed on the next loop
                                           iteration, useful after animations.
        room_map (Dict[str, Room]): A mapping of room names to Room objects,
                                    used for fast lookups (e.g., for debug commands).
        command_handlers (Dict[str, function]): A dictionary mapping primary
                                                command words (like "GO", "TAKE")
                                                to their handler methods.
        _full_phrase_command_handlers (Dict[str, function]): A dictionary for
            handling exact multi-word commands.
        _prefix_command_handlers (Dict[str, function]): A dictionary for handling
            commands that start with a specific phrase but may have variable
            endings (e.g., buying items with prices).
    """
    def __init__(self) -> None:
        """
        Initializes the Game object.

        Sets up the UI, player, time system, creates all game rooms and their
        connections, and initializes game state variables.
        """
        logging.info("Starting new game")
        self.ui = TextUI()
        self.player = Player("Marmoris")
        self.time = ColonyTime()
        self.create_rooms()
        self.current_room = self.player_home
        self.mining_attempts = 0
        self.total_donations = 0
        self.intended_destination: Optional[str] = None
        self.debug_mode = False
        self.suppress_next_room_display = False
        
        # Build room map for debug goto
        self.room_map = {
            room.name.lower(): room for room in [
                self.player_home, self.residential_corridor,
                self.residential_entrance, self.central_plaza, self.colony_market,
                self.memorial_pond, self.security_checkpoint_residential,
                self.security_checkpoint_industrial,
                self.security_checkpoint_residential_gate,
                self.security_checkpoint_industrial_gate, self.industrial_plaza,
                self.refinery, self.mine_entrance, self.deposit_station,
                self.communications_tower_entrance
            ]
        }
        
        self.command_handlers = {
            "QUIT": self.quit_game,
            "HELP": self.print_help,
            "MAP": self.show_map,
            "GO": self.do_go_command,
            "TAKE": self.take_item,
            "DROP": self.drop_item,
            "INVENTORY": self.show_inventory,
            "OPEN": self.open_container,
            "LOOK": self.look_at,
            "TALK": self.talk_to,
            "INSERT": self.insert_item,
            "INVESTIGATE": self.investigate,
            "CHECK": self.check_item,
            "READ": self.read,
            "DONATE": self.donate,
            "DEBUG": self.handle_debug_command
        }

        self._full_phrase_command_handlers = {
            "MINE AWAY": self._handle_mine_away,
            "DONATE MINSHIN INTO DONATION TERMINAL": self._handle_donate_minshin,
            "DEPOSIT RESOURCES": self._handle_deposit_resources,
            "DEPOSIT NON-AMBROSIUM MATERIALS": self._handle_deposit_non_ambrosium_materials,
            "CHECK WEEKLY QUOTA": self._handle_check_weekly_quota,
            "CHECK NEWS": self._handle_check_news,
            "PERSONAL INFORMATION": self._handle_personal_information,
            "WHO IS THIS MAN AND WHY IS COVERED IN GREY DUST": self._handle_ask_about_cecil,
            'SAY "YOU ALRIGHT CECIL"': self._handle_ask_cecil_alright,
            "ARE YOU SURE YOU ALRIGHT?": self._handle_ask_cecil_sure_alright,
            "OFFER LUCKY COIN": self._handle_cecil_coin_quest,
            "ASK ABOUT THEBIAN GROUND SOIL": self._handle_ask_ephsus_ground_soil,
            "ASK WHY LOOKS LIKE SHE'S CONTEMPLATING": self._handle_ask_ephsus_contemplating,
            "OFFER THEBIAN GROUND SOIL": self._handle_ephsus_soil_quest,
            "ASK ABOUT THE INDUSTRIAL SECTOR": self._handle_ask_creedal_industrial,
            "ASK ABOUT THE RESIDENTIAL SECTOR": self._handle_ask_weatherbee_residential,
            "TALK TO COLONY FOREMAN LONG": self._handle_talk_foreman_long,
            "GO BACK": self._handle_go_back,
            "LEAVE": self._handle_go_back,
            "STEP AWAY": self._handle_go_back,
            "STEP AWAY FROM BULLETIN BOARD": self._handle_go_back,
            "GO BACK TO PLAZA": self._handle_go_back,
            "REMOVE ID CARD AND GO BACK": self._handle_go_back,
            "DEBUGMODE": self._handle_debug_mode,
            "VISIT HINTER'S PROPHECIES": self._handle_visit_hinter,
            ("WHAT SHOULD I PAY MY ATTENTION TO? "
             "(50 MINSHIN)"): self._handle_hinter_prophecy_request,
            "APPROACH MERCHANT ARMEDAS STALL": self._handle_approach_armedas_stall,
            "ASK WHY CREEDAL IS DROOLING": self._handle_ask_why_creedal_is_drooling,
            "STAY STRONG CREED": self._handle_stay_strong_creed,
            "OFFER STEAMED BUNS": self._handle_creedal_food_quest,
            "CONGRATULATIONS ON YOUR NEW JOB": self._handle_congratulations_on_new_job,
            "HOWS YOUR SPIRITS NOW WEATHERBEE": self._handle_hows_your_spirits_now_weatherbee,
            "GIVE WEATHERBEE A HIGH FIVE": self._handle_weatherbee_spirits_quest,
            "APPROACH TERMINAL": self._handle_approach_comms_tower_terminal,
            "INSERT ID CARD": self._handle_insert_id_card_comms_tower,
            "INSERT COMMUNICATIONS TOWER ID CARD": self._handle_insert_comms_tower_id_card,
            "APPROACH BLACKEST OF MARKETS STALL": self._handle_approach_blackest_market,
            (f"BUY COMMUNICATIONS TOWER ID CARD ({BLACK_MARKET_ID_PRICE} "
             "MINSHIN)"): self._handle_buy_comms_tower_card,
            "VIEW 'HOW TO MINE' HANDBOOK": self._handle_view_how_to_mine_handbook,
            ("VIEW 'REFINERY FOR DUMMIES' "
             "HANDBOOK"): self._handle_view_refinery_for_dummies_handbook,
            "VIEW 'DEPOSITING 101' HANDBOOK": self._handle_view_depositing_101_handbook,
        }

        self._prefix_command_handlers = {
            f"BUY OLYMPUS XL BACKPACK ({BACKPACK_PRICE} MINSHIN)": self._handle_buy_backpack,
            f"BUY STEAMED BUNS ({STEAMED_BUNS_PRICE} MINSHIN)": self._handle_buy_buns,
            (f"BUY HEAVY BEAM MINING GUN UPGRADE ({MINING_UPGRADE_PRICE} "
             "MINSHIN)"): self._handle_buy_gun,
        }

    def create_rooms(self) -> None:
        """
        Creates all Room objects and establishes their exits.
        """
        # Create all rooms
        self.player_home = RoomFactory.create_player_home()
        self.residential_corridor = RoomFactory.create_residential_corridor()
        self.residential_entrance = RoomFactory.create_residential_entrance()
        self.central_plaza = RoomFactory.create_central_plaza()
        self.colony_market = RoomFactory.create_market()
        self.memorial_pond = RoomFactory.create_memorial_pond()
        self.security_checkpoint_residential = RoomFactory.create_security_checkpoint_residential()
        self.security_checkpoint_industrial = RoomFactory.create_security_checkpoint_industrial()
        self.security_checkpoint_residential_gate = RoomFactory.create_security_checkpoint_residential_gate()
        self.security_checkpoint_industrial_gate = RoomFactory.create_security_checkpoint_industrial_gate()
        
        self.industrial_plaza = RoomFactory.create_industrial_plaza()
        self.refinery = RoomFactory.create_refinery() 
        
        self.mine_entrance = RoomFactory.create_mine_entrance()
        self.deposit_station = RoomFactory.create_deposit_station()
        self.communications_tower_entrance = RoomFactory.create_communications_tower_entrance()
        
        # Connect rooms
        self.player_home.add_exit("residential corridor", self.residential_corridor)
        self.residential_corridor.add_exit("your quarters", self.player_home)
        self.residential_corridor.add_exit("residential entrance", self.residential_entrance)
        self.residential_entrance.add_exit("residential corridor", self.residential_corridor)
        self.residential_entrance.add_exit("central plaza", self.central_plaza)
        
        self.central_plaza.add_exit("residential district", self.residential_entrance)
        self.central_plaza.add_exit("colony market", self.colony_market)
        self.central_plaza.add_exit("memorial pond", self.memorial_pond)
        self.central_plaza.add_exit("security checkpoint", self.security_checkpoint_residential)
        self.central_plaza.add_exit("communications tower", self.communications_tower_entrance)
        
        self.communications_tower_entrance.add_exit("central plaza", self.central_plaza)
        self.colony_market.add_exit("central plaza", self.central_plaza)
        self.memorial_pond.add_exit("central plaza", self.central_plaza)
        
        self.security_checkpoint_residential.add_exit("central plaza", self.central_plaza)
        self.security_checkpoint_residential_gate.add_exit("industrial plaza", self.industrial_plaza)
        
        self.security_checkpoint_industrial.add_exit("industrial plaza", self.industrial_plaza)
        self.security_checkpoint_industrial_gate.add_exit("central plaza", self.central_plaza)
        
        self.industrial_plaza.add_exit("security checkpoint", self.security_checkpoint_industrial)
        self.industrial_plaza.add_exit("refinery", self.refinery)
        self.industrial_plaza.add_exit("mine entrance", self.mine_entrance)
        self.industrial_plaza.add_exit("deposit station", self.deposit_station)
        
        self.refinery.add_exit("industrial plaza", self.industrial_plaza)
        self.mine_entrance.add_exit("industrial plaza", self.industrial_plaza)
        self.deposit_station.add_exit("industrial plaza", self.industrial_plaza)

    def play(self) -> None:
        """
        Starts and manages the main game loop.
        """
        self.ui.display_room(self.current_room, self.player, self.time)

        finished = False
        while not finished:
            command_word, second_word = self.ui.get_command(self.current_room)

            if command_word is None and second_word is None:
                 logging.info("Received None command, possibly empty input or invalid number. Redisplaying room.")
                 self.ui.display_room(self.current_room, self.player, self.time)
                 continue 

            try:
                logging.info(f"Passing to handle_action: command_word='{command_word}', second_word='{second_word}'")
                finished = self.handle_action(command_word, second_word)
            except Exception as e:
                 logging.error(f"Error during handle_action: {e}", exc_info=True)
                 self.current_room.add_message(f"An unexpected error occurred: {str(e)}")

            if not finished:
                if self.time.days >= QUOTA_PERIOD_DAYS:
                    if self.player.all_quests_complete():
                        self.display_good_ending()
                    elif self.player.quota_fulfilled < self.player.ambrosium_quota:
                        self.display_deportation_ending()
                    else:
                        self.display_average_worker_ending()
                    finished = True

                if self.suppress_next_room_display:
                    self.suppress_next_room_display = False
                else:
                    self.ui.display_room(self.current_room, self.player, self.time)

    def display_intro(self) -> None:
        """
        Displays the game's introduction sequence.
        """
        self.ui.clear_screen()
        width = shutil.get_terminal_size().columns
        
        intro_lines = [
            ("INITIALIZING COLONY DATABASE...", 0.05, 1),
            ("ACCESS GRANTED", 0.05, 1),
            ("LOADING PERSONNEL FILE...", 0.05, 2),
            ("", 0, 0.5),
            ("+------------------------------------+", 0.02, 0.1),
            ("|  [OLYMPUS RESOURCES CONFIDENTIAL]  |", 0.02, 0.1),
            ("+------------------------------------+", 0.02, 0.5),
            ("[TERMINAL ACCESS: COLONY 4B]", 0.03, 1),
            ("[DATE: THEBIAN YEAR 97 POST-ESTABLISHMENT]", 0.03, 1.5),
            ("", 0, 0.5),
            ("ACCESSING COLONY HISTORY...", 0.05, 1),
            ("", 0, 0.2),
            ("+---------------------------+", 0.02, 0.1),
            ("|  RELEVANT COLONY HISTORY  |", 0.02, 0.1),
            ("+---------------------------+", 0.02, 1),
            ("The surface of Thebes is a wasteland, battered year-round by "
             "relentless, choking dust storms that make life above ground "
             "impossible. But beneath its hostile exterior, deep mineral scans "
             "revealed enormous underground deposits, most importantly, Ambrosium, "
             "the critical element behind Olympus Resources' flagship product: the "
             "\"Olympians,\" a line of artificial humans that revolutionise industry", 0, 0.1),
            ("After a brutal corporate bidding war, Olympus Resources won the "
             "extraction rights and dispatched teams of miners to establish fully "
             "underground colonies, each built to survive in isolation with their "
             "own oxygen generation systems and internal currency, the Minshin. "
             "Life in these colonies is strictly controlled; the only link to the "
             "outside world is a heavily guarded communications tower, operated "
             "exclusively by Olympus Resources' senior staff. When Mining Colony "
             "4A suffered a catastrophic collapse, Olympus sent in a replacement "
             "team—founding Colony 4B.", 0, 1.5),
            ("", 0, 0.5),
            ("+------------------+", 0.02, 0.1),
            ("|  CURRENT STATUS  |", 0.02, 0.1),
            ("+------------------+", 0.02, 1),
            ("Colony 4A: [TERMINATED - CATASTROPHIC STRUCTURAL FAILURE]", 0.03, 1),
            ("Colony 4B: [ACTIVE - CURRENT LOCATION]", 0.03, 2),
            ("", 0, 0.5),
            ("+------------------+", 0.02, 0.1),
            ("|  PERSONNEL FILE  |", 0.02, 0.1),
            ("+------------------+", 0.02, 1),
            ("NAME: MARMORIS GOLD", 0, 0.2),
            ("YEARS SERVED: 97", 0, 0.2),
            ("POSITION: AMBROSIUM MINER", 0, 0.2),
            ("STATUS: ACTIVE", 0, 1.5),
            ("", 0, 0.5),
            ("+---------------------------+", 0.02, 0.1),
            ("|  NOTICE TO ALL PERSONNEL  |", 0.02, 0.1),
            ("+---------------------------+", 0.02, 1),
            ("*****************************************", 0.02, 0.1),
            ("*  [!] MANDATORY QUOTA REMINDER [!]   *", 0.02, 0.1),
            ("*****************************************", 0.02, 1),
            ("", 0, 0.5),
            (f"Required Deposit: {WEEKLY_AMBROSIUM_QUOTA} Ambrosium crystals / "
             f"{QUOTA_PERIOD_DAYS} Thebian days", 0.02, 1),
            ("Failure to meet quota will result in immediate contract termination and "
             "deportation.", 0.02, 2),
            ("", 0, 0),
        ]

        for line, char_delay, line_pause in intro_lines:
            wrapped_lines = textwrap.wrap(line, width)
            for wrapped_line in wrapped_lines:
                padding = ""
                stripped_line = wrapped_line.strip()
                if stripped_line:
                    first_char = stripped_line[0]
                    if (first_char in ['+', '|', '*']):
                        padding = " " * ((width - len(wrapped_line)) // 2)

                sys.stdout.write(padding)
                for char in wrapped_line:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(char_delay)
                print() 
            time.sleep(line_pause)
        
        prompt = "Enter anything to continue..."
        for char in prompt:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.05)

        input()

    def handle_action(self, command_word: Optional[str], second_word: Optional[str]) -> bool:
        """
        Processes a single player action by dispatching to the correct handler.

        This method is the primary command router. It first checks for special
        game states (like 'donating'), then attempts to match the player's
        input against multi-word commands, and finally falls back to standard
        single-word commands.

        :param command_word: The first word of the player's command (the verb).
        :param second_word: The rest of the command string (the argument/noun).
        :return: ``True`` if the game should end (e.g., from a 'quit' command),
                 otherwise ``False``.
        """
        if command_word is None:
            logging.warning("handle_action received None command_word.")
            self.current_room.add_message("I don't understand that command.")
            return False

        # Handle the special 'donating' state separately.
        if self.current_room.current_interaction_state == "donating":
            # Allow some commands to bypass the donation logic
            if command_word.upper() in ["QUIT", "HELP", "MAP", "DEBUG", "INVENTORY"]:
                handler = self.command_handlers.get(command_word.upper())
                if handler:
                    argument = second_word.lower() if second_word else ""
                    result = handler(argument)
                    return result if result is not None else False
            
            # If not a bypass command, treat it as donation-related input.
            # We reconstruct the full input for handle_donation.
            full_input = command_word
            if second_word:
                full_input += " " + second_word
            return self.handle_donation(full_input)

        full_command_text = f"{command_word} {second_word}".upper() if second_word else command_word.upper()
        
        try:
            # 1. Check for full phrase and prefix commands first.
            # handle_full_phrase_commands returns True if a handler was found and executed.
            if self.handle_full_phrase_commands(full_command_text):
                return False  # A command was handled, so the game doesn't end.

            # 2. If not a full phrase, try standard single-word commands.
            action_key = command_word.upper()
            handler = self.command_handlers.get(action_key)
            if handler:
                argument = second_word.lower() if second_word else ""
                result = handler(argument)
                # The handler returns True if the game should end (e.g., quit).
                return result if result is not None else False

            # 3. If no handler was found for any command type.
            self.current_room.add_message(f"I don't understand '{full_command_text}'.")
            logging.warning(
                f"Unhandled action: '{full_command_text}' in state "
                f"'{self.current_room.current_interaction_state}'"
            )

        except Exception as e:
            logging.error(f"Error processing action {full_command_text}: {e}", exc_info=True)
            self.current_room.add_message(f"An error occurred trying to '{full_command_text}'.")

        return False

    def handle_full_phrase_commands(self, full_command_text: str) -> bool:
        """
        Checks for and executes handlers for exact multi-word commands.

        This method searches both the full-phrase and prefix-based command
        dictionaries for a matching handler.

        :param full_command_text: The complete, uppercased command from the player.
        :return: ``True`` if a handler was found and executed, otherwise ``False``.
        """
        handler = self._full_phrase_command_handlers.get(full_command_text)
        if handler:
            return handler()

        for prefix, prefix_handler in self._prefix_command_handlers.items():
            if full_command_text.startswith(prefix):
                return prefix_handler()

        return False

    def _handle_mine_away(self) -> bool:
        self.mine_away()
        return True

    def _handle_donate_minshin(self) -> bool:
        self.current_room.add_message(
            f"Donations Received: {self.total_donations}/"
            f"{FOREMAN_SPAWN_DONATION_THRESHOLD} Minshin."
        )
        self.current_room.add_message(
            f"Make a custom donation. (Minimum {MINIMUM_DONATION}, or 'go back')"
        )
        self.current_room.set_interaction_state("donating")
        return True

    def _handle_deposit_resources(self) -> bool:
        if self.current_room.name == "Deposit Station":
            self.current_room.add_message("You approach the deposit terminal. You'll need to use your ID card.")
            self.current_room.add_interaction_state("deposit_prompt", ["insert ID card", "go back"])
            self.current_room.set_interaction_state("deposit_prompt")
        else:
            self.current_room.add_message("You can only deposit Ambrosium at the Deposit Station.")
        return True

    def _handle_deposit_non_ambrosium_materials(self) -> bool:
        if self.current_room.name == "Refinery":
            self.current_room.add_message("You approach the refinery deposit hatch. You'll need to use your ID card.")
            self.current_room.add_interaction_state("refinery_prompt", ["insert ID card", "go back"])
            self.current_room.set_interaction_state("refinery_prompt")
        else:
            self.current_room.add_message("You can only deposit other materials at the Refinery.")
        return True

    def _handle_check_weekly_quota(self) -> bool:
        if self.current_room.current_interaction_state == "terminal":
            needed = max(0, self.player.ambrosium_quota - self.player.quota_fulfilled)
            days_left = max(0, QUOTA_PERIOD_DAYS - self.time.days)
            quota_msg = (
                f"Current Quota: {self.player.quota_fulfilled}/"
                f"{self.player.ambrosium_quota} Ambrosium Crystals. "
                f"Days passed: {self.time.days}. You need {needed} more in "
                f"{days_left} days."
            )
            self.current_room.add_message(quota_msg)
        else:
            self.current_room.add_message("You need to be at the terminal.")
        return True

    def _handle_check_news(self) -> bool:
        if self.current_room.current_interaction_state == "terminal":
            self.current_room.add_message(
                '''Terminal News Feed: "Olympus Resources stock up 5% after 
                successful Ambrosium extraction report from colonies 4B, 5C and 6A. 
                Annual bonus upped to potentially 100,000 Minshin."'''
            )
        else:
            self.current_room.add_message("You need to be at the terminal.")
        return True

    def _handle_personal_information(self) -> bool:
        if self.current_room.current_interaction_state == "terminal":
            self.current_room.set_interaction_state("personal_info")
            self.current_room.add_message(
                "Please insert your ID card to view personal information."
            )
        else:
            self.current_room.add_message("You need to be at the terminal.")
        return True

    def _handle_ask_about_cecil(self) -> bool:
        if self.current_room.current_interaction_state == "cecil_talk":
            self.current_room.add_message(
                'Cecil is a Clagnum Miner who extracts Clagnum suspended in grey dust using extractor guns.'
                'Unlike the putty form you have seen, this variant coats him entirely—hence the name "Greyman.".'
            )
            self.current_room.set_interaction_state("cecil_info")
        else:
            self.current_room.add_message("That doesn't make sense right now.")
        return True

    def _handle_ask_cecil_alright(self) -> bool:
        if self.current_room.current_interaction_state == "cecil_talk":
            self.current_room.add_message(
                "Cecil brandishes a weak smile, although the tear stains through "
                "the dirt encrusted on his face does not fool you. This is the "
                "worse job. Thank god you got the promotion to Ambrosium miner."
            )
            self.current_room.set_interaction_state("cecil_alright")
        else:
            self.current_room.add_message("That doesn't make sense right now.")
        return True

    def _handle_ask_cecil_sure_alright(self) -> bool:
        if self.current_room.current_interaction_state == "cecil_alright":
            self.current_room.add_message(
                "I know this sound stupid *sob* but I lost my lucky coin in the "
                "industrial sector. I have no clue where it is *sob*. Its my only "
                "reminder of home *much larger sob*"
            )
            self.current_room.set_interaction_state("cecil_quest_prompt")
            if self.player.has_item(ITEMS["lucky coin"]):
                self.current_room.interaction_states["cecil_quest_prompt"].interactions.insert(
                    0, "offer lucky coin"
                )
        else:
            self.current_room.add_message("That doesn't make sense right now.")
        return True

    def _handle_ask_ephsus_ground_soil(self) -> bool:
        if self.current_room.current_interaction_state == "ephsus_initial":
            self.current_room.add_message(
                "Thebian ground soil is packed with an extensive foundation. "
                "The soil has derived from the incredible pressures and tubidation "
                "by external weather conditions combined with whatever originated from "
                "Thebes's lqiuid metal core. Another science officer found dormant seeds "
                "waiting for the right conditions to sprout. There hasn't been sufficient water "
                "on Thebes for thousands of years! how exciting, maybe non human multicellular life "
                "can thrive?.."
            )
        else:
            self.current_room.add_message("That doesn't make sense right now.")
        return True

    def _handle_ask_ephsus_contemplating(self) -> bool:
        if self.current_room.current_interaction_state == "ephsus_initial":
            if not self.player.ephsus_quest_complete:
                self.current_room.add_message(
                    f"I've got to submit my Thebian ground soil audit in the next "
                    f"{QUOTA_PERIOD_DAYS} days but that blasted security officer "
                    f"wont let me through without my ID. *Ephsus shakes her head "
                    f"and looks down*. You couldn't get me samples could you? I "
                    f"need {SOIL_SAMPLES_REQUIRED} samples of ground soil"
                )
                self.current_room.set_interaction_state("ephsus_quest_prompt")
            else:
                self.current_room.add_message("Thanks to you, my audit is going smoothly!")
        else:
            self.current_room.add_message("That doesn't make sense right now.")
        return True

    def _handle_ask_creedal_industrial(self) -> bool:
        if self.current_room.current_interaction_state == "creedal_talk":
            self.current_room.add_message(
                "'Just the usual grind. Miners in, resources out. Don't cause any trouble.'"
            )
        else:
            self.current_room.add_message("That doesn't make sense right now.")
        return True

    def _handle_ask_weatherbee_residential(self) -> bool:
        if self.current_room.current_interaction_state == "weatherbee_talk":
            self.current_room.add_message(
                "'It's quiet. Too quiet. Just make sure you meet your quota.'"
            )
        else:
            self.current_room.add_message("That doesn't make sense right now.")
        return True

    def _handle_talk_foreman_long(self) -> bool:
        if self.current_room.name == "Memorial Pond" and not self.player.long_quest_complete:
            self.player.long_quest_complete = True
            logging.info("Player completed Long's quest.")
            try:
                npc_index = self.memorial_pond.npcs.index("Colony Foreman Long")
                self.memorial_pond.npcs[npc_index] = "Colony Foreman Long ✓"
            except ValueError:
                pass 
            
            self.display_foreman_appreciation()

            if self.player.all_quests_complete():
                self.display_good_ending()
            else:
                self.current_room.set_interaction_state("main")
        else:
            self.talk_to("colony foreman long")
        return True

    def _handle_go_back(self) -> bool:
        parent_state = self.current_room.get_parent_state()
        self.current_room.set_interaction_state(parent_state)
        self.current_room.add_message("You step back.")
        return True

    def _handle_debug_mode(self) -> bool:
        self.debug_mode = not self.debug_mode
        status = "ON" if self.debug_mode else "OFF"
        self.current_room.add_message(f"Debug mode is now {status}.")
        return True

    def _handle_visit_hinter(self) -> bool:
        self.visit_hinter()
        return True

    def _handle_hinter_prophecy_request(self) -> bool:
        self.handle_hinter_prophecy()
        return True

    def _handle_approach_armedas_stall(self) -> bool:
        self.handle_market_stall()
        return True

    def _handle_buy_backpack(self) -> bool:
        self.buy_market_item("backpack")
        return True

    def _handle_buy_buns(self) -> bool:
        self.buy_market_item("buns")
        return True

    def _handle_buy_gun(self) -> bool:
        self.buy_market_item("gun")
        return True

    def _handle_ask_why_creedal_is_drooling(self) -> bool:
        if self.current_room.current_interaction_state == "creedal_talk":
            self.current_room.add_message(
                '''"I'm just so hungry…"
    *Creedal slumps into himself and then sits upright violently when he realises he may be coming off as unprofessional*
    "Must stay on duty."
    *Creedal is clearly having an internal conflict*
    "Some steamed buns would be delicious about now…"'''
        )
        
            self.current_room.set_interaction_state("creedal_quest_prompt")
            if self.player.has_item(ITEMS["Steamed Buns"]):
                self.current_room.interaction_states[
                    "creedal_quest_prompt"
                ].interactions.insert(0, "offer steamed buns")
        else:
            self.current_room.add_message("That doesn't make sense right now.")
        return True

    def _handle_stay_strong_creed(self) -> bool:
        if self.current_room.current_interaction_state == "creedal_quest_prompt":
            self.current_room.add_message('He said "yeah"')
        else:
            self.current_room.add_message("That doesn't make sense right now.")
        return True

    def _handle_congratulations_on_new_job(self) -> bool:
        if (self.current_room.name == "Security Checkpoint (Industrial)" and
                self.player.weatherbee_quest_read_bulletin):
            if not self.player.weatherbee_quest_congratulated:
                self.current_room.add_message(
                    'Weatherbee became giddy with the congratulations. "Thank you, '
                    'thank you. The mines were too much for me. Truth is I enjoy '
                    'sitting all day. I have so much time to think about whats '
                    'outside, what I should do today, you get it. I would always '
                    'get so demoralised leaving the mines at 15:00. Hopefully my '
                    'spirits are good whilst im here!"'
                )
                self.player.weatherbee_quest_congratulated = True
            else:
                self.current_room.add_message('"Thank you again!" he says, beaming.')
        else:
            self.current_room.add_message("That doesn't make sense right now.")
        return True

    def _handle_hows_your_spirits_now_weatherbee(self) -> bool:
        if (self.current_room.name == "Security Checkpoint (Industrial)" and
                self.player.weatherbee_quest_congratulated and
                not self.player.weatherbee_quest_complete and
                FACILITY_CLOSE_HOUR <= self.time.hours < FACILITY_OPEN_HOUR):
            self.current_room.add_message(
                '"Not good. Some support would be good here. A crisp high five '
                'wouldn\'t go a miss."'
            )
            self.current_room.set_interaction_state("weatherbee_spirits_prompt")
        else:
                self.current_room.add_message("That doesn't make sense right now. Maybe ask him later?")
        return True

    def _handle_approach_comms_tower_terminal(self) -> bool:
        if self.current_room.name == "Communications Tower Entrance":
            self.current_room.set_interaction_state("approaching_terminal")
            interactions = ["insert ID card"]
            if self.player.has_item(ITEMS["Communications Tower ID Card"]):
                interactions.append("insert Communications Tower ID Card")
            interactions.append("go back")
            self.current_room.interaction_states["approaching_terminal"].interactions = interactions
            self.current_room.add_message(
                "The terminal's green text prompts you to enter your ID card"
            )
            return True
        return False

    def _handle_insert_id_card_comms_tower(self) -> bool:
        if self.current_room.name == "Communications Tower Entrance":
            if not self.player.has_item(ITEMS["ID card"]):
                self.current_room.add_message("You have no ID card to insert")
            else:
                self.current_room.add_message("The terminal blinked and displayed: 'Access Denied'.")
            return True
        return False

    def _handle_insert_comms_tower_id_card(self) -> bool:
        if self.current_room.name == "Communications Tower Entrance":
            if not self.player.has_item(ITEMS["Communications Tower ID Card"]):
                self.current_room.add_message("You have no Communications Tower ID Card to insert")
            else:
                self._run_terminal_animation([
                    ("Scanning card...", 1.0),
                    ("Scan Complete", 0.5),
                    ("Forgery Detected", 0.5),
                    ("Removing Card from Circulation", 1.0),
                    ("Have a great day.", 0.5)
                ])
                self.player.remove_from_inventory(ITEMS["Communications Tower ID Card"])
                self.current_room.set_interaction_state("main")
            return True
        return False

    def _handle_approach_blackest_market(self) -> bool:
        if self.player.bought_blackest_market_card:
            self.current_room.add_message("The dark alley where the stall once stood is empty.")
            return True
        if self.current_room.name == "Colony Market":
            if self.time.days >= 1:
                self.current_room.set_interaction_state("blackest_market")
                self.current_room.add_message("A shadowy figure beckons you closer. 'Looking for something special?'")
                self.current_room.interaction_states["blackest_market"].interactions = [
                    (f"buy Communications Tower ID Card ({BLACK_MARKET_ID_PRICE} "
                     "Minshin)"),
                    "go back"
                ]
            else:
                self.current_room.set_interaction_state("blackest_market_sign")
                self.current_room.add_message(
                    "The stall is closed, with a sign reading: 'Coming soon, "
                    "Blackest of Markets, where you can find all your totally "
                    "legal *wink* items.'"
                )
            return True
        return False

    def _handle_view_how_to_mine_handbook(self) -> bool:
        if self.current_room.name == "Mine Entrance":
            self.current_room.add_message(
                "Rule number 1. Make sure you have your mining gun. Once equipped mine "
                "away and you will recieve a variety of minerals based on your luck. "
                "Happy mining"
            )
            return True
        return False

    def _handle_view_refinery_for_dummies_handbook(self) -> bool:
        if self.current_room.name == "Refinery":
            self.current_room.add_message(
                "The refinery is for NON-AMBROSIUM materials only. All you "
                "gotta do is insert your ID card and then deposit all your "
                "materials and the refinery will do the rest. Give it a minute "
                "and then your payment will be appended to the ID card."
            )
            return True
        return False

    def _handle_view_depositing_101_handbook(self) -> bool:
        if self.current_room.name == "Deposit Station":
            self.current_room.add_message(
                "Just insert your ID card and deposit all your ambrosium from this day's "
                "haul. Allow the machine to do its analysis and then make sure to remove "
                "your card once you get the all clear."
            )
            return True
        return False

    def check_for_foreman_spawn(self) -> None:
        """
        Checks if the donation total is sufficient to spawn Colony Foreman Long.
        """
        foreman_exists = any("Colony Foreman Long" in npc for npc in self.memorial_pond.npcs)
        
        if self.total_donations >= FOREMAN_SPAWN_DONATION_THRESHOLD and not foreman_exists:
            self.memorial_pond.add_npc("Colony Foreman Long")
            self.memorial_pond.add_message(
                "\nA man with a stern but weary face, wearing a foreman's "
                "jacket, has appeared by the pond. He nods at you."
            )
    def quit_game(self, argument: str) -> bool:
        """
        Handles the 'QUIT' command.
        """
        return True

    def print_help(self, argument: str) -> None:
        """
        Displays help text to the player.
        """
        help_text = """Primary Commands:
- go <location>: Move to another location (e.g., 'go central plaza').
- take <item>: Pick up an item (e.g., 'take ID card').
- drop <item>: Drop an item from your inventory.
- inventory: Check your inventory.
- quit: Exit the game.
- map: Display the colony map.

Contextual Actions:
The game will also present you with numbered options for specific interactions like
talking to people or looking at objects. Type the number to perform the action."""
        self.current_room.add_message(help_text)

    def show_map(self, argument: str) -> None:
        """
        Handles the 'MAP' command.
        """
        self.ui.display_map(self.current_room.name)
        self.suppress_next_room_display = True

    def do_go_command(self, destination: str) -> None:
        """
        Handles the 'GO' command to move the player between rooms.

        This method contains special logic for security checkpoints and
        triggers travel animations for specific routes.

        :param destination: The location the player wants to move to.
        """
        if (self.current_room.name == "Security Checkpoint (Residential)" and
                destination in ["industrial sector", "industrial plaza"]):
            if self.player.has_item(ITEMS["ID card"]):
                self.current_room.add_message(
                    "You scan your ID card. The blast door hisses open, revealing a small "
                    "security airlock. Creedal nods you through."
                )
                self.current_room = self.security_checkpoint_residential_gate
            else:
                self.current_room.add_message("You need your ID card to pass. Creedal shakes his head.")
            return
        elif (self.current_room.name == "Security Checkpoint (Industrial)" and
              destination in ["residential sector", "central plaza"]):
            if self.player.has_item(ITEMS["ID card"]):
                self.current_room.add_message(
                    "You scan your ID card. The gate slides open. Weatherbee watches "
                    "you leave without a word."
                )
                self.current_room = self.security_checkpoint_industrial_gate
            else:
                self.current_room.add_message(
                    "You need your ID card to pass. Weatherbee holds up a hand to stop you."
                )
            return

        try:
            if not destination:
                self.current_room.add_message("Go where?")
                return

            if (self.current_room.name == "Industrial Plaza" and
                    destination in ["refinery", "deposit station"]):
                if FACILITY_CLOSE_HOUR <= self.time.hours < FACILITY_OPEN_HOUR:
                    self.current_room.add_message(
                        f"The {destination.title()} is closed from {FACILITY_CLOSE_HOUR}:00-"
                        f"{FACILITY_OPEN_HOUR}:00 for standard maintenance."
                    )
                    return

            if ((self.current_room.name == "Residential Entrance" and destination == "central plaza") or
               (self.current_room.name == "Central Plaza" and "residential" in destination)):
                magno_steps = [
                    ("Waiting for Magnotube...", 1.0),
                    ("Boarding Magnotube...", 1.0),
                    ("En-route...", 1.5),
                    ("Arrived.", 0.5)
                ]
                self._run_travel_animation(magno_steps)
            elif ((self.current_room.name == "Residential Checkpoint Gate" and "industrial" in destination) or
                 (self.current_room.name == "Industrial Checkpoint Gate" and "central" in destination)):
                gate_steps = [
                    ("Waiting...", 1.0),
                    ("Waiting some more...", 1.5),
                    ("Doors open.", 0.5)
                ]
                self._run_travel_animation(gate_steps)

            next_room = self.current_room.get_exit(destination)
            if next_room:
                if next_room.name == "Residential Corridor":
                    RoomFactory.reset_residential_corridor(next_room)
                
                if next_room.name == "Colony Market":
                    market_interactions = next_room.interaction_states["main"].interactions
                    stall_interaction = "approach Blackest of Markets stall"
                    if (stall_interaction not in market_interactions and
                            not self.player.bought_blackest_market_card):
                        market_interactions.append(stall_interaction)
                        if "blackest_market" not in next_room.interaction_states:
                            next_room.add_interaction_state("blackest_market", ["go back"], parent="main")
                        if "blackest_market_sign" not in next_room.interaction_states:
                             next_room.add_interaction_state("blackest_market_sign", ["go back"], parent="main")

                self.current_room = next_room
                self.time.advance_time(0.5)
            else:
                self.current_room.add_message(f"There is no way to go '{destination}'!")
                
        except Exception as e:
            logging.error(f"Error in do_go_command with direction '{destination}': {e}", exc_info=True)
            self.current_room.add_message(f"Error moving to new location: {str(e)}")

    def take_item(self, item_name: str) -> None:
        """
        Handles the 'TAKE' command.
        """
        if not item_name:
            self.current_room.add_message("Take what?")
            return
            
        item_name = item_name.lower()
        
        if self.current_room.current_interaction_state == "cupboard":
            container_items = self.current_room.hidden_items.get("cupboard", [])
            item_to_take = next((item for item in container_items if item.name.lower() == item_name), None)
            if item_to_take:
                if self.player.add_to_inventory(item_to_take):
                    container_items.remove(item_to_take) 
                    self.current_room.add_message(f"You took the {item_to_take.name}.")
                    logging.info(f"Player took {item_to_take.name} from a container in {self.current_room.name}.")
                    if container_items:
                        interactions = ["take " + item.name for item in container_items] + ["go back"]
                        self.current_room.add_interaction_state("cupboard", interactions)
                    else:
                        self.current_room.add_message("The cupboard is now empty.")
                        self.current_room.set_interaction_state("main")
                else:
                    self.current_room.add_message("Your inventory is full.")
            else:
                self.current_room.add_message(f"There is no '{item_name}' in the cupboard.")
            return

        item_to_take = None
        for room_item in self.current_room.items:
            if room_item.name.lower() == item_name:
                item_to_take = room_item
                break
        
        if item_to_take:
            if self.player.add_to_inventory(item_to_take):
                self.current_room.remove_item(item_to_take)
                self.current_room.add_message(f"You picked up the {item_to_take.name}.")
                logging.info(f"Player took {item_to_take.name} from {self.current_room.name}.")
            else:
                self.current_room.add_message("Your inventory is full.")
        else:
            self.current_room.add_message(f"There is no {item_name} here to take.")

    def drop_item(self, item_name: str) -> None:
        """
        Handles the 'DROP' command.
        """
        if not item_name:
            self.current_room.add_message("Drop what?")
            return

        item_to_drop = self.player.get_item_by_name(item_name)
        
        if item_to_drop:
            if item_to_drop.type == ItemType.KEY_ITEM:
                self.current_room.add_message("You should probably hold on to this.")
                return
            
            if self.player.remove_from_inventory(item_to_drop):
                self.current_room.add_item(item_to_drop)
                self.current_room.add_message(f"You dropped the {item_to_drop.name}.")
        else:
            self.current_room.add_message(f"You don't have a {item_name}.")

    def show_inventory(self, argument: str) -> None:
        """
        Handles the 'INVENTORY' command.
        """
        inventory_text = self.player.get_inventory_display()
        self.current_room.add_message(inventory_text)
        self.current_room.add_interaction_state("inventory", ["go back"])
        self.current_room.set_interaction_state("inventory")

    def open_container(self, container_name: str) -> None:
        """
        Handles the 'OPEN' command for containers like cupboards.

        When a container is opened for the first time, its contents are revealed
        and new interactions (e.g., 'take' commands) become available.

        :param container_name: The name of the container to open.
        """
        if not container_name:
            self.current_room.add_message("Open what?")
            return
        if container_name == "cupboard":
            if "cupboard" in self.current_room.hidden_items and "cupboard" not in self.current_room.containers_opened:
                self.current_room.containers_opened.append("cupboard")
                
                items_in_cupboard = self.current_room.hidden_items["cupboard"]
                if items_in_cupboard:
                    self.current_room.add_message("The cupboard's contents have made themselves known.")
                    interactions = ["take " + item.name for item in items_in_cupboard] + ["go back"]
                    self.current_room.add_interaction_state("cupboard", interactions)
                    self.current_room.set_interaction_state("cupboard")
                else:
                    self.current_room.add_message("It's empty.")
            elif "cupboard" in self.current_room.containers_opened:
                self.current_room.add_message("You already opened the cupboard.")
            else:
                self.current_room.add_message("There is no cupboard here.")
        else:
            self.current_room.add_message(f"You can't open the {container_name}.")

    def look_at(self, target: str) -> None:
        """
        Handles the 'LOOK AT' command.
        """
        if not target:
            self.current_room.add_message("Look at what?")
            return
        if target in ["bulletin board", "at bulletin board"]:
            if self.current_room.name == "Residential Entrance":
                self.current_room.set_interaction_state("bulletin_board")
                self.current_room.add_message("You look at the bulletin board.")
            else:
                self.current_room.add_message("There is no bulletin board here.")
        else:
            self.current_room.add_message(f"You see nothing special about the {target}.")
            
    def talk_to(self, npc_name: str) -> None:
        """
        Handles the 'TALK' command by initiating a conversation with an NPC.

        This method delegates to the Player object to determine the correct
        dialogue and interaction state based on quest progression. It also
        dynamically updates the available interactions for certain NPCs.

        :param npc_name: The name of the NPC to talk to.
        """
        if not npc_name:
            self.current_room.add_message("Talk to who?")
            return
        new_state, message = self.player.talk_to_npc(npc_name)
        self.current_room.add_message(message)
        if new_state:
            self.current_room.set_interaction_state(new_state)

            if new_state == "weatherbee_talk":
                interactions = self.current_room.interaction_states["weatherbee_talk"].interactions
                
                if "congratulations on your new job" in interactions:
                    interactions.remove("congratulations on your new job")
                if "hows your spirits now weatherbee" in interactions:
                    interactions.remove("hows your spirits now weatherbee")

                if (self.player.weatherbee_quest_congratulated and
                        not self.player.weatherbee_quest_complete and
                        FACILITY_CLOSE_HOUR <= self.time.hours < FACILITY_OPEN_HOUR):
                    interactions.insert(0, "hows your spirits now weatherbee")
                elif self.player.weatherbee_quest_read_bulletin:
                    interactions.insert(0, "congratulations on your new job")

    def insert_item(self, item_name: str) -> None:
        """
        Handles the 'INSERT' command.
        """
        if not item_name:
            self.current_room.add_message("Insert what?")
            return
        if item_name == "id card":
            if not self.player.has_item(ITEMS["ID card"]):
                self.current_room.add_message("You don't have an ID card.")
                return

            state = self.current_room.current_interaction_state
            if state == "personal_info":
                self.current_room.set_interaction_state("viewing_info")
                personal_info = (
                    f"Accessing Personnel File...\n"
                    f"Name: {self.player.name} Gold\n"
                    f"Years Served: 97\n"
                    f"Position: Ambrosium Miner\n"
                    f"Status: Active\n"
                    f"Minshin Balance: {self.player.minshin}"
                )
                self.current_room.add_message(personal_info)
            elif state == "deposit_prompt":
                self.deposit_resources()
                self.current_room.set_interaction_state("main")
            elif state == "refinery_prompt":
                self.deposit_non_ambrosium()
                self.current_room.set_interaction_state("main")
            else:
                self.current_room.add_message("There's nowhere to insert that here.")
        else:
            self.current_room.add_message(f"You can't insert a {item_name}.")

    def investigate(self, target: str) -> None:
        """
        Handles the 'INVESTIGATE' command.
        """
        if not target:
            self.current_room.add_message("Investigate what?")
            return
        target = target.strip().lower()
        if target == "memorial fountain" and self.current_room.name == "Memorial Pond":
            self.current_room.set_interaction_state("memorial_fountain")
        else:
            self.current_room.add_message(f"You're not sure how to investigate {target}.")

    def check_item(self, item_name: str) -> None:
        """
        Handles the 'CHECK' command for interactive objects like terminals.
        
        :param item_name: The object the player wants to check.
        """
        if not item_name:
            self.current_room.add_message("Check what?")
            return
        if item_name == "terminal" and self.current_room.name == "Your Quarters":
            self.current_room.set_interaction_state("terminal")
            self.current_room.add_message("You access the terminal.")
        else:
            self.current_room.add_message(f"You can't check a {item_name} here.")

    def read(self, target: str) -> None:
        """
        Handles the 'READ' command.
        """
        if not target:
            self.current_room.add_message("Read what?")
            return
        target = target.strip().lower()

        if self.current_room.current_interaction_state == "bulletin_board":
            if "quota increase" in target:
                self.current_room.add_message(
                    "[NOTICE] Effective next cycle, the weekly Ambrosium quota "
                    "will be raised to 25 crystals. Service to Olympus is "
                    "paramount."
                )
            elif "oxygen generators" in target:
                self.current_room.add_message(
                    '[WARNING] Reports of generator malfunctions have increased '
                    'by 32% in the past month. "all is well, its just a case '
                    'of routine repairs" Says Colony Foreman Long .'
                )
            elif "job listings" in target:
                self.current_room.add_message(
                    "[AD] The recent vacancy for SECURITY CHECKPOINT OFFICER "
                    "(INDUSTRIAL) (FULL TIME) has been filled by a Mr. "
                    "Weatherbee. All subsequent applications will be ignored."
                )
                self.player.weatherbee_quest_read_bulletin = True
            elif "advert for a vendor" in target:
                poster = """+-------------------------------------------------+
                        |                                                 |
                        |               ** ARMEDAS STALL **               |
                        |                                                 |
                        |      "Come here come here to Armeda's stall!"   |
                        |                                                 |
                        |   Tired of your old clunker? We got...          |
                        |   >>> HEAVY BEAM MINING GUN UPGRADES! <<<       |
                        |         *Make your mining sweeter!*             |
                        |                                                 |
                        |   Running out of space? Check out our...        |
                        |   >>> OLYMPUS XL BACKPACKS! <<<                 |
                        |                                                 |
                        |   Hungry? We have...                            |
                        |   >>> DELICIOUS STEAMED BUNS! <<<               |
                        |         *Caters for all your needs!*            |
                        |                                                 |
                        +-------------------------------------------------+"""
                self.current_room.add_message(poster)
            else:
                self.current_room.add_message(f"There is no notice about '{target}' on the board.")
            return

        if "plaque" in target and self.current_room.name == "Memorial Pond":
            self.current_room.add_message(
                "The plaque is cold to the touch. It reads: 'In memory of "
                " Colony 4A. May their memory pave the way for a "
                "prosperous future under the guidance of Olympus.'"
            )
            self.current_room.set_interaction_state("read_plaque")
        else:
            self.current_room.add_message(f"You can't find anything called '{target}' to read here.")

    def donate(self, target: str) -> None:
        """
        Handles the 'DONATE' command (as a fallback).
        
        This advises the player on the correct way to donate.
        """
        self.current_room.add_message(
            "Donations are handled via the 'donate minshin into donation "
            "terminal' option at the Memorial Pond."
        )

    def handle_debug_command(self, argument: str) -> None:
        """
        Handles all 'DEBUG' commands.
        """
        if not self.debug_mode:
            self.current_room.add_message("Debug mode is not active.")
            return

        if not argument:
            self.current_room.add_message(
                "Usage: debug <command> <args...>. Available: set, give, goto"
            )
            return

        parts = argument.lower().split()
        command = parts[0]
        args = parts[1:]

        try:
            if command == "set":
                if len(args) < 2:
                    self.current_room.add_message(
                        "Usage: debug set <system> <value>. Systems: time, day, "
                        "minshin, quota"
                    )
                    return
                system, value = args[0], args[1]
                if system == "time":
                    self.time.hours = float(value)
                    self.current_room.add_message(f"Debug: Time set to {self.time.hours}.")
                elif system == "day":
                    self.time.days = int(value)
                    self.current_room.add_message(f"Debug: Day set to {self.time.days}.")
                elif system == "minshin":
                    self.player.minshin = int(value)
                    self.current_room.add_message(f"Debug: Minshin set to {self.player.minshin}.")
                elif system == "quota":
                    self.player.quota_fulfilled = int(value)
                    self.current_room.add_message(f"Debug: Quota fulfilled set to {self.player.quota_fulfilled}.")
                else:
                    self.current_room.add_message(f"Debug: Unknown system '{system}'.")
            
            elif command == "give":
                if not args:
                    self.current_room.add_message("Usage: debug give <item_name>")
                    return
                item_name = " ".join(args)
                item_key = next((k for k in ITEMS if k.lower() == item_name.lower()), None)
                if item_key and item_key in ITEMS:
                    item = ITEMS[item_key]
                    if self.player.add_to_inventory(item):
                        self.current_room.add_message(f"Debug: Gave player {item.name}.")
                    else:
                        self.current_room.add_message("Debug: Player inventory is full.")
                else:
                    self.current_room.add_message(f"Debug: Unknown item '{item_name}'.")

            elif command == "goto":
                if not args:
                    self.current_room.add_message("Usage: debug goto <room_name>")
                    return
                room_name = " ".join(args)
                target_room = self.room_map.get(room_name.lower())
                if target_room:
                    self.current_room = target_room
                    self.current_room.add_message(f"Debug: Teleported to {target_room.name}.")
                else:
                    self.current_room.add_message(f"Debug: Unknown room '{room_name}'.")
                    self.current_room.add_message(
                        f"Available: {', '.join(self.room_map.keys())}"
                    )
            else:
                self.current_room.add_message(f"Unknown debug command '{command}'.")

        except (ValueError, IndexError) as e:
            self.current_room.add_message(f"Debug command failed: {e}")


def main() -> None:
    """
    The main entry point for the game.

    This function initializes the ``Game`` object, displays the introduction,
    and starts the main game loop, while also handling graceful exit
    conditions like ``KeyboardInterrupt``.
    """
    with open('game.log', 'w'):
        pass
        
    game = Game()
    game.display_intro()
    try:
        game.play()
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting game. Thank you for playing!")
    except Exception as e:
        logging.critical(
            "A critical error occurred in the main game loop.", exc_info=True
        )
        print(f"\n\nA critical error forced the game to close: {e}")
        print("Please check the game.log file for more details.")

if __name__ == "__main__":
    main()