"""
Defines the Room and RoomFactory classes for the Colony 4B game.

This module is central to building the game's world. It contains:
- The ``InteractionState`` class, for managing contextual commands.
- The ``Room`` class, a data-centric component that represents a single
  location in the game world, holding its own state.
- The ``RoomFactory`` class, which uses the factory design pattern to
  decouple the main game from the complex process of creating and
  connecting all the game's rooms.
"""
from typing import Dict, List, Optional, Tuple
from items import Item, ITEMS
import logging

class InteractionState:
    """
    Represents a specific interaction context within a room.

    Each state has a list of available actions and can point to a parent
    state, allowing for a hierarchical menu system.

    Attributes:
        interactions (List[str]): A list of command strings available in this state.
        parent (Optional[str]): The name of the parent state to return to.
    """
    def __init__(
        self, interactions: List[str], parent: Optional[str] = "main"
    ) -> None:
        """
        Initializes an InteractionState object.
        
        :param interactions: A list of command strings available in this state.
        :param parent: The name of the parent state.
        """
        self.interactions = interactions
        self.parent = parent

class Room:
    """
    Represents a single location in the game world.

    A room has a name, a description, and can contain items, NPCs, and exits
    to other rooms. It also manages its own set of interaction states to
    handle contextual commands.

    Attributes:
        name (str): The name of the room.
        description (str): The descriptive text for the room.
        exits (Dict[str, 'Room']): A dictionary mapping exit names (str) to
                                 linked Room objects.
        items (List[Item]): A list of visible items in the room.
        hidden_items (Dict[str, List[Item]]): A dictionary mapping container
                                              names (str) to lists of
                                              hidden Item objects.
        containers_opened (List[str]): A list of container names (str) that
                                       have been opened by the player.
        npcs (List[str]): A list of the names (str) of NPCs present in the room.
        messages (List[str]): A temporary list of messages to be displayed on
                              the next UI refresh.
        current_interaction_state (str): The key (str) for the current active
                                         interaction state.
        interaction_states (Dict[str, InteractionState]): A dictionary mapping
                                                          state names (str) to
                                                          their InteractionState
                                                          objects.
    """
    def __init__(self, name: str, description: str) -> None:
        """
        Initializes a Room object.
        
        :param name: The name for the room.
        :param description: The descriptive text for the room.
        """
        self.name = name
        self.description = description
        self.exits: Dict[str, 'Room'] = {}
        self.items: List[Item] = []
        self.hidden_items: Dict[str, List[Item]] = {}  # Items hidden in containers
        self.containers_opened: List[str] = []  # Track which containers have been opened
        self.npcs: List[str] = []
        self.messages: List[str] = []
        self.current_interaction_state: str = "main"
        self.interaction_states: Dict[str, InteractionState] = {
            "main": InteractionState([], parent=None),
            "inventory": InteractionState(["go back"]),
            "terminal": InteractionState([
                "check weekly quota", "check news", "personal information", "go back"
            ]),
            "personal_info": InteractionState(["insert id card", "go back"], parent="terminal"),
            "viewing_info": InteractionState(["remove ID card and go back"], parent="terminal"),
            "cupboard": InteractionState(["take ID card", "take mining gun", "go back"])
        }

    def add_exit(self, direction: str, room: 'Room') -> None:
        """
        Adds a visible exit to another room.

        This method connects the current room to another, and adds a 'go <direction>'
        command to the room's main list of interactions.

        :param direction: The name of the direction or destination.
        :param room: The Room object that this exit leads to.
        """
        if not isinstance(direction, str):
            raise ValueError("Direction must be a string")
        if not isinstance(room, Room):
            raise ValueError("Must provide a valid Room object")
            
        self.exits[direction] = room
        self.interaction_states["main"].interactions.append(f"go {direction}")

    def add_hidden_exit(self, direction: str, room: 'Room') -> None:
        """
        Adds a hidden exit to another room.

        This exit is functional but does not create a 'go' command in the
        room's interaction list. It's used for programmatic room changes.

        :param direction: The name of the direction or destination.
        :param room: The Room object that this exit leads to.
        """
        if not isinstance(direction, str):
            raise ValueError("Direction must be a string")
        if not isinstance(room, Room):
            raise ValueError("Must provide a valid Room object")
            
        self.exits[direction] = room

    def get_exit(self, direction: str) -> Optional['Room']:
        """
        Retrieves a Room object for a given exit direction.

        :param direction: The name of the exit direction.
        :return: The corresponding Room object if the exit exists, otherwise None.
        """
        if not isinstance(direction, str):
            raise ValueError("Direction must be a string")
            
        return self.exits.get(direction)

    def add_item(self, item_name: str) -> None:
        """
        Adds a visible item to the room from the global ITEMS dictionary.

        Also adds a corresponding 'take <item>' interaction to the room's
        main state.

        :param item_name: The key of the item in the global ITEMS dictionary.
        """
        if item_name in ITEMS:
            self.items.append(ITEMS[item_name])
            self.interaction_states["main"].interactions.append(f"take {item_name}")  # Add to main state

    def remove_item(self, item: Item) -> None:
        """
        Removes an item from the room.

        Also removes the corresponding 'take <item>' interaction.

        :param item: The Item object to remove from the room.
        """
        if item in self.items:
            self.items.remove(item)
            self.interaction_states["main"].interactions = [
                i for i in self.interaction_states["main"].interactions
                if i != f"take {item.name}"
            ]

    def add_npc(self, npc: str) -> None:
        """
        Adds an NPC to the room.

        This method adds the NPC's name to the list and ensures a 'talk to <npc>'
        interaction is present in the main state, avoiding duplicates.

        :param npc: The name of the NPC to add.
        """
        if npc not in self.npcs:
            self.npcs.append(npc)
        
        # Ensure the interaction is only added once
        talk_interaction = f"talk to {npc}"
        if talk_interaction not in self.interaction_states["main"].interactions:
            self.interaction_states["main"].interactions.append(talk_interaction)

    def add_hidden_items(self, container: str, items: List[str]) -> None:
        """
        Adds a list of items to a hidden container in the room.

        It also adds an 'open <container>' interaction to the room's main state.

        :param container: The name of the container (e.g., 'cupboard').
        :param items: A list of item keys from the global ITEMS dictionary.
        """
        self.hidden_items[container] = [ITEMS[item_name] for item_name in items]
        # Add the container interaction to main state
        self.interaction_states["main"].interactions.append(f"open {container}")

    def get_description(self) -> str:
        """
        Generates the full descriptive text for the room.

        This includes the room's base description, plus lists of any visible
        items and NPCs.

        :return: A formatted string containing the full room description.
        """
        desc_parts = [
            f"=== {self.name} ===",
            self.description
        ]
        
        # Gather visible items
        visible_items = list(self.items) # Make a copy
        if self.current_interaction_state == "cupboard" and "cupboard" in self.containers_opened:
            visible_items.extend(self.hidden_items.get("cupboard", []))

        if visible_items:
            item_list = ["\nItems here:"]
            for item in visible_items:
                item_list.append(f"- {item.name}")
            desc_parts.append("\n".join(item_list))
                
        if self.npcs:
            npc_list = ["\nPeople here:"]
            for npc in self.npcs:
                npc_list.append(f"- {npc}")
            desc_parts.append("\n".join(npc_list))
                
        return "\n".join(desc_parts)

    def get_available_interactions(self) -> List[str]:
        """
        Gets the list of available command interactions for the current state.
        
        :return: A list of command strings.
        """
        state_obj = self.interaction_states.get(self.current_interaction_state)
        return state_obj.interactions if state_obj else []

    def add_message(self, message: str) -> None:
        """
        Adds a message to the room's message queue.

        These messages are displayed to the player on the next UI refresh.

        :param message: The message string to add.
        """
        self.messages.append(message)

    def get_messages(self) -> List[str]:
        """
        Retrieves all messages from the queue and clears it.

        :return: A list of all pending message strings.
        """
        messages = self.messages.copy()
        self.messages.clear()
        return messages

    def add_interaction_state(
        self, state_name: str, interactions: List[str], parent: Optional[str] = "main"
    ) -> None:
        """
        Adds a new interaction state to the room.

        :param state_name: The name for the new state.
        :param interactions: A list of command strings for this state.
        :param parent: The name of the parent state to return to.
        """
        if not isinstance(state_name, str) or not state_name:
            raise ValueError("State name must be a non-empty string")
        if not isinstance(interactions, list):
            raise ValueError("Interactions must be a list of strings")
        
        self.interaction_states[state_name] = InteractionState(interactions, parent)
        logging.info(
            f"Added interaction state '{state_name}' with parent '{parent}' "
            f"and interactions: {interactions}"
        )

    def add_simple_interaction_state(self, state_name: str, 
                                    parent: Optional[str] = "main") -> None:
        """
        Add an interaction state with only 'go back' option.
        
        A convenience method for states that only need a return option.
        
        Args:
            state_name: The name for the new state
            parent: The name of the parent state to return to
        """
        self.add_interaction_state(state_name, ["go back"], parent)

    def set_interaction_state(self, state: str) -> None:
        """
        Changes the room's current interaction state.

        If the provided state is invalid, it logs an error and defaults
        to the 'main' state.

        :param state: The name of the state to switch to.
        """
        try:
            if not isinstance(state, str):
                raise ValueError("State must be a string")
                
            if state not in self.interaction_states:
                raise ValueError(f"Invalid state: {state}")
                
            self.current_interaction_state = state
            logging.info(f"Room {self.name} state changed to: {state}")
            
        except Exception as e:
            logging.error(f"Error setting room state: {e}")
            self.current_interaction_state = "main"  # Fallback to main state

    def get_parent_state(self) -> str:
        """
        Gets the parent of the current interaction state.
        
        :return: The name of the parent state, or 'main' as a fallback.
        """
        current_state_obj = self.interaction_states.get(self.current_interaction_state)
        if current_state_obj and current_state_obj.parent:
            return current_state_obj.parent
        return "main" # Default fallback

