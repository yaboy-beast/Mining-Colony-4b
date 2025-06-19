"""
Basic items for Colony 4B.
"""
from enum import Enum, auto

class ItemType(Enum):
    """
    Defines the types of items available in the game.
    
    This enumeration is used to categorize items, which can affect
    how they behave (e.g., key items cannot be dropped).
    
    Attributes:
        KEY_ITEM (auto): An important item for quests or progression.
        RESOURCE (auto): A raw material that can be collected or sold.
        CONSUMABLE (auto): An item that can be used up.
    """
    KEY_ITEM = auto()  # Important quest/key items
    RESOURCE = auto()  # Resources like Ambrosium
    CONSUMABLE = auto()  # Usable items like health packs

class Item:
    """
    Represents an item in the game.

    Each item has a name, a description, and a type that defines its
    general category and behavior within the game.

    Attributes:
        name (str): The name of the item.
        description (str): A brief description of the item.
        type (ItemType): The type of the item, from the ItemType enum.
    """
    def __init__(self, name: str, description: str, item_type: ItemType):
        """
        Initializes an Item object.

        :param name: The name for the item.
        :param description: The descriptive text for the item.
        :param item_type: The type of the item, from the ItemType enum.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Item name must be a non-empty string")
        if not isinstance(description, str):
            raise ValueError("Item description must be a string")
        if not isinstance(item_type, ItemType):
            raise ValueError("Invalid item type")
        
        self.name = name
        self.description = description
        self.type = item_type

def _key_item(name: str, desc: str) -> Item:
    """Helper to create a key item."""
    return Item(name, desc, ItemType.KEY_ITEM)

def _resource(name: str, desc: str) -> Item:
    """Helper to create a resource item."""
    return Item(name, desc, ItemType.RESOURCE)

# Define all available items
ITEMS = {
    # Key Items
    "ID card": _key_item(
        "ID card",
        "Your colony identification card."
    ),
    "mining gun": _key_item(
        "mining gun",
        "Standard-issue mining tool for extracting Ambrosium."
    ),
    "lucky coin": _key_item(
        "lucky coin",
        "A worn coin with what seems to be a clover minted upon it."
    ),
    "Steamed Buns": _key_item(
        "Steamed Buns",
        "a set of delicous steamed buns. Who knows whats inside"
    ),
    "Communications Tower ID Card": _key_item(
        "Communications Tower ID Card",
        "An ID card that might grant access to restricted areas. "
        "The quality is questionable."
    ),
    
    # Resources
    "Ambrosium Crystal": _resource(
        "Ambrosium Crystal",
        "Why you are here"
    ),
    "Thebian Ground Soil": _resource(
        "Thebian Ground Soil",
        "Common soil from the mines of Thebes."
    ),
    "Clagnum Putty": _resource(
        "Clagnum Putty",
        "A sticky substance found in the mines."
    ),
    "Matterstone Ore": _resource(
        "Matterstone Ore",
        "A rare ore with unique properties."
    ),
    "Ambrosium Cluster": _resource(
        "Ambrosium Cluster",
        "A cluster of Ambrosium crystals."
    ),
}