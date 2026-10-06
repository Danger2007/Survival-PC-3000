from datetime import datetime
import pygame
from .quest_tab import QuestsTab
from .notes_tab import NotesTab
from .settings_tab import SettingsTab
from .workshops_tab import WorkshopsTab
from .stats_tab import StatsTab
from tab import ThreadHandler
import settings


class DataTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        # 0-QUESTS, 1-WORKSHOPS, 2-STATS, 3-NOTES, 4-SETTINGS
        self.current_sub_tab_index = 0
    
        self.footer_font = tab_instance.footer_font
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 11)
        
        self.tab_instance.init_footer(
            self, 
            (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
            self._init_footer_text()
        )
        
        self.quests_tab = QuestsTab(self.screen, self.tab_instance, self.draw_space)
        self.workshops_tab = WorkshopsTab(self.screen, self.tab_instance, self.draw_space)
        self.stats_tab = StatsTab(self.screen, self.tab_instance, self.draw_space)
        self.notes_tab = NotesTab(self.screen, self.tab_instance, self.draw_space)
        self.settings_tab = SettingsTab(self.screen, self.tab_instance, self.draw_space)
        
        sub_tab_map = {
            0: self.quests_tab,
            1: self.workshops_tab,
            2: self.stats_tab,
            3: self.notes_tab,
            4: self.settings_tab
        }
        
        self.sub_tab_thread_handler = ThreadHandler(sub_tab_map, self.current_sub_tab_index)

    def _init_footer_text(self):
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        return footer_surface

    def get_active_subtab(self):
        match self.current_sub_tab_index:
            case 0: return self.quests_tab
            case 1: return self.workshops_tab
            case 2: return self.stats_tab
            case 3: return self.notes_tab
            case 4: return self.settings_tab
            case _: return self

    def is_editing(self):
        active = self.get_active_subtab()
        if active and active != self and hasattr(active, 'is_editing'):
            return active.is_editing()
        return False

    def handle_x_press(self):
        active = self.get_active_subtab()
        if active and active != self and hasattr(active, 'handle_x_press'):
            active.handle_x_press()

    def change_sub_tab(self, sub_tab: int):
        ui_style = str(getattr(settings, 'UI_STYLE', 'fallout_4')).lower()
        is_nv = any(k in ui_style for k in ['nv', 'new_vegas', 'newvegas', 'fnv'])

        # Se siamo in modalità Fallout: New Vegas, salta WORKSHOPS (1) e STATS (2)
        if is_nv and sub_tab in (1, 2):
            return

        self.current_sub_tab_index = sub_tab
        self.sub_tab_thread_handler.update_tab_index(sub_tab)

    def scroll(self, direction: bool):
        active = self.get_active_subtab()
        if active and hasattr(active, 'scroll'):
            active.scroll(direction)

    def select_item(self):
        active = self.get_active_subtab()
        if active and hasattr(active, 'select_item'):
            return active.select_item()
        return False

    def handle_threads(self, tab_selected: bool):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)

    def _render_system_datetime(self):
        color_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
        ui_style = str(getattr(settings, 'UI_STYLE', 'fallout_4')).lower()
        is_nv = any(k in ui_style for k in ['nv', 'new_vegas', 'newvegas', 'fnv'])

        now = datetime.now()
        date_str = now.strftime("%m.%d.%Y")
        time_str = now.strftime("%I:%M %p")

        date_surf = self.font_small.render(date_str, True, color_light)
        time_surf = self.font_small.render(time_str, True, color_light)

        bottom_bar_h = getattr(settings, 'BOTTOM_BAR_HEIGHT', 25)
        footer_top = settings.SCREEN_HEIGHT - bottom_bar_h
        cell_width = settings.SCREEN_WIDTH // 3

        pos_y = footer_top + (bottom_bar_h - date_surf.get_height()) // 2
        date_x = 6
        time_x = cell_width + 6

        if is_nv:
            pos_y -= 20
        else:
            time_x -= 30

        self.screen.blit(date_surf, (date_x, pos_y))
        self.screen.blit(time_surf, (time_x, pos_y))

    def render(self):
        self.tab_instance.render_footer(self)
        active = self.get_active_subtab()
        if active and hasattr(active, 'render'):
            active.render()
        self._render_system_datetime()

    def toggle_focus(self):
        active = self.get_active_subtab()
        if active and hasattr(active, 'toggle_focus'):
            active.toggle_focus()