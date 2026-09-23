from datetime import datetime
import pygame
from .quest_tab import QuestsTab
# from .workshops_tab import WorkshopsTab
# from .stats_tab import StatsTab
from .notes_tab import NotesTab
from .settings_tab import SettingsTab
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
        # Font per la data e l'ora nel footer
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 11)
        
        self.tab_instance.init_footer(
            self, 
            (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
            self._init_footer_text()
        )
        
        self.quests_tab = QuestsTab(self.screen, self.tab_instance, self.draw_space)
        # self.workshops_tab = WorkshopsTab(self.screen, self.tab_instance, self.draw_space)
        # self.stats_tab = StatsTab(self.screen, self.tab_instance, self.draw_space)
        self.notes_tab = NotesTab(self.screen, self.tab_instance, self.draw_space)
        self.settings_tab = SettingsTab(self.screen, self.tab_instance, self.draw_space)
        
        sub_tab_map = {
            0: self.quests_tab,
            # 1: self.workshops_tab,
            # 2: self.stats_tab,
            3: self.notes_tab,
            4: self.settings_tab
        }
        
        self.sub_tab_thread_handler = ThreadHandler(sub_tab_map, self.current_sub_tab_index)

    def _init_footer_text(self):
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        return footer_surface

    def change_sub_tab(self, sub_tab: int):
        self.current_sub_tab_index = sub_tab
        self.sub_tab_thread_handler.update_tab_index(sub_tab)

    def scroll(self, direction: bool):
        match self.current_sub_tab_index:
            case 0:  # Quests
                self.quests_tab.scroll(direction)
            case 1:  # Workshops
                pass
            case 2:  # Stats
                pass
            case 3:  # Notes
                self.notes_tab.scroll(direction)
            case 4:  # Settings
                self.settings_tab.scroll(direction)
            case _:
                pass

    def select_item(self):
        match self.current_sub_tab_index:
            case 0:  # Quests
                self.quests_tab.select_item()
            case 1:  # Workshops
                pass
            case 2:  # Stats
                pass
            case 3:  # Notes
                self.notes_tab.select_item()
            case 4:  # Settings
                self.settings_tab.select_item()
            case _:
                pass

    def handle_threads(self, tab_selected: bool):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)

    def _render_system_datetime(self):
        """Renders the current system date and time in the footer area."""
        color_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
        ui_style = str(getattr(settings, 'UI_STYLE', 'Fallout_4')).lower()
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
        
        match self.current_sub_tab_index:
            case 0:  # Quests
                self.quests_tab.render()
            case 1:  # Workshops
                pass
            case 2:  # Stats
                pass
            case 3:  # Notes
                self.notes_tab.render()
            case 4:  # Settings
                self.settings_tab.render()
            case _:
                pass

        # Disegna la data e l'ora sopra il footer renderizzato
        self._render_system_datetime()

    def toggle_focus(self):
        match self.current_sub_tab_index:
            case 0:  # Quests
                if hasattr(self.quests_tab, 'toggle_focus'):
                    self.quests_tab.toggle_focus()
            case 3:  # Notes
                if hasattr(self.notes_tab, 'toggle_focus'):
                    self.notes_tab.toggle_focus()
            case 4:  # Settings
                if hasattr(self.settings_tab, 'toggle_focus'):
                    self.settings_tab.toggle_focus()
            case _:
                pass