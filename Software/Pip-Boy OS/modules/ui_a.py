from threading import Thread, Event, Lock
from collections import Counter
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
    'torso_crippled': ((48, 54),  (+1, -1)),

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

    if assets:
        if hp_pct >= 0.8: face_idx = 1
        elif hp_pct >= 0.6: face_idx = 2
        elif hp_pct >= 0.4: face_idx = 3
        elif hp_pct >= 0.2: face_idx = 4
        else: face_idx = 5

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

    bar_positions = {
        'head':  (center_x - 13, center_y - 80, 32, 5),
        'torso': (center_x - 15, center_y - 18, 32, 5),
        'arm_r': (center_x - 75, center_y - 50, 28, 5),
        'arm_l': (center_x + 48, center_y - 50, 28, 5),
        'leg_r': (center_x - 75, center_y + 32, 28, 5),
        'leg_l': (center_x + 46, center_y + 32, 28, 5),
    }

    crippled_text_offsets = {
        'head':  (center_x - 18, center_y - 88),
        'torso': (center_x - 18, center_y - 20),
        'arm_r': (center_x - 130, center_y - 22),
        'arm_l': (center_x + 100, center_y - 22),
        'leg_r': (center_x - 110, center_y + 46),
        'leg_l': (center_x + 80,  center_y + 46),
    }

    pad = 1            
    tri_w = 6          
    ext_len = 16       

    for limb_key, (bx, by, bw, bh) in bar_positions.items():
        val = limbs.get(limb_key, 100)
        pct = max(0.0, min(1.0, val / 100.0))

        if val <= 0:
            tx, ty = crippled_text_offsets[limb_key]
            crip_txt = font_small.render("CRIPPLED", True, color)
            screen.blit(crip_txt, (tx, ty))

        fill_w = int((bw - 2) * pct)
        if fill_w > 0:
            pygame.draw.rect(screen, color, (bx + 1, by + 1, fill_w, bh - 2))

        vert_height = bh - 2   
        top_y = by - pad
        bottom_y = by + vert_height        
        tri_bottom_y = by + bh - 3        
        left_x = bx - pad
        right_x = bx + bw + pad

        if limb_key in ['head', 'torso']:
            u_points = [
                (left_x, bottom_y),
                (left_x, top_y),
                (right_x, top_y),
                (right_x, bottom_y)
            ]
            pygame.draw.lines(screen, color, False, u_points, 1)

        elif limb_key in ['arm_r', 'leg_r']:
            pygame.draw.line(screen, color, (left_x, top_y), (left_x, bottom_y), 1)
            pygame.draw.line(screen, color, (left_x, top_y), (right_x + ext_len - 2, top_y), 1)
            tri_points = [
                (right_x, top_y),
                (right_x, tri_bottom_y),
                (right_x + tri_w, top_y)
            ]
            pygame.draw.polygon(screen, color, tri_points, 0)

        elif limb_key in ['arm_l', 'leg_l']:
            pygame.draw.line(screen, color, (right_x, top_y), (right_x, bottom_y), 1)
            pygame.draw.line(screen, color, (right_x, top_y), (left_x - ext_len + 2, top_y), 1)
            tri_points = [
                (left_x, top_y),
                (left_x, tri_bottom_y),
                (left_x - tri_w, top_y)
            ]
            pygame.draw.polygon(screen, color, tri_points, 0)


def aggregate_items(raw_items):
    """ Aggrega elementi uguali nel formato 'Nome Oggetto (Quantità)' """
    counts = Counter(raw_items)
    aggregated = []
    for item, count in counts.items():
        if count > 1:
            aggregated.append(f"{item} ({count})")
        else:
            aggregated.append(item)
    return aggregated


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
                 selection_dot_margin=settings.RADIO_STATION_SELECTION_MARGIN,
                 auto_aggregate=True):
        self.draw_space = draw_space
        self.font = font
        self.enable_dot = enable_dot
        self.font_height = self.font.get_height() + 2
        self.selection_rect_width = draw_space.width
        self.selection_rect_color = selection_rect_color
        self.text_color = text_color
        self.selected_text_color = selected_text_color
        self.text_margin = text_margin
        self.auto_aggregate = auto_aggregate

        self.stats = stats
        if self.stats is not None:
            if len(self.stats) != len(items):
                raise ValueError("Length of stats must match the number of items")
            self.stats_color = stats_color
            self.selected_stats_color = selected_stats_color
            self.max_stat_width = max([self.font.size(str(stat))[0] for stat in self.stats])

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
        
        if self.auto_aggregate:
            self.items = aggregate_items(items)
        else:
            self.items = items
        
        if len(self.items) > 0:
            if self.selected_index >= len(self.items):
                self.selected_index = max(0, len(self.items) - 1)
        
        self._prepare_list_surface()
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
            text_surface = self.font.render(item, True, self.text_color)
            self.list_surface.blit(text_surface, (self.text_margin, i * self.font_height))
            if self.stats is not None:
                stat = str(self.stats[i])
                stat_surface = self.font.render(stat, True, self.stats_color)
                stat_x = stats_column_center_x - (stat_surface.get_width() // 2)
                self.list_surface.blit(stat_surface, (stat_x, i * self.font_height))
        self.update_list()

    def _create_dots(self):
        self.dot = pygame.Surface((self.dot_size, self.dot_size), pygame.SRCALPHA)
        self.dot.fill(self.dot_color)
        self.dot_darker = pygame.Surface((self.dot_size, self.dot_size), pygame.SRCALPHA)
        self.dot_darker.fill(self.dot_darker_color)

    def _init_selection_rect(self):
        self.selection_rect = pygame.Rect(
            0, 0, self.selection_rect_width, self.font_height
        )

    def set_items(self, items, stats=None):
        if self.auto_aggregate:
            self.items = aggregate_items(items)
        else:
            self.items = items

        if stats is not None:
            if len(stats) != len(self.items):
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

        # Disegna il rettangolo verde pieno per l'elemento selezionato
        pygame.draw.rect(self.view_surface, self.selection_rect_color, self.selection_rect)
        self.view_surface.blit(self.selected_text, (self.text_margin, self.selection_rect.y + 1))
        
        if self.stats is not None:
            stat_x = self.selection_rect_width - self.max_stat_width - (self.selected_stat.get_width() // 2)
            self.view_surface.blit(self.selected_stat, (stat_x, self.selection_rect.y + 1))

        if self.enable_dot and active_index is not None and was_selected:
            dot = (self.dot_darker if (active_index == self.selected_index)
                   else self.dot)
            dot_y = (active_index * self.font_height + 
                    (self.font_height // 2) - 
                    (self.dot_size // 2))
            self.view_surface.blit(dot, (self.text_margin - self.selection_dot_margin, dot_y))

        screen.blit(self.view_surface, (self.draw_space.x, self.draw_space.y))


class ItemGrid:
    def __init__(self, draw_space, font, padding=5, text_margin=0.5):
        self.draw_space = draw_space
        self.font = font
        self.line_height = self.font.get_height()
        self.padding = padding
        self.precomputed_bg = []
        self.precomputed_text = []
        self.precomputed_divider = None
        self.top_margin = text_margin
        self.bottom_margin = text_margin * 2
        self.text_cache = {}

    def _get_rendered_text(self, text, color):
        key = (text, color)
        if key not in self.text_cache:
            self.text_cache[key] = self.font.render(text, True, color)
        return self.text_cache[key]

    def update(self, entries):
        self.precomputed_bg = []
        self.precomputed_text = []
        self.precomputed_divider = None
        current_y = self.draw_space.top
        label_x = self.draw_space.left + self.padding

        for entry in entries:
            if current_y >= self.draw_space.bottom:
                break

            bg_color = settings.PIP_BOY_DARKER if entry.get("highlight") else settings.PIP_BOY_DARK
            entry_lines = []
            label_y = current_y + self.top_margin
            icon_x = label_x
            icon_front_x = label_x
            value_x = self.draw_space.right - self.padding
            
            if entry.get("icon_front") and "icon" in entry:
                icon_surface = entry["icon"]
                entry_lines.append(("icon", icon_surface, (icon_x, label_y + 1)))
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

            additional_lines = max(0, len(entry.get("lines", [])) - 1)
            entry_height = int(self.top_margin) + self.line_height + additional_lines * self.line_height + int(self.bottom_margin)

            self.precomputed_bg.append((
                pygame.Rect(
                    self.draw_space.left,
                    current_y,
                    self.draw_space.width,
                    entry_height
                ),
                bg_color
            ))

            for element in entry_lines:
                self.precomputed_text.append((element[1], element[2]))

            if self.precomputed_divider is None and entry.get("split") and icon_x is not None:
                self.precomputed_divider = pygame.Rect(
                    icon_x,
                    current_y,
                    self.padding,
                    entry_height
                )

            current_y += entry_height
            if entry != entries[-1]:
                current_y += self.padding

    def render(self, surface):
        for rect, bg_color in self.precomputed_bg:
            pygame.draw.rect(surface, bg_color, rect)

        for text_surface, pos in self.precomputed_text:
            surface.blit(text_surface, pos)

        if self.precomputed_divider is not None:
            pygame.draw.rect(surface, settings.BACKGROUND, self.precomputed_divider)


def draw_item_preview_box(screen, rect, font, color, text="IMAGE NOT FOUND"):
    """ Disegna il box dell'immagine / modello in alto a destra """
    pygame.draw.rect(screen, color, rect, 0)
    txt_surf = font.render(text, True, settings.PIP_BOY_DARK)
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)


def draw_bottom_status_bar(screen, screen_w, screen_h, font, color, weight="73.9/150", caps="1000"):
    """ Disegna la barra inferiore con Peso e Tappi """
    bar_y = screen_h - 22
    line_y = bar_y
    
    # Linea orizzontale di separazione
    pygame.draw.line(screen, color, (0, line_y), (screen_w, line_y), 1)

    # Box 1: Peso
    weight_rect = pygame.Rect(0, line_y, 110, 22)
    pygame.draw.rect(screen, color, weight_rect, 0)
    
    # Icona Peso (Zainetto/Peso)
    icon_weight = font.render("💼", True, settings.PIP_BOY_DARK)
    screen.blit(icon_weight, (5, line_y + 3))
    
    weight_txt = font.render(weight, True, settings.PIP_BOY_DARK)
    screen.blit(weight_txt, (22, line_y + 3))

    # Divisore
    pygame.draw.line(screen, settings.BACKGROUND, (110, line_y), (110, screen_h), 2)

    # Box 2: Tappi
    caps_rect = pygame.Rect(112, line_y, 90, 22)
    pygame.draw.rect(screen, color, caps_rect, 0)
    
    caps_icon = font.render("©", True, settings.PIP_BOY_DARK)
    screen.blit(caps_icon, (118, line_y + 3))
    
    caps_txt = font.render(str(caps), True, settings.PIP_BOY_DARK)
    screen.blit(caps_txt, (133, line_y + 3))

    # Divisore
    pygame.draw.line(screen, settings.BACKGROUND, (202, line_y), (202, screen_h), 2)


def draw_nv_ui(screen, player_data, current_tab="INV", current_subtab=3, custom_subtabs=None):
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

    # =========================================================
    # --- 1. HEADER PRINCIPALE (STAT, INV, DATA, MAP, RADIO) ---
    # =========================================================
    header_line_y = 14
    margin_left = 10

    main_tabs = ["STAT", "INV", "DATA", "MAP", "RADIO"]
    tab_x = margin_left
    gap_main = 20

    for tab in main_tabs:
        is_curr = (tab == str(current_tab).upper())
        if is_curr:
            txt_surf = font_large.render(f"[{tab}]", True, COLOR_NV)
        else:
            txt_surf = font.render(tab, True, COLOR_NV)
        
        screen.blit(txt_surf, (tab_x, 2))
        tab_x += txt_surf.get_width() + gap_main

    pygame.draw.line(screen, COLOR_NV, (margin_left, header_line_y), (screen_w - margin_left, header_line_y), 1)

    # =========================================================
    # --- 2. SUB-TAB SUPERIORI (WEAPONS APPAREL AID MISC JUNK AMMO) ---
    # =========================================================
    subtabs_map = {
        'STATS': ["Status", "S.P.E.C.I.A.L.", "Skills", "Perks", "General"],
        'ITEMS': ["REL", "AID", "MISC", "JUNK", "MODS", "AMMO"],
        'INV':   ["REL", "AID", "MISC", "JUNK", "MODS", "AMMO"],
        'DATA':  ["Quests", "Local Map", "World Map", "Notes", "Radio"]
    }

    subtabs = custom_subtabs if (custom_subtabs and len(custom_subtabs) > 0) else subtabs_map.get(str(current_tab).upper(), subtabs_map['INV'])

    sub_y = 22
    sub_x = 5
    sub_gap = 10

    for i, st_name in enumerate(subtabs):
        is_sel = (i == current_subtab)
        txt_surf = font.render(st_name, True, COLOR_NV if is_sel else settings.PIP_BOY_DARKER)
        screen.blit(txt_surf, (sub_x, sub_y))
        sub_x += txt_surf.get_width() + sub_gap

    # =========================================================
    # --- 3. ANTEPRIMA IMMAGINE E GRID PESO/VALORE (INV/ITEMS) ---
    # =========================================================
    if str(current_tab).upper() in ["INV", "ITEMS"]:
        # Box Immagine/Modello in alto a destra
        img_rect = pygame.Rect(180, 48, 110, 60)
        draw_item_preview_box(screen, img_rect, font, COLOR_NV, "IMAGE NOT FOUND")

    # =========================================================
    # --- 4. BARRA DI STATO INFERIORE (FOOTER) ---
    # =========================================================
    draw_bottom_status_bar(screen, screen_w, screen_h, font, COLOR_NV, weight="73.9/150", caps="1000")