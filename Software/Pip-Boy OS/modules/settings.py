import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from data_models import LimbPosition, IconConfig
from items import ItemLoader, Inventory

# Import sicuro delle chiavi segrete per evitare crash se il file non esiste
try:
    from settings_secrets import *
except ImportError:
    pass

import platform

#######################################################
# Load items from the items.ini file
#######################################################
loader = ItemLoader('items.ini')
items = loader.load_items()

# ==================================================
# Constants (Modify only if program structure changes)
# ==================================================
TABS = ("STAT", "INV", "DATA", "MAP", "RADIO")

UI_STYLE = "Fallout_4"
if UI_STYLE == "Fallout_NV":
    SUBTABS = {
        'STATS': ['STATUS', 'S.P.E.C.I.A.L.', 'SKILLS', 'PERKS', 'GENERAL'],
        "ITEMS": ("WEAPONS", "APPAREL", "AID", "MISC", "AMMO"),
        "DATA": ("QUESTS", "LOCAL MAP", "WORLD MAP", "NOTES", "RADIO")
    }
else:
    SUBTABS = {
        'STAT': ['STATUS', 'S.P.E.C.I.A.L.', 'PERKS'],
        "INV": ("WEAPONS", "APPAREL", "AID", "MISC", "JUNK", "MODS", "AMMO"),
        "DATA": ("QUESTS", "WORKSHOPS", "STATS", "SETTINGS")
    }

# ==================================================
# User Configuration (Adjust these for setup/preferences)
# ==================================================

# ------------------
# UI Layout
# ------------------
UI_STYLE = "Fallout_4"
TAB_MARGIN = 20
TAB_VERTICAL_OFFSET = 0
TAB_VERTICAL_LINE_OFFSET = 10
TAB_HORIZONTAL_LINE_OFFSET = 4
TAB_SCREEN_EDGE_LENGTH = 2
TAB_HORIZONTAL_LENGTH = TAB_HORIZONTAL_LINE_OFFSET // 1.1
TAB_BOTTOM_MARGIN = 2
BOTTOM_BAR_VERTICAL_MARGINS = 2
BOTTOM_BAR_HEIGHT = 18
BOTTOM_BAR_MARGIN = 5
TAB_SIDE_MARGIN = 0
SUBTAB_SPACING = 5
SUBTAB_VERTICAL_OFFSET = 1
LIST_TOP_MARGIN = 10

# ------------------
# General Settings
# ------------------
RASPI = False 
SPEED = 1
GAME_ACCURATE_MODE = False
YEARS_ADDED = 263

# ------------------
# Screen Settings
# ------------------
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 255
FPS = 24
FULLSCREEN = True if RASPI else False 
BACKGROUND = (0, 0, 0)
PIP_BOY_LIGHT = (0, 255, 0)
try:
    from modules.user_config import *
except ImportError:
    try:
        from user_config import *
    except ImportError:
        pass
if 'PIP_BOY_LIGHT' in globals():
    PIP_BOY_MIDDLE = (int(PIP_BOY_LIGHT[0] * 0.75), int(PIP_BOY_LIGHT[1] * 0.75), int(PIP_BOY_LIGHT[2] * 0.75))
    PIP_BOY_DARKER = (int(PIP_BOY_LIGHT[0] * 0.5), int(PIP_BOY_LIGHT[1] * 0.5), int(PIP_BOY_LIGHT[2] * 0.5))
    PIP_BOY_DARK = PIP_BOY_DARKER
else:
    PIP_BOY_MIDDLE= (int(PIP_BOY_LIGHT[0] * 0.75), int(PIP_BOY_LIGHT[1] * 0.75), int(PIP_BOY_LIGHT[2] * 0.75))
    PIP_BOY_MID = PIP_BOY_MIDDLE
    PIP_BOY_DARK = (int(PIP_BOY_LIGHT[0] * 0.5), int(PIP_BOY_LIGHT[1] * 0.5), int(PIP_BOY_LIGHT[2] * 0.5))
    PIP_BOY_DARKER = PIP_BOY_DARK

# ------------------
# Audio Settings
# ------------------
SOUND_ON = True
VOLUME = 1
MUSIC_VOLUME = 1
SWITCH_SOUND_CHANCE = 70

# ------------------
# Visual Effects
# ------------------
SHOW_CRT = True
BLOOM_EFFECT = True
GLITCH_MOVE_CHANCE = 60
BOOT_SCREEN = False
RANDOM_GLITCHES = True
RANDOM_GLITCH_CHANCE = 0.5

