import hashlib
import io
import json
import math
import os
import random
from threading import Lock, Thread
import requests
import pygame
import settings
from typing import Tuple, List, Dict, Optional
from pygame.math import Vector2
from PIL import Image
from util_functs import Utils




class BaseMap:
    def __init__(self, screen: pygame.Surface, draw_space: pygame.Rect, 
        map_image: pygame.Surface):
        self.screen = screen
        self.draw_space = draw_space
        self.map_image = map_image
        self.map_surface = map_image.copy()

        # Zoom configuration
        self.min_zoom = self._calculate_min_zoom()
        self.max_zoom = settings.MIN_MAP_ZOOM
        self.map_zoom = max(min(settings.INITIAL_MAP_ZOOM, self.max_zoom), self.min_zoom)

        # Navigation state
        self.zoomed_map_surface = self._update_zoomed_surface()
        self.map_offset = Vector2(self._calculate_initial_offset())
        self.directions = [
            (-settings.MAP_MOVE_SPEED, 0),   # Left
            (0, -settings.MAP_MOVE_SPEED),   # Up
            (0, settings.MAP_MOVE_SPEED),  # Down
            (settings.MAP_MOVE_SPEED, 0)   # Right
        ]
        
        self.is_initialized = True

    def _calculate_initial_offset(self) -> Vector2:
        """Calculate initial offset to center the map."""
        return Vector2(
            (self.zoomed_map_surface.get_width() - self.draw_space.width) / 2,
            (self.zoomed_map_surface.get_height() - self.draw_space.height) / 2
        )

    def _update_zoomed_surface(self) -> pygame.Surface:
        """Update zoomed surface using smooth scaling."""
        new_size = Vector2(self.map_surface.get_size()) * self.map_zoom
        return pygame.transform.smoothscale(self.map_surface, new_size.xy)

    def _calculate_min_zoom(self) -> float:
        """Calculate minimum zoom to fit image within draw space."""
        img_size = Vector2(self.map_surface.get_size())
        draw_size = Vector2(self.draw_space.size)
        return max(draw_size.x / img_size.x, draw_size.y / img_size.y)

    def clamp_offset(self):
        """Keep map offset within valid bounds."""
        zoomed_size = Vector2(self.zoomed_map_surface.get_size())
        draw_size = Vector2(self.draw_space.size)
        max_offset = zoomed_size - draw_size

        # Ensure map_offset is a Vector2
        if not isinstance(self.map_offset, Vector2):
            self.map_offset = Vector2(self.map_offset)

        # Clamp the offset
        for axis in [0, 1]:  # 0 for x, 1 for y
            if zoomed_size[axis] < draw_size[axis]:
                self.map_offset[axis] = (zoomed_size[axis] - draw_size[axis]) / 2
            else:
                self.map_offset[axis] = max(0, min(self.map_offset[axis], max_offset[axis]))

    def zoom(self, zoom_in: bool):
        """Zoom while maintaining view center."""
        old_zoom = self.map_zoom
        zoom_step = old_zoom * settings.MAP_ZOOM_SPEED
        new_zoom = old_zoom + zoom_step if zoom_in else old_zoom - zoom_step
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

        if new_zoom == old_zoom:
            return

        # Calculate original center position
        view_center = Vector2(self.draw_space.center) - Vector2(self.draw_space.topleft)
        orig_center = (Vector2(self.map_offset) + view_center) / old_zoom

        # Update zoom state
        self.map_zoom = new_zoom
        self.zoomed_map_surface = self._update_zoomed_surface()
        self.map_offset = orig_center * new_zoom - view_center
        self.clamp_offset()

    def navigate(self, direction: int):
        """
        Move the map view in one of four directions.
        :param direction: 0: right, 1: down, 2: up, 3: left.
        """
        if 0 <= direction < 4:
            if not isinstance(self.map_offset, Vector2):
                self.map_offset = Vector2(self.map_offset)
            dx, dy = self.directions[direction]
            self.map_offset += Vector2(dx, dy)
            self.clamp_offset()


    def render(self):
        """Draw the visible portion of the map."""
        src_rect = pygame.Rect(*self.map_offset, *self.draw_space.size)
        src_rect.clamp(self.zoomed_map_surface.get_rect())
        self.screen.blit(self.zoomed_map_surface, self.draw_space.topleft, src_rect)

class WorldMap(BaseMap):
    def __init__(self, screen: pygame.Surface, draw_space: pygame.Rect):
        fake_loc = str(getattr(settings, 'FAKE_LOCATION', 'Commonwealth')).lower()
        show_markers = getattr(settings, 'SHOW_ALL_MARKERS', True)
        
        # File path selection based on location and marker settings (/images/worldmap for fallout 4 or /images/new_vegas_icons/map_nv for fallout new vegas)
        if 'mojave' in fake_loc:
            map_path = settings.MOJAVE_MAP_MARKERS if show_markers else settings.MOJAVE_MAP
        else:
            map_path = (getattr(settings, 'COMMONWEALTH_MAP_MARKERS', '') if show_markers 
                        else getattr(settings, 'COMMONWEALTH_MAP', ''))
            
        # Loads the map image and checks for alternative extensions if not found
        if not map_path or not os.path.exists(map_path):
            base_no_ext, _ = os.path.splitext(map_path)
            for ext in ['.webp', '.png', '.jpg', '.jpeg']:
                test_path = base_no_ext + ext
                if os.path.exists(test_path):
                    map_path = test_path
                    break
                    
        map_image = Utils.tint_image(pygame.image.load(map_path).convert_alpha())
        super().__init__(screen, draw_space, map_image)


class RealMap(BaseMap):
    """Dynamic real-world map using Geoapify and OpenStreetMap API."""    

    def __init__(self, screen: pygame.Surface, draw_space: pygame.Rect, 
                 api_zoom: int = 13):
        
        self.screen = screen
        self.lat, self.lon = settings.LATITUDE, settings.LONGITUDE
        self.api_zoom = api_zoom
        self.draw_space = draw_space
        
        # Loads icons if the folder exists
        if hasattr(settings, 'MAP_ICONS_BASE_FOLDER') and os.path.exists(settings.MAP_ICONS_BASE_FOLDER):
            self.icons = Utils.load_svgs_dict(settings.MAP_ICONS_BASE_FOLDER, settings.MAP_ICON_SIZE)
        else:
            self.icons = {}

        self.failed_connection = False

        self._cache_lock = Lock()
        self._places_cache_lock = Lock()
        self.rendered_map_lock = Lock()
        
        self.is_initialized = False
        Thread(target=self.init_map, daemon=True).start()

    # Blocks zoom if connection fails
    def zoom(self, zoom_in: bool):
        if self.failed_connection:
            return
        super().zoom(zoom_in)

    # Blocks navigation if connection fails
    def navigate(self, direction: int):
        if self.failed_connection:
            return
        super().navigate(direction)

    def init_map(self):
        image = self._fetch_map_image()
        places = self._fetch_places(image) if not self.failed_connection else []
        rendered_map = self._draw_markers(image, places) if not self.failed_connection else image
        
        # Initialises the base code with the image rendered
        super().__init__(self.screen, self.draw_space, rendered_map)

    def _invert_surface(self, surface: pygame.Surface) -> pygame.Surface:
        """Converte la superficie in scala di grigi ed inverte usando PIL per eliminare ogni sfumatura di colore."""
        # Converts the Pygame Surface in a string of Pixel RGB values
        raw_str = pygame.image.tostring(surface, 'RGBA')
        pil_img = Image.frombytes('RGBA', surface.get_size(), raw_str)
        
        # Converts to a grey scale
        gray_img = pil_img.convert('L')
        
        # Inverts the grey scale (0 = Black, 255 = White)
        inv_gray = Image.eval(gray_img, lambda x: 255 - x)
        
        # Re-converts in RGB for Pygame
        inv_rgba = inv_gray.convert('RGBA')
        
        # Returns as a Pygame Surface
        return pygame.image.fromstring(inv_rgba.tobytes(), inv_rgba.size, 'RGBA')

    def _fetch_map_image(self) -> pygame.Surface:
        """Retrieve map image with caching."""
        os.makedirs(settings.MAP_CACHE, exist_ok=True)
        filename = f"{self.lat:.6f}_{self.lon:.6f}_{self.api_zoom}_{settings.MAP_SIZE}.png"
        cache_path = os.path.join(settings.MAP_CACHE, filename)

        # If image is in the cache
        if os.path.exists(cache_path):
            map_img = pygame.image.load(cache_path).convert_alpha()
            self.failed_connection = False
            # Inverts colors and applies the Pip-Boy selected color theme
            map_img_inverted = self._invert_surface(map_img)
            return Utils.tint_image(map_img_inverted)

        # Building of the Geoapify URL
        api_key = getattr(settings, 'GEOAPIFY_API_KEY', '') or getattr(settings, 'GEOAPIFY_KEY', '')
        url = (
            f"https://maps.geoapify.com/v1/staticmap"
            f"?style=klokantech-basic"
            f"&width={settings.MAP_SIZE}&height={settings.MAP_SIZE}"
            f"&center=lonlat:{self.lon},{self.lat}"
            f"&zoom={self.api_zoom}"
            f"&apiKey={api_key}"
        )
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            with open(cache_path, "wb") as f:
                f.write(response.content)

            map_img = pygame.image.load(io.BytesIO(response.content)).convert_alpha()
            self.failed_connection = False
            
            # Inverts colors and applies the Pip-Boy selected color theme
            map_img_inverted = self._invert_surface(map_img)
            return Utils.tint_image(map_img_inverted)
            
        except Exception as e:
            print(f"ERROR MAP API: {e}")
            self.failed_connection = True
            map_img = pygame.Surface((settings.MAP_SIZE, settings.MAP_SIZE))
            if hasattr(settings, 'PIP_BOY_DARK'):
                map_img.fill(settings.PIP_BOY_DARK)
            return map_img

    def _fetch_places(self, map_image: pygame.Surface) -> list:
        """
        Placeholder for fetching POIs from an API. Currently returns an empty list.
        """
        return []

    def _draw_markers(self, map_image: pygame.Surface, places: list) -> pygame.Surface:
        surface = map_image.copy()
        center_x = surface.get_width() // 2
        center_y = surface.get_height() // 2
        
        # Creates a simple cursor for the user's location
        color = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        points = [
            (center_x, center_y - 8),
            (center_x - 6, center_y + 6),
            (center_x + 6, center_y + 6)
        ]
        pygame.draw.polygon(surface, color, points)
        
        return surface

    def render(self):
        if self.failed_connection: # Fallback Image in case of connection failure
            # Dark background for no connection
            bg_color = settings.PIP_BOY_DARK if hasattr(settings, 'PIP_BOY_DARK') else (0, 0, 0)
            self.screen.fill(bg_color, self.draw_space)

            # Rectangle
            box_w, box_h = 160, 50
            box_x = self.draw_space.x + (self.draw_space.width - box_w) // 2
            box_y = self.draw_space.y + (self.draw_space.height - box_h) // 2
            
            pygame.draw.rect(self.screen, settings.PIP_BOY_LIGHT, (box_x, box_y, box_w, box_h), 2)
            
            # Text "NO CONNECTION"
            map_font = pygame.font.Font(settings.TECH_MONO_FONT_PATH, 12)
            text_surface = map_font.render("NO CONNECTION", True, settings.PIP_BOY_LIGHT)
            text_x = box_x + (box_w - text_surface.get_width()) // 2
            text_y = box_y + (box_h - text_surface.get_height()) // 2
            self.screen.blit(text_surface, (text_x, text_y))
        else:
            super().render()