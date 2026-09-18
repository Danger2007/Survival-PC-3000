import os
import re
import random
from threading import Lock
import pygame
import settings
from ui import GenericList
from items import Inventory
from util_functs import Utils


class InvBase:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect, category, enable_turntable: bool = True, enable_dot: bool = False):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.enable_turntable = enable_turntable
        
        # Searching for UI Style (Fallout New Vegas vs Fallout 4)
        self.ui_style = str(getattr(settings, 'UI_STYLE', 'Fallout_4')).lower()
        self.is_nv = any(k in self.ui_style for k in ['nv', 'new_vegas', 'newvegas', 'fnv'])

        # Header Configuration and Styling
        if self.is_nv:
            self.header_text_left = ") ITEMS"
            self.top_margin_spacing = 18
            if hasattr(self.tab_instance, 'header_text_left'):
                setattr(self.tab_instance, 'header_text_left', ") ITEMS")
            if hasattr(self.tab_instance, 'top_margin_spacing'):
                setattr(self.tab_instance, 'top_margin_spacing', 18)
            self._suppress_fo4_tab_rendering()

        if isinstance(category, (list, tuple)):
            self.category = [c.strip().title() for c in category if isinstance(c, str)]
        elif isinstance(category, str):
            self.category = category.strip().title()
        else:
            self.category = category

        self._anim_cache = {}
        self.inv_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.footer_font = getattr(tab_instance, 'footer_font', self.inv_font)              
        inventory = Inventory()

        # Object Initialization and Inventory Retrieval
        if isinstance(self.category, (list, tuple)):
            self.inv_items = []
            combined_pairs = []
            for cat in self.category:
                self.inv_items.extend(inventory.get_all_items(cat))
                u_items = inventory.get_unique_items(cat)
                names = inventory.get_item_names(cat)
                for item, name in zip(u_items, names):
                    combined_pairs.append((item, name))
            
            combined_pairs.sort(key=lambda pair: getattr(pair[0], 'name', '').lower())
            self.unique_items = [p[0] for p in combined_pairs]
            item_names = [p[1] for p in combined_pairs]
        else:
            self.inv_items = inventory.get_all_items(self.category)
            self.unique_items = inventory.get_unique_items(self.category) if self.inv_items else []
            item_names = inventory.get_item_names(self.category) if self.inv_items else []

        self.weight = sum(getattr(item, 'weight', 0) for item in inventory.get_all_items())
        self._init_icons()

        self.no_items = not bool(self.inv_items)
        self.active_item_index = 0 if self.unique_items else None
        self.previous_item_index = None

        self.item_selected = bool(self.unique_items and self.active_item_index is not None)

        if not self.is_nv and hasattr(self.tab_instance, 'init_footer'):
            self.tab_instance.init_footer(
                self, 
                (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
                self.init_footer_text()
            )

        if self.no_items:
            return

        # Verifies whether the category is equippable (Weapons / Apparel)
        is_equippable = self._is_equippable_category()

        # Geometry list
        if self.is_nv:
            left_margin = 20
            self.list_draw_space = pygame.Rect(
                self.draw_space.left + left_margin,
                self.draw_space.top + 8,
                int(self.draw_space.width * 0.35),
                self.draw_space.height - 16
            )
            self.inv_list = GenericList(
                draw_space=self.list_draw_space,
                font=self.inv_font,
                items=[],
                enable_dot=False,
            )
            self.refresh_list_display()
            self._setup_nv_list_style()
        else:
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
                enable_dot=(enable_dot and is_equippable),
            )
            self._setup_fo4_list_style(enable_dot=is_equippable)

        self.static_image = None
        if self.enable_turntable:
            self._init_turntable()

        if self.unique_items:
            self.update_item_display()

    def _is_equippable_category(self) -> bool:
        """Indicates whether the current category is equippable (Weapons / Apparel)."""
        cat_str = ""
        if isinstance(self.category, (list, tuple)):
            cat_str = " ".join(str(c) for c in self.category).lower()
        elif isinstance(self.category, str):
            cat_str = self.category.lower()
        return any(k in cat_str for k in ["weapon", "arm", "apparel", "armor", "clothing"])

    def refresh_list_display(self):
        """Updates the display names in the inventory list, appending a '+' for items with modifications."""
        if not hasattr(self, 'inv_list') or not self.inv_list or not self.is_nv:
            return

        display_names = []
        if self.unique_items:
            for item in self.unique_items:
                has_mods = bool(
                    getattr(item, 'mods', None) or 
                    getattr(item, 'installed_mods', None) or 
                    getattr(item, 'weapon_mods', None)
                )
                mod_suffix = " +" if has_mods else ""
                display_names.append(f"{item.name}{mod_suffix}")
        
        self.inv_list.items = display_names

    def _setup_nv_list_style(self):
        if not self.is_nv or not hasattr(self, 'inv_list') or not self.inv_list:
            return

        setattr(self.inv_list, 'is_nv', True)
        setattr(self.inv_list, 'outline_only', True)
        setattr(self.inv_list, 'selection_style', 'outline')

        def custom_nv_render(screen, selected_index=None, *args, **kwargs):
            if selected_index is None:
                selected_index = getattr(self.inv_list, 'selected_index', 0)

            items = getattr(self.inv_list, 'items', [])
            font = getattr(self.inv_list, 'font', self.inv_font)
            draw_space = getattr(self.inv_list, 'draw_space', self.list_draw_space)
            
            pip_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))

            if not items:
                return

            row_height = font.get_linesize() + 5
            visible_count = max(1, draw_space.height // row_height)
            
            scroll_offset = getattr(self.inv_list, 'scroll_offset', 0)
            if selected_index < scroll_offset:
                scroll_offset = selected_index
            elif selected_index >= scroll_offset + visible_count:
                scroll_offset = selected_index - visible_count + 1
            setattr(self.inv_list, 'scroll_offset', scroll_offset)

            is_equippable = self._is_equippable_category()

            y = draw_space.top
            for i in range(scroll_offset, min(len(items), scroll_offset + visible_count)):
                item_text = items[i].rstrip()
                is_selected = (i == selected_index)

                item_rect = pygame.Rect(
                    draw_space.left - 4,
                    y - 1,
                    draw_space.width + 6,
                    row_height - 2
                )

                if is_selected:
                    pygame.draw.rect(screen, pip_light, item_rect, width=1)

                sq_size = 5
                sq_x = draw_space.left + 2
                sq_y = item_rect.centery - (sq_size // 2)

                if is_equippable:
                    is_equipped = False
                    if self.unique_items and i < len(self.unique_items):
                        item_obj = self.unique_items[i]
                        is_equipped = bool(
                            getattr(item_obj, 'equipped', False) or 
                            getattr(item_obj, 'is_equipped', False)
                        )

                    if is_equipped:
                        pygame.draw.rect(screen, pip_light, (sq_x, sq_y, sq_size, sq_size))

                text_x = sq_x + sq_size + 5

                txt_surf = font.render(item_text, True, pip_light)
                txt_rect = txt_surf.get_rect(midleft=(text_x, item_rect.centery))
                screen.blit(txt_surf, txt_rect)

                y += row_height

        self.inv_list.render = custom_nv_render

    def _setup_fo4_list_style(self, enable_dot: bool = True):
        if self.is_nv or not hasattr(self, 'inv_list') or not self.inv_list:
            return

        def custom_fo4_render(screen, selected_index=None, *args, **kwargs):
            if selected_index is None:
                selected_index = getattr(self.inv_list, 'selected_index', 0)

            items = getattr(self.inv_list, 'items', [])
            font = getattr(self.inv_list, 'font', self.inv_font)
            draw_space = getattr(self.inv_list, 'draw_space', self.list_draw_space)

            pip_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
            pip_dark = getattr(settings, "PIP_BOY_DARK", (0, 30, 0))

            if not items:
                return

            row_height = font.get_linesize() + 6
            visible_count = max(1, draw_space.height // row_height)

            scroll_offset = getattr(self.inv_list, 'scroll_offset', 0)
            if selected_index < scroll_offset:
                scroll_offset = selected_index
            elif selected_index >= scroll_offset + visible_count:
                scroll_offset = selected_index - visible_count + 1
            setattr(self.inv_list, 'scroll_offset', scroll_offset)

            is_equippable = self._is_equippable_category()

            y = draw_space.top
            for i in range(scroll_offset, min(len(items), scroll_offset + visible_count)):
                item_text = items[i].rstrip()
                is_selected = (i == selected_index)

                item_rect = pygame.Rect(
                    draw_space.left,
                    y,
                    draw_space.width,
                    row_height - 2
                )

                if is_selected:
                    pygame.draw.rect(screen, pip_light, item_rect)
                    text_color = pip_dark
                    sq_color = pip_dark
                else:
                    text_color = pip_light
                    sq_color = pip_light

                sq_size = 6
                sq_x = draw_space.left + 6

                if is_equippable and enable_dot:
                    is_equipped = False
                    if self.unique_items and i < len(self.unique_items):
                        item_obj = self.unique_items[i]
                        is_equipped = bool(
                            getattr(item_obj, 'equipped', False) or 
                            getattr(item_obj, 'is_equipped', False)
                        )

                    sq_y = item_rect.centery - (sq_size // 2)
                    if is_equipped:
                        pygame.draw.rect(screen, sq_color, (sq_x, sq_y, sq_size, sq_size))

                    text_x = sq_x + sq_size + 6
                else:
                    text_x = draw_space.left + 6

                txt_surf = font.render(item_text, True, text_color)
                txt_rect = txt_surf.get_rect(midleft=(text_x, item_rect.centery))
                screen.blit(txt_surf, txt_rect)

                y += row_height

        self.inv_list.render = custom_fo4_render

    def toggle_equip(self):
        """Equip or unequip the currently selected item and updates the interface."""
        if self.no_items or not self.unique_items or self.active_item_index is None:
            return

        if not self._is_equippable_category():
            return

        selected_item = self.unique_items[self.active_item_index]
        is_currently_equipped = bool(
            getattr(selected_item, 'equipped', False) or 
            getattr(selected_item, 'is_equipped', False)
        )

        if is_currently_equipped:
            setattr(selected_item, 'equipped', False)
            setattr(selected_item, 'is_equipped', False)
        else:
            selected_slot = getattr(selected_item, 'slot', None)
            for item in self.unique_items:
                item_slot = getattr(item, 'slot', None)
                if selected_slot is None or item_slot == selected_slot:
                    setattr(item, 'equipped', False)
                    setattr(item, 'is_equipped', False)

            setattr(selected_item, 'equipped', True)
            setattr(selected_item, 'is_equipped', True)

        self.item_selected = True

        # Update the display based on the UI style
        if self.is_nv:
            self.refresh_list_display()
        else:
            if hasattr(self.tab_instance, 'init_footer'):
                self.tab_instance.init_footer(
                    self, 
                    (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
                    self.init_footer_text()
                )

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.toggle_equip()

    def _suppress_fo4_tab_rendering(self):
        if not self.is_nv or not hasattr(self, 'tab_instance') or not self.tab_instance:
            return

        methods_to_disable = [
            'render_footer', 'draw_footer', 
            'render_stats', 'draw_stats', 
            'render_grid', 'draw_grid',
            'render_stats_grid', 'draw_stats_grid',
            'render_item_stats', 'draw_item_stats'
        ]

        for method_name in methods_to_disable:
            if hasattr(self.tab_instance, method_name):
                setattr(self.tab_instance, method_name, lambda *args, **kwargs: None)

    def _get_project_root(self) -> str:
        curr = os.path.abspath(__file__)
        while curr != os.path.dirname(curr):
            curr = os.path.dirname(curr)
            if os.path.exists(os.path.join(curr, "images")):
                return curr
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _init_turntable(self):
        turntable_width = (self.draw_space.right - self.list_draw_space.right - getattr(settings, 'GRID_RIGHT_MARGIN', 10)) - 15
        turntable_height = self.list_draw_space.height // 2

        if self.is_nv:
            right_panel_x = self.list_draw_space.right + 10
            right_panel_width = self.draw_space.right - right_panel_x - 10
            image_area_height = int((self.draw_space.height - 16) * 0.50)

            self.turntable_draw_space = pygame.Rect(
                right_panel_x,
                self.draw_space.top + 8,
                right_panel_width,
                image_area_height
            )
        else:
            center_x = (settings.SCREEN_WIDTH // 2) + 80
            self.turntable_draw_space = pygame.Rect(0, 0, turntable_width, turntable_height)
            self.turntable_draw_space.center = (center_x, self.draw_space.top + (turntable_height // 2))

        self.turntable_lock = Lock()
        self.item_turntable = None

    def _init_icons(self):
        self.big_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 4)
        self.small_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 2)
        
        self.weight_icon = Utils.load_svg(self.big_icon_size, settings.WEIGHT_ICON)
        self.caps_icon = Utils.load_svg(self.big_icon_size, settings.CAPS_ICON)
        
        if hasattr(settings, 'DAMAGE_TYPES_ICONS'):
            self.damage_icons = {
                dtype: Utils.load_svg(self.small_icon_size, path)
                for dtype, path in settings.DAMAGE_TYPES_ICONS.items()
            }

    def _create_fallback_image(self) -> pygame.Surface:
        h = max(20, self.turntable_draw_space.height - 50)
        if self.is_nv:
            w = max(20, self.turntable_draw_space.width - 50)
        else:
            w = max(20, self.turntable_draw_space.width + 10)
    
        surf = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
        color_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
        color_middle = getattr(settings, "PIP_BOY_MIDDLE", (0, 191, 0))

        if not self.is_nv:
            surf.fill(color_middle)
            text_surf = self.inv_font.render("IMAGE NOT FOUND", True, (0, 0, 0))
        else:
            pygame.draw.rect(surf, color_light, surf.get_rect(), width=1)
            text_surf = self.inv_font.render("IMAGE NOT FOUND", True, color_light)

        text_rect = text_surf.get_rect(center=(w // 2, h // 2))
        surf.blit(text_surf, text_rect)
        return surf

    def select_item(self):    
        if self.no_items:
            return
        self.active_item_index = self.inv_list.selected_index
        self.toggle_equip()

    def scroll(self, direction: bool):
        if self.no_items:
            return
        prev_index = self.inv_list.change_selection(direction)
        self.active_item_index = self.inv_list.selected_index

        if self.inv_list.selected_index != prev_index:
            self.item_selected = bool(
                self.unique_items and 
                self.active_item_index is not None and 
                0 <= self.active_item_index < len(self.unique_items)
            )
            self.update_item_display()

    def update_item_display(self):
        if self.is_nv:
            if self.unique_items and self.inv_list.selected_index < len(self.unique_items):
                selected_item = self.unique_items[self.inv_list.selected_index]
                self.static_image = self._load_nv_static_image(selected_item)
                if not self.static_image:
                    self.static_image = self._create_fallback_image()
        else:
            if hasattr(self.tab_instance, 'init_footer'):
                self.tab_instance.init_footer(
                    self, 
                    (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
                    self.init_footer_text()
                )
            if self.enable_turntable:
                self.start_item_animation()

    def _load_nv_static_image(self, item) -> pygame.Surface | None:
        root_dir = self._get_project_root()
        nv_icons_dir = os.path.join(root_dir, "images", "new_vegas_icons")

        cat_str = ""
        if isinstance(self.category, (list, tuple)):
            cat_str = " ".join(str(c) for c in self.category).lower()
        elif isinstance(self.category, str):
            cat_str = self.category.lower()

        cat_subfolders = []
        if "apparel" in cat_str or "armor" in cat_str or "clothing" in cat_str:
            cat_subfolders = ["apparel", "armor", "clothing", "apparel_icons"]
        elif "weapon" in cat_str or "arm" in cat_str:
            cat_subfolders = ["weapons", "weapon", "weapons_icons"]
        elif "aid" in cat_str or "food" in cat_str:
            cat_subfolders = ["aid", "food", "medical", "aid_icons"]
        elif "misc" in cat_str:
            cat_subfolders = ["misc", "miscellaneous", "misc_icons"]
        elif "ammo" in cat_str or "junk" in cat_str:
            cat_subfolders = ["ammo", "junk", "ammo_icons"]

        direct_paths = []
        for attr in ['image', 'icon', 'icon_path', 'img', 'texture', 'path']:
            val = getattr(item, attr, None)
            if isinstance(val, str) and val:
                direct_paths.extend([
                    val,
                    os.path.join(root_dir, val),
                    os.path.join(root_dir, "images", val),
                    os.path.join(nv_icons_dir, val),
                    os.path.join(root_dir, "images", "inventory", val)
                ])
                for sub in cat_subfolders:
                    direct_paths.append(os.path.join(nv_icons_dir, sub, val))

        for p in direct_paths:
            if os.path.isfile(p):
                return self._process_loaded_image(p)

        candidate_strings = []
        for attr in ['name', 'icon', 'icons', 'image', 'icon_path', 'id']:
            val = getattr(item, attr, None)
            if isinstance(val, (list, tuple)):
                candidate_strings.extend([e for e in val if isinstance(e, str)])
            elif isinstance(val, str) and val:
                candidate_strings.append(val)

        def normalize(text: str) -> str:
            return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower() if text else ""

        def extract_words(text: str) -> set:
            return set(re.findall(r'[a-zA-Z0-9]+', str(text).lower()))

        candidate_norms = []
        candidate_words = set()

        for c_str in candidate_strings:
            clean_str = os.path.splitext(os.path.basename(c_str))[0]
            norm = normalize(clean_str)
            if norm:
                candidate_norms.append(norm)
                candidate_words.update(extract_words(clean_str))

        if not candidate_norms:
            return None

        search_dirs = []
        for sub in cat_subfolders:
            sub_path = os.path.join(nv_icons_dir, sub)
            if os.path.exists(sub_path):
                search_dirs.append((sub_path, 30))

        if os.path.exists(nv_icons_dir):
            search_dirs.append((nv_icons_dir, 15))

        inv_dir = os.path.join(root_dir, "images", "inventory")
        if os.path.exists(inv_dir):
            search_dirs.append((inv_dir, 0))

        best_match_path = None
        best_score = 0

        for base_dir, folder_bonus in search_dirs:
            for root, _, files in os.walk(base_dir):
                for file in files:
                    if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp')):
                        continue
                    
                    name_no_ext = os.path.splitext(file)[0]
                    clean_file = re.sub(r'(_icon|icon)$', '', name_no_ext, flags=re.IGNORECASE)
                    file_norm = normalize(clean_file)
                    file_words = extract_words(clean_file)

                    if not file_norm:
                        continue

                    score = 0
                    for c_norm in candidate_norms:
                        if file_norm == c_norm:
                            score = max(score, 100)
                        elif file_norm.startswith(c_norm) or c_norm.startswith(file_norm):
                            score = max(score, 80)
                        elif file_norm in c_norm or c_norm in file_norm:
                            score = max(score, 70)

                    if score == 0 and candidate_words and file_words:
                        overlap = len(candidate_words & file_words) / float(len(candidate_words))
                        if overlap > 0.3:
                            score = int(overlap * 60)

                    if score > 0:
                        total_score = score + folder_bonus
                        if total_score > best_score:
                            best_score = total_score
                            best_match_path = os.path.join(root, file)

        if best_match_path and os.path.exists(best_match_path):
            return self._process_loaded_image(best_match_path)

        return None

    def _process_loaded_image(self, img_path: str) -> pygame.Surface | None:
        try:
            img = pygame.image.load(img_path).convert_alpha()
            color_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
            tint_surf = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            tint_surf.fill((*color_light[:3], 255))
            img.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            cat_str = ""
            if isinstance(self.category, (list, tuple)):
                cat_str = " ".join(str(c) for c in self.category).lower()
            elif isinstance(self.category, str):
                cat_str = self.category.lower()

            is_weapon_or_apparel = any(k in cat_str for k in ["weapon", "arm", "apparel", "armor", "clothing"])
            scale_factor = 0.88 if is_weapon_or_apparel else 0.80

            w, h = img.get_size()
            max_w = int(self.turntable_draw_space.width * scale_factor)
            max_h = int(self.turntable_draw_space.height * scale_factor)
            scale = min(max_w / max(1, w), max_h / max(1, h))
            
            new_width = max(1, int(w * scale))
            new_height = max(1, int(h * scale))
            return pygame.transform.smoothscale(img, (new_width, new_height))
        except Exception:
            return None

    def start_item_animation(self):
        if self.is_nv or not self.enable_turntable:
            return

        if self.item_turntable:
            self.item_turntable.stop()
            self.item_turntable = None

        if not self.unique_items or self.inv_list.selected_index >= len(self.unique_items):
            return

        selected_item = self.unique_items[self.inv_list.selected_index]   
        item_key = getattr(selected_item, 'name', 'unknown')

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

                    icons = [Utils.scale_image_abs(img, height=self.turntable_draw_space.height) for img in icons if img]

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

            def start(self): pass
            def stop(self): pass

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
            frame_duration=getattr(settings, 'SPEED', 1) * 100
        )
        self.item_turntable.start()

    def _find_item_folder(self, item) -> str | None:
        root_dir = self._get_project_root()
        inv_base_dir = os.path.join(root_dir, "images", "inventory")

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

    def init_footer_text(self):
        weight_surface = self.init_footer_weight()
        caps_surface = self.init_footer_caps()
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        footer_surface.blit(weight_surface, (0, 0))
        footer_surface.blit(caps_surface, (0, 0))
        return footer_surface

    def init_footer_weight(self):
        weight_text = f"{self.weight}/{settings.MAX_CARRY_WEIGHT}"
        weight_surface = self.footer_font.render(weight_text, True, settings.PIP_BOY_LIGHT)
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        icon_y = (settings.BOTTOM_BAR_HEIGHT - self.weight_icon.get_height()) // 2
        text_y = (settings.BOTTOM_BAR_HEIGHT - weight_surface.get_height()) // 2
        
        footer_surface.blit(self.weight_icon, (settings.BOTTOM_BAR_MARGIN, icon_y))
        footer_surface.blit(weight_surface, (self.weight_icon.get_width() + (settings.BOTTOM_BAR_MARGIN * 2), text_y))

        return footer_surface

    def init_footer_caps(self):
        caps_text = f"{settings.CAPS}"
        caps_surface = self.footer_font.render(caps_text, True, settings.PIP_BOY_LIGHT)
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        icon_y = (settings.BOTTOM_BAR_HEIGHT - self.caps_icon.get_height()) // 2
        text_y = (settings.BOTTOM_BAR_HEIGHT - caps_surface.get_height()) // 2
        
        start_x = settings.SCREEN_WIDTH // 4 + 4
        footer_surface.blit(self.caps_icon, (start_x, icon_y))
        footer_surface.blit(caps_surface, (start_x + self.caps_icon.get_width() + settings.BOTTOM_BAR_MARGIN, text_y))

        return footer_surface

    def handle_threads(self, tab_selected: bool):
        if self.no_items:
            return
        if tab_selected and self.enable_turntable:
            self.update_item_display()
        elif not tab_selected and self.enable_turntable and self.item_turntable:
            self.item_turntable.stop()
            self.item_turntable = None

    def calculate_grid_space(self):
        if self.is_nv:
            grid_top = self.turntable_draw_space.bottom + 4
            grid_width = self.turntable_draw_space.width
            grid_height = self.draw_space.bottom - grid_top - 8
            return pygame.Rect(self.turntable_draw_space.left, grid_top, grid_width, grid_height)

        list_space = self.list_draw_space
        grid_top = list_space.top + (list_space.height * 0.38)
        grid_height = list_space.bottom - grid_top
        
        center_x = (settings.SCREEN_WIDTH // 2) + 80
        grid_width = (self.draw_space.right - list_space.right - getattr(settings, 'GRID_RIGHT_MARGIN', 10)) - 20
        
        grid_rect = pygame.Rect(0, 0, grid_width, grid_height)
        grid_rect.centerx = center_x
        grid_rect.top = grid_top
        return grid_rect

    def _draw_nv_stats_grid(self, rect: pygame.Rect, item):
        color = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
        bg_color = (0, 0, 0)

        cat_str = ""
        if isinstance(self.category, (list, tuple)):
            cat_str = " ".join(str(c) for c in self.category).lower()
        elif isinstance(self.category, str):
            cat_str = self.category.lower()

        is_weapon = "weapon" in cat_str or "arm" in cat_str
        is_apparel = "apparel" in cat_str or "armor" in cat_str or "clothing" in cat_str
        has_cnd = is_weapon or is_apparel or hasattr(item, 'cnd')

        row_h = 17

        if is_weapon or is_apparel:
            m_surf = self.inv_font.render("Maintain R)", True, color)
            x_m = self.turntable_draw_space.right - m_surf.get_width() - 2
            y_m = self.turntable_draw_space.top - 2
            self.screen.blit(m_surf, (x_m, y_m))
            
            if is_weapon:
                mod_prompt = self.inv_font.render("Mod X)", True, color)
                self.screen.blit(mod_prompt, (self.turntable_draw_space.right - mod_prompt.get_width() - 2, y_m + 20))

        if is_weapon:
            dps = str(getattr(item, 'dps', 0))
            vw = f"{getattr(item, 'vw', 0.0):.1f}"
            str_req = str(getattr(item, 'str_req', 0))
            dam = str(getattr(item, 'damage', 0))
            wg = f"{getattr(item, 'weight', 0.0):.2f}"
            val = str(getattr(item, 'value', 0))

            rows = [
                [("DPS", dps), ("V/W", vw), ("STR", str_req)],
                [("DAM", dam), ("WG", wg), ("VAL", val)]
            ]
        elif is_apparel:
            dr = str(getattr(item, 'dr', getattr(item, 'damage_res', 0)))
            dt = str(getattr(item, 'dt', getattr(item, 'damage_threshold', 0)))
            wg = f"{getattr(item, 'weight', 0.0):.1f}"
            val = str(getattr(item, 'value', 0))

            rows = [
                [("DR", dr), ("DT", dt)],
                [("WG", wg), ("VAL", val)]
            ]
        else:
            wg = f"{getattr(item, 'weight', 0.0):.1f}"
            val = str(getattr(item, 'value', 0))

            rows = [
                [("WG", wg), ("VAL", val)]
            ]

        y_current = rect.top

        for row_data in rows:
            y_top = y_current
            y_bottom = y_top + row_h

            num_cols = len(row_data)
            if num_cols == 3:
                col_widths = [int(rect.width * 0.33), int(rect.width * 0.39), rect.width - int(rect.width * 0.33) - int(rect.width * 0.39)]
            elif num_cols == 2:
                col_widths = [rect.width // 2, rect.width - (rect.width // 2)]
            else:
                col_widths = [rect.width]

            x_left = rect.left
            for c_idx, (label, val_str) in enumerate(row_data):
                cur_w = col_widths[c_idx]
                x_right = x_left + cur_w if c_idx < num_cols - 1 else rect.right
                
                pygame.draw.line(self.screen, color, (x_left + 6, y_top), (x_right, y_top), 1)
                pygame.draw.line(self.screen, color, (x_right, y_top), (x_right, y_bottom - 6), 1)

                lbl_surf = self.inv_font.render(label, True, color)
                val_surf = self.inv_font.render(val_str, True, color)
                
                self.screen.blit(lbl_surf, (x_left + 6, y_top + 2))
                self.screen.blit(val_surf, (x_right - val_surf.get_width() - 5, y_top + 2))

                x_left = x_right

            y_current = y_bottom
        # Draw condition bar and ammo count for weapons
        if has_cnd:
            y_top = y_current
            y_bottom = y_top + row_h
            
            cnd_w = int(rect.width * 0.33)
            x_left_cnd = rect.left
            x_right_cnd = rect.left + cnd_w

            pygame.draw.line(self.screen, color, (x_left_cnd + 6, y_top), (x_right_cnd, y_top), 1)
            pygame.draw.line(self.screen, color, (x_right_cnd, y_top), (x_right_cnd, y_bottom - 6), 1)

            cnd_lbl = self.inv_font.render("CND", True, color)
            self.screen.blit(cnd_lbl, (x_left_cnd + 6, y_top + 2))

            bar_x = x_left_cnd + 6 + cnd_lbl.get_width() + 4
            bar_y = y_top + 5
            bar_w = max(10, x_right_cnd - bar_x - 5)
            bar_h = 7

            cnd_max = getattr(item, 'cnd_max', 100)
            if hasattr(item, 'cnd') and item.cnd is not None:
                cnd_val = item.cnd
            else:
                if not hasattr(item, '_random_cnd'):
                    item._random_cnd = random.randint(15, 100)
                cnd_val = item._random_cnd

            condition_pct = min(1.0, max(0.0, float(cnd_val) / max(1, float(cnd_max))))

            pygame.draw.rect(self.screen, color, (bar_x, bar_y, bar_w, bar_h), 1)
            fill_w = int((bar_w - 2) * condition_pct)
            if fill_w > 0:
                pygame.draw.rect(self.screen, color, (bar_x + 1, bar_y + 1, fill_w, bar_h - 2))

            notch_x = bar_x + 1 + int((bar_w - 2) * 0.80)
            notch_depth = 2

            if condition_pct < 0.80:
                pygame.draw.line(self.screen, color, (notch_x, bar_y), (notch_x, bar_y + notch_depth), 1)
                pygame.draw.line(self.screen, color, (notch_x, bar_y + bar_h - 1), (notch_x, bar_y + bar_h - 1 - notch_depth), 1)
            else:
                pygame.draw.line(self.screen, bg_color, (notch_x, bar_y), (notch_x, bar_y + notch_depth), 1)
                pygame.draw.line(self.screen, bg_color, (notch_x, bar_y + bar_h - 1), (notch_x, bar_y + bar_h - 1 - notch_depth), 1)

            if is_weapon:
                x_left_ammo = x_right_cnd
                x_right_ammo = rect.right

                pygame.draw.line(self.screen, color, (x_left_ammo + 6, y_top), (x_right_ammo, y_top), 1)
                pygame.draw.line(self.screen, color, (x_right_ammo, y_top), (x_right_ammo, y_bottom - 6), 1)

                ammo_type = getattr(item, 'ammo_type', None) or getattr(item, 'ammo', None)
                if ammo_type:
                    ammo_count = getattr(item, 'ammo_count', None)
                    if ammo_count is None:
                        if hasattr(settings, 'TOTAL_AMMO') and ammo_type in settings.TOTAL_AMMO:
                            ammo_count = settings.TOTAL_AMMO[ammo_type]
                        else:
                            ammo_count = 0

                    ammo_text = f"{ammo_type} ({ammo_count})"
                    ammo_surf = self.inv_font.render(ammo_text, True, color)
                    self.screen.blit(ammo_surf, (x_right_ammo - ammo_surf.get_width() - 5, y_top + 2))

            y_current = y_bottom
        # Draw installed mods list for weapons
        if is_weapon:
            mods_val = (
                getattr(item, 'mods', None) or 
                getattr(item, 'installed_mods', None) or 
                getattr(item, 'weapon_mods', None)
            )

            if mods_val:
                if isinstance(mods_val, (list, tuple)):
                    mods_list = [str(m).strip() for m in mods_val if str(m).strip()]
                elif isinstance(mods_val, str):
                    mods_list = [m.strip() for m in mods_val.split(',') if m.strip()]
                else:
                    mods_list = [str(mods_val).strip()]

                if mods_list:
                    mod_row_h = 13
                    y_top = y_current
                    total_h = (len(mods_list) * mod_row_h) + 2
                    y_bottom = y_top + total_h
                    x_left = rect.left
                    x_right = rect.right

                    pygame.draw.line(self.screen, color, (x_left + 6, y_top), (x_right, y_top), 1)
                    pygame.draw.line(self.screen, color, (x_right, y_top), (x_right, y_bottom - 31), 1)

                    for idx, mod_name in enumerate(mods_list):
                        mod_y = y_top + (idx * mod_row_h)
                        max_val_w = x_right - (x_left + 6) - 5
                        val_surf = self.inv_font.render(mod_name, True, color)

                        if val_surf.get_width() > max_val_w and max_val_w > 10:
                            truncated_text = mod_name
                            while len(truncated_text) > 3 and self.inv_font.render(truncated_text + "...", True, color).get_width() > max_val_w:
                                truncated_text = truncated_text[:-1]
                            val_surf = self.inv_font.render(truncated_text + "...", True, color)

                        self.screen.blit(val_surf, (x_right - val_surf.get_width() - 5, mod_y + 1))

                    y_current = y_bottom

    def render(self):
        if self.no_items:
            return

        if self.is_nv:
            self.inv_list.render(self.screen, self.active_item_index, False)
            if self.static_image:
                rect = self.static_image.get_rect(center=self.turntable_draw_space.center)
                rect.centerx -= 20
                self.screen.blit(self.static_image, rect)

            if self.unique_items and self.active_item_index is not None and self.active_item_index < len(self.unique_items):
                selected_item = self.unique_items[self.active_item_index]
                grid_rect = self.calculate_grid_space()
                self._draw_nv_stats_grid(grid_rect, selected_item)
        else:
            self.tab_instance.render_footer(self)
            self.inv_list.render(self.screen, self.active_item_index, False)
            if self.enable_turntable and self.item_turntable:
                self.item_turntable.render()

            if hasattr(self.tab_instance, 'render_stats') and self.item_selected:
                if self.unique_items and self.active_item_index is not None and self.active_item_index < len(self.unique_items):
                    self.tab_instance.render_stats(self.unique_items[self.active_item_index])