# ------------------
# Path Configuration
# ------------------
from paths import *

# ------------------
# Player Settings
# ------------------
PLAYER_NAME = "DanieleM"
HP_MAX = 120
HP_CURRENT = 100
AP_MAX = 90
AP_CURRENT = 90
RADIATION_CURRENT = 0 # percentage of hp
RADIATION_VALUE = RADIATION_CURRENT * 10
LEVEL = 28
XP_CURRENT = 39
ADDICTED = False

DEFAULT_LIMB_DAMAGE = [70, 14, 69, 54, 28, 100]
CRIPPLED_THRESHOLD = 20
DAMAGED_THRESHOLD = 50
DEFAULT_STATS_DAMAGE = [
    IconConfig(STAT_TAB_RETICLE, 18),
    IconConfig(STAT_TAB_BOLT, 10)
]
DEFAULT_STATS_ARMOR = [
    IconConfig(STAT_TAB_SHIELD, 5),
    IconConfig(STAT_TAB_RADIATION, 10)
]
DEFAULT_SPECIAL_STATS = [2, 3, 2, 7, 3, 1, 0]
SPECIAL_STATS_BONUS = [0, 0, 0, 0, 0, 0, 0]

_inventory = Inventory()
_inventory.add_item(items['10mm Pistol'], 2)
_inventory.add_item(items['Fat Man'])
_inventory.add_item(items['Vault 111 Jumpsuit'])
_inventory.add_item(items['Road Leathers'], 3)
_inventory.add_item(items['Stimpak'], 5)
_inventory.add_item(items['RadAway'], 2)
_inventory.add_item(items['Nuka-Cola'], 3)
_inventory.add_item(items['Abraxo Cleaner'])
_inventory.add_item(items['Fusion Core'])
_inventory.add_item(items['.308 Round'], 10)
_inventory.add_item(items['Fusion Cell'], 25)
_inventory.add_item(items['10mm Round'], 37)
_inventory.add_item(items['Mini Nuke'])

# Esportazione lista base per le schede dell'inventario
INV_BASE = _inventory.get_all_items()

# Calcolo dei bonus S.P.E.C.I.A.L.
SPECIAL_KEYS = ['STR', 'PER', 'END', 'CHR', 'INT', 'AGI', 'LUK']
for item in _inventory.get_all_items():
    if hasattr(item, 'special_bonuses') and isinstance(item.special_bonuses, dict):
        for i, stat_key in enumerate(SPECIAL_KEYS):
            SPECIAL_STATS_BONUS[i] += item.special_bonuses.get(stat_key, 0)

MAX_WEIGHT = 200 + (DEFAULT_SPECIAL_STATS[0] * 10)
CAPS = 1000

TOTAL_AMMO = {}
for item in _inventory.get_all_items():
    if item.category == 'Ammo':
        if item.name in TOTAL_AMMO:
            TOTAL_AMMO[item.name] += 1
        else:
            TOTAL_AMMO[item.name] = 1
            
# ------------------
# Stat Tab Settings
# ------------------
# Status subtab
CONDITIONBOY_SCALE = 4
CONDITIONBOY_OFFSET = 12
LIMB_POSITIONS = [
    LimbPosition(0, 10, 'head'),
    LimbPosition(-50, 50, 'left_arm'),
    LimbPosition(50, 50, 'right_arm'),
    LimbPosition(-50, 95, 'left_leg'),
    LimbPosition(50, 95, 'right_leg'),
    LimbPosition(0, 130, 'torso')
]
DAMAGE_ARMOUR_MARGIN_SMALL = 2
DAMAGE_ARMOUR_ICON_SMALL_SIZE = 0.5
DAMAGE_ARMOUR_MARGIN_BIG = 8
DAMAGE_ARMOUR_ICON_BIG_SIZE = 0.45
DAMAGE_ARMOUR_ICON_ABSOLUTE_SIZE = 11.5
DAMAGE_ARMOUR_ICON_MARGIN = 7
LIMB_DAMAGE_WIDTH = 20

