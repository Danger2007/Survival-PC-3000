from datetime import datetime
from threading import Thread, Lock
import pygame
from .quest_tab import QuestsTab
from .notes_tab import NotesTab
from .settings_tab import SettingsTab
from .workshops_tab import WorkshopsTab
from .stats_tab import StatsTab
from util_functs import Utils
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
        self.date = Utils.get_date()
        self.time = Utils.get_time()
        
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

        # Thread per l'aggiornamento dinamico dell'orario
        self.footer_time_thread = Thread(target=self.update_footer_time, daemon=True)
        self.footer_time_thread.start()

    def _blit_footer_time(self):
        time_surface = self.footer_font.render(self.time, True, settings.PIP_BOY_LIGHT)
        self.tab_instance.update_footer(self, time_surface, (settings.SCREEN_WIDTH // 4 + 4, 2))

    def update_footer_time(self):
        while True:
            self.time = Utils.get_time()
            self._blit_footer_time()
            now = datetime.now()
            wait_time = 60 - now.second
            pygame.time.wait(wait_time * 1000)

    def _init_footer_text(self):
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA)
        date_surface = self.footer_font.render(self.date, True, settings.PIP_BOY_LIGHT)
        location_surface = self.footer_font.render(
            settings.FAKE_LOCATION if getattr(settings, 'GAME_ACCURATE_MODE', False) else getattr(settings, 'REAL_LOCATION', ''), 
            True, 
            settings.PIP_BOY_LIGHT
        )
        footer_surface.blit(date_surface, (2, 2))
        footer_surface.blit(location_surface, (settings.SCREEN_WIDTH - location_surface.get_width() - 2, 2))
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

    def render(self):
        self.tab_instance.render_footer(self)
        active = self.get_active_subtab()
        if active and hasattr(active, 'render'):
            active.render()

    def toggle_focus(self):
        active = self.get_active_subtab()
        if active and hasattr(active, 'toggle_focus'):
            active.toggle_focus()