class RoomFactory:
    """
    A factory class for creating and configuring all game rooms.

    This class encapsulates the logic for building the entire game world,
    following the factory design pattern. It uses static methods to construct
    each room with its specific description, items, NPCs, and interaction
    states. This design choice promotes high cohesion by keeping all room
    creation logic in one place and low coupling by separating the `Game`
    class from the details of world-building.
    """
    
    # Store rooms as class variables to prevent recreation
    _industrial_plaza = None
    _refinery = None
    
    @staticmethod
    def create_player_home() -> Room:
        """
        Creates the player's starting room, 'Your Quarters'.
        
        :return: A configured Room object for the player's home.
        """
        room = Room("Your Quarters", 
                   "Your small but cozy living space in the residential sector.")
        
        # Add hidden items to cupboard
        room.add_hidden_items("cupboard", ["ID card", "mining gun"])
        
        # Add terminal interaction to main state
        room.interaction_states["main"].interactions.append("check terminal")
        
        return room
        
    @staticmethod
    def create_residential_corridor() -> Room:
        """
        Creates the 'Residential Corridor' room.
        
        :return: A configured Room object for the residential corridor.
        """
        room = Room("Residential Corridor",
                   "A long corridor connecting various living quarters.")
        
        # Cecil is now a permanent resident.
        room.add_npc("Greyman Cecil")
        logging.info("Greyman Cecil is present in the Residential Corridor.")
        
        # Add Cecil interaction states
        room.add_interaction_state("cecil_talk", [
            "who is this man and why is covered in grey dust",
            'say "you alright cecil"',
            "leave"
        ])
        room.add_simple_interaction_state("cecil_info", parent="cecil_talk")
        room.add_interaction_state(
            "cecil_alright", ["are you sure you alright?", "go back"], parent="cecil_talk"
        )
        room.add_simple_interaction_state(
            "cecil_quest_prompt", parent="cecil_alright"
        )
        
        return room
        
    @staticmethod
    def reset_residential_corridor(room: Room) -> None:
        """
        Resets the state of the residential corridor.
        
        This method ensures that Greyman Cecil and his associated interaction
        are present in the room.

        :param room: The Room object for the residential corridor.
        """
        # This function is now simpler as Cecil is always present.
        # We just need to ensure the NPC and the interaction exist.
        if "Greyman Cecil" not in room.npcs:
            room.add_npc("Greyman Cecil")
        
        # Add main interaction for Cecil if not already present
        if "talk to Greyman Cecil" not in room.interaction_states["main"].interactions:
            room.interaction_states["main"].interactions.append("talk to Greyman Cecil")
        
    @staticmethod
    def create_residential_entrance() -> Room:
        """
        Creates the 'Residential Entrance' room.
        
        :return: A configured Room object for the residential entrance.
        """
        room = Room("Residential Entrance",
                   "The main entrance to the residential sector.")
        
        # Add bulletin board interaction states
        room.add_interaction_state("bulletin_board", [
            "read notice about quota increase",
            "read warning about oxygen generators",
            "read recent job listings",
            "read an advert for a vendor at the market",
            "step away from bulletin board"
        ])
        
        # Add main interaction for the bulletin board
        room.interaction_states["main"].interactions.append("look at bulletin board")
        
        return room
        
    @staticmethod
    def create_central_plaza() -> Room:
        """
        Creates the 'Central Plaza' room.
        
        :return: A configured Room object for the central plaza.
        """
        room = Room("Central Plaza",
                   ("The heart of Colony 4B where all sectors meet. A grand "
                    "open space with multiple pathways."))
        
        # Add initial interaction for Ephsus
        room.add_npc("Science Officer Ephsus")
        
        # Add Ephsus initial description state
        room.add_interaction_state("ephsus_initial", [
            "ask about thebian ground soil",
            "ask why looks like she's contemplating",
            "go back to plaza"
        ])

        room.add_interaction_state("ephsus_quest_prompt", [
            "offer thebian ground soil",
            "go back"
        ], parent="ephsus_initial")
        
        # Add Ephsus response states with "go back" options
        room.add_simple_interaction_state("ephsus_matterstone", parent="ephsus_initial")
        
        room.add_simple_interaction_state("ephsus_contemplating", parent="ephsus_initial")
        
        # Add tower gaze state
        room.add_simple_interaction_state("tower_gaze")
        
        return room
        
    @staticmethod
    def create_market() -> Room:
        """
        Creates the 'Colony Market' room.
        
        :return: A configured Room object for the market.
        """
        room = Room("Colony Market",
                   "A bustling marketplace where colonists trade goods and supplies.")
        room.add_simple_interaction_state("market_stall", parent="main")
        room.add_simple_interaction_state("blackest_market", parent="main")
        room.add_simple_interaction_state("blackest_market_sign", parent="main")
        room.interaction_states["main"].interactions.append(
            "approach Merchant Armedas stall"
        )
        room.interaction_states["main"].interactions.append(
            "approach Blackest of Markets stall"
        )
        room.interaction_states["main"].interactions.append("visit Hinter's Prophecies")
        room.add_interaction_state("hinter_prophecies", [
            "what should I pay my attention to? (50 Minshin)",
            "leave"
        ], parent="main")
        return room
        
    @staticmethod
    def create_memorial_pond() -> Room:
        """
        Creates the 'Memorial Pond' room.
        
        :return: A configured Room object for the memorial pond.
        """
        room = Room("Memorial Pond",
                   "A peaceful area with a serene pond, dedicated to the colonists of 4A.")
        
        # Add interaction for investigating the memorial fountain
        main_interactions = room.interaction_states["main"].interactions
        main_interactions.append("read memorial pond plaque")
        main_interactions.append("donate minshin into donation terminal")

        # Add interaction state for reading the plaque
        room.add_simple_interaction_state("read_plaque")

        # Add state for donation input
        room.add_interaction_state("donating", [])
        
        # Add Foreman Long's potential interaction states
        room.add_interaction_state("foreman_long_initial", [
            "ask about his job",
            "ask why he's here",
            "leave"
        ])
        room.add_simple_interaction_state("foreman_long_job", parent="foreman_long_initial")
        room.add_simple_interaction_state("foreman_long_reason", parent="foreman_long_initial")

        return room
        
    @staticmethod
    def create_security_checkpoint_residential() -> Room:
        """
        Creates the residential side of the security checkpoint.
        
        :return: A configured Room object for the residential checkpoint.
        """
        room = Room("Security Checkpoint (Residential)",
                   ("The residential side of the heavily monitored checkpoint. A "
                    "large blast door blocks the way to the industrial sector. "
                    "Security Officer Creedal watches you impassively. The way "
                    "back to the Central Plaza is open."))
        room.add_npc("Security Officer Creedal")
        room.add_interaction_state("creedal_talk", [
            "ask about the industrial sector",
            "ask why creedal is drooling",
            "go back"
        ])
        room.add_interaction_state("creedal_quest_prompt", [
            "stay strong creed",
            "go back"
        ], parent="creedal_talk")
        room.interaction_states["main"].interactions.append("go industrial sector")
        return room

    @staticmethod
    def create_security_checkpoint_industrial() -> Room:
        """
        Creates the industrial side of the security checkpoint.
        
        :return: A configured Room object for the industrial checkpoint.
        """
        room = Room("Security Checkpoint (Industrial)",
                   ("The industrial side of the checkpoint. A security gate "
                    "blocks the path to the residential sector, watched by the "
                    "stern Security Officer Weatherbee. The Industrial Plaza is "
                    "behind you."))
        room.add_npc("Security Officer Weatherbee")
        room.add_interaction_state("weatherbee_talk", [
            "ask about the residential sector",
            "go back"
        ])
        room.add_interaction_state("weatherbee_spirits_prompt", [
            "give weatherbee a high five",
            "go back"
        ], parent="weatherbee_talk")
        room.interaction_states["main"].interactions.append("go residential sector")
        return room

    @staticmethod
    def create_security_checkpoint_residential_gate() -> Room:
        """
        Creates the airlock gate on the residential side of the checkpoint.
        
        :return: A configured Room object for the residential checkpoint gate.
        """
        room = Room(
            "Residential Checkpoint Gate",
            ("You are in a small, sterile airlock. The blast door to the "
             "residential checkpoint has closed behind you. The only way is "
             "forward into the Industrial Plaza.")
        )
        return room
    
    @staticmethod
    def create_security_checkpoint_industrial_gate() -> Room:
        """
        Creates the airlock gate on the industrial side of the checkpoint.
        
        :return: A configured Room object for the industrial checkpoint gate.
        """
        room = Room(
            "Industrial Checkpoint Gate",
            ("A small, sterile security airlock. The gate to the industrial "
             "checkpoint has closed behind you. The only way is forward to the "
             "Central Plaza.")
        )
        return room
        
    @staticmethod
    def create_industrial_plaza() -> Room:
        """
        Creates the 'Industrial Plaza' room.
        
        Uses a cached instance to prevent re-creation.
        
        :return: A configured Room object for the industrial plaza.
        """
        # Only create if not already created
        if RoomFactory._industrial_plaza is None:
            RoomFactory._industrial_plaza = Room("Industrial Plaza",
                   ("The industrial sector where mining operations are managed. "
                    "The air hums with machinery."))
            
        return RoomFactory._industrial_plaza

    @staticmethod
    def create_refinery() -> Room:
        """
        Creates the 'Refinery' room.
        
        Uses a cached instance to prevent re-creation.
        
        :return: A configured Room object for the refinery.
        """
        if RoomFactory._refinery is None:
            room = Room("Refinery",
                       "A facility for processing and refining raw materials.")
            
            # Add deposit interaction
            room.interaction_states["main"].interactions.append(
                "deposit non-ambrosium materials"
            )
            room.interaction_states["main"].interactions.append(
                "view 'refinery for dummies' handbook"
            )
            room.add_interaction_state("refinery_prompt", ["insert ID card", "go back"])
            RoomFactory._refinery = room
        return RoomFactory._refinery

    @staticmethod
    def connect_industrial_and_refinery() -> Tuple[Room, Room]:
        """
        Connects the Industrial Plaza and Refinery rooms.
        
        A helper method to ensure the exits between these two cached rooms
        are correctly established.
        
        :return: A tuple containing the industrial plaza and refinery Room objects.
        """
        industrial_plaza = RoomFactory.create_industrial_plaza()
        refinery = RoomFactory.create_refinery()
        
        # Connect the rooms
        industrial_plaza.add_exit("refinery", refinery)
        refinery.add_exit("industrial plaza", industrial_plaza)
        
        return industrial_plaza, refinery
        
    @staticmethod
    def create_mine_entrance() -> Room:
        """
        Creates the 'Mine Entrance' room.
        
        :return: A configured Room object for the mine entrance.
        """
        room = Room("Mine Entrance",
                   "The entrance to the Ambrosium mines. This is where you work.")
        room.add_item("Ambrosium Crystal")
        
        # Add "mine away" interaction - this is the only place it should be available
        room.interaction_states["main"].interactions.append("mine away")
        room.interaction_states["main"].interactions.append("view 'how to mine' handbook")
        
        return room
        
    @staticmethod
    def create_deposit_station() -> Room:
        """
        Creates the 'Deposit Station' room.
        
        :return: A configured Room object for the deposit station.
        """
        room = Room("Deposit Station",
                   ("A facility where miners can deposit their Ambrosium "
                    "findings and receive payment."))
        room.add_item("lucky coin")
        
        # Add "deposit resources" interaction
        room.interaction_states["main"].interactions.append("deposit resources")
        room.interaction_states["main"].interactions.append(
            "view 'depositing 101' handbook"
        )
        room.add_interaction_state("deposit_prompt", ["insert ID card", "go back"])
        
        return room

    @staticmethod
    def create_communications_tower_entrance() -> Room:
        """
        Creates the 'Communications Tower Entrance' room.
        
        :return: A configured Room object for the communications tower entrance.
        """
        room = Room("Communications Tower Entrance",
                   ("The entrance to the massive communications tower. A "
                    "terminal sits next to the sealed doors."))
        
        # Add terminal interaction
        room.interaction_states["main"].interactions.append("approach terminal")
        # Start with just the basic ID card option
        room.add_interaction_state("approaching_terminal", [
            "insert ID card",
            "go back"
        ])
        
        return room