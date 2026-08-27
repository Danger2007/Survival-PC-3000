import pygame
from .weapons_tab import WeaponsTab
from .apparel_tab import ApparelTab
from .aid_tab import AidTab
from .junk_tab import JunkTab
from .misc_tab import MiscTab
from .ammo_tab import AmmoTab
from tab import ThreadHandler


class InvTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        self.current_sub_tab_index = 0  # 0-Weapons, 1-Apparel, 2-Aid, 3-Misc, 4-Junk, 5-Mods, 6-Ammo#
        
        self.footer_font = tab_instance.footer_font
        
        self.weapons_tab = WeaponsTab(self.screen, self.tab_instance, self.draw_space)
        self.apparel_tab = ApparelTab(self.screen, self.tab_instance, self.draw_space)
        self.aid_tab = AidTab(self.screen, self.tab_instance, self.draw_space)
        self.misc_tab = MiscTab(self.screen, self.tab_instance, self.draw_space)
        self.junk_tab = JunkTab(self.screen, self.tab_instance, self.draw_space)
        # self.mods_tab = ModsTab(self.screen, self.tab_instance, self.draw_space)
        self.ammo_tab = AmmoTab(self.screen, self.tab_instance, self.draw_space)
        
        
        sub_tab_map = {
            0: self.weapons_tab,
            1: self.apparel_tab,
            2: self.aid_tab,
            3: self.misc_tab,
            4: self.junk_tab,
            # 5: None,
            6: self.ammo_tab
        }
        
        self.sub_tab_thread_handler = ThreadHandler(sub_tab_map, self.current_sub_tab_index)



    def change_sub_tab(self, sub_tab: int):
        self.current_sub_tab_index = sub_tab
        self.sub_tab_thread_handler.update_tab_index(sub_tab)


    def scroll(self, direction: bool):
        match self.current_sub_tab_index:
            case 0: # Weapons
                self.weapons_tab.scroll(direction)
            case 1: # Apparel
                self.apparel_tab.scroll(direction)
            case 2: # Aid
                self.aid_tab.scroll(direction)
            case 3: # Misc
                self.misc_tab.scroll(direction)
            case 4: # Junk
                self.junk_tab.scroll(direction)
            case 5: # Mods
                pass
            case 6: # Ammo
                self.ammo_tab.scroll(direction)
            case _: # DEFAULT
                pass


    def select_item(self):
        match self.current_sub_tab_index:
            case 0: # Weapons
                self.weapons_tab.select_item()
            case 1: # Apparel
                self.apparel_tab.select_item()
            case 2: # Aid
                self.aid_tab.select_item()
            case 3: # Misc
                self.misc_tab.select_item()
            case 4: # Junk
                self.junk_tab.select_item()
            case 5: # Mods
                pass
            case 6: # Ammo
                self.ammo_tab.select_item()
            case _: # DEFAULT
                pass


                
        
    def handle_threads(self, tab_selected: bool):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)
    


    def render(self):
        match self.current_sub_tab_index:
            case 0: # Weapons
                self.weapons_tab.render()
            case 1: # Apparel
                self.apparel_tab.render()
            case 2: # Aid
                self.aid_tab.render()
            case 3: # Misc
                self.misc_tab.render()
            case 4: # Junk
                self.junk_tab.render()
            case 5: # Mods
                pass
            case 6: # Ammo
                self.ammo_tab.render()
            case _: # DEFAULT
                pass
        
