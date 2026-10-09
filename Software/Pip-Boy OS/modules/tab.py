import datetime
import os
import pygame
import settings
try:
    import user_config
except ImportError:
    user_config = None
from threading import Thread
from typing import Callable, Dict, Optional

class ThreadHandler:
    """
    A generic handler that manages a mapping between tab indices and their
    associated thread functions, as well as tracking the current and previous
    tab indices. When the tab index is updated, the previous index is stored
    internally, and you can start threads for both tabs accordingly.
    """
    def __init__(self, tab_map: Dict[int, Callable[[bool], None]], initial_tab_index: Optional[int] = None):
        """
        :param tab_map: A dictionary mapping tab indices to a callable
                        that takes a boolean flag.
        :param initial_tab_index: Optionally, set an initial current tab index.
        """
        self.tab_map = tab_map
        self.current_tab_index = initial_tab_index
        self.previous_tab_index = None
        
        self.handle_current_tab()

    def update_tab_index(self, new_index: int):
        """
        Update the current tab index. The old current index becomes the previous tab index.
        
        :param new_index: The new current tab index.
        """
        self.previous_tab_index = self.current_tab_index
        self.current_tab_index = new_index

        if self.current_tab_index != self.previous_tab_index:
            self.handle_current_tab()
            self.handle_previous_tab()        

    def _start_thread(self, tab_index: int, flag: bool) -> None:
        """
        Internal method to start a thread for the tab associated with tab_index.
        
        :param tab_index: The index of the tab.
        :param flag: The boolean flag to pass to the thread function.
        """

        tab = self.tab_map.get(tab_index)
        if tab:
            func = getattr(tab, f"handle_threads", None)  # Get the start or stop method dynamically
            if func and callable(func):
                Thread(target=func, args=(flag,)).start()            

    def handle_current_tab(self) -> None:
        """
        Starts a thread for the current tab with flag True.
        """
        if self.current_tab_index is not None:
            self._start_thread(self.current_tab_index, True)

    def handle_previous_tab(self) -> None:
        """
        Starts a thread for the previous tab with flag False.
        """
        if self.previous_tab_index is not None:
            self._start_thread(self.previous_tab_index, False)



class Tab:
    def __init__(self, screen):
        self.footer_font = pygame.font.Font(settings.ROBOTO_CONDENSED_BOLD_PATH, 12)
        self.screen = screen
        
        now = datetime.datetime.now()
        self.current_date = now.strftime("%d.%m.")
        
        # 1. Recupera DATE_MODE da user_config (se presente), altrimenti da settings
        date_mode = getattr(user_config, 'DATE_MODE', None) if user_config else None
        if date_mode is None:
            date_mode = getattr(settings, 'DATE_MODE', 'Game')
            
        # 2. Recupera UI_STYLE nello stesso modo per sicurezza
        ui_style = getattr(user_config, 'UI_STYLE', None) if user_config else None
        if ui_style is None:
            ui_style = getattr(settings, 'UI_STYLE', '')
        ui_style = str(ui_style).lower()

        # 3. Imposta l'anno in base al valore effettivamente sovrascritto
        if date_mode == 'Real':
            self.current_year = now.strftime("%Y")
        elif date_mode == 'Game':
            if ui_style == 'fallout_nv':
                self.current_year = "2281"
            else:
                self.current_year = "2287"
        else:
            self.current_year = now.strftime("%Y")
            
        self.tab_footers = {}

    def init_footer(self, object, margins=None, text_surface=None):
        key = object
        
        # Create a new surface for the footer
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT))
        footer_surface.fill(settings.PIP_BOY_DARK)
        
        if margins is not None:
            line = 0
            for margin in margins:
                line += margin - settings.BOTTOM_BAR_VERTICAL_MARGINS // 2
                pygame.draw.line(
                    footer_surface,
                    settings.BACKGROUND,
                    (line, 0),
                    (line, settings.BOTTOM_BAR_HEIGHT),
                    settings.BOTTOM_BAR_VERTICAL_MARGINS  # Line width
                )
                
        if text_surface is not None:
            if isinstance(text_surface, (list, tuple)):
                for item in text_surface:
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        footer_surface.blit(item[0], item[1])
                    elif isinstance(item, pygame.Surface):
                        footer_surface.blit(item, (0, 0))
            else:
                footer_surface.blit(text_surface, (0, 0))
            
            
        # Store the surface in the dictionary
        self.tab_footers[key] = footer_surface
        
        
    # Update footer and only the part of the footer that needs to be updated    
    def update_footer(self, object, text_surface, destination=(0, 0)):
        # clear the nescary part of the footer
        self.tab_footers[object].fill(settings.PIP_BOY_DARK, (destination[0], destination[1], text_surface.get_width(), text_surface.get_height()))
        
        # Blit the updated text to the footer
        self.tab_footers[object].blit(
            text_surface,
            (destination)
        )

        
    def render_footer(self, object):
        if str(getattr(settings, 'UI_STYLE', '')).lower() == 'fallout_nv':
            return
        # Blit the pre-rendered footer to the screen
        self.screen.blit(
            self.tab_footers[object],
            (0, settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT)
        )
        
