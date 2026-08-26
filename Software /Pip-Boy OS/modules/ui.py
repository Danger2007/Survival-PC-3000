# generic_list.py
from threading import Thread, Event, Lock
import pygame
import settings
from util_functs import Utils
from cpp import wireframe
import os

VAULTBOY_CACHE = {}

# --------------------------------------------------------------------------
# CONFIGURAZIONE ANATOMICA PERFETTA (Allineata al Pip-Boy)
# Formato: 'chiave': ((larghezza, altezza), (offset_x, offset_y))
# --------------------------------------------------------------------------
PART_CONFIG = {
    # TORSO
    'torso_ok':       ((48, 54),  (+1, -1)),
    'torso_crippled': ((48, 54),  (+1, -1)), #to modify

    # HEAD AND FACES
    'head_ok':        ((42, 42),  (+3, -49)),
    'head_crippled':  ((42, 42),  (+3, -49)),
    'face_1':         ((23, 28),  (-2, -43)), #100%
    'face_2':         ((23, 28),  (-2, -43)), #99-75%
    'face_3':         ((23, 28),  (-2, -43)), #75-50%
    'face_4':         ((23, 28),  (-2, -43)), #50-25%
    'face_5':         ((23, 28),  (-2, -43)), #25-0%

    # ARMS
    'arm_r_ok':       ((60, 30),  (-47, -16)), # Arm Right of screen
    'arm_r_crippled': ((60, 30),  (-47, -16)),
    'arm_l_ok':       ((60, 30),  (+50, -17)), # Arm Left of screen
    'arm_l_crippled': ((60, 30),  (+50, -17)),

    # LEGS
    'leg_r_ok':       ((38, 52),  (-23, +46)), # Leg Right of screen
    'leg_r_crippled': ((38, 52),  (-23, +46)),
    'leg_l_ok':       ((38, 52),  (+14, +46)), # Leg Left of screen
    'leg_l_crippled': ((38, 52),  (+14, +46)),
}


def load_vaultboy_assets():
    if VAULTBOY_CACHE:
        return VAULTBOY_CACHE

    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(base_dir, "..", "images", "new_vegas_icons", "condition_nv")

    file_mapping = {
        'head_ok': 'Head_CND_Intact.png',
        'head_crippled': 'Head_CND_Crippled.png',
        'torso_ok': 'Torso_CND_Intact.png',
        'torso_crippled': 'Torso_CND_Crippled.png',
        'arm_l_ok': 'LeftArm_CND_Intact.png',
        'arm_l_crippled': 'LeftArm_CND_Crippled.png',
        'arm_r_ok': 'RightArm_CND_Intact.png',
        'arm_r_crippled': 'RightArm_CND_Crippled.png',
        'leg_l_ok': 'LeftLeg_CND_Intact.png',
        'leg_l_crippled': 'LeftLeg_CND_Crippled.png',
        'leg_r_ok': 'RightLeg_CND_Intact.png',
        'leg_r_crippled': 'RightLeg_CND_Crippled.png',
    }

    for i in range(1, 6):
        file_mapping[f'face_{i}'] = f'Face_CND_{i}.png'

    for key, filename in file_mapping.items():
        if key in PART_CONFIG:
            target_size, offset = PART_CONFIG[key]
            path = os.path.join(base_path, filename)

            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                scaled_img = pygame.transform.smoothscale(img, target_size)
                VAULTBOY_CACHE[key] = (scaled_img, offset)
            else:
                print(f"[UI Warning] File non trovato: {path}")

    return VAULTBOY_CACHE


def draw_vaultboy_and_cnd(screen, player_data, center_x, center_y, color):
    assets = load_vaultboy_assets()
    try:
        font_small = pygame.font.Font(settings.MAIN_FONT_PATH, 9)
    except:
        font_small = pygame.font.SysFont(None, 12)
    limbs = player_data.get('limbs', {
        'head': 100, 'torso': 100, 'arm_l': 100,
        'arm_r': 100, 'leg_l': 100, 'leg_r': 100
    })

    hp = player_data.get('hp', 280)
    max_hp = player_data.get('max_hp', 280)
    hp_pct = (hp / max_hp) if max_hp > 0 else 1.0

    # ----------------------------------------------------
    # 1. DISAGNO DEL VAULT BOY (Assemblato)
    # ----------------------------------------------------
    if assets:
        if hp_pct >= 0.8: face_idx = 1
        elif hp_pct >= 0.6: face_idx = 2
        elif hp_pct >= 0.4: face_idx = 3
        elif hp_pct >= 0.2: face_idx = 4
        else: face_idx = 5

        # Disegna in quest'ordine per sovrapposizioni corrette
        layers = ['torso', 'leg_l', 'leg_r', 'arm_l', 'arm_r', 'head']

        for part in layers:
            is_ok = limbs.get(part, 100) > 0
            state = 'ok' if is_ok else 'crippled'
            key = f"{part}_{state}"

            if key in assets:
                img, (off_x, off_y) = assets[key]
                tinted_img = img.copy()
                tinted_img.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
                rect = tinted_img.get_rect(center=(center_x + off_x, center_y + off_y))
                screen.blit(tinted_img, rect)

        face_key = f"face_{face_idx}"
        if face_key in assets:
            face_img, (off_x, off_y) = assets[face_key]
            tinted_face = face_img.copy()
            tinted_face.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
            face_rect = tinted_face.get_rect(center=(center_x + off_x, center_y + off_y))
            screen.blit(tinted_face, face_rect)
    # ----------------------------------------------------
    # 2. PARTS HEALTH BAR & CRIPPLED (Riallineate al tuo Vault Boy)
    # ----------------------------------------------------
    bar_positions = {
        'head':  (center_x - 13, center_y - 80, 32, 5), # Sopra la testa
        'torso': (center_x - 15, center_y - 18,  32, 5), # Sul petto
        'arm_r': (center_x - 75, center_y - 50, 28, 5), # A sinistra del braccio dx screen
        'arm_l': (center_x + 48, center_y - 50, 28, 5), # A destra del braccio sx screen
        'leg_r': (center_x - 75, center_y + 32, 28, 5), # A sinistra della gamba dx screen
        'leg_l': (center_x + 46, center_y + 32, 28, 5), # A destra della gamba sx screen
    }

    crippled_text_offsets = {
        'head':  (center_x - 18, center_y - 88),
        'torso': (center_x - 18, center_y - 20),
        'arm_r': (center_x - 130, center_y - 22),
        'arm_l': (center_x + 100, center_y - 22),
        'leg_r': (center_x - 110, center_y + 46),
        'leg_l': (center_x + 80,  center_y + 46),
    }
    # ----------------------------------------------------
    # 3. CORNICI BARRE SALUTE (Geometria Pip-Boy Originale)
    # ----------------------------------------------------
    pad = 1            # Spazio barra-cornice
    tri_w = 6          # Larghezza del triangolo (dalla base alla punta)
    ext_len = 16       # Quanto si allunga la linea orizzontale verso il Vault Boy

    for limb_key, (bx, by, bw, bh) in bar_positions.items():
        val = limbs.get(limb_key, 100)
        pct = max(0.0, min(1.0, val / 100.0))

        # Scritta CRIPPLED se arto a 0
        if val <= 0:
            tx, ty = crippled_text_offsets[limb_key]
            crip_txt = font_small.render("CRIPPLED", True, color)
            screen.blit(crip_txt, (tx, ty))

        # Riempimento barra interna
        fill_w = int((bw - 2) * pct)
        if fill_w > 0:
            pygame.draw.rect(screen, color, (bx + 1, by + 1, fill_w, bh - 2))

        # --------------------------------------------------
        # PARAMETRO ALTEZZA LINEE VERTICALI
        # --------------------------------------------------
        vert_height = bh - 2   # <--- CAMBIA QUESTO VALORE PER REGLARE L'ALTEZZA VERTICALE

        top_y = by - pad
        bottom_y = by + vert_height        # Fondo della stanghetta verticale
        tri_bottom_y = by + bh - 3        # La base del triangolo finisce 2px prima del fondo barra
        left_x = bx - pad
        right_x = bx + bw + pad

        # --- DISEGNO CORNICI ---
        if limb_key in ['head', 'torso']:
            # U Ribaltata semplice per Testa e Torso
            u_points = [
                (left_x, bottom_y),
                (left_x, top_y),
                (right_x, top_y),
                (right_x, bottom_y)
            ]
            pygame.draw.lines(screen, color, False, u_points, 1)

        elif limb_key in ['arm_r', 'leg_r']:
            # Arti a SINISTRA dello Schermo (Vault Boy a destra)
            # 1. Stanghetta verticale esterna a sinistra
            pygame.draw.line(screen, color, (left_x, top_y), (left_x, bottom_y), 1)
            # 2. Linea orizzontale superiore che si estende verso il Vault Boy
            pygame.draw.line(screen, color, (left_x, top_y), (right_x + ext_len - 2, top_y), 1)
            # 3. Triangolo PIENO (Base verticale sulla barra, punta verso il Vault Boy)
            tri_points = [
                (right_x, top_y),
                (right_x, tri_bottom_y),
                (right_x + tri_w, top_y)
            ]
            pygame.draw.polygon(screen, color, tri_points, 0)

        elif limb_key in ['arm_l', 'leg_l']:
            # Arti a DESTRA dello Schermo (Vault Boy a sinistra)
            # 1. Stanghetta verticale esterna a destra
            pygame.draw.line(screen, color, (right_x, top_y), (right_x, bottom_y), 1)
            # 2. Linea orizzontale superiore che si estende verso il Vault Boy
            pygame.draw.line(screen, color, (right_x, top_y), (left_x - ext_len + 2, top_y), 1)
            # 3. Triangolo PIENO (Base verticale sulla barra, punta verso il Vault Boy)
            tri_points = [
                (left_x, top_y),
                (left_x, tri_bottom_y),
                (left_x - tri_w, top_y)
            ]
            pygame.draw.polygon(screen, color, tri_points, 0)

###############################################
# Generic UI elements for the Pip-OS project #
###############################################

# Generic list class for displaying items with selection
# Supports stats display and selection dot rendering

class GenericList:
    def __init__(self, draw_space, font, items=["",], enable_dot=False,
                 selection_rect_color=settings.PIP_BOY_LIGHT,
                 text_color=settings.PIP_BOY_LIGHT,
                 selected_text_color=settings.PIP_BOY_DARK,
                 stats=None,
                 stats_color=settings.PIP_BOY_LIGHT,
                 selected_stats_color=settings.PIP_BOY_DARK,
                 dot_color=settings.PIP_BOY_LIGHT,
                 dot_darker_color=settings.PIP_BOY_DARK,
                 dot_size=settings.RADIO_STATION_SELECTION_DOT_SIZE,
                 text_margin=settings.RADIO_STATION_TEXT_MARGIN,
                 selection_dot_margin=settings.RADIO_STATION_SELECTION_MARGIN):
        self.draw_space = draw_space
        self.font = font
        self.enable_dot = enable_dot
        self.font_height = self.font.get_height()
        self.selection_rect_width = draw_space.width
        self.selection_rect_color = selection_rect_color
        self.text_color = text_color
        self.selected_text_color = selected_text_color
        self.text_margin = text_margin

        # Stats-related properties
        self.stats = stats
        if self.stats is not None:
            if len(self.stats) != len(items):
                raise ValueError("Length of stats must match the number of items")
            self.stats_color = stats_color
            self.selected_stats_color = selected_stats_color
            self.max_stat_width = max([self.font.size(str(stat))[0] for stat in self.stats])

        
        # Dot-related properties (only initialized if needed)
        self.dot = None
        self.dot_darker = None
        self.dot_size = dot_size
        self.selection_dot_margin = selection_dot_margin
        self.dot_color = dot_color
        self.dot_darker_color = dot_darker_color


        self.list_surface = None
        self.selected_text = None
        self.selected_stat = None
        
        self.view_surface = pygame.Surface((self.draw_space.width, self.draw_space.height), pygame.SRCALPHA)

        self._init_selection_rect()
           
        self.selected_index = 0
        self.previously_selected_index = 0
        self.items = items
        
        if len(self.items) > 0:
            if self.selected_index >= len(self.items):
                self.selected_index = max(0, len(self.items) - 1)
        
        self._prepare_list_surface()
        # Only create dots if enabled
        if self.enable_dot:
            self._create_dots()

    def _prepare_list_surface(self):
        if not self.items:
            self.list_surface = pygame.Surface((self.draw_space.width, 0), pygame.SRCALPHA)
            return
        height = self.font_height * len(self.items)
        self.list_surface = pygame.Surface((self.draw_space.width, height), pygame.SRCALPHA)
        
        if self.stats is not None:
            stats_column_center_x = self.selection_rect_width - self.max_stat_width
        for i, item in enumerate(self.items):
            # Render item label
            text_surface = self.font.render(item, True, self.text_color)
            self.list_surface.blit(text_surface, (self.text_margin, i * self.font_height))
            # Render stat if enabled
            if self.stats is not None:
                stat = str(self.stats[i])
                stat_surface = self.font.render(stat, True, self.stats_color)
                stat_x = stats_column_center_x - (stat_surface.get_width() // 2)
                self.list_surface.blit(stat_surface, (stat_x, i * self.font_height))
        self.update_list()

    def _create_dots(self):
        """Initialize dot surfaces only if enabled"""
        self.dot = pygame.Surface((self.dot_size, self.dot_size), pygame.SRCALPHA)
        self.dot.fill(self.dot_color)
        self.dot_darker = pygame.Surface((self.dot_size, self.dot_size), pygame.SRCALPHA)
        self.dot_darker.fill(self.dot_darker_color)

    def _init_selection_rect(self):
        self.selection_rect = pygame.Rect(
            0, 0, self.selection_rect_width, self.font_height
        )

    def set_items(self, items, stats=None):
        self.items = items
        if stats is not None:
            if len(stats) != len(items):
                raise ValueError("Length of stats must match the number of items")
            self.stats = stats
        else:
            self.stats = None
        if self.selected_index >= len(self.items):
            self.selected_index = max(0, len(self.items) - 1)
        self._prepare_list_surface()
        

    def update_list(self):
        if not self.items:
            self.selected_text = None
            return
        self.selection_rect.y = self.selected_index * self.font_height
        selected_item = self.items[self.selected_index]
        self.selected_text = self.font.render(selected_item, True, self.selected_text_color)
        if self.stats is not None:
            stat = str(self.stats[self.selected_index])
            self.selected_stat = self.font.render(stat, True, self.selected_stats_color)


    def change_selection(self, direction: bool):
        new_index = self.selected_index + (-1 if direction else 1)

        prev_index = self.selected_index
        if 0 <= new_index < len(self.items):
            self.selected_index = new_index
            self.update_list()    
        return prev_index

    def render(self, screen, active_index=None, was_selected=False):
        if not self.list_surface or not self.selected_text:
            return

        self.view_surface.fill(settings.BACKGROUND)
        self.view_surface.blit(self.list_surface, (0, 0))

        # Draw selection rectangle
        pygame.draw.rect(self.view_surface, self.selection_rect_color, self.selection_rect)
        self.view_surface.blit(self.selected_text, (self.text_margin, self.selection_rect.y))
        
        if self.stats is not None:
            stat_x = self.selection_rect_width - self.max_stat_width- (self.selected_stat.get_width() // 2)
            self.view_surface.blit(self.selected_stat, (stat_x, self.selection_rect.y))

        # Conditional dot rendering
        if self.enable_dot and active_index is not None and was_selected:
            dot = (self.dot_darker if (active_index == self.selected_index)
                   else self.dot)
            dot_y = (active_index * self.font_height + 
                    (self.font_height // 2) - 
                    (self.dot_size // 2))
            self.view_surface.blit(dot, (self.text_margin - self.selection_dot_margin, dot_y))

        screen.blit(self.view_surface, (self.draw_space.x, self.draw_space.y))






# Generic grid class for displaying items with labels and values
# Supports vertical dividers and highlighting of entries


class ItemGrid:
    def __init__(self, draw_space, font, padding=5, text_margin=0.5):
        self.draw_space = draw_space
        self.font = font
        self.line_height = self.font.get_height()
        self.padding = padding
        self.precomputed_bg = []
        self.precomputed_text = []
        self.precomputed_divider = None  # Only one divider per grid
        self.top_margin = text_margin
        self.bottom_margin = text_margin * 2
        self.text_cache = {}  # New surface cache
        


    def _get_rendered_text(self, text, color):
        key = (text, color)
        if key not in self.text_cache:
            self.text_cache[key] = self.font.render(text, True, color)
        return self.text_cache[key]


    def update(self, entries):
        """Prepare all rendering elements with proper alignment, adding a vertical divider if needed."""
        self.precomputed_bg = []
        self.precomputed_text = []
        self.precomputed_divider = None  # Reset divider each update
        current_y = self.draw_space.bottom - settings.GRID_BOTTOM_MARGIN
        current_y = self.draw_space.top
        """
        current_y = self.draw_space.bottom - settings.GRID_BOTTOM_MARGIN
        total_height = sum(
            (
                self.top_margin +
                self.line_height +
                (max(0, len(entry.get("lines", [])) - 1) * self.line_height) +
                self.bottom_margin
            ) + self.padding
            for entry in entries
        )

        current_y -= total_height
        current_y = max(current_y, self.draw_space.top)  # Clamp to top boundary
        """
        label_x = self.draw_space.left + self.padding

        for entry in entries:
            if current_y >= self.draw_space.bottom:
                break  # Stop if no space left

            bg_color = settings.PIP_BOY_DARKER if entry.get("highlight") else settings.PIP_BOY_DARK
            entry_lines = []
            label_y = current_y + self.top_margin
            icon_x = label_x
            icon_front_x = label_x
            value_x = self.draw_space.right - self.padding
            
            if entry.get("icon_front") and "icon" in entry:
                icon_surface = entry["icon"]
                entry_lines.append(("icon", icon_surface, (icon_x, label_y + 1)))
                # Move label to the right of the icon
                icon_front_x += icon_surface.get_width() + self.padding

            label_surface = self._get_rendered_text(entry["label"], settings.PIP_BOY_LIGHT)
            label_pos = (icon_front_x, label_y)
            entry_lines.append(("label", label_surface, label_pos))

            value_y = label_y        


            if "lines" in entry:
                for i, line in enumerate(entry["lines"]):
                    if i > 0:
                        value_y += self.line_height
                    components = []
                    line_width = 0

                    if "icon" in line:
                        icon_x = value_x - (line["icon"].get_width() // 2)
                        components.append(line["icon"])
                        line_width += line["icon"].get_width() + self.padding

                    text_surface = self.font.render(str(line["value"]), True, settings.PIP_BOY_LIGHT)
                    components.append(text_surface)
                    line_width += text_surface.get_width()

                    # Right-align components
                    current_x = value_x - line_width
                    for component in components:
                        y_pos = value_y + (1 if component == line.get("icon") else 0)
                        entry_lines.append(("component", component, (current_x, y_pos)))
                        icon_x -= component.get_width()
                        current_x += component.get_width() + self.padding
                        

                
            if "value" in entry:
                text_surface = self._get_rendered_text(str(entry["value"]), settings.PIP_BOY_LIGHT)
                text_width = text_surface.get_width()
                entry_lines.append(("value", text_surface, (value_x - text_width, value_y)))
                
            if not entry.get("icon_front") and "icon" in entry:
                icon_surface = entry["icon"]
                icon_x = value_x - icon_surface.get_width() - text_width - (self.padding * 2)
                entry_lines.append(("icon", icon_surface, (icon_x, value_y + 1)))

            # Entry height calculation
            additional_lines = max(0, len(entry.get("lines", [])) - 1)
            entry_height = int(self.top_margin) + self.line_height + additional_lines * self.line_height + int(self.bottom_margin)

            # Store background rectangle
            self.precomputed_bg.append((
                pygame.Rect(
                    self.draw_space.left,
                    current_y,
                    self.draw_space.width,
                    entry_height
                ),
                bg_color
            ))

            # Store text elements
            for element in entry_lines:
                self.precomputed_text.append((element[1], element[2]))

            # Add vertical divider if needed (only one per grid)
            if self.precomputed_divider is None and entry.get("split") and icon_x is not None:
                self.precomputed_divider = pygame.Rect(
                    icon_x,  # Position divider left of the icon
                    current_y,
                    self.padding,
                    entry_height
                )

            current_y += entry_height
            if entry != entries[-1]:  # Only add padding if it's not the last entry
                current_y += self.padding


    def render(self, surface):
        # Draw backgrounds first
        for rect, bg_color in self.precomputed_bg:
            pygame.draw.rect(surface, bg_color, rect)

        # Draw text and icons
        for text_surface, pos in self.precomputed_text:
            surface.blit(text_surface, pos)

        # Draw the vertical divider if it exists
        if self.precomputed_divider is not None:
            pygame.draw.rect(surface, settings.BACKGROUND, self.precomputed_divider)

# Animated image class for displaying sequences of images
# Supports looping and stopping the animation

        
class AnimatedImage:
    def __init__(self, screen, images, position: tuple, frame_duration: int, frame_order: list=None, loop: bool = True, sound_path: str = None):
        self.screen = screen
        self.images = images
        self.position = position
        self.frame_duration = frame_duration / 1000  # Convert to seconds
        self.frame_order = frame_order or list(range(len(images)))
        self.loop = loop
        self.sound_path = sound_path

        self.current_frame_index = 0
        self.done = False
        self.running = False  # Flag for controlling the thread
        self.stop_event = Event()  # Event to stop the thread
        self.lock = Lock()  # Lock to prevent race conditions in render()
        self.thread = None  # The update thread

    def _update_loop(self):
        """Thread function for updating frames."""
        while not self.stop_event.is_set() and not self.done:
            with self.lock:  # Ensure thread safety for frame updates
                if self.done:
                    break

                self.current_frame_index += 1
                if self.current_frame_index >= len(self.frame_order):
                    if self.loop:
                        self.current_frame_index = 0
                        self.play_sound()
                    else:
                        self.done = True
                        break

            # Instead of sleep, wait with the option to interrupt instantly
            self.stop_event.wait(timeout=self.frame_duration)


    def play_sound(self):
        """Play the sound effect if provided."""
        if self.sound_path:
            Utils.play_sfx(self.sound_path, settings.VOLUME / 8, channel=5)

    def start(self):
        """Start the animation thread."""
        if self.thread is None or not self.thread.is_alive():
            self.done = False
            self.stop_event.clear()
            self.thread = Thread(target=self._update_loop, daemon=True)
            self.play_sound()
            self.thread.start()

    def stop(self):
        """Stop the animation instantly."""
        ch = pygame.mixer.Channel(5)
        ch.stop()  # Stops any sound currently on this channel
        self.stop_event.set()  # Signal thread to exit
        self.thread = None  # Allow restarting without blocking

    def render(self):
        """Render the current frame (thread-safe)."""
        with self.lock:
            self.screen.blit(self.images[self.frame_order[self.current_frame_index]], self.position)

    def reset(self):
        """Reset the animation and restart it."""
        self.stop()
        self.current_frame_index = 0
        self.done = False
        self.start()



class WireframeItem:
    def __init__(self, screen, position, draw_space, model_path,
                 frame_duration: int = 100, loop: bool = True):
        self.screen = screen
        self.position = position
        self.rect = draw_space
        self.loop = loop

        # Wrap the C++ renderer
        self.renderer = wireframe.WireframeRenderer(draw_space.width, draw_space.height, 125.0)
        self.renderer.load_model(model_path)
        self.renderer.set_camera(5.0, -2.0, -30.0)
        self.renderer.set_rotation(0.0, 0.0, 0.0)
        # Thread state
        self.frame_duration = frame_duration / 500.0  # seconds
        self.done = False
        self.stop_event = Event()
        self.lock = Lock()
        self.thread = None

        # Last rendered lines (safe to reuse between frames)
        self.lines = []

    def _update_loop(self):
        """Thread function for updating rotation frames."""
        while not self.stop_event.is_set() and not self.done:
            with self.lock:
                # Get next rotation frame from C++ backend
                self.lines = self.renderer.render()
                if not self.lines and not self.loop:
                    self.done = True
                    break
            # Wait with the ability to break early
            self.stop_event.wait(timeout=self.frame_duration)

    def start(self):
        """Start the rotation loop thread."""
        if self.thread is None or not self.thread.is_alive():
            self.done = False
            self.stop_event.clear()
            self.renderer.start()
            self.thread = Thread(target=self._update_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop the rotation instantly."""
        self.stop_event.set()
        self.renderer.stop()
        self.thread = None

    def reset(self):
        """Reset and restart the rotation."""
        self.stop()
        self.done = False
        self.lines = []
        self.start()

    def render(self):
        """Blit the current frame to the screen (thread-safe)."""
        with self.lock:
            for line in self.lines:
                
                # print the line 
                
                pygame.draw.aaline(
                    self.screen,
                    settings.PIP_BOY_LIGHT,
                    (line.x1 + self.position[0], line.y1 + self.position[1]),
                    (line.x2 + self.position[0], line.y2 + self.position[1])
                )


def draw_nv_ui(screen, player_data, current_tab="STATS", current_subtab=0):
    COLOR_NV = settings.PIP_BOY_LIGHT
    
    font = pygame.font.Font(settings.MAIN_FONT_PATH, 11)
    font_large = pygame.font.Font(settings.MAIN_FONT_PATH, 13)

    screen_w = screen.get_width()
    screen_h = screen.get_height()

    if isinstance(player_data, dict):
        hp = player_data.get('hp', 280)
        max_hp = player_data.get('max_hp', 280)
        ap = player_data.get('ap', 85)
        max_ap = player_data.get('max_ap', 85)
        xp = player_data.get('xp', 1880)
        next_xp = player_data.get('next_xp', 2000)
        name = player_data.get('name', 'DanieleM')
        level = player_data.get('level', 28)
        status_side_index = player_data.get('status_side_index', 0)
    else:
        hp = getattr(settings, 'PLAYER_HP', 280)
        max_hp = getattr(settings, 'PLAYER_MAX_HP', 280)
        ap = getattr(settings, 'PLAYER_AP', 85)
        max_ap = getattr(settings, 'PLAYER_MAX_AP', 85)
        xp = getattr(settings, 'PLAYER_XP', 1880)
        next_xp = getattr(settings, 'PLAYER_NEXT_XP', 2000)
        name = getattr(settings, 'PLAYER_NAME', 'DanieleM')
        level = getattr(settings, 'PLAYER_LEVEL', 28)
        status_side_index = 0

    # =================
    # --- 1. HEADER ---
    # =================
    header_line_y = 14
    tick_h = 8
    margin_left = 10

    # --- Main Title (┌── STATS ──) ---
    tab_name = str(current_tab).upper()
    tab_txt = font_large.render(tab_name, True, COLOR_NV)

    wing_len = 12  # Space between Side and Menu Title
    text_gap = 4

    left_tick_x = margin_left
    left_line_end = left_tick_x + wing_len

    tab_rect = tab_txt.get_rect(left=left_line_end + text_gap + 10, centery=header_line_y)

    right_line_start = tab_rect.right + text_gap
    right_tick_x = right_line_start + wing_len

    # Right Side (┌──)
    pygame.draw.line(screen, COLOR_NV, (left_tick_x, header_line_y), (left_tick_x, header_line_y + tick_h), 1)
    pygame.draw.line(screen, COLOR_NV, (left_tick_x, header_line_y), (left_line_end + 5, header_line_y), 1)

    # Menu Title (STATS/ITEMS/DATA)
    screen.blit(tab_txt, tab_rect)

    # Left Side (──)
    pygame.draw.line(screen, COLOR_NV, (right_line_start + 5, header_line_y), (right_tick_x + 10, header_line_y), 1)

    # --- Right statistics (LVL, HP, AP, XP) ---
    stats_items = [
        f"LVL {level}",
        f"HP {hp}/{max_hp}",
        f"AP {ap}/{max_ap}",
        f"XP {xp}/{next_xp}"
    ]

    padding_x = 2
    spacing_between_boxes = 4
    curr_right = screen_w - 10

    for item in reversed(stats_items):
        txt_surf = font.render(item, True, COLOR_NV)
        txt_w = txt_surf.get_width()
        
        box_right = curr_right
        box_left = box_right - (txt_w + padding_x * 2)
        
        # Statistics "L" Part (┐)
        pygame.draw.line(screen, COLOR_NV, (box_left, header_line_y), (box_right, header_line_y), 1)
        pygame.draw.line(screen, COLOR_NV, (box_right, header_line_y), (box_right, header_line_y + tick_h), 1)
        
        screen.blit(txt_surf, (box_left + padding_x, header_line_y + 3))
        
        curr_right = box_left - spacing_between_boxes

    # ======================================================
    # --- 2. LATERAL SUBMENÙ OF STATUS (CND / RAD / EFF) ---
    # ======================================================
    if tab_name in ["STAT", "STATS"] and current_subtab == 0:
        side_options = ["CND", "RAD", "EFF"]
        side_y = 55
        for idx, opt in enumerate(side_options):
            txt = font.render(opt, True, COLOR_NV)
            if idx == status_side_index:
                box = pygame.Rect(8, side_y - 2, txt.get_width() + 6, txt.get_height() + 3)
                pygame.draw.rect(screen, COLOR_NV, box, 1)
            screen.blit(txt, (11, side_y))
            side_y += 20

        vb_center_x = screen_w // 2 - 10
        vb_center_y = screen_h // 2 - 5

        # Gestione dei 3 Sotto-Tab Laterali:
        if status_side_index == 0:
            # Schermata CND (Vault Boy + Condizione Arti + Quick Items)
            draw_vaultboy_and_cnd(screen, player_data, vb_center_x, vb_center_y, COLOR_NV)
            
            quick_items = player_data.get('quick_items', ["(5) Stimpak S)", "(3) Doctor's Bag E)"]) if isinstance(player_data, dict) else ["(5) Stimpak S)", "(3) Doctor's Bag E)"]
            item_y = 45
            for item_str in quick_items:
                item_txt = font.render(item_str, True, COLOR_NV)
                item_rect = item_txt.get_rect(right=screen_w - 20, top=item_y)
                screen.blit(item_txt, item_rect)
                item_y += 37

        elif status_side_index == 1:
            # Schermata RAD (Radiazioni completa con scala e freccia)
            draw_rad_screen(screen, player_data, COLOR_NV, font, font_large, screen_w, screen_h)

        elif status_side_index == 2:
            # Schermata EFF (Lista effetti attivi completa)
            draw_eff_screen(screen, player_data, COLOR_NV, font, font_large, screen_w, screen_h)

    # =================================
    # --- 3. FOOTER (LOWER SUBMENU) ---
    # =================================
    subtabs_map = {
        'STATS': ["Status", "S.P.E.C.I.A.L.", "Skills", "Perks", "General"],
        'ITEMS': ["Weapons", "Apparel", "Aid", "Misc", "Ammo"],
        'DATA': ["Quests", "Local Map", "World Map", "Notes", "Radio"]
    }

    subtabs = subtabs_map.get(tab_name, subtabs_map.get('STATS'))
    
    # Name and Level
    if tab_name in ["STAT", "STATS"] and current_subtab == 0 and status_side_index == 0:
        char_txt = font.render(f"{name} - Level {level}", True, COLOR_NV)
        rect_char = char_txt.get_rect()
        rect_char.centerx = screen_w // 2 - 10
        rect_char.bottom = screen_h - 42
        screen.blit(char_txt, rect_char)

    sub_y = screen_h - 18
    box_pad_x = 3
    box_pad_y = 2
    dash_margin = 5  # Text-Line interspace if submenu is not selected
    gap_between_items = 18

    item_widths = [font.size(st)[0] for st in subtabs]
    total_content_w = sum(item_widths) + (len(subtabs) - 1) * gap_between_items
    start_x = max(20, (screen_w - total_content_w) // 2)

    item_x_positions = []
    curr_x = start_x
    for w in item_widths:
        item_x_positions.append(curr_x)
        curr_x += w + gap_between_items

    txt_h = font.size("A")[1]
    line_y = sub_y + (txt_h // 2)
    corner_tick_h = tick_h

    margin_left = 10
    margin_right = screen_w - 10

    # Submenus Rendering
    for i, st_name in enumerate(subtabs):
        x = item_x_positions[i]
        w = item_widths[i]
        txt_surf = font.render(st_name, True, COLOR_NV)

        is_selected = (i == current_subtab)

        # Selection Rectangle
        if is_selected:
            box_rect = pygame.Rect(x - box_pad_x, sub_y - box_pad_y, w + box_pad_x * 2, txt_h + box_pad_y * 2)
            pygame.draw.rect(screen, COLOR_NV, box_rect, 1)

        screen.blit(txt_surf, (x, sub_y))

        # --- Left Angle (└) ---
        if i == 0:
            pygame.draw.line(screen, COLOR_NV, (margin_left, line_y - corner_tick_h), (margin_left, line_y), 1)
            line_end_x = (x - box_pad_x) if is_selected else (x - dash_margin)
            if line_end_x > margin_left:
                pygame.draw.line(screen, COLOR_NV, (margin_left, line_y), (line_end_x, line_y), 1)
        
        # --- Separating Lines ---
        if i < len(subtabs) - 1:
            next_is_selected = (i + 1 == current_subtab)
            next_x = item_x_positions[i + 1]

            seg_start_x = (x + w + box_pad_x) if is_selected else (x + w + dash_margin)
            seg_end_x = (next_x - box_pad_x) if next_is_selected else (next_x - dash_margin)

            if seg_end_x > seg_start_x:
                pygame.draw.line(screen, COLOR_NV, (seg_start_x, line_y), (seg_end_x, line_y), 1)
        else:
            # --- Right Angle (┘) ---
            seg_start_x = (x + w + box_pad_x) if is_selected else (x + w + dash_margin)
            if margin_right > seg_start_x:
                pygame.draw.line(screen, COLOR_NV, (seg_start_x, line_y), (margin_right, line_y), 1)
            pygame.draw.line(screen, COLOR_NV, (margin_right, line_y - corner_tick_h), (margin_right, line_y), 1)

def draw_rad_screen(screen, player_data, COLOR_NV, font, font_large, screen_w, screen_h):
    """Renderizza il sotto-tab RAD con scala riallineata a sinistra e distanza triangolo-50 RAD corretta."""
    rads = player_data.get('rads', getattr(settings, 'RADIATION_VALUE', 312))
    rad_resist = player_data.get('rad_resist', getattr(settings, 'RAD_RESIST', 6))

    # 1. RADAWAY / RAD-X
    quick_rad_items = player_data.get('quick_rad_items', ["(1) RadAway A)", "(3) Rad-X X)"])
    item_y = 45
    for item_str in quick_rad_items:
        item_txt = font.render(item_str, True, COLOR_NV)
        item_rect = item_txt.get_rect(right=screen_w - 15, top=item_y)
        screen.blit(item_txt, item_rect)
        item_y += 25

    # Coordinate di riferimento
    center_x = 115
    right_x = screen_w - 10
    eff_top_y = 120
    eff_bottom_y = 170

    # 2. RIQUADRO SUPERIORE "EFF"
    if rads >= 800: rad_eff_str = "-3 END, -2 AGL, -2 STR"
    elif rads >= 600: rad_eff_str = "-2 END, -2 AGL"
    elif rads >= 400: rad_eff_str = "-2 END, -1 AGL"
    elif rads >= 200: rad_eff_str = "-1 END"
    else: rad_eff_str = "NONE"

    pygame.draw.line(screen, COLOR_NV, (center_x, eff_top_y), (right_x, eff_top_y), 1)
    pygame.draw.line(screen, COLOR_NV, (right_x, eff_top_y), (right_x, eff_bottom_y - 17), 1)

    eff_label = font_large.render("EFF", True, COLOR_NV)
    eff_val = font_large.render(rad_eff_str, True, COLOR_NV)
    screen.blit(eff_label, (center_x, eff_top_y + 2))
    screen.blit(eff_val, eff_val.get_rect(right=right_x - 15, top=eff_top_y + 2))

    # 3. LINEA DI SEPARAZIONE ORIZZONTALE
    pygame.draw.line(screen, COLOR_NV, (0, eff_bottom_y), (center_x - 5, eff_bottom_y), 1)

    # 4. SEZIONE INFERIORE (RAD RESIST | DIVISORE VERTICALE | RADS METER)
    bot_y = eff_bottom_y + 2

    # Linea verticale divisoria
    pygame.draw.line(screen, COLOR_NV, (center_x - 5, eff_bottom_y), (center_x - 5, eff_bottom_y + 20), 1)

    # RAD RESIST (A sinistra)
    rr_label = font.render("RAD RESIST", True, COLOR_NV)
    rr_val = font.render(f"{rad_resist}%", True, COLOR_NV)
    screen.blit(rr_label, (10, bot_y))
    screen.blit(rr_val, rr_val.get_rect(right=center_x - 10, top=bot_y))

    # RADS (A destra)
    rads_label = font.render("RADS", True, COLOR_NV)
    rads_x = center_x 
    screen.blit(rads_label, (rads_x, bot_y))

    # =========================================================
    # --- SCALA GRADUATA RIALLINEATA ---
    # =========================================================
    # Spostamento scala a sinistra di 8px
    meter_x1 = rads_x + rads_label.get_width() + 10
    meter_x2 = right_x - 8
    meter_y = eff_bottom_y
    meter_w = max(10, meter_x2 - meter_x1)

    # Linea orizzontale della scala radiazioni e bordo verticale destro
    pygame.draw.line(screen, COLOR_NV, (center_x, meter_y), (right_x, meter_y), 1)
    pygame.draw.line(screen, COLOR_NV, (right_x, eff_bottom_y), (right_x, eff_bottom_y + 20), 1)

    # NUMERI 500 E 1000 (SOPRA LA LINEA)
    lbl_500 = font.render("500", True, COLOR_NV)
    lbl_1000 = font.render("1000", True, COLOR_NV)
    screen.blit(lbl_500, lbl_500.get_rect(center=(meter_x1 + meter_w // 2, meter_y - 7)))
    screen.blit(lbl_1000, lbl_1000.get_rect(right=meter_x2, bottom=meter_y - 2))

    # TRIANGOLI AGLI ESTREMI
    # 0 RAD (Sinistra: arretrato di 2px extra per dare respiro al tick dei 50 RAD)
    tri_0 = [
        (meter_x1 - 5, meter_y),
        (meter_x1, meter_y),
        (meter_x1, meter_y + 6)
    ]
    pygame.draw.polygon(screen, COLOR_NV, tri_0)

    # 1000 RAD (Destra)
    tri_1000 = [
        (meter_x2 + 3, meter_y),
        (meter_x2 - 2, meter_y),
        (meter_x2 - 2, meter_y + 6)
    ]
    pygame.draw.polygon(screen, COLOR_NV, tri_1000)

    # TACCHE LUNGHE (4 tacche: 200, 400, 600, 800 RAD)
    long_ticks = [200, 400, 600, 800]
    for val in long_ticks:
        tx = meter_x1 + int((val / 1000.0) * meter_w)
        pygame.draw.line(screen, COLOR_NV, (tx, meter_y), (tx, meter_y + 7), 1)

    # TACCHE CORTE (10 tacche: 50, 150, 250, 350, 450, 550, 650, 750, 850, 950 RAD)
    short_ticks = [50, 150, 250, 350, 450, 550, 650, 750, 850, 950]
    for val in short_ticks:
        tx = meter_x1 + int((val / 1000.0) * meter_w)
        pygame.draw.line(screen, COLOR_NV, (tx, meter_y), (tx, meter_y + 4), 1)

    # INDICATORE VALORE ATTUALE + FRECCIA VETTORIALE
    clamped_rads = max(0, min(1000, rads))
    indicator_x = meter_x1 + int((clamped_rads / 1000.0) * meter_w)

    # 1. Numero Radiazioni (posizionato a sinistra della freccia)
    ind_txt = font.render(f"{rads}", True, COLOR_NV)
    screen.blit(ind_txt, ind_txt.get_rect(right=indicator_x - 5, top=meter_y + 15))

    # 2. Freccia
    arrow_top_y = meter_y + 9
    arrow_bot_y = meter_y + 22
    
    head_pts = [
        (indicator_x, arrow_top_y), 
        (indicator_x - 4, arrow_top_y + 5), 
        (indicator_x + 4, arrow_top_y + 5)
    ]
    pygame.draw.polygon(screen, COLOR_NV, head_pts)
    pygame.draw.line(screen, COLOR_NV, (indicator_x, arrow_top_y), (indicator_x, arrow_bot_y + 7), 1)


def draw_eff_screen(screen, player_data, COLOR_NV, font, font_large, screen_w, screen_h):
    """Renderizza il sotto-tab EFF senza la linea di chiusura finale."""
    default_effects = [
        ("Boxing Times", "Unarmed +20 (53s)"),
        ("Buffout", "HP +60 (233s), END +3 (233s)"),
        ("Hoarder Penalty", "STR -1, PER -1, LCK -1, INT -1, END -1, CHR -1, AGL -1"),
        ("Legion Praetorian Armor", "Unarmed +10, Melee Weap. +5, AGL +1"),
        ("Merchant Outfit", "Barter +5"),
        ("Sunset Sarsaparilla", "HP +2 (25s)"),
        ("Weapon Binding Ritual", "Unarm. Dam. +10 (233s), HP -2 (1s)")
    ]
    effects = player_data.get('effects', default_effects)

    if not effects:
        empty_txt = font_large.render("NO ACTIVE EFFECTS", True, COLOR_NV)
        screen.blit(empty_txt, empty_txt.get_rect(center=(screen_w // 2 + 20, screen_h // 2)))
        return

    start_x = 42
    max_w = screen_w - start_x - 10
    curr_y = 37
    name_col_w = 120

    # LINEA DI SEPARAZIONE IN CIMA
    pygame.draw.line(screen, COLOR_NV, (start_x, curr_y), (start_x + max_w, curr_y), 1)
    curr_y += 4

    num_effects = len(effects)
    for idx, (name, desc) in enumerate(effects):
        name_txt = font.render(name, True, COLOR_NV)
        screen.blit(name_txt, (start_x, curr_y))

        desc_x = start_x + name_col_w
        desc_max_w = max_w - name_col_w
        
        words = desc.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= desc_max_w:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        line_y = curr_y
        for line in lines:
            l_surface = font.render(line, True, COLOR_NV)
            screen.blit(l_surface, (desc_x, line_y))
            line_y += 14

        item_height = max(18, (line_y - curr_y) + 2)
        curr_y += item_height

        # Disegna la linea divisoria SOLO SE NON è l'ultimo elemento
        if idx < num_effects - 1:
            pygame.draw.line(screen, COLOR_NV, (start_x, curr_y), (start_x + max_w, curr_y), 1)
            curr_y += 3