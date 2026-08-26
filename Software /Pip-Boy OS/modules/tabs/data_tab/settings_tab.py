# settings_tab.py
import os
import pygame
import ast
from threading import Thread
from ui import GenericList
from items import Inventory
import settings
from util_functs import Utils

class SettingsTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.category = "Settings"
        
        self.inv_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.footer_font = tab_instance.footer_font
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        TABS_DIR = os.path.dirname(CURRENT_DIR)
        MODULES_DIR = os.path.dirname(TABS_DIR)
        self.config_path = os.path.join(MODULES_DIR, 'user_config.py')
        
        self._init_icons()
        self._load_settings()
        self._init_list()
        
    def _init_icons(self):
        self.big_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 4)
        self.save_icon = Utils.load_svg(self.big_icon_size, settings.GUN_ICON)
        
    def _load_settings(self):
        self.settings = []
        with open(self.config_path, 'r') as f:
            lines = f.readlines()

        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith('# ---'):
                current_section = line.split('- ')[-1].strip()
            elif ' = ' in line and not line.startswith('#'):
                var_name, value = line.split(' = ', 1)
                var_name = var_name.strip()
                raw_value = value.split('#')[0].strip()
                
                self.settings.append({
                    'section': current_section,
                    'var_name': var_name,
                    'display_name': ' '.join(var_name.split('_')).title(),
                    'value': ast.literal_eval(raw_value),
                    'type': type(ast.literal_eval(raw_value)),
                    'comment': value.split('#')[1].strip() if '#' in value else ''
                })
                
    def _init_list(self):
        self.list_draw_space = pygame.Rect(
            self.draw_space.left + 20,
            self.draw_space.top + settings.LIST_TOP_MARGIN,
            self.draw_space.width - 40,
            self.draw_space.height - settings.LIST_TOP_MARGIN * 2
        )
        
        items = [s['display_name'] for s in self.settings]
        self.settings_list = GenericList(
            draw_space=self.list_draw_space,
            font=self.inv_font,
            items=items,
            enable_dot=True        )
        
    def select_item(self):
        current_setting = self.settings[self.settings_list.selected_index]
        if current_setting['type'] == bool:
            current_setting['value'] = not current_setting['value']
        elif current_setting['type'] in (int, float):
            # Will be handled via increment/decrement in adjust_setting
            pass
            
    def adjust_setting(self, increment=True):
        current = self.settings[self.settings_list.selected_index]
        if current['type'] == int:
            current['value'] = max(0, current['value'] + (1 if increment else -1))
        elif current['type'] == float:
            current['value'] = round(max(0.0, current['value'] + (0.1 if increment else -0.1)), 1)

    def scroll(self, direction: bool):
        pass
        
    def save_settings(self):
        output = []
        current_section = None
        with open(self.config_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('# ---'):
                current_section = stripped.split('- ')[-1].strip()
                output.append(line)
            elif ' = ' in stripped and not stripped.startswith('#'):
                var_name = stripped.split(' = ')[0].strip()
                setting = next((s for s in self.settings if s['var_name'] == var_name), None)
                if setting:
                    comment = f'  # {setting["comment"]}' if setting["comment"] else ''
                    new_line = f"{var_name} = {repr(setting['value'])}{comment}\n"
                    output.append(new_line)
                else:
                    output.append(line)
            else:
                output.append(line)

        with open(self.config_path, 'w') as f:
            f.writelines(output)

    def render(self):        
        pass