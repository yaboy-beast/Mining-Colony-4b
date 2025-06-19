"""
Defines the Player class for the Colony 4B game.

This module contains the ``Player`` class, which is a data-centric
component responsible for managing the player's state, including their
inventory, currency, quest progression, and other dynamic attributes
throughout the game.
"""

from typing import List, Optional
from items import Item, ItemType
from game_constants import (
    WEEKLY_AMBROSIUM_QUOTA, INITIAL_MINSHIN, MAX_INVENTORY_DEFAULT,
    MAX_RESOURCE_STACK
)

class Player:
    """
    Represents the player character in the game.

    This class manages the player's attributes, including their name,
    inventory, currency (Minshin), and quest progression flags.

    Attributes:
        name (str): The player's name.
        minshin (int): The amount of currency the player possesses.
        inventory (List[Item]): A list of Item objects in the player's
                                inventory.
        max_inventory (int): The maximum number of items the player can
                             carry. This can be upgraded.
        ambrosium_quota (int): The number of Ambrosium crystals required
                               per cycle.
        quota_fulfilled (int): The number of Ambrosium crystals the
                               player has deposited this cycle.
        quota_celebration_shown (bool): A flag to ensure the quota
                                        celebration message is only
                                        displayed once per cycle.
        has_found_skeleton (bool): A flag for triggering the secret
                                   skeleton-discovery ending.
        long_quest_complete (bool): Flag for tracking Foreman Long's quest status.
        ephsus_quest_complete (bool): Flag for tracking Science Officer
                                      Ephsus's quest status.
        ephsus_soil_given (int): A counter for the number of soil samples
                                 given to Ephsus.
        creedal_quest_complete (bool): Flag for tracking Security Officer
                                       Creedal's quest status.
        cecil_quest_complete (bool): Flag for tracking Greyman Cecil's
                                     quest status.
        weatherbee_quest_read_bulletin (bool): A flag to track if the player
                                               has read the bulletin about
                                               Weatherbee's new job.
        weatherbee_quest_congratulated (bool): A flag to track if the player
                                               has congratulated Weatherbee.
        weatherbee_quest_complete (bool): Flag for tracking Security Officer
                                          Weatherbee's quest status.
        bought_xl_backpack (bool): Flag to track the inventory upgrade purchase.
        bought_steamed_buns (bool): Flag to track the steamed buns purchase.
        bought_mining_gun_upgrade (bool): Flag to track the mining gun upgrade
                                          purchase.
        bought_blackest_market_card (bool): Flag to track the black market
                                            ID card purchase.
    """
    def __init__(self, name: str) -> None:
        """
        Initializes a Player object.

        :param name: The name for the player character.
        """
        self.name = name
        self.minshin = INITIAL_MINSHIN
        self.inventory: List[Item] = []
        self.max_inventory = MAX_INVENTORY_DEFAULT
        self.ambrosium_quota = WEEKLY_AMBROSIUM_QUOTA
        self.quota_fulfilled = 0
        self.quota_celebration_shown = False
        self.has_found_skeleton = False
        
        # Quest flags track the completion of various NPC storylines.
        self.long_quest_complete = False
        self.ephsus_quest_complete = False
        self.ephsus_soil_given = 0
        self.creedal_quest_complete = False
        self.cecil_quest_complete = False
        self.weatherbee_quest_read_bulletin = False
        self.weatherbee_quest_congratulated = False
        self.weatherbee_quest_complete = False

        # Market purchase flags track items bought from vendors.
        self.bought_xl_backpack = False
        self.bought_steamed_buns = False
        self.bought_mining_gun_upgrade = False
        self.bought_blackest_market_card = False

    def is_inventory_full(self) -> bool:
        """
        Checks if the player's inventory has reached its maximum capacity.
        
        This check is based on the number of item slots, not stack sizes.

        :return: True if the inventory is full, False otherwise.
        """
        return len(self.inventory) >= self.max_inventory

    def add_to_inventory(self, item: Item) -> bool:
        """
        Adds an item to the player's inventory if it is not full.

        For stackable resources, it checks if the stack limit has been
        reached. The stack limit is defined by ``MAX_RESOURCE_STACK``.

        :param item: The Item object to add.
        :return: True if the item was added successfully, False otherwise.
        :raises ValueError: If the provided item is not a valid Item object.
        """
        if not isinstance(item, Item):
            raise ValueError("Invalid item type provided to inventory")

        # For resources, check if the stack for this specific item is full.
        if item.type == ItemType.RESOURCE:
            resource_count = sum(1 for inv_item in self.inventory 
                               if inv_item.name == item.name)
            if resource_count >= MAX_RESOURCE_STACK:
                return False  # Can't stack more of this specific resource.
            
        if not self.is_inventory_full():
            self.inventory.append(item)
            return True
            
        return False

    def remove_from_inventory(self, item: Item) -> bool:
        """
        Removes an item from the player's inventory.

        This method will fail if the item is an essential (non-consumable)
        key item, preventing the player from dropping critical quest objects.

        :param item: The Item object to remove.
        :return: True if the item was removed successfully, False otherwise.
        :raises ValueError: If the provided item is not a valid Item object.
        """
        if not isinstance(item, Item):
            raise ValueError("Invalid item type provided for removal")

        # Prevent dropping essential key items, while allowing specific
        # quest-related key items to be removed.
        if (item.type == ItemType.KEY_ITEM and
                item.name not in ["Steamed Buns", "lucky coin", 
                                  "Communications Tower ID Card"]):
            return False
        
        if item in self.inventory:
            self.inventory.remove(item)
            return True
            
        return False

    def has_item(self, item: 'Item') -> bool:
        """
        Checks if a specific item is present in the player's inventory.

        :param item: The Item object to check for.
        :return: True if the player has the item, False otherwise.
        """
        return item in self.inventory

    def get_item_by_name(self, item_name: str) -> Optional['Item']:
        """
        Finds and returns an item from inventory by its name.

        The search is case-insensitive.

        :param item_name: The name of the item to find.
        :return: The Item object if found, otherwise None.
        """
        item_name = item_name.lower()
        for item in self.inventory:
            if item.name.lower() == item_name:
                return item
        return None

    def collect_ambrosium(self, amount: int) -> None:
        """
        Adds to the player's quota and awards a corresponding amount of Minshin.
        This method is a placeholder and is not actively used in the game's
        final implementation, as deposit logic is handled elsewhere.

        :param amount: The amount of ambrosium collected.
        """
        self.quota_fulfilled += amount
        self.minshin += amount * 5  # 5 minshin per ambrosium

    def get_inventory_display(self) -> str:
        """
        Generates a formatted string of the player's inventory contents.

        Items are counted and grouped for a clean, readable display.

        :return: A formatted string listing all items in the inventory.
        """
        if not self.inventory:
            return "Your inventory is empty."
        
        from collections import Counter
        inventory_counts = Counter(item.name for item in self.inventory)
        
        inventory_lines = []
        # Use a temporary set to avoid adding descriptions for the same
        # item type more than once.
        processed_items = set()
        for name, count in inventory_counts.items():
            if name not in processed_items:
                # Find the first item object with this name to get its description.
                item_obj = next((item for item in self.inventory 
                                 if item.name == name), None)
                if item_obj:
                    line = f"- {name}"
                    if count > 1:
                        line += f" (x{count})"
                    line += f": {item_obj.description}"
                    inventory_lines.append(line)
                    processed_items.add(name)

        return "Your inventory contains:\n" + "\n".join(inventory_lines)

    def all_quests_complete(self) -> bool:
        """
        Checks if all major NPC quests have been completed.

        This is used to determine if the player has achieved the "good"
        ending of the game.

        :return: True if all quest flags are set to True, False otherwise.
        """
        return all([
            self.long_quest_complete,
            self.ephsus_quest_complete,
            self.creedal_quest_complete,
            self.cecil_quest_complete,
            self.weatherbee_quest_complete
        ])

    def talk_to_npc(self, full_npc_name: str) -> tuple[Optional[str], str]:
        """
        Determines the interaction state and dialogue for an NPC.

        This method checks the NPC's name and the player's quest
        progression to return the appropriate new interaction state for the
        room and a corresponding line of dialogue.

        :param full_npc_name: The full name of the NPC to talk to.
        :return: A tuple containing the new state name (or None if no
                 state change) and a message string.
        """
        npc_name_lower = full_npc_name.lower()
        if "greyman cecil" in npc_name_lower:
            if not self.cecil_quest_complete:
                return "cecil_talk", "You approach Greyman Cecil."
            else:
                return None, "'Cecil's respect for you is almost palpable.'"
        elif "ephsus" in npc_name_lower:
            if not self.ephsus_quest_complete:
                return "ephsus_initial", "You approach Science Officer Ephsus."
            else:
                return None, "'Ephsus's respect for you is almost palpable.'"
        elif "creedal" in npc_name_lower:
            if not self.creedal_quest_complete:
                return "creedal_talk", "You approach Security Officer Creedal."
            else:
                return None, "'Creedal's respect for you is almost palpable.'"
        elif "weatherbee" in npc_name_lower:
            if self.weatherbee_quest_complete:
                return None, "'Weatherbee's respect for you is almost palpable.'"
            return "weatherbee_talk", ("You approach the stern-faced Security "
                                      "Officer Weatherbee.")
        elif "colony foreman long" in npc_name_lower:
            if not self.long_quest_complete:
                # The main interaction is handled in the Game class.
                # This logic is for subsequent talks.
                return "foreman_long_initial", "You approach Colony Foreman Long."
            else:
                return None, "'Long's respect for you is almost palpable.'"
        else:
            return None, (
                f"You try talking to {full_npc_name}, but don't know where to "
                "start."
            ) 