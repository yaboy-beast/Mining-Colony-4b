"""
Global constants for the Colony 4B game.

This module centralizes all the "magic numbers" and configuration
variables used throughout the game. This approach improves readability
and maintainability, as game balance can be adjusted from a single
location.
"""

# --- Donation and NPC Interaction ---
FOREMAN_SPAWN_DONATION_THRESHOLD = 200  # Minshin needed to make Foreman appear
MINIMUM_DONATION = 10  # Minimum Minshin donation allowed
PROPHECY_COST = 50  # Cost for a prophecy from Hinter
SOIL_SAMPLES_REQUIRED = 10  # Soil samples needed for Ephsus's quest

# --- Prices for Items and Upgrades ---
BLACK_MARKET_ID_PRICE = 4000  # Cost of the illegal ID card
BACKPACK_PRICE = 500  # Cost of the inventory upgrade
STEAMED_BUNS_PRICE = 150  # Cost of the steamed buns for Creedal's quest
MINING_UPGRADE_PRICE = 1500  # Cost of the mining gun upgrade
SOIL_SELL_PRICE = 10  # Minshin received per Thebian Ground Soil
CLAGNUM_SELL_PRICE = 50  # Minshin received per Clagnum Putty
MATTERSTONE_SELL_PRICE = 100  # Minshin received per Matterstone Ore

# --- Game Rules, Timings, and Quotas ---
WEEKLY_AMBROSIUM_QUOTA = 20  # Ambrosium crystals required per cycle
QUOTA_PERIOD_DAYS = 3  # Number of days in a work cycle
FACILITY_CLOSE_HOUR = 15  # Hour when industrial facilities close (24h format)
FACILITY_OPEN_HOUR = 20  # Hour when industrial facilities reopen (24h format)

# --- Mining and Discovery Mechanics ---
SKELETON_DISCOVERY_THRESHOLD = 40  # Mining attempts before skeleton can be found
SKELETON_DISCOVERY_CHANCE = 0.5  # Chance to find skeleton after threshold
AMBROSIUM_CLUSTER_VALUE = 5  # How many crystals a cluster is worth
MINSHIN_PER_AMBROSIUM_POST_QUOTA = 250  # Bonus for ambrosium after quota

# --- Player Initial Statistics and Inventory ---
INITIAL_MINSHIN = 50  # Starting Minshin for the player
MAX_INVENTORY_DEFAULT = 10  # Default player inventory size
MAX_INVENTORY_UPGRADED = 20  # Upgraded player inventory size
MAX_RESOURCE_STACK = 10  # Max stack size for a single resource type 