# Special subtab
SPECIAL = ("Strength", "Perception", "Endurance", "Charisma", "Intelligence", "Agility", "Luck")
SPECIAL_IMAGE_SCALE = 0.45
SPECIAL_DESCRIPTIONS = [
    "Strength is a measure of your raw physical power. It affects how much you can carry, and the damage of all melee attacks.",
    "Perception is your environmental awareness and 'sixth sense', and affects weapon accuracy in V.A.T.S.",
    "Endurance is a measure of your overall physical fitness. It affect your total Health and the Action Point drain from sprinting.",
    "Charisma is your ability to charm and convince others. It affects your success to persuade in dialogue and prices when you barter.",
    "Intelligence is a measure of your overall metal acuity, and affects the number of Experience Points earned",
    "Agility is a measure of your overall fitnesse and reflexes. It affects the number of Action Points in V.A.T.S. and your ability to sneak",
    "Luck is a measure of your general good fortune, and affects the recharge rate of Critical Hits, and the chances of finding better items."
]

# Perks subtab
DEFAULT_PERKS_NV = [
    {"name": "Lady Killer", "rank": 1, "max_rank": 1, "desc": "In combat, you do +10% damage against female opponents. Outside of combat, you'll sometimes have access to unique dialogue options when dealing with the opposite sex."},
    {"name": "Mysterious Stranger", "rank": 1, "max_rank": 1, "desc": "Gives you your own personal guardian angel... armed with a fully loaded .44 Magnum. With this perk, the Mysterious Stranger appears occasionally in V.A.T.S. mode to lend a hand, with deadly efficiency."},
    {"name": "Commando", "rank": 1, "max_rank": 3, "desc": "While using a rifle (or similar two-handed weapon), your accuracy in V.A.T.S. is significantly increased."},
    {"name": "Cowboy", "rank": 1, "max_rank": 3, "desc": "You do 25% more damage when using any revolver, lever-action firearm, dynamite, knife, or hatchet."},
    {"name": "Four Eyes", "rank": 1, "max_rank": 1, "desc": "While wearing any type of glasses, you have +1 PER. Without glasses, you have -1 PER."},
    {"name": "Good Natured", "rank": 1, "max_rank": 1, "desc": "You're Good Natured at heart, more prone to solving problems with your mind than violence. You gain +5 to Barter, Medicine, Repair, Science, and Speech, but have -5 to Energy Weapons, Explosives, Guns, Melee Weapons, and Unarmed."},
    {"name": "Computer Whiz", "rank": 1, "max_rank": 1, "desc": "Fail a hack attempt and get locked out of a computer? Not if you're a computer whiz! With this perk, you get a second chance at any computer you were previously locked out of."},
]
DEFAULT_PERKS_FO4 = [
    {
        "name": "Black Widow",
        "rank": 1,          
        "max_rank": 3,      
        "rank_descs": [
            "You're charming... and dangerous. Men suffer +5% damage in combat, and are easier to persuade in dialogue.",
            "Men now suffer +10% damage in combat, and are even easier to persuade in dialogue. They are also easier to pacify with the Intimidation perk.",
            "Men now suffer +15% damage in combat, and are much easier to persuade in dialogue. They are now even easier to pacify with the Intimidation perk."
        ]
    }
]

# Skills subtab
DEFAULT_SKILLS = [
    {"name": "Barter", "value": 55, "mod": "+", "desc": "The Barter skill affects the prices you get for buying and selling items. In general, the higher your Barter skill, the lower your prices on purchased items."},
    {"name": "Energy Weapons", "value": 16, "mod": "", "desc": "The Energy Weapons skill determines your effectiveness with all energy-based weapons, including Laser Pistols and Plasma Rifles."},
    {"name": "Explosives", "value": 21, "mod": "", "desc": "The Explosives skill determines the damage of explosive weapons and your success at defusing mines and traps."},
    {"name": "Lockpick", "value": 37, "mod": "", "desc": "The Lockpick skill is used to open locked doors and containers."},
    {"name": "Medicine", "value": 18, "mod": "-", "desc": "The Medicine skill determines how much health you recover from using a Stimpak, and the effectiveness of RadAway and Rad-X."},
    {"name": "Melee Weapons", "value": 39, "mod": "+", "desc": "The Melee Weapons skill determines your effectiveness with hand-to-hand weapons."},
    {"name": "Repair", "value": 16, "mod": "-", "desc": "The Repair skill allows you to maintain your weapons and armor in top condition, and lets you create items and ammunition at Reloading Benches."},
    {"name": "Science", "value": 16, "mod": "-", "desc": "The Science skill represents your knowledge of computers, allowing you to hack locked terminals. It also affects your efficiency at Workbenches."},
    {"name": "Guns", "value": 16, "mod": "", "desc": "The Guns skill determines your accuracy and damage with any weapon that utilizes conventional ammunition (e.g., .22 LR, 9mm, 5.56mm, .308, etc.)."},
    {"name": "Sneak", "value": 21, "mod": "", "desc": "The Sneak skill makes it easier to move undetected, pickpocket someone, or plant a live grenade on an unsuspecting target. Successfully attacking someone while undetected always results in a critical hit."},
    {"name": "Speech", "value": 38, "mod": "+", "desc": "The Speech skill is used to convince others to see things your way. It can be used to get information that might otherwise be kept secret, or to talk your way out of a problematic situation."},
    {"name": "Unarmed", "value": 17, "mod": "", "desc": "The Unarmed skill is used for fighting without weapons, or with weapons designed specifically for hand-to-hand combat (e.g., Brass Knuckles, Boxing Gloves, Power Fists)."},
    {"name": "Survival", "value": 10, "mod": "", "desc": "The Survival skill allows you to create powerful poisons, chems, and consumable food and drink items at camp fires scattered around the wasteland as the skill is increased."}
]

# ------------------
# Inventory Tab Settings
# ------------------
MAX_CARRY_WEIGHT = 150
GRID_BOTTOM_MARGIN = 0
GRID_RIGHT_MARGIN = 35
GRID_LEFT_MARGIN = 5
TURNTABLE_LEFT_MARGIN = 15

# ------------------
# Radio Tab Settings
# ------------------
RADIO_STATION_MARGIN = 10
RADIO_STATION_TEXT_MARGIN = 10
RADIO_STATION_SELECTION_MARGIN = 6
RADIO_STATION_SELECTION_DOT_SIZE = 4
RADIO_WAVE_POINTS = 12
RADIO_WAVE_VARIANCE = 5
RADIO_WAVE_SMOOTHING = 0.5
RADIO_WAVE_MAX = 10
RADIO_WAVE_MIN = 2
RADIO_WAVE_VISUALIZER_X_OFFSET = 10
RADIO_WAVE_VISUALIZER_Y_OFFSET = 10
RADIO_WAVE_VISUALIZER_SIZE_OFFSET = 50
RADIO_WAVE_VISUALIZER_GRID_LINES = 15
RADIO_WAVE_BATCH_SIZE = 5
RADIO_WAVE_SMOOTHING_FACTOR = 0.05
INTERMISSION_FREQUENCY = 50
FM_RADIO = False

# ------------------
# Map Tab Settings
# ------------------
REAL_MAP = False
FAKE_LOCATION = "Commonwealth"
# --- MAPS FALLOUT: NEW VEGAS ---
NV_MAP_DIR = os.path.join(BASE_DIR, "images", "new_vegas_icons", "map_nv")
MOJAVE_MAP = os.path.join(NV_MAP_DIR, "MojaveMapNoPOI.webp")
MOJAVE_MAP_MARKERS = os.path.join(NV_MAP_DIR, "MojaveMap.webp")
SHOW_ALL_MARKERS = True
MAP_ZOOM_SPEED = 0.2
MAP_MOVE_SPEED = 30
MIN_MAP_ZOOM = 1.5
INITIAL_MAP_ZOOM = 1
MARKER_SCALE_MIN = 0.5
MARKER_SCALE_MAX = 1.5
MAP_EDGES_OFFSET = 5
MAP_SIZE = 1024
EXTRA_MAP_SIZE = 100
LOGO_SIZE = 7.3
MAP_ZOOM = 12
MAP_ICON_SIZE = 30
MAP_PLACES_ZOOM = 20000
MAP_MIN_NODE_DISTANCE = 200

MAP_TYPE_PRIORITY = {
    "town": 50,
    "police": 5,
    "village": 50,
    "ruins": 20,
    "base": 10,
    "bunker": 40,
    "hamlet": 10,
    "farmland": 10,
    "lake": 6,
    "bridge": 6,
    "industrial": 9,
}

OSM_KEYS = (
    "place",
    "water",
    "historic",
    "landuse",
    "military",
    "man_made",
    "amenity",
)

MAP_TILE_SIZE = 512

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_CONFIG_PATH = os.path.join(CURRENT_DIR, 'user_config.py')
if os.path.exists(USER_CONFIG_PATH):
    from user_config import *

GEOAPIFY_KEY = 'YOUR_GEOAPIFY_KEY'
GEOAPIFY_API_KEY = 'YOUR_GEOAPIFY_KEY'