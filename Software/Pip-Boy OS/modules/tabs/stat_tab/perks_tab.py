import os
import math
import pygame
import settings


def draw_star(surface, color, center, outer_radius=6, inner_radius=2.2, filled=True, width=1):
    """Disegna una stella vettoriale a 5 punte con base delle punte ridotta."""
    points = []
    angle = -math.pi / 2
    step = math.pi / 5

    for i in range(10):
        r = outer_radius if i % 2 == 0 else inner_radius
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
        angle += step

    if filled:
        pygame.draw.polygon(surface, color, points)
    else:
        pygame.draw.polygon(surface, color, points, width)


def colorize_surface(surface, color):
    """Applica la tinta del Pip-Boy a un'icona conservandone l'alpha."""
    if surface is None:
        return None
    tinted = surface.copy()
    r, g, b = color[0], color[1], color[2]
    tinted.fill((r, g, b, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


class PerksTab:
    """
    Gestisce la tab dei Perks nel Pip-Boy rispecchiando il layout originale di
    Fallout: New Vegas e Fallout 4.
    """
    def __init__(self, screen, tab_base=None, draw_space=None):
        self.screen = screen
        self.tab_base = tab_base
        self.draw_space = draw_space if draw_space else pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        
        self.selected_index = 0
        self.scroll_offset = 0
        self.perks_data = []
        self._image_cache = {}
        
        self.load_perks_data()

    def load_perks_data(self):
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        
        if 'nv' in ui_style or 'vegas' in ui_style:
            self.perks_data = getattr(settings, 'DEFAULT_PERKS_NV', 
                              getattr(settings, 'PERKS_FALLOUT_NV', []))
        else:
            self.perks_data = getattr(settings, 'DEFAULT_PERKS_FO4', 
                              getattr(settings, 'PERKS_FALLOUT_4', []))
        
        if not self.perks_data:
            self.perks_data = getattr(settings, 'DEFAULT_PERKS', 
                              getattr(settings, 'PERKS', []))

    def _get_field(self, perk, field_name, default=None):
        if isinstance(perk, dict):
            return perk.get(field_name, default)
        return getattr(perk, field_name, default)

    def scroll_perks(self, direction):
        if not self.perks_data:
            return

        if isinstance(direction, bool):
            delta = -1 if direction else 1
        elif isinstance(direction, str):
            delta = -1 if direction.lower() in ("up", "su", "prev") else 1
        else:
            delta = 1 if direction > 0 else -1

        new_index = self.selected_index + delta
        self.selected_index = max(0, min(len(self.perks_data) - 1, new_index))

    def handle_input(self, event):
        if not self.perks_data:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = min(len(self.perks_data) - 1, self.selected_index + 1)
            elif event.key == pygame.K_PAGEUP:
                self.selected_index = max(0, self.selected_index - 5)
            elif event.key == pygame.K_PAGEDOWN:
                self.selected_index = min(len(self.perks_data) - 1, self.selected_index + 5)

    def _load_and_scale_img(self, img_path, max_size, cache_key):
        """Carica l'immagine (Pygame/PIL) e la scala mantenendo le proporzioni."""
        surf = None
        try:
            surf = pygame.image.load(img_path).convert_alpha()
        except Exception:
            try:
                from PIL import Image
                pil_img = Image.open(img_path).convert("RGBA")
                data = pil_img.tobytes()
                surf = pygame.image.fromstring(data, pil_img.size, "RGBA").convert_alpha()
            except Exception:
                surf = None

        if surf:
            w, h = surf.get_size()
            max_w, max_h = max_size
            ratio = min(max_w / max(1, w), max_h / max(1, h))
            new_size = (max(1, int(w * ratio)), max(1, int(h * ratio)))
            
            scaled_surf = pygame.transform.smoothscale(surf, new_size)
            self._image_cache[cache_key] = scaled_surf
            return scaled_surf

        self._image_cache[cache_key] = None
        return None

    def _get_perk_image(self, perk, max_size=(80, 80)):
        """Risolve i percorsi delle immagini partendo dalla radice fuori da modules."""
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        is_nv = 'nv' in ui_style or 'vegas' in ui_style
        
        perk_name = str(self._get_field(perk, 'name', ''))
        if not perk_name:
            return None

        cache_key = f"{perk_name}_{is_nv}_{max_size}"
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        curr_file_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = getattr(settings, 'BASE_DIR', os.path.abspath(os.path.join(curr_file_dir, "..", "..", "..")))
        
        explicit_path = self._get_field(perk, 'image', self._get_field(perk, 'icon', None))
        if explicit_path:
            full_explicit = explicit_path if os.path.isabs(explicit_path) else os.path.join(root_dir, explicit_path)
            if os.path.exists(full_explicit):
                return self._load_and_scale_img(full_explicit, max_size, cache_key)

        search_dirs = [
            os.path.join(root_dir, "images", "new_vegas_icons", "perks_nv"),
            os.path.join(root_dir, "images", "new_vegas_icons", "perks"),
            os.path.join(root_dir, "images", "stats", "perks"),
            os.path.join(root_dir, "images", "perks_nv"),
            os.path.join(root_dir, "images", "perks"),
        ]

        clean_name = perk_name.replace("'", "").strip()
        name_variants = [
            clean_name.replace(' ', '_'),
            clean_name.replace(' ', ''),
            f"Fo4_{clean_name.replace(' ', '_')}",
            f"Fo4_{clean_name.replace(' ', '')}",
            clean_name.lower().replace(' ', '_'),
            clean_name.lower().replace(' ', ''),
        ]

        extensions = ['.webp', '.png', '.jpg', '.dds']

        for folder in search_dirs:
            if not os.path.exists(folder):
                continue
            for name in name_variants:
                for ext in extensions:
                    full_path = os.path.join(folder, f"{name}{ext}")
                    if os.path.exists(full_path):
                        return self._load_and_scale_img(full_path, max_size, cache_key)

        self._image_cache[cache_key] = None
        return None

    def update(self):
        if not self.perks_data:
            self.load_perks_data()

    def render(self):
        if not self.perks_data:
            self.load_perks_data()
            
        if not self.perks_data:
            return

        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        if 'nv' in ui_style or 'vegas' in ui_style:
            self._render_fallout_nv_ui()
        else:
            self._render_fallout4_ui()

    def _get_font(self, size=11):
        font_path = getattr(settings, 'MAIN_FONT_PATH', None)
        if font_path:
            try:
                return pygame.font.Font(font_path, size)
            except Exception:
                pass
        return pygame.font.SysFont("monospace", size, bold=True)

    def _wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def _render_fallout_nv_ui(self):
        """Layout SKILLS/PERKS per Fallout: New Vegas."""
        color = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        screen_w = settings.SCREEN_WIDTH
        screen_h = settings.SCREEN_HEIGHT
        
        FONT_SIZE = 12
        font_main = pygame.font.Font(getattr(settings, 'MAIN_FONT_PATH', None), FONT_SIZE)
        font_desc = pygame.font.Font(getattr(settings, 'MAIN_FONT_PATH', None), FONT_SIZE - 3)
        LINE_HEIGHT = 18

        left_x = int(screen_w * 0.12)
        left_w = int(screen_w * 0.36)
        
        right_x = int(screen_w * 0.52)
        right_w = int(screen_w * 0.45)
        
        top_y = int(screen_h * 0.18)
        bottom_y = int(screen_h * 0.82)
        available_h = bottom_y - top_y

        MAX_VISIBLE_ITEMS = max(1, available_h // LINE_HEIGHT)
        total_items = len(self.perks_data)
        
        scroll_offset = max(0, min(self.selected_index - MAX_VISIBLE_ITEMS // 2, total_items - MAX_VISIBLE_ITEMS))
        scroll_offset = max(0, scroll_offset)

        # --- CONTROLLI SCROLLER A SINISTRA ---
        slider_x = left_x - 18
        arrow_w = 5
        arrow_h = 8
        notch = 3

        top_arrow_y = top_y
        up_arrow_pts = [
            (slider_x, top_arrow_y),
            (slider_x + arrow_w, top_arrow_y + arrow_h),
            (slider_x, top_arrow_y + arrow_h - notch),
            (slider_x - arrow_w, top_arrow_y + arrow_h)
        ]
        pygame.draw.polygon(self.screen, color, up_arrow_pts)

        bottom_arrow_y = bottom_y
        down_arrow_pts = [
            (slider_x, bottom_arrow_y),
            (slider_x + arrow_w, bottom_arrow_y - arrow_h),
            (slider_x, bottom_arrow_y - arrow_h + notch),
            (slider_x - arrow_w, bottom_arrow_y - arrow_h)
        ]
        pygame.draw.polygon(self.screen, color, down_arrow_pts)

        track_top = top_arrow_y + arrow_h - notch + 5
        track_bottom = bottom_arrow_y - arrow_h + notch - 5
        track_length = track_bottom - track_top

        pygame.draw.line(self.screen, color, (slider_x, track_top), (slider_x, track_bottom), 1)

        if total_items > MAX_VISIBLE_ITEMS:
            bar_length = max(12, int(track_length * (MAX_VISIBLE_ITEMS / total_items)))
            max_scroll = total_items - MAX_VISIBLE_ITEMS
            scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
            
            bar_top = track_top + int(scroll_ratio * (track_length - bar_length))
            bar_bottom = bar_top + bar_length
            pygame.draw.line(self.screen, color, (slider_x, bar_top), (slider_x, bar_bottom), 2)

        # --- LISTA PERKS A SINISTRA ---
        visible_perks = self.perks_data[scroll_offset : scroll_offset + MAX_VISIBLE_ITEMS]
        
        for idx_in_view, perk in enumerate(visible_perks):
            actual_index = scroll_offset + idx_in_view
            y_pos = top_y + (idx_in_view * LINE_HEIGHT)
            is_selected = (actual_index == self.selected_index)
            
            perk_name = str(self._get_field(perk, 'name', ''))
            rank = int(self._get_field(perk, 'rank', 1))
            display_text = f"{perk_name} ({rank})" if rank > 1 else perk_name

            if is_selected:
                select_rect = pygame.Rect(left_x - 4, y_pos, left_w + 8, LINE_HEIGHT - 1)
                pygame.draw.rect(self.screen, color, select_rect, 1)

            text_surf = font_main.render(display_text, True, color)
            self.screen.blit(text_surf, (left_x, y_pos + (LINE_HEIGHT - text_surf.get_height()) // 2))

        # --- PANNELLO DESTRO ---
        if 0 <= self.selected_index < total_items:
            selected_perk = self.perks_data[self.selected_index]
            
            img_h = int(available_h * 0.55)
            perk_img = self._get_perk_image(selected_perk, max_size=(right_w, img_h))
            
            if perk_img:
                colored_img = colorize_surface(perk_img, color)
                center_x = right_x + (right_w - colored_img.get_width()) // 2
                center_y = top_y + (img_h - colored_img.get_height()) // 2
                self.screen.blit(colored_img, (center_x, center_y))

            divider_y = top_y + img_h + 5
            pygame.draw.line(self.screen, color, (right_x, divider_y), (right_x + right_w, divider_y), 1)
            pygame.draw.line(self.screen, color, (right_x + right_w, divider_y), (right_x + right_w, divider_y + 7), 1)

            desc_y = divider_y + 8
            desc_text = str(self._get_field(selected_perk, 'desc', ''))
            lines = self._wrap_text(desc_text, font_desc, right_w - 5)
            
            curr_y = desc_y
            for line in lines:
                if curr_y + font_desc.get_height() > bottom_y + 10:
                    break
                surf = font_desc.render(line, True, color)
                self.screen.blit(surf, (right_x, curr_y))
                curr_y += font_desc.get_height() + 2

    def _render_fallout4_ui(self):
        """Layout Fallout 4 con descrizioni dinamiche in base al grado del Perk."""
        color_light = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        font_main = self._get_font(11)
        font_small = self._get_font(9)

        x_left = self.draw_space.x + 8
        y_start = self.draw_space.y + 8
        list_width = 125
        line_height = 15
        max_visible_items = 8

        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + max_visible_items:
            self.scroll_offset = self.selected_index - max_visible_items + 1

        # --- LISTA A SINISTRA ---
        visible_perks = self.perks_data[self.scroll_offset : self.scroll_offset + max_visible_items]
        for i, perk in enumerate(visible_perks):
            actual_idx = self.scroll_offset + i
            is_selected = (actual_idx == self.selected_index)
            perk_name = str(self._get_field(perk, 'name', ''))
            item_y = y_start + (i * line_height)

            if is_selected:
                bg_rect = pygame.Rect(x_left - 2, item_y, list_width, line_height - 2)
                pygame.draw.rect(self.screen, color_light, bg_rect)
                text_surf = font_main.render(perk_name, True, (0, 0, 0))
            else:
                text_surf = font_main.render(perk_name, True, color_light)

            self.screen.blit(text_surf, (x_left, item_y))

        # --- PANNELLO DESTRO (VAULT BOY + STELLE + DESCRIZIONE DEL RANK CORRENTE) ---
        if 0 <= self.selected_index < len(self.perks_data):
            selected_perk = self.perks_data[self.selected_index]
            x_right = x_left + list_width + 12
            right_width = self.draw_space.right - x_right - 8
            
            perk_img = self._get_perk_image(selected_perk, max_size=(right_width, 105))
            current_y = y_start

            if perk_img:
                colored_img = colorize_surface(perk_img, color_light)
                img_x = x_right + (right_width - colored_img.get_width()) // 2
                self.screen.blit(colored_img, (img_x, current_y))
                current_y += colored_img.get_height() + 4

            # DETERMINAZIONE DEL RANK E DELLA DESCRIZIONE SPECIFICA
            rank = int(self._get_field(selected_perk, 'rank', 1))
            rank_descs = self._get_field(selected_perk, 'rank_descs', None)
            ranks_data = self._get_field(selected_perk, 'ranks', None)
            
            if rank_descs and isinstance(rank_descs, (list, tuple)) and len(rank_descs) > 0:
                max_rank = int(self._get_field(selected_perk, 'max_rank', len(rank_descs)))
                idx = max(0, min(rank - 1, len(rank_descs) - 1))
                desc_text = str(rank_descs[idx])
            elif ranks_data and isinstance(ranks_data, (list, tuple)) and len(ranks_data) > 0:
                max_rank = int(self._get_field(selected_perk, 'max_rank', len(ranks_data)))
                idx = max(0, min(rank - 1, len(ranks_data) - 1))
                r_item = ranks_data[idx]
                desc_text = r_item.get('desc', '') if isinstance(r_item, dict) else str(r_item)
            else:
                max_rank = int(self._get_field(selected_perk, 'max_rank', 5))
                desc_text = str(self._get_field(selected_perk, 'desc', ''))

            # INDICATORI STELLE VETTORIALI
            star_spacing = 14
            total_stars_w = max_rank * star_spacing
            start_star_x = x_right + (right_width - total_stars_w) // 2 + (star_spacing // 2)

            for r in range(max_rank):
                cx = start_star_x + (r * star_spacing)
                cy = current_y + 4
                is_filled = (r < rank)
                draw_star(self.screen, color_light, (cx, cy), outer_radius=5, inner_radius=1.8, filled=is_filled, width=1)

            current_y += 12

            lines = self._wrap_text(desc_text, font_small, right_width)
            desc_line_h = font_small.get_height() + 1
            for line in lines:
                if current_y + desc_line_h > self.draw_space.bottom - 2:
                    break
                surf = font_small.render(line, True, color_light)
                self.screen.blit(surf, (x_right, current_y))
                current_y += desc_line_h