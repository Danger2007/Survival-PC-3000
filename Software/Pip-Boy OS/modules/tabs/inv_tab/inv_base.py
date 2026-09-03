import os
import re
from threading import Thread, Lock
import pygame
import settings
from ui import GenericList, AnimatedImage, WireframeItem
from items import Inventory
from util_functs import Utils


class InvBase:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect, category: str, enable_turntable: bool = True, enable_dot: bool = False):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.enable_turntable = enable_turntable
        
        # Normalizza la categoria (es. "AMMO" -> "Ammo", "MISC" -> "Misc") per renderla dinamica tra stili
        self.category = category.strip().title() if isinstance(category, str) else category
        
        # Cache per memorizzare i frame dell'animazione caricati in memoria o i fallback
        self._anim_cache = {}
        
        self.inv_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.footer_font = tab_instance.footer_font              
        inventory = Inventory()
        self.inv_items = inventory.get_all_items(self.category)
        self.weight = sum(item.weight for item in inventory.get_all_items())
        self._init_icons()
        
        self.no_items = True if not self.inv_items else False
        if self.no_items:
            return
                
        self.item_selected = False
        self.active_item_index = None
        self.previous_item_index = None
        
        self.unique_items = inventory.get_unique_items(self.category)
        
        item_names = inventory.get_item_names(self.category)
        self.list_draw_space = pygame.Rect(
            self.draw_space.left,
            self.draw_space.top + 2 * settings.LIST_TOP_MARGIN,
            (self.draw_space.centerx + (self.draw_space.centerx // 6)) - 10,
            self.draw_space.height - 2 * settings.LIST_TOP_MARGIN
        )
        
        self.inv_list = GenericList(
            draw_space=self.list_draw_space,
            font=self.inv_font,
            items=item_names,
            enable_dot=enable_dot,
        )
        
        if self.enable_turntable:
            self._init_turntable()

    def _init_turntable(self):
        center_x = (settings.SCREEN_WIDTH // 2) + 80
        turntable_width = (self.draw_space.right - self.list_draw_space.right - settings.GRID_RIGHT_MARGIN) - 20
        turntable_height = self.list_draw_space.height // 2
        self.turntable_draw_space = pygame.Rect(0, 0, turntable_width, turntable_height)
        self.turntable_draw_space.center = (center_x, self.draw_space.top + (turntable_height // 2))
        self.turntable_lock = Lock
        self.item_turntable = None

    def _init_icons(self):
        self.big_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 4)
        self.small_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 2)
        
        self.weight_icon = Utils.load_svg(self.big_icon_size, settings.WEIGHT_ICON)
        self.caps_icon = Utils.load_svg(self.big_icon_size, settings.CAPS_ICON)
        
        self.damage_icons = {
            dtype: Utils.load_svg(self.small_icon_size, path)
            for dtype, path in settings.DAMAGE_TYPES_ICONS.items()
        }        

    def _find_item_folder(self, item) -> str | None:
        """
        Cerca dinamicamente la cartella dell'oggetto scansionando l'intera directory
        'images/inventory/' (incluse sottocartelle come items, armor, weapons, ecc.).
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tabs_dir = os.path.dirname(current_dir)
        modules_dir = os.path.dirname(tabs_dir)
        project_root = os.path.dirname(modules_dir)
        inv_base_dir = os.path.join(project_root, "images", "inventory")

        if not os.path.exists(inv_base_dir):
            return None

        def normalize(text: str) -> str:
            return re.sub(r'[^a-zA-Z0-9]', '', text).lower() if text else ""

        targets = {normalize(getattr(item, 'icons', '')), normalize(getattr(item, 'name', ''))}
        targets.discard("")

        if not targets:
            return None

        for root, dirs, _ in os.walk(inv_base_dir):
            for dir_name in dirs:
                if normalize(dir_name) in targets:
                    return os.path.join(root, dir_name)

        return None

    def _create_fallback_image(self) -> pygame.Surface:
        """
        Crea la superficie di fallback "IMAGE NOT FOUND":
        - Stile Fallout_NV: Riquadro vuoto (bordo 2px) con testo PIP_BOY_LIGHT (Invariato).
        - Stile Fallout_4: Riquadro pieno PIP_BOY_MIDDLE con testo PIP_BOY_LIGHT.
        """
        w = max(20, self.turntable_draw_space.width + 10)
        h = max(20, self.turntable_draw_space.height - 50)
        
        surf = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
        color_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
        color_middle = getattr(settings, "PIP_BOY_MIDDLE", (0, 191, 0))
        ui_style = getattr(settings, "UI_STYLE", "Fallout_NV")
        is_fo4 = ui_style == "Fallout_4"

        if is_fo4:
            # Stile Fallout 4: Sfondo PIP_BOY_MIDDLE e testo PIP_BOY_LIGHT
            surf.fill(color_middle)
            text_surf = self.inv_font.render("IMAGE NOT FOUND", True, (0,0,0))
        else:
            # Stile New Vegas: Riquadro vuoto con bordo e testo PIP_BOY_LIGHT
            pygame.draw.rect(surf, color_light, surf.get_rect(), width=1)
            text_surf = self.inv_font.render("IMAGE NOT FOUND", True, color_light)

        text_rect = text_surf.get_rect(center=(w // 2, h // 2))
        surf.blit(text_surf, text_rect)
        return surf

    def select_item(self):    
        if self.no_items:
            return
        
        if self.inv_list.selected_index == self.active_item_index:
            self.item_selected = not self.item_selected
        else:
            self.item_selected = True  
        self.active_item_index = self.inv_list.selected_index

    def scroll(self, direction: bool):
        if self.no_items:
            return
        prev_index = self.inv_list.change_selection(direction)

        if self.enable_turntable and self.inv_list.selected_index != prev_index:
            Thread(target=self.start_item_animation).start() 
        
    def init_footer_weight(self):
        weight_text = f"{self.weight}/{settings.MAX_CARRY_WEIGHT}"
        weight_surface = self.footer_font.render(weight_text, True, settings.PIP_BOY_LIGHT)
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        y_pos = settings.BOTTOM_BAR_HEIGHT // 2 - weight_surface.get_height() // 2
        footer_surface.blit(self.weight_icon, (y_pos, 3))
        footer_surface.blit(weight_surface, (self.weight_icon.get_width() + settings.BOTTOM_BAR_MARGIN, 2))

        return footer_surface

    def init_footer_caps(self):
        caps_text = f"{settings.CAPS}"
        caps_surface = self.footer_font.render(caps_text, True, settings.PIP_BOY_LIGHT)
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        y_pos = settings.BOTTOM_BAR_HEIGHT // 2 - caps_surface.get_height() // 2
        footer_surface.blit(self.caps_icon, (settings.SCREEN_WIDTH // 4 + 4, y_pos))
        footer_surface.blit(caps_surface, (settings.SCREEN_WIDTH // 4 + self.caps_icon.get_width() + settings.BOTTOM_BAR_MARGIN, 2))

        return footer_surface

    def start_item_animation(self):
        if self.item_turntable:
            self.item_turntable.stop()
            self.item_turntable = None
            
        if not self.unique_items or self.inv_list.selected_index >= len(self.unique_items):
            return

        selected_item = self.unique_items[self.inv_list.selected_index]   
        item_key = selected_item.name

        # Verifica prima la cache
        if item_key in self._anim_cache:
            icons = self._anim_cache[item_key]
        else:
            folder_path = self._find_item_folder(selected_item)
            icons = []

            if folder_path:
                loaded = Utils.load_images(folder_path)
                if loaded:
                    if isinstance(loaded, dict):
                        icons = list(loaded.values())
                    elif isinstance(loaded, list) and len(loaded) > 0 and isinstance(loaded[0], tuple):
                        icons = [item[1] for item in loaded]
                    elif isinstance(loaded, list):
                        icons = loaded

                    # Ridimensiona solo le immagini reali caricate da disco
                    icons = [Utils.scale_image_abs(img, height=self.turntable_draw_space.height) for img in icons if img]

            # Se non sono state trovate immagini valide su disco, genera il riquadro di fallback
            if not icons:
                icons = [self._create_fallback_image()]

            self._anim_cache[item_key] = icons
                
        class Animation2D:
            def __init__(self, screen, center_pos, images, frame_duration):
                self.screen = screen
                self.center_pos = center_pos
                self.images = images
                self.frame_duration = frame_duration
                self.current_frame = 0
                self.last_update = pygame.time.get_ticks()

            def start(self):
                pass

            def stop(self):
                pass

            def render(self):
                now = pygame.time.get_ticks()
                if now - self.last_update > self.frame_duration:
                    self.current_frame = (self.current_frame + 1) % len(self.images)
                    self.last_update = now
        
                img = self.images[self.current_frame]
                img_rect = img.get_rect(center=self.center_pos)
                self.screen.blit(img, img_rect)

        self.item_turntable = Animation2D(
            self.screen,
            self.turntable_draw_space.center,
            icons,
            frame_duration=settings.SPEED * 100
        )
        self.item_turntable.start()

    def handle_threads(self, tab_selected: bool):
        """ Handle the threads"""
        if self.no_items:
            return
        if tab_selected and self.enable_turntable:
            Thread(target=self.start_item_animation).start()
        elif not tab_selected and self.enable_turntable and self.item_turntable:
            self.item_turntable.stop()
            self.item_turntable = None
            
    def calculate_grid_space(self):
        list_space = self.list_draw_space
        grid_top = list_space.top + (list_space.height * 0.38)
        grid_height = list_space.bottom - grid_top
        
        center_x = (settings.SCREEN_WIDTH // 2) + 80
        grid_width = (self.draw_space.right - list_space.right - settings.GRID_RIGHT_MARGIN) - 20
        
        grid_rect = pygame.Rect(0, 0, grid_width, grid_height)
        grid_rect.centerx = center_x
        grid_rect.top = grid_top
        return grid_rect
        
    def render(self):
        self.tab_instance.render_footer(self)
        if self.no_items:
            return
        self.inv_list.render(self.screen, self.active_item_index, self.item_selected)
        if self.enable_turntable and self.item_turntable:
            self.item_turntable.render()