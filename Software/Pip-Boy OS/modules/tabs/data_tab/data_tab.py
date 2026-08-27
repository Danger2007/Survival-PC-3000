import pygame
# from .quests_tab import QuestsTab
# from .workshops_tab import WorkshopsTab
# from .stats_tab import StatsTab
from .settings_tab import SettingsTab
from tab import ThreadHandler
import settings


class DataTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        self.current_sub_tab_index = 0  # 0-Quests, 1-Workshops, 2-Stats
    
        
        self.footer_font = tab_instance.footer_font
        
        self.tab_instance.init_footer(
            self, 
            (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
            self._init_footer_text()
        )
        
        # self.quests_tab = QuestsTab(self.screen, self.tab_instance, self.draw_space)
        # self.workshops_tab = WorkshopsTab(self.screen, self.tab_instance, self.draw_space)
        # self.stats_tab = StatsTab(self.screen, self.tab_instance, self.draw_space)
        
        self.settings_tab = SettingsTab(self.screen, self.tab_instance, self.draw_space)
        
        sub_tab_map = {
            # 0: self.quests_tab,
            # 1: self.workshops_tab,
            # 2: self.stats_tab,
            3: self.settings_tab
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
                # self.quests_tab.scroll(direction)
                pass
            case 1:  # Workshops
                # self.workshops_tab.scroll(direction)
                pass
            case 2:  # Stats
                # self.stats_tab.scroll(direction)
                pass
            case 3:  # Settings
                self.settings_tab.scroll(direction)
            case _:  # DEFAULT
                pass

    def select_item(self):
        match self.current_sub_tab_index:
            case 0:  # Quests
                # self.quests_tab.select_item()
                pass
            case 1:  # Workshops
                # self.workshops_tab.select_item()
                pass
            case 2:  # Stats
                # self.stats_tab.select_item()
                pass
            case 3:  # Settings
                self.settings_tab.select_item()
            case _:  # DEFAULT
                pass

    def handle_threads(self, tab_selected: bool):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)

    def render(self):
        self.tab_instance.render_footer(self)
        
        match self.current_sub_tab_index:
            case 0:  # Quests
                # self.quests_tab.render()
                pass
            case 1:  # Workshops
                # self.workshops_tab.render()
                pass
            case 2:  # Stats
                # self.stats_tab.render()
                pass
            case 3:  # Settings
                self.settings_tab.render()
            case _:  # DEFAULT
                pass