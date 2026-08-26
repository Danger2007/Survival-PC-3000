import os
import pygame
import settings
from threading import Thread
from ui import GenericList, AnimatedImage
from util_functs import Utils


def colorize_surface(surface, color):
    """Applica la tinta del Pip-Boy ad un'immagine mantenendo la trasparenza."""
    if surface is None:
        return None
    tinted = surface.copy()
    r, g, b = color[0], color[1], color[2]
    tinted.fill((r, g, b, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


def load_nv_special_image(special_name):
    """Carica l'immagine statica .webp per New Vegas."""
    clean_name = special_name.strip()
    possible_filenames = [
        f"{clean_name.lower()}.webp",
        f"{clean_name.capitalize()}.webp",
        f"{clean_name.upper()}.webp",
        f"{clean_name.lower()}.png",
        f"{clean_name.capitalize()}.png"
    ]
    
    base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.abspath(__file__)))
    search_dirs = [
        os.path.join(base_dir, "images", "new_vegas_icons", "special_nv"),
        os.path.join(base_dir, "images", "special_nv"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "new_vegas_icons", "special_nv")
    ]
    
    for s_dir in search_dirs:
        for fname in possible_filenames:
            full_path = os.path.normpath(os.path.join(s_dir, fname))
            if os.path.exists(full_path):
                try:
                    return pygame.image.load(full_path).convert_alpha()
                except Exception:
                    try:
                        from PIL import Image
                        pil_img = Image.open(full_path).convert("RGBA")
                        data = pil_img.tobytes()
                        return pygame.image.fromstring(data, pil_img.size, "RGBA").convert_alpha()
                    except Exception as e:
                        print(f"[DEBUG PIP-BOY] Errore caricamento {full_path}: {e}")
                        
    print(f"[DEBUG PIP-BOY] Immagine NV non trovata per '{special_name}'")
    return None


class SpecialTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        self.ui_style = getattr(settings, 'UI_STYLE', 'Fallout_4')
        self.is_nv = (self.ui_style == "Fallout_NV")
        
        self.special_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 12)
        self.description_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 9) 
        
        list_draw_space = pygame.Rect(
            self.draw_space.left,
            self.draw_space.top + 2 * settings.LIST_TOP_MARGIN,
            self.draw_space.centerx - 2 * settings.TAB_SIDE_MARGIN,
            self.draw_space.height - 2 * settings.LIST_TOP_MARGIN
        )

        self.special_list = GenericList(
            stats=settings.DEFAULT_SPECIAL_STATS,
            draw_space=list_draw_space,
            items=[settings.SPECIAL[i] for i in range(len(settings.SPECIAL))],
            font=self.special_font
        )
        
        self.selected_special_index = 0
        self.previous_special_index = 0
        
        self.special_text = self._init_special_text()
        
        self.special_images, self.frame_orders = self._init_images()
        self.animated_images = {}
        
        for special in settings.SPECIAL:
            image_width = self.special_images[special][0].get_width()
            self.animated_images[special] = AnimatedImage(
                self.screen,
                self.special_images[special],
                (self.draw_space.centerx + self.draw_space.width // 4 - image_width // 2,
                 self.draw_space.top + settings.LIST_TOP_MARGIN),
                settings.SPEED * 200,
                self.frame_orders[special],
                loop=True,
                sound_path=f"{settings.SPECIAL_SOUNDS}/{special.lower()}.ogg" if not settings.GAME_ACCURATE_MODE else None
            )

        self.nv_special_images = {}
        if self.is_nv:
            for special in settings.SPECIAL:
                self.nv_special_images[special] = load_nv_special_image(special)

    def handle_threads(self, tab_selected: bool):
        if self.is_nv:
            return

        if tab_selected:
            self.animated_images[settings.SPECIAL[self.selected_special_index]].start()
        else:
            self.animated_images[settings.SPECIAL[self.selected_special_index]].stop()

    def scroll_special(self, direction: bool):
        prev_index = self.special_list.change_selection(direction)
        selected_index = self.special_list.selected_index
        
        if selected_index != prev_index:
            self.selected_special_index = selected_index
            if not self.is_nv:
                self.animated_images[settings.SPECIAL[prev_index]].stop()
                self.animated_images[settings.SPECIAL[self.selected_special_index]].reset()
                self.animated_images[settings.SPECIAL[self.selected_special_index]].start()

    def _init_special_text(self):
        special_discriptions = {}
        # Calcolo della larghezza della colonna destra ridotta di 7px a destra per il wrapping
        right_x = self.draw_space.centerx + settings.TAB_SIDE_MARGIN
        right_w = (self.draw_space.right - right_x) - settings.TAB_SIDE_MARGIN
        wrap_w = right_w - 15

        for description in settings.SPECIAL_DESCRIPTIONS:
            text = self.description_font.render(description, True, settings.PIP_BOY_LIGHT, wraplength=wrap_w)
            surface = pygame.surface.Surface((wrap_w, text.get_height()), pygame.SRCALPHA)
            surface.blit(text, (0, 0))
            special_discriptions[description.split(" ")[0]] = surface
        return special_discriptions

    def _init_images(self):
        special_images = {}
        frame_orders = {}
        for i, special in enumerate(settings.SPECIAL):
            path = f"{settings.SPECIAL_BASE_FOLDER}/{special.lower()}"
            images = []
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.endswith(".png"):
                        images.append(Utils.scale_image(
                            Utils.tint_image(
                                pygame.image.load(os.path.join(path, file)).convert_alpha()
                            ),
                            settings.SPECIAL_IMAGE_SCALE
                        ))
                        
                if os.path.exists(os.path.join(path, "frameorder.ini")):
                    with open(os.path.join(path, "frameorder.ini"), "r") as f:
                        frame_orders[settings.SPECIAL[i]] = [int(frame) for frame in (f.read().split(","))]
                else:
                    frame_orders[settings.SPECIAL[i]] = list(range(0, len(images)))
            else:
                frame_orders[settings.SPECIAL[i]] = [0]
                images = [pygame.Surface((1, 1))]
                
            special_images[settings.SPECIAL[i]] = images

        return special_images, frame_orders

    def _render_special_images(self, selected_special):
        if selected_special in self.animated_images:
            self.animated_images[selected_special].render()

    def _render_special_text(self, selected_special, pos_x=None, pos_y=None):
        if selected_special in self.special_text:
            x = pos_x if pos_x is not None else self.draw_space.centerx
            y = pos_y if pos_y is not None else (self.draw_space.centery + (self.draw_space.centery // 4))
            self.screen.blit(self.special_text[selected_special], (x, y))

    def _render_fallout4_ui(self):
        selected_special = settings.SPECIAL[self.selected_special_index]
        self.special_list.render(self.screen)
        self._render_special_images(selected_special)
        self._render_special_text(selected_special)

    def _render_new_vegas_ui(self):
        selected_special = settings.SPECIAL[self.selected_special_index]
        stats = getattr(settings, 'DEFAULT_SPECIAL_STATS', {})
        
        # 1. LISTA SPECIAL
        left_x = self.draw_space.left + settings.TAB_SIDE_MARGIN + 15
        top_y = self.draw_space.top + (2 * settings.LIST_TOP_MARGIN) - 15
        list_w = int(self.draw_space.width * 0.40)
        
        line_height = self.special_font.get_height() + 6
        
        for idx, special in enumerate(settings.SPECIAL):
            item_y = top_y + (idx * line_height)
            is_selected = (idx == self.selected_special_index)
            
            if is_selected:
                select_rect = pygame.Rect(left_x - 4, item_y, list_w + 8, line_height - 1)
                pygame.draw.rect(self.screen, settings.PIP_BOY_LIGHT, select_rect, 1)
            
            name_surf = self.special_font.render(special, True, settings.PIP_BOY_LIGHT)
            self.screen.blit(name_surf, (left_x, item_y + (line_height - name_surf.get_height()) // 2))
            
            if isinstance(stats, dict):
                val_str = str(stats.get(special, stats.get(special.lower(), 0)))
            elif isinstance(stats, (list, tuple)) and idx < len(stats):
                val_str = str(stats[idx])
            else:
                val_str = "0"
                
            val_surf = self.special_font.render(val_str, True, settings.PIP_BOY_LIGHT)
            val_x = left_x + list_w - val_surf.get_width()
            self.screen.blit(val_surf, (val_x, item_y + (line_height - val_surf.get_height()) // 2))

        # 2. ICONA STATICA WEBP
        right_x = self.draw_space.centerx + settings.TAB_SIDE_MARGIN
        right_w = (self.draw_space.right - right_x) - settings.TAB_SIDE_MARGIN
        target_h = int(self.draw_space.height * 0.52)

        icon_surf = self.nv_special_images.get(selected_special)
        if icon_surf:
            orig_w, orig_h = icon_surf.get_size()
            scale = min(right_w / orig_w, target_h / orig_h)
            new_size = (int(orig_w * scale), int(orig_h * scale))
            
            scaled_img = pygame.transform.smoothscale(icon_surf, new_size)
            colored_img = colorize_surface(scaled_img, settings.PIP_BOY_LIGHT)
            
            center_x = right_x + (right_w - new_size[0]) // 2
            center_y = top_y + (target_h - new_size[1]) // 2
            self.screen.blit(colored_img, (center_x, center_y))

        # 3. LINEA DIVISORIA CON ANGOLO A DESTRA
        divider_y = top_y + target_h + 4
        pygame.draw.line(self.screen, settings.PIP_BOY_LIGHT, (right_x, divider_y), (right_x + right_w - 10, divider_y), 1)
        pygame.draw.line(self.screen, settings.PIP_BOY_LIGHT, (right_x + right_w - 10, divider_y), (right_x + right_w - 10, divider_y + 7), 1)

        # 4. TESTO DESCRIZIONE (Allineato a sinistra con right_x, a capo 7px prima del bordo destro)
        self._render_special_text(selected_special, pos_x=right_x, pos_y=divider_y + 8)

    def render(self):
        """Render the entire tab UI dynamically based on settings.UI_STYLE."""
        if not self.special_list or not self.special_text:
            return

        if self.is_nv:
            self._render_new_vegas_ui()
        else:
            self._render_fallout4_ui()