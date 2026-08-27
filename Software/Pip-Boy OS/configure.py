from enum import Enum
import re
from ast import literal_eval
import os
import time
import sys

import keyboard



# Configuration
SETTINGS_FILE = "modules/settings.py"
USER_CONFIG_FILE = "modules/user_config.py"
EDITABLE_SETTINGS = {
    'PLAYER_NAME', 'HP_MAX', 'HP_CURRENT', 'AP_MAX', 'AP_CURRENT', 'LEVEL',
    'PIP_BOY_LIGHT', 'PIP_BOY_MID', 'PIP_BOY_DARK', 'PIP_BOY_DARKER',
    'SCREEN_WIDTH', 'SCREEN_HEIGHT', 'FPS', 'SOUND_ON', 'SHOW_CRT', 'BLOOM_EFFECT',
    'REAL_MAP', 'FM_RADIO', 'FAKE_LOCATION', 'UI_STYLE','SHOW_ALL_MARKERS'
}

DEFAULT_SETTINGS = {
    'PLAYER_NAME': 'VAULT-DWELLER',
    'HP_MAX': 100,
    'HP_CURRENT': 100,
    'AP_MAX': 100,
    'AP_CURRENT': 100,
    'LEVEL': 1,
    'PIP_BOY_LIGHT': (0, 255, 0),
    'PIP_BOY_MID': (0, 127, 0),
    'PIP_BOY_DARK': (0, 63, 0), #It was in the original code, but kelmes1 removed it in , or maybe he made a typo
    'PIP_BOY_DARKER': (0, 63, 0),
    'SCREEN_WIDTH': 320,
    'SCREEN_HEIGHT': 240,
    'FPS': 30,
    'SOUND_ON': True,
    'SHOW_CRT': True,
    'BLOOM_EFFECT': True,
    'REAL_MAP': False,
    'FM_RADIO': False,
    'FAKE_LOCATION': 'Commonwealth',
    'UI_STYLE': 'Fallout_4',
    'SHOW_ALL_MARKERS': True
}

class PipBoyTheme:
    class Color(Enum):
        PRIMARY = "\033[38;5;40m"   # Pip-Boy Green
        SECONDARY = "\033[38;5;34m" # Darker Green
        ACCENT = "\033[38;5;226m"   # Amber
        WARNING = "\033[38;5;196m"  # Red
        DISABLED = "\033[38;5;240m" # Gray
        RESET = "\033[0m"

    @classmethod
    def apply_crt_effect(cls, text):
        crt_pattern = [
            "▗▄▖▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒",
            "▝▀▘▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒"
        ]
        return "".join([f"{cls.Color.DISABLED.value}{c}{cls.Color.RESET.value}" for c in crt_pattern[0]]) + "\n" + text

class PipBoyDisplay:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def draw_border():
        border = PipBoyTheme.Color.SECONDARY.value + "╔" + "═"*76 + "╗" + PipBoyTheme.Color.RESET.value
        print(border)

    @staticmethod
    def draw_divider():
        print(PipBoyTheme.Color.SECONDARY.value + "╠" + "═"*76 + "╣" + PipBoyTheme.Color.RESET.value)

    @staticmethod
    def draw_footer():
        footer = PipBoyTheme.Color.SECONDARY.value + "╚" + "═"*76 + "╝" + PipBoyTheme.Color.RESET.value
        print(footer)

    @staticmethod
    def typewriter(text, delay=0.02):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def loading_animation(duration=1):
        frames = ["[■□□□□□□□□□]", "[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", 
                 "[■■■■■□□□□□]", "[■■■■■■□□□□]", "[■■■■■■■□□□]", "[■■■■■■■■□□]",
                 "[■■■■■■■■■□]", "[■■■■■■■■■■]"]
        end_time = time.time() + duration
        while time.time() < end_time:
            for frame in frames:
                sys.stdout.write("\r" + PipBoyTheme.Color.ACCENT.value + frame + PipBoyTheme.Color.RESET.value)
                sys.stdout.flush()
                time.sleep(0.1)
        print("\r" + " "*15)

