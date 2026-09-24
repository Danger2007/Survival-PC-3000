import os
from threading import Thread, Lock
import pygame
import settings
from tab import ThreadHandler
from .world_tab import WorldMap, RealMap
from datetime import datetime
from util_functs import Utils


class MapTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        ui_style = str(getattr(settings, 'UI_STYLE', 'fallout_4')).lower()
        if ui_style in ('fallout_nv', 'fallout_new_vegas'):
            top_margin = getattr(settings, 'TOP_BAR_HEIGHT', 35)
            bottom_margin = 30
            
            self.draw_space = pygame.Rect(
                draw_space.x,
                top_margin,
                draw_space.width,
                settings.SCREEN_HEIGHT - top_margin - bottom_margin
            )
        else:
            self.draw_space = draw_space

        self.current_sub_tab_index = 0
        self.footer_font = tab_instance.footer_font
        self.date = Utils.get_date()
        self.time = Utils.get_time()

        if getattr(settings, 'REAL_MAP', False):
            self.world_map_subtab = RealMap(self.screen, self.draw_space, settings.MAP_ZOOM)
        else:
            self.world_map_subtab = WorldMap(self.screen, self.draw_space)

        # --- Impostazioni Zoom Local / World Map ---
        initial_zoom = 1.0
        if hasattr(self.world_map_subtab, 'zoom_level'):
            initial_zoom = self.world_map_subtab.zoom_level
        elif hasattr(self.world_map_subtab, 'map_zoom'):
            initial_zoom = self.world_map_subtab.map_zoom

        self.world_zoom = initial_zoom  # Zoom per World Map (invariato)
        self.local_zoom = 2.2           # Zoom per Local Map (più zoommata)
        self.is_local_map = None
                
        self.tab_instance.init_footer(
            self, 
            (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
            self._init_footer_text()
        )
 
        sub_tab_map = {
            0: self.world_map_subtab
        }
        
        self.footer_time_thread = Thread(target=self.update_footer_time, daemon=True)
        self.sub_tab_thread_handler = ThreadHandler(sub_tab_map, self.current_sub_tab_index)
        
        self.datetime_lock = Lock()
        self.footer_time_thread.start()

    def _get_current_zoom(self) -> float:
        if hasattr(self.world_map_subtab, 'zoom_level'):
            return self.world_map_subtab.zoom_level
        elif hasattr(self.world_map_subtab, 'map_zoom'):
            return self.world_map_subtab.map_zoom
        return self.local_zoom if self.is_local_map else self.world_zoom

    def _apply_zoom(self, target_zoom: float):
        """Applica lo zoom assoluto alla mappa senza eseguire zoom relativi"""
        if hasattr(self.world_map_subtab, 'set_zoom') and callable(getattr(self.world_map_subtab, 'set_zoom')):
            self.world_map_subtab.set_zoom(target_zoom)
        elif hasattr(self.world_map_subtab, 'zoom_level'):
            self.world_map_subtab.zoom_level = target_zoom
        elif hasattr(self.world_map_subtab, 'map_zoom'):
            self.world_map_subtab.map_zoom = target_zoom

    def set_map_mode(self, is_local: bool):
        """Method to switch between local and world map modes, preserving zoom levels"""
        if self.is_local_map == is_local:
            return

        # Saves the current zoom level before switching modes
        if self.is_local_map is not None:
            current_zoom = self._get_current_zoom()
            if self.is_local_map:
                self.local_zoom = current_zoom
            else:
                self.world_zoom = current_zoom

        self.is_local_map = is_local
        target_zoom = self.local_zoom if is_local else self.world_zoom
        self._apply_zoom(target_zoom)

    def _blit_footer_time(self):
        time_surface = self.footer_font.render(self.time, True, settings.PIP_BOY_LIGHT)
        self.tab_instance.update_footer(self, time_surface, (settings.SCREEN_WIDTH // 4 + 4, 2))

    def _init_footer_text(self):
        """Create surface with map-related footer information"""
        date_surface = self.footer_font.render(self.date, True, settings.PIP_BOY_LIGHT)
        location_surface = self.footer_font.render(
            settings.FAKE_LOCATION if settings.GAME_ACCURATE_MODE else settings.REAL_LOCATION, 
            True, 
            settings.PIP_BOY_LIGHT
        )
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA)
        footer_surface.blit(date_surface, (2, 2))
        footer_surface.blit(location_surface, (settings.SCREEN_WIDTH - location_surface.width - 2, 2))
        
        return footer_surface

    def change_sub_tab(self, sub_tab: int):
        self.current_sub_tab_index = sub_tab
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)

    def scroll(self, direction: bool):
        if self.world_map_subtab.is_initialized:
            self.world_map_subtab.zoom(direction)
            new_zoom = self._get_current_zoom()
            if self.is_local_map:
                self.local_zoom = new_zoom
            else:
                self.world_zoom = new_zoom

    def update_footer_time(self):
        while True:
            self.time = Utils.get_time()
            self._blit_footer_time()
            now = datetime.now()
            wait_time = 60 - now.second
            pygame.time.wait(wait_time * 1000)
            
    def navigate(self, direction: int):
        if self.world_map_subtab.is_initialized:
            self.world_map_subtab.navigate(direction)

    def handle_threads(self, tab_selected: bool):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)

    def render(self):
        self.tab_instance.render_footer(self)
        match self.current_sub_tab_index:
            case 0:  # Map View
                if self.world_map_subtab.is_initialized:
                    self.world_map_subtab.render()