import pygame
import settings
from .status_tab import StatusTab
from .special_tab import SpecialTab
from .perks_tab import PerksTab 
from .general_tab import GeneralTab
from tab import ThreadHandler
import ui as ui
from .skills_tab import draw_skills_tab

class StatTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        self.current_sub_tab_index = 0
        
        self.dynamic_footer_text = [
            ("HP", settings.HP_CURRENT, settings.HP_MAX),
            ("LEVEL", settings.LEVEL),
            ("AP", settings.AP_CURRENT, settings.AP_MAX),
            ("XP", settings.XP_CURRENT)
        ]
        
        self.footer_font = tab_instance.footer_font
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 2), self.init_footer_text())
        
        self.status_tab = StatusTab(self.screen, self.tab_instance, self.draw_space)
        self.special_tab = SpecialTab(self.screen, self.tab_instance, self.draw_space)
        self.perks_tab = PerksTab(self.screen, self.tab_instance, self.draw_space) 
        self.general_tab = GeneralTab(self.screen, self.tab_instance, self.draw_space)
        
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        
        if ui_style == 'fallout_nv':
            sub_tab_map = {
                0: self.status_tab,
                1: self.special_tab,
                2: None, # Skills
                3: self.perks_tab,
                4: self.general_tab
            }
        else:
            # Mappa Fallout 4: STATUS (0), SPECIAL (1), PERKS (2), SKILLS (3)
            sub_tab_map = {
                0: self.status_tab,
                1: self.special_tab,
                2: self.perks_tab
            }
        
        # Rimuovi la riga duplicata che c'era prima
        self.sub_tab_thread_handler = ThreadHandler(sub_tab_map, self.current_sub_tab_index)
    
    def init_footer_text(self): 
        hp_string = f"{self.dynamic_footer_text[0][0]} {self.dynamic_footer_text[0][1]}/{self.dynamic_footer_text[0][2]}"
        level_string = f"{self.dynamic_footer_text[1][0]} {self.dynamic_footer_text[1][1]}"
        ap_string = f"{self.dynamic_footer_text[2][0]} {self.dynamic_footer_text[2][1]}/{self.dynamic_footer_text[2][2]}"
        
        hp_surface = self.footer_font.render(hp_string, True, settings.PIP_BOY_LIGHT)
        level_surface = self.footer_font.render(level_string, True, settings.PIP_BOY_LIGHT)
        ap_surface = self.footer_font.render(ap_string, True, settings.PIP_BOY_LIGHT)
        
        xp_rect_base = pygame.Rect(
            level_surface.get_width() + settings.SCREEN_WIDTH // 3.6, 
            (settings.BOTTOM_BAR_HEIGHT // 1.7) // 2, 
            settings.SCREEN_WIDTH // 3.2, 
            settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 1.8)
        )
        xp_rect = xp_rect_base.copy()
        xp_rect.width = xp_rect.width * (settings.XP_CURRENT / 100)
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        footer_surface.blit(hp_surface, (2, 2))
        footer_surface.blit(level_surface, (settings.SCREEN_WIDTH // 3.8, 2))
        pygame.draw.rect(footer_surface, settings.PIP_BOY_LIGHT, xp_rect)
        pygame.draw.rect(footer_surface, settings.PIP_BOY_DARKER, xp_rect_base, 1)
        footer_surface.blit(ap_surface, (settings.SCREEN_WIDTH // 1.2, 2))
        
        return footer_surface
    
    def change_sub_tab(self, sub_tab: int):
        self.current_sub_tab_index = sub_tab
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)

    def handle_threads(self, tab_selected: bool):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)
        
    def handle_input(self, event):
        """Inoltra l'input alla scheda attiva se necessario."""
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_style == 'fallout_nv':
            if self.current_sub_tab_index == 3:
                self.perks_tab.handle_input(event)
            elif self.current_sub_tab_index == 4 and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.general_tab.toggle_mode()
        else:
            if self.current_sub_tab_index == 2:
                self.perks_tab.handle_input(event)

    def _scroll_skills(self, direction: bool):
        skills_count = len(getattr(settings, 'DEFAULT_SKILLS', []))
        if skills_count > 0:
            delta = -1 if direction else 1
            self.selected_skill_index = (getattr(self, 'selected_skill_index', 0) + delta) % skills_count

    def scroll(self, direction: bool):
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        
        if ui_style == 'fallout_nv':
            match self.current_sub_tab_index:
                case 0: self.status_tab.scroll(direction)
                case 1: self.special_tab.scroll_special(direction)
                case 2: self._scroll_skills(direction)
                case 3: self.perks_tab.scroll_perks(direction)
                case 4: self.general_tab.scroll_general(direction)
                case _: pass
        else:
            match self.current_sub_tab_index:
                case 0: self.status_tab.scroll(direction)
                case 1: self.special_tab.scroll_special(direction)
                case 2: self.perks_tab.scroll_perks(direction)
                case 3: self._scroll_skills(direction)
                case _: pass

    def select_item(self):
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        if ui_style == 'fallout_nv' and self.current_sub_tab_index == 4:
            self.general_tab.toggle_mode()

    def render(self):
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        
        if ui_style != 'fallout_nv':
            self.tab_instance.render_footer(self)

        if ui_style == 'fallout_nv':
            match self.current_sub_tab_index:
                case 0: self.status_tab.render()
                case 1: self.special_tab.render()
                case 2:
                    skills_data = getattr(settings, 'DEFAULT_SKILLS', [])
                    selected_idx = getattr(self, 'selected_skill_index', 0)
                    draw_skills_tab(
                        self.screen, skills_data, selected_idx,
                        settings.PIP_BOY_LIGHT, self.footer_font,
                        settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
                    )
                case 3: self.perks_tab.render()
                case 4: self.general_tab.render()
        else:
            match self.current_sub_tab_index:
                case 0: self.status_tab.render()
                case 1: self.special_tab.render()
                case 2: self.perks_tab.render()
                case 3:
                    skills_data = getattr(settings, 'DEFAULT_SKILLS', [])
                    selected_idx = getattr(self, 'selected_skill_index', 0)
                    draw_skills_tab(
                        self.screen, skills_data, selected_idx,
                        settings.PIP_BOY_LIGHT, self.footer_font,
                        settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
                    )
                    