def parse_settings():
    """Load settings with proper priority: DEFAULT < settings.py < user_config.py"""
    settings = DEFAULT_SETTINGS.copy()
    
    def load_from_file(filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read()
                for match in re.finditer(r'^([A-Z_]+)\s*=\s*(.*)$', content, re.M):
                    var_name = match.group(1)
                    if var_name in EDITABLE_SETTINGS:
                        try:
                            settings[var_name] = literal_eval(match.group(2).strip())
                        except:
                            pass

    load_from_file(SETTINGS_FILE)
    load_from_file(USER_CONFIG_FILE)
    return settings

def update_user_config(new_settings):
    """Save only modified settings compared to original defaults"""
    # Load original defaults without user config
    original_defaults = DEFAULT_SETTINGS.copy()
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            content = f.read()
            for match in re.finditer(r'^([A-Z_]+)\s*=\s*(.*)$', content, re.M):
                var_name = match.group(1)
                if var_name in EDITABLE_SETTINGS:
                    try:
                        original_defaults[var_name] = literal_eval(match.group(2).strip())
                    except:
                        pass

    # Filter settings that differ from original defaults
    filtered_settings = {
        k: v for k, v in new_settings.items()
        if k in EDITABLE_SETTINGS and v != original_defaults.get(k, None)
    }
    
    # Generate config file content
    output = "# User Configuration (Auto-generated)\n# Overrides settings.py\n\n"
    for var, value in filtered_settings.items():
        if isinstance(value, str):
            output += f'{var} = "{value}"\n'
        elif isinstance(value, tuple):
            output += f'{var} = {tuple(value)}\n'
        else:
            output += f'{var} = {value}\n'
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    USER_CONFIG_FILE  = os.path.join(base_dir, "modules", "user_config.py")
    with open(USER_CONFIG_FILE, 'w') as f:
        f.write(output)

def display_header(title):
    PipBoyDisplay.clear()
    print(PipBoyTheme.Color.PRIMARY.value)
     #print(r"""
    # /$$$$$$$  /$$$$$$ /$$$$$$$  /$$$$$$$   /$$$$$$  /$$     /$$
    #| $$__  $$|_  $$_/| $$__  $$| $$__  $$ /$$__  $$|  $$   /$$/
    #| $$  \ $$  | $$  | $$  \ $$| $$  \ $$| $$  \ $$ \  $$ /$$/ 
    #| $$$$$$$/  | $$  | $$$$$$$/| $$$$$$$ | $$  | $$  \  $$$$/  
    #| $$____/   | $$  | $$____/ | $$__  $$| $$  | $$   \  $$/   
    #| $$        | $$  | $$      | $$  \ $$| $$  | $$    | $$    
    #| $$       /$$$$$$| $$      | $$$$$$$/|  $$$$$$/    | $$    
    #|__/      |______/|__/      |_______/  \______/     |__/    
    #""")
    print(r"""
      /$$$$$$$  /$$   /$$ /$$$$$$$  /$$       /$$ /$$$$$$$   /$$$$$$  
     /$$_____/ | $$  | $$| $$__  $$| $$      | $$| $$__  $$ /$$__  $$ 
    | $$       | $$  | $$| $$  \ $$| $$      | $$| $$  \ $$| $$  \__/ 
    |  $$$$$$  | $$  | $$| $$$$$$$/|  $$     /$$/| $$$$$$$/| $$       
     \____  $$ | $$  | $$| $$__  $$ \  $$   /$$/ | $$____/ | $$       
     ____ / $$/| $$  | $$| $$  \ $$  \  $$ /$$/  | $$      | $$    $$ 
    |  $$$$$$/ |  $$$$$$/| $$  | $$   \  $$$$/   | $$      |  $$$$$$/ 
     \______/   \______/ |__/  |__/    \____/    |__/       \______/  
    """)
    print(f"{PipBoyTheme.Color.ACCENT.value}=== {title} ==={PipBoyTheme.Color.RESET.value}\n")

def draw_menu(options, selected_index):
    PipBoyDisplay.draw_border()
    for i, (text, value) in enumerate(options):
        prefix = f"{PipBoyTheme.Color.ACCENT.value}▶ {PipBoyTheme.Color.PRIMARY.value}" if i == selected_index else "  "
        if value is None:
            print(f"{prefix}{text}")
        else:
            value_color = PipBoyTheme.Color.ACCENT.value if isinstance(value, str) else PipBoyTheme.Color.PRIMARY.value
            print(f"{prefix}{text.ljust(60)}{value_color}{value}{PipBoyTheme.Color.RESET.value}")
    PipBoyDisplay.draw_footer()

last_key_time = 0
KEY_DEBOUNCE = 0.2  # 200ms cooldown

def get_key():
    global last_key_time
    while True:
        event = keyboard.read_event(suppress=True)
        now = time.time()
        
        if now - last_key_time < KEY_DEBOUNCE:
            continue
            
        if event.event_type == keyboard.KEY_DOWN:
            last_key_time = now
            if event.name == 'up':
                return 'up'
            elif event.name == 'down':
                return 'down'
            elif event.name == 'enter':
                return 'enter'
            elif event.name == 'esc':
                return 'esc'


def draw_color_preview(color):
    """Draw ASCII art color preview with proper color codes"""
    # Calculate text color (white or black based on brightness)
    brightness = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])
    text_color = "\033[38;2;255;255;255m" if brightness < 127 else "\033[38;2;0;0;0m"
    reset = "\033[0m"
    
    preview = [
        "████████████████████████████████████████████████████████████",
        "████████████████████████████████████████████████████████████",
        f"██  CURRENT COLOR: {str(color).ljust(36)}  ██",
        "████████████████████████████████████████████████████████████"
    ]
    
    for line in preview:
        colored_line = []
        for char in line:
            if char == "█":
                # Full block with selected color
                colored_line.append(
                    f"\033[48;2;{color[0]};{color[1]};{color[2]}m"  # Background
                    f"\033[38;2;{color[0]};{color[1]};{color[2]}m"  # Foreground
                    "▄"  # Use lower half block
                )
            else:
                # Text with contrasting color
                colored_line.append(f"{text_color}{char}")
        colored_line.append(reset)
        print("".join(colored_line))
        
def validate_int_input(prompt, min_val, max_val):
    """Get validated integer input with retry logic"""
    while True:
        try:
            PipBoyDisplay.typewriter(f"{PipBoyTheme.Color.PRIMARY.value}{prompt}: ", 0.01)
            value = int(input())
            if min_val <= value <= max_val:
                return value
            raise ValueError
        except ValueError:
            PipBoyDisplay.typewriter(f"{PipBoyTheme.Color.WARNING.value}INVALID INPUT - ENTER VALUE BETWEEN {min_val}-{max_val}", 0.03)
            time.sleep(0.5)

def player_settings_menu(settings):
    selected = 0
    while True:
        options = [
            (f"Name: {settings['PLAYER_NAME']}", "VAULT-DWELLER ID"),
            (f"HP: {settings['HP_CURRENT']}/{settings['HP_MAX']}", "HEALTH STATUS"),
            (f"AP: {settings['AP_CURRENT']}/{settings['AP_MAX']}", "ACTION POINTS"),
            (f"Level: {settings['LEVEL']}", "VAULT-TEC RATING"),
            ("Return to Main Menu", "BACK")
        ]
        
        display_header("PLAYER CONFIGURATION")
        draw_menu(options, selected)
        
        key = get_key()
        if key == 'up' and selected > 0:
            selected -= 1
        elif key == 'down' and selected < len(options)-1:
            selected += 1
        elif key == 'enter':
            if selected == 0:
                PipBoyDisplay.typewriter(f"{PipBoyTheme.Color.PRIMARY.value}ENTER NEW NAME: ", 0.05)
                settings['PLAYER_NAME'] = input().strip()[:20]
            elif selected == 1:
                settings['HP_CURRENT'] = validate_int_input("CURRENT HP (0-999)", 0, 999)
                settings['HP_MAX'] = validate_int_input("MAX HP (1-999)", 1, 999)
            elif selected == 2:
                settings['AP_CURRENT'] = validate_int_input("CURRENT AP (0-999)", 0, 999)
                settings['AP_MAX'] = validate_int_input("MAX AP (1-999)", 1, 999)
            elif selected == 3:
                settings['LEVEL'] = validate_int_input("VAULT-TEC RATING LEVEL (1-99)", 1, 99)
            elif selected == 4:
                return
        elif key == 'esc':
            return

def color_settings_menu(settings):
    selected = 0
    color = settings['PIP_BOY_LIGHT']
    while True:
        options = [
            ("Classic Green", "VAULT-TEC STANDARD"),
            ("Amber", "PRE-WAR MILSPEC"),
            ("Blue", "ROBOCO INDUSTRIAL"),
            ("White", "EXPERIMENTAL"),
            ("Custom RGB", "ADVANCED CONFIG"),
            ("Return to Main Menu", "BACK")
        ]
        
        display_header("DISPLAY COLOR PROFILE")
        draw_color_preview(color)
        draw_menu(options, selected)
        
        key = get_key()
        if key == 'up' and selected > 0:
            selected -= 1
        elif key == 'down' and selected < len(options)-1:
            selected += 1
        elif key == 'enter':
            if selected == 0:
                color = (0, 255, 0)
            elif selected == 1:
                color = (255, 191, 0)
            elif selected == 2:
                color = (0, 127, 255)
            elif selected == 3:
                color = (255, 255, 255)
            elif selected == 4:
                r = validate_int_input("RED VALUE (0-255)", 0, 255)
                g = validate_int_input("GREEN VALUE (0-255)", 0, 255)
                b = validate_int_input("BLUE VALUE (0-255)", 0, 255)
                color = (r, g, b)
            elif selected == 5:
                settings['PIP_BOY_LIGHT'] = color
                settings['PIP_BOY_MID'] = tuple(x//2 for x in color)
                settings['PIP_BOY_DARKER'] = tuple(x//4 for x in color)
                settings['PIP_BOY_DARK'] = tuple(x//8 for x in color)
                return
        elif key == 'esc':
            return


def system_settings_menu(settings):
    selected = 0
    while True:
        options = [
            (f"Resolution: {settings['SCREEN_WIDTH']}x{settings['SCREEN_HEIGHT']}", "DISPLAY DIMENSIONS"),
            (f"FPS: {settings['FPS']}", "REFRESH RATE"),
            (f"Sound: {'ENABLED' if settings['SOUND_ON'] else 'DISABLED'}", "AUDIO OUTPUT"),
            (f"CRT Effect: {'ACTIVE' if settings['SHOW_CRT'] else 'OFFLINE'}", "RETRO FILTER"),
            (f"Bloom Effect: {'ACTIVE' if settings['BLOOM_EFFECT'] else 'OFFLINE'}", "LIGHTING SYSTEM"),
            ("Return to Main Menu", "BACK")
        ]
        
        display_header("SYSTEM PREFERENCES")
        draw_menu(options, selected)
        
        key = get_key()
        if key == 'up' and selected > 0:
            selected -= 1
        elif key == 'down' and selected < len(options)-1:
            selected += 1
        elif key == 'enter':
            if selected == 0:
                settings['SCREEN_WIDTH'] = validate_int_input("HORIZONTAL RESOLUTION", 320, 3840)
                settings['SCREEN_HEIGHT'] = validate_int_input("VERTICAL RESOLUTION", 240, 2160)
            elif selected == 1:
                settings['FPS'] = validate_int_input("FRAMES PER SECOND", 24, 144)
            elif selected == 2:
                settings['SOUND_ON'] = not settings['SOUND_ON']
            elif selected == 3:
                settings['SHOW_CRT'] = not settings['SHOW_CRT']
            elif selected == 4:
                settings['BLOOM_EFFECT'] = not settings['BLOOM_EFFECT']
            elif selected == 5:
                return
        elif key == 'esc':
            return
        
MAP_PRESETS = [
    {"label": "Mojave (with POI)", "REAL_MAP": False, "FAKE_LOCATION": "Mojave", "SHOW_ALL_MARKERS": True},
    {"label": "Mojave (without POI)", "REAL_MAP": False, "FAKE_LOCATION": "Mojave", "SHOW_ALL_MARKERS": False},
    {"label": "Commonwealth (with POI)", "REAL_MAP": False, "FAKE_LOCATION": "Commonwealth", "SHOW_ALL_MARKERS": True},
    {"label": "Commonwealth (without POI)", "REAL_MAP": False, "FAKE_LOCATION": "Commonwealth", "SHOW_ALL_MARKERS": False},
    {"label": "Mappa Satellitare Reale (needed Geoapify API key)", "REAL_MAP": True, "FAKE_LOCATION": "Commonwealth", "SHOW_ALL_MARKERS": True}
]

def get_current_map_preset_index(settings):
    if settings.get('REAL_MAP', False):
        return 4
    loc = settings.get('FAKE_LOCATION', 'Commonwealth')
    show_poi = settings.get('SHOW_ALL_MARKERS', True)
    if loc == "Mojave":
        return 0 if show_poi else 1
    else:
        return 2 if show_poi else 3

def system_mode_menu(settings):
    selected = 0
    while True:
        STYLE_NAMES = {
            'Fallout_4': 'Fallout 4',
            'Fallout_NV': 'Fallout New Vegas'
        }
        ui_style_raw = settings.get('UI_STYLE', 'Fallout_4')
        ui_style_display = STYLE_NAMES.get(ui_style_raw, ui_style_raw)
        
        current_map_idx = get_current_map_preset_index(settings)
        map_preset_label = MAP_PRESETS[current_map_idx]["label"]
        
        fm_radio_str = "FM HARDWARE MODULE" if settings.get('FM_RADIO', False) else "FALLOUT RADIOS"
        
        options = [
            (f"Style: {ui_style_display}", "UI STYLE"),
            (f"Map Selection: {map_preset_label}", "MAP TYPE"),
            (f"Radio: {fm_radio_str}", "RADIO SOURCE"),
            ("Return to Main Menu", "BACK")
        ]
        
        display_header("SYSTEM MODES CONFIGURATION")
        draw_menu(options, selected)
        
        key = get_key()
        if key == 'up' and selected > 0:
            selected -= 1
        elif key == 'down' and selected < len(options) - 1:
            selected += 1
        elif key == 'enter':
            if selected == 0:
                current_style = settings.get('UI_STYLE', 'Fallout_4')
                settings['UI_STYLE'] = "Fallout_NV" if current_style == "Fallout_4" else "Fallout_4"
            elif selected == 1:
                # Passa alla mappa successiva tra le 5 disponibili
                next_map_idx = (current_map_idx + 1) % len(MAP_PRESETS)
                preset = MAP_PRESETS[next_map_idx]
                settings['REAL_MAP'] = preset['REAL_MAP']
                settings['FAKE_LOCATION'] = preset['FAKE_LOCATION']
                settings['SHOW_ALL_MARKERS'] = preset['SHOW_ALL_MARKERS']
            elif selected == 2:
                settings['FM_RADIO'] = not settings.get('FM_RADIO', False)
            elif selected == 3:
                return
        elif key == 'esc':
            return

def main():
    PipBoyDisplay.clear()
    PipBoyDisplay.typewriter(f"{PipBoyTheme.Color.PRIMARY.value}INITIALIZING VAULT-TEC CONFIGURATION SYSTEM...")
    PipBoyDisplay.loading_animation()
    
    settings = parse_settings()
    selected = 0
    
    while True:
        options = [
            ("Player Configuration", "STATUS: ONLINE"),
            ("Display Settings", "COLOR PROFILE"),
            ("System Preferences", "ADVANCED OPTIONS"),
            ("Data Types", "REAL DATA: ACQUIRED"),
            ("Save & Exit Program", "WRITE TO MEMORY")
        ]
        
        display_header("MAIN SYSTEM MENU")
        draw_menu(options, selected)
        
        key = get_key()
        if key == 'up' and selected > 0:
            selected -= 1
        elif key == 'down' and selected < len(options)-1:
            selected += 1
        elif key == 'enter':
            if selected == 0:
                player_settings_menu(settings)
            elif selected == 1:
                color_settings_menu(settings)
            elif selected == 2:
                system_settings_menu(settings)
            elif selected == 3:
                system_mode_menu(settings)
            elif selected == 4:
                PipBoyDisplay.typewriter(f"{PipBoyTheme.Color.PRIMARY.value}SAVING CONFIGURATION TO MEMORY...")
                PipBoyDisplay.loading_animation()
                update_user_config(settings)
                PipBoyDisplay.typewriter(f"{PipBoyTheme.Color.ACCENT.value}CONFIGURATION SAVED TO {USER_CONFIG_FILE}")
                time.sleep(1)
                return
        elif key == 'esc':
            return
        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{PipBoyTheme.Color.WARNING.value}TERMINAL INTERRUPTED - EXITING SAFE MODE{PipBoyTheme.Color.RESET.value}")