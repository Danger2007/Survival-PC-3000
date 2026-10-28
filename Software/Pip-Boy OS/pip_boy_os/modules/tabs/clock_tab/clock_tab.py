import pygame
import settings
from util_functs import Utils
import threading
import urllib.request
import json
import os
from datetime import datetime

class ClockTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        # Fonts
        self.font_title = pygame.font.Font(settings.MAIN_FONT_PATH, 14)
        self.font_clock = pygame.font.Font(settings.MAIN_FONT_PATH, 54)
        self.font_date = pygame.font.Font(settings.MAIN_FONT_PATH, 16)
        self.font_sub = pygame.font.Font(settings.MAIN_FONT_PATH, 12)

        # Starting values for weather and temperature (Fallback)
        self.temperature = "--°C"
        self.weather_label = "CONNECTING..."
        self.current_icon = None
        
        self._load_icons()
        self._start_weather_thread()

    def _tint_image(self, image, color):
        """Colors an image with the specified color while preserving its alpha channel."""
        tinted = image.copy()
        tinted.fill(color[:3] + (0,), special_flags=pygame.BLEND_RGB_MULT)
        return tinted

    def _load_icons(self):
        """Loads weather icons from the specified directory (images/svgs/weather_icons) and tints them with the Pip-Boy light color."""
        weather_dir = os.path.join(settings.BASE_DIR, 'images', 'svgs', 'weather_icons')
        self.icons = {}
        
        icon_names = [
            'sunny', 'moon', 'cloudy', 'fog', 'windy', 'dawn_dusk',
            'mostly-cloudy-day', 'mostly-cloudy-night', 
            'partially-cloudy-day', 'partially-cloudy-night',
            'slightly-raining', 'raining', 'heavily-raining',
            'partially-raining-day', 'partially-raining-night',
            'snowing', 'partially-snowing-day', 'partially-snowing-night', 'snowing-windy',
            'hailing', 'hailing-raining', 'raining-snowing',
            'thunderstorm', 'heavy-thunderstorm', 'thunderstorm-hailing',
            'thunderstorm-scattered-day', 'thunderstorm-scattered-night'
        ]
        
        for name in icon_names:
            path = os.path.join(weather_dir, f"{name}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (34, 34))
                    self.icons[name] = self._tint_image(img, settings.PIP_BOY_LIGHT)
                except Exception:
                    pass

    def _get_icon_and_label(self, desc: str):
        """Returns the appropriate icon and label based on the weather description."""
        desc = desc.lower()
        hour = datetime.now().hour
        is_night = hour < 6 or hour > 20

        if 'thunder' in desc or 'storm' in desc or 'lightning' in desc:
            if 'hail' in desc:
                return self.icons.get('thunderstorm-hailing') or self.icons.get('thunderstorm'), "THUNDERSTORM"
            if 'heavy' in desc or 'strong' in desc:
                return self.icons.get('heavy-thunderstorm') or self.icons.get('thunderstorm'), "HEAVY STORM"
            icon = self.icons.get('thunderstorm-scattered-night' if is_night else 'thunderstorm-scattered-day') or self.icons.get('thunderstorm')
            return icon, "THUNDERSTORM"
        
        elif 'hail' in desc:
            return self.icons.get('hailing'), "HAIL"
        elif 'sleet' in desc or 'mix' in desc or 'raining-snowing' in desc:
            return self.icons.get('raining-snowing') or self.icons.get('hailing-raining'), "RAIN & SNOW"
            
        elif 'snow' in desc or 'blizzard' in desc:
            if 'wind' in desc:
                return self.icons.get('snowing-windy'), "BLIZZARD"
            icon = self.icons.get('partially-snowing-night' if is_night else 'partially-snowing-day') if 'partly' in desc else self.icons.get('snowing')
            return icon, "SNOWING"
            
        elif 'heavy rain' in desc or 'torrential' in desc or 'downpour' in desc:
            return self.icons.get('heavily-raining'), "HEAVY RAIN"
        elif 'light' in desc or 'drizzle' in desc or 'patchy' in desc:
            return self.icons.get('slightly-raining'), "LIGHT RAIN"
        elif 'rain' in desc or 'shower' in desc:
            icon = self.icons.get('partially-raining-night' if is_night else 'partially-raining-day') if 'patchy' in desc or 'light' in desc else self.icons.get('raining')
            return icon, "RAINING"
            
        elif 'wind' in desc or 'gale' in desc:
            return self.icons.get('windy'), "WINDY"
        elif 'fog' in desc or 'mist' in desc or 'haze' in desc:
            return self.icons.get('fog'), "FOGGY"
            
        elif 'overcast' in desc or 'cloud' in desc:
            if 'partly' in desc or 'scattered' in desc or 'few' in desc:
                return self.icons.get('partially-cloudy-night' if is_night else 'partially-cloudy-day'), "PARTLY CLOUDY"
            if 'mostly' in desc or 'broken' in desc:
                return self.icons.get('mostly-cloudy-night' if is_night else 'mostly-cloudy-day'), "MOSTLY CLOUDY"
            return self.icons.get('cloudy'), "CLOUDY"
            
        elif 'dawn' in desc or 'dusk' in desc or 'sunset' in desc or 'sunrise' in desc:
            return self.icons.get('dawn_dusk'), "DAWN / DUSK"
        elif is_night:
            return self.icons.get('moon'), "CLEAR NIGHT"
            
        return self.icons.get('sunny') or self.icons.get('cloudy'), "SUNNY"

    def _start_weather_thread(self):
        def fetch_weather():
            try:
                # Checks if REAL_LOCATION is defined in settings.py (as settings imports REAL_LOCATION from settings_secret this check is always true)
                location = getattr(settings, 'REAL_LOCATION', None)
                
                # If for some reason REAL_LOCATION is unavailable, it uses FAKE_LOCATION (creating random data)
                if not location or location == 'YOUR_REAL_LOCATION':
                    location = getattr(settings, 'FAKE_LOCATION', 'Rome')
                
                url = f"https://wttr.in/{urllib.parse.quote(location)}?format=j1"
                
                req = urllib.request.Request(url, headers={'User-Agent': 'PipBoy-Terminal'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    current = data['current_condition'][0]
                    temp_c = current['temp_C']
                    desc = current['weatherDesc'][0]['value']
                    
                    self.temperature = f"{temp_c}°C"
                    self.current_icon, self.weather_label = self._get_icon_and_label(desc)
            except Exception:
                self.temperature = "N/A"
                self.weather_label = "RAD-STORM"
                self.current_icon = self.icons.get('cloudy')

        t = threading.Thread(target=fetch_weather, daemon=True)
        t.start()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            return "dismiss_screensaver"
        return None

    def scroll(self, direction: bool):
        pass

    def render(self):
        COLOR_LIGHT = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))

        # 1. Fullscreen background and border
        screen_rect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
        self.screen.fill((0, 8, 0))  
        pygame.draw.rect(self.screen, COLOR_LIGHT, screen_rect, 2)

        # 2. Header
        header_rect = pygame.Rect(screen_rect.left + 15, screen_rect.top + 12, screen_rect.width - 30, 26)
        title_surf = self.font_title.render("VAULT-TEC SYSTEM SCREENSAVER // ACTIVE", True, COLOR_LIGHT)
        self.screen.blit(title_surf, (header_rect.left, header_rect.top))
        
        divider_y = header_rect.bottom + 4
        pygame.draw.line(self.screen, COLOR_LIGHT, (screen_rect.left + 15, divider_y), (screen_rect.right - 15, divider_y), 1)

        # 3. Central clock
        current_time_str = Utils.get_time()
        clock_surf = self.font_clock.render(current_time_str, True, COLOR_LIGHT)
        clock_rect = clock_surf.get_rect(center=(screen_rect.centerx, screen_rect.centery - 25))
        self.screen.blit(clock_surf, clock_rect)

        # 4. Date
        current_date_str = Utils.get_date()
        date_surf = self.font_date.render(current_date_str, True, COLOR_LIGHT)
        date_rect = date_surf.get_rect(center=(screen_rect.centerx, clock_rect.bottom + 12))
        self.screen.blit(date_surf, date_rect)

        # 5. Weather and temperature
        y_pos = date_rect.bottom + 22
        weather_text = f"{self.weather_label}    TEMP: {self.temperature}"
        weather_surf = self.font_sub.render(weather_text, True, COLOR_LIGHT)

        if self.current_icon:
            spacing = 10
            # Block's totaal width (icon + spacing + text)
            total_block_width = self.current_icon.get_width() + spacing + weather_surf.get_width()
            
            # Point of origin for the block to be centered on the screen
            start_x = screen_rect.centerx - (total_block_width // 2)
            
            # Icons and text positioning
            icon_rect = self.current_icon.get_rect(x=start_x, centery=y_pos)
            weather_rect = weather_surf.get_rect(x=icon_rect.right + spacing, centery=y_pos)
            
            self.screen.blit(self.current_icon, icon_rect)
            self.screen.blit(weather_surf, weather_rect)
        else:
            weather_rect = weather_surf.get_rect(center=(screen_rect.centerx, y_pos))
            self.screen.blit(weather_surf, weather_rect)

        # 6. Footer
        footer_y = screen_rect.bottom - 22
        pygame.draw.line(self.screen, COLOR_LIGHT, (screen_rect.left + 15, footer_y - 8), (screen_rect.right - 15, footer_y - 8), 1)
        
        press_surf = self.font_sub.render("PRESS ANY KEY TO RESUME TERMINAL SESSION", True, COLOR_LIGHT)
        press_rect = press_surf.get_rect(center=(screen_rect.centerx, footer_y + 4))
        self.screen.blit(press_surf, press_rect)