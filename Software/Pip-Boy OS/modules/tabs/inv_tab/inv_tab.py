import pygame
import settings
from .weapons_tab import WeaponsTab
from .apparel_tab import ApparelTab
from .aid_tab import AidTab
from .junk_tab import JunkTab
from .misc_tab import MiscTab
from .ammo_tab import AmmoTab
from .inv_base import InvBase
from tab import ThreadHandler


class InvTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.footer_font = getattr(tab_instance, 'footer_font', None)
        
        self.weapons_tab = WeaponsTab(self.screen, self.tab_instance, self.draw_space)
        self.apparel_tab = ApparelTab(self.screen, self.tab_instance, self.draw_space)
        self.aid_tab = AidTab(self.screen, self.tab_instance, self.draw_space)
        self.misc_tab = MiscTab(self.screen, self.tab_instance, self.draw_space)
        self.junk_tab = JunkTab(self.screen, self.tab_instance, self.draw_space)
        self.mods_tab = InvBase(self.screen, self.tab_instance, self.draw_space, category='Mods', enable_turntable=True)
        self.ammo_tab = AmmoTab(self.screen, self.tab_instance, self.draw_space)
        
        self.current_sub_tab_index = 0
        self.sub_tabs = []
        self.sub_tab_thread_handler = None
        
        self.refresh_tab_layout()

    def refresh_tab_layout(self):
        """
        Configura la lista delle sotto-schede in base allo stile grafico attivo (FO4 vs NV).
        """
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        is_nv = ui_style == 'fallout_nv'
        
        # Rigenera MiscTab per caricare il corretto insieme di categorie
        self.misc_tab = MiscTab(self.screen, self.tab_instance, self.draw_space)

        if is_nv:
            # Layout Fallout New Vegas (5 Tab: Misc accorpa Misc, Junk e Mods)
            self.sub_tabs = [
                self.weapons_tab, # 0
                self.apparel_tab, # 1
                self.aid_tab,     # 2
                self.misc_tab,    # 3
                self.ammo_tab     # 4
            ]
        else:
            # Layout Fallout 4 (7 Tab)
            self.sub_tabs = [
                self.weapons_tab, # 0: WEAPONS
                self.apparel_tab, # 1: APPAREL
                self.aid_tab,     # 2: AID
                self.misc_tab,    # 3: MISC
                self.junk_tab,    # 4: JUNK
                self.mods_tab,    # 5: MODS
                self.ammo_tab     # 6: AMMO
            ]

        sub_tab_map = {i: tab for i, tab in enumerate(self.sub_tabs)}
        self.sub_tab_thread_handler = ThreadHandler(sub_tab_map, self.current_sub_tab_index)

    def get_current_tab(self):
        if 0 <= self.current_sub_tab_index < len(self.sub_tabs):
            return self.sub_tabs[self.current_sub_tab_index]
        return None

    def change_sub_tab(self, sub_tab: int):
        if not self.sub_tabs:
            return
            
        if sub_tab >= len(self.sub_tabs):
            sub_tab = len(self.sub_tabs) - 1
        elif sub_tab < 0:
            sub_tab = 0
            
        self.current_sub_tab_index = sub_tab
        if self.sub_tab_thread_handler:
            self.sub_tab_thread_handler.update_tab_index(sub_tab)

    def scroll(self, direction: bool):
        current = self.get_current_tab()
        if current and hasattr(current, 'scroll'):
            current.scroll(direction)

    def select_item(self):
        current = self.get_current_tab()
        if current and hasattr(current, 'select_item'):
            current.select_item()

    def handle_threads(self, tab_selected: bool):
        if self.sub_tab_thread_handler:
            self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)

    def render(self):
        current = self.get_current_tab()
        if current and hasattr(current, 'render'):
            current.render()