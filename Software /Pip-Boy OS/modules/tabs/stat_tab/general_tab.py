import os
import pygame
import settings

_GENERAL_ICON_CACHE = {}

# Mappatura dei nomi fazione verso i file esatti della cartella reputation_general_nv
REPUTATION_IMAGE_MAP = {
    "Boomers": "BoomersReputation",
    "Brotherhood of Steel": "BrotherhoodOfSteelReputation",
    "Caesar's Legion": "CaesarLegionReputation",
    "Followers of the Apocalypse": "FollowersApocalypseReputation",
    "Freeside": "FreesideReputation",
    "Goodsprings": "GoodspringsReputation",
    "Great Khans": "GreatKhansNewVegas",
    "NCR": "NCRReputation",
    "Novac": "NovacReputation",
    "Powder Gangers": "PowderNewVegas",
    "Primm": "PrimmReputation",
    "The Strip": "NewVegasReputation",
    "White Gloves": "WhiteGloveSociety"
}

# Mappatura Karma -> file .png esatti
KARMA_IMAGE_MAP = {
    "Very Evil": "Very_Evil",
    "Evil": "Evil",
    "Neutral": "Neutral",
    "Good": "Good",
    "Very Good": "Very_Good"
}


def find_general_image_file(name, folder):
    """Cerca le immagini nelle sottocartelle karma_general_nv o reputation_general_nv."""
    if folder == "reputation_general_nv":
        target_name = REPUTATION_IMAGE_MAP.get(name, name)
    elif folder == "karma_general_nv":
        target_name = KARMA_IMAGE_MAP.get(name, name)
    else:
        target_name = name

    clean_name = target_name.strip()
    words = clean_name.split()

    pascal = "".join(w.capitalize() for w in words)
    under_title = "_".join(w.capitalize() for w in words)
    lower_under = clean_name.lower().replace(" ", "_")

    candidates = [clean_name, pascal, under_title, lower_under, clean_name.lower()]
    unique_candidates = []
    for c in candidates:
        if c and c not in unique_candidates:
            unique_candidates.append(c)

    exts = [".png", ".webp", ".dds"]
    possible_filenames = [f"{stem}{ext}" for stem in unique_candidates for ext in exts]

    base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.abspath(__file__)))
    search_dirs = [
        os.path.join(base_dir, "images", "new_vegas_icons", folder),
        os.path.join(base_dir, "images", folder),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "new_vegas_icons", folder)
    ]

    for s_dir in search_dirs:
        for fname in possible_filenames:
            full_path = os.path.normpath(os.path.join(s_dir, fname))
            if os.path.exists(full_path):
                return full_path
    return None


def load_general_icon(name, folder):
    """Carica e metti in cache le icone di Karma e Reputazione."""
    cache_key = f"{folder}_{name}"
    if cache_key in _GENERAL_ICON_CACHE:
        return _GENERAL_ICON_CACHE[cache_key]

    file_path = find_general_image_file(name, folder)
    if not file_path:
        _GENERAL_ICON_CACHE[cache_key] = None
        return None

    try:
        img = pygame.image.load(file_path).convert_alpha()
        _GENERAL_ICON_CACHE[cache_key] = img
        return img
    except Exception:
        try:
            from PIL import Image
            pil_img = Image.open(file_path).convert("RGBA")
            data = pil_img.tobytes()
            img = pygame.image.fromstring(data, pil_img.size, "RGBA").convert_alpha()
            _GENERAL_ICON_CACHE[cache_key] = img
            return img
        except Exception as e_pil:
            print(f"[DEBUG PIP-BOY] Errore caricamento icona {file_path}: {e_pil}")

    _GENERAL_ICON_CACHE[cache_key] = None
    return None


def colorize_surface(surface, color):
    """Applica il colore del Pip-Boy all'immagine mantenendo la trasparenza."""
    if surface is None:
        return None
    tinted = surface.copy()
    r, g, b = color[0], color[1], color[2]
    tinted.fill((r, g, b, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


class GeneralTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        self.ui_style = getattr(settings, 'UI_STYLE', 'Fallout_4')
        self.is_nv = (self.ui_style == "Fallout_NV")

        # Modalità attiva: "GENERAL" o "REPUTATION"
        self.mode = "GENERAL"

        self.selected_general_index = 0
        self.selected_rep_index = 0

        # Dati General Stats
        self.general_stats = getattr(settings, "DEFAULT_GENERAL_STATS", [
            {"name": "Quests Completed", "value": 3},
            {"name": "Locations Discovered", "value": 2},
            {"name": "People Killed", "value": 0},
            {"name": "Creatures Killed", "value": 3},
            {"name": "Locks Picked", "value": 0},
            {"name": "Computers Hacked", "value": 0},
            {"name": "Stimpaks Taken", "value": 0},
            {"name": "Rad-X Taken", "value": 0},
            {"name": "RadAway Taken", "value": 0},
            {"name": "Chems Taken", "value": 0}
        ])

        # Dati Karma
        self.karma_alignment = "Neutral"
        self.karma_title = "Renegade"

        # Dati Reputazioni
        self.reputations = getattr(settings, "DEFAULT_REPUTATIONS", [
            {"name": "Boomers", "status": "Neutral"},
            {"name": "Brotherhood of Steel", "status": "Neutral"},
            {"name": "Caesar's Legion", "status": "Neutral"},
            {"name": "Followers of the Apocalypse", "status": "Neutral"},
            {"name": "Freeside", "status": "Neutral"},
            {"name": "Great Khans", "status": "Neutral"},
            {"name": "NCR", "status": "Idolized"},
            {"name": "Novac", "status": "Neutral"},
            {"name": "Powder Gangers", "status": "Shunned"},
            {"name": "The Strip", "status": "Neutral"}
        ])

    def handle_threads(self, tab_selected: bool):
        pass

    def toggle_mode(self):
        """Alterna tra GENERAL e REPUTATION."""
        if self.mode == "GENERAL":
            self.mode = "REPUTATION"
        else:
            self.mode = "GENERAL"

    def scroll_general(self, direction: bool):
        """Scorri l'elenco della sub-tab attiva."""
        if self.mode == "GENERAL":
            if direction:  # SU
                if self.selected_general_index > 0:
                    self.selected_general_index -= 1
            else:  # GIÙ
                if self.selected_general_index < len(self.general_stats) - 1:
                    self.selected_general_index += 1
        else:
            if direction:  # SU
                if self.selected_rep_index > 0:
                    self.selected_rep_index -= 1
            else:  # GIÙ
                if self.selected_rep_index < len(self.reputations) - 1:
                    self.selected_rep_index += 1

    def _render_new_vegas_ui(self):
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        color = settings.PIP_BOY_LIGHT

        # FONT & LINE HEIGHT
        FONT_SIZE = 12
        main_font = pygame.font.Font(settings.MAIN_FONT_PATH, FONT_SIZE)
        sub_font = pygame.font.Font(settings.MAIN_FONT_PATH, FONT_SIZE - 2)
        LINE_HEIGHT = 18

        # --- GEOMETRIA ---
        left_x = max(20, int(screen_w * 0.12) - 5)
        # Ampliamo leggermente la larghezza fissa del riquadro per non far uscire i testi lunghi
        left_w = int(screen_w * 0.45)

        right_x = left_x + left_w + 10
        right_w = screen_w - right_x - 10

        top_y = int(screen_h * 0.18)
        bottom_y = int(screen_h * 0.82) + 15
        available_h = bottom_y - top_y

        right_offset_y = 12

        active_list = self.general_stats if self.mode == "GENERAL" else self.reputations
        active_index = self.selected_general_index if self.mode == "GENERAL" else self.selected_rep_index

        # 1. TOGGLE BUTTON
        toggle_text = "Reputation ENTER)" if self.mode == "GENERAL" else "General ENTER)"
        toggle_surf = main_font.render(toggle_text, True, color)
        toggle_x = right_x + right_w - toggle_surf.get_width() - 10
        self.screen.blit(toggle_surf, (toggle_x, top_y - 20 + right_offset_y))

        # 2. SCROLL LOGIC
        MAX_VISIBLE_ITEMS = max(1, available_h // LINE_HEIGHT)
        scroll_offset = max(0, min(active_index - MAX_VISIBLE_ITEMS // 2, len(active_list) - MAX_VISIBLE_ITEMS))
        scroll_offset = max(0, scroll_offset)

        # 3. SLIDER & ARROWS
        slider_x = left_x - 18
        arrow_w = 5
        arrow_h = 8
        notch = 3

        # Arrow UP
        top_arrow_y = top_y
        up_arrow_pts = [
            (slider_x, top_arrow_y),
            (slider_x + arrow_w, top_arrow_y + arrow_h),
            (slider_x, top_arrow_y + arrow_h - notch),
            (slider_x - arrow_w, top_arrow_y + arrow_h)
        ]
        pygame.draw.polygon(self.screen, color, up_arrow_pts)

        # Arrow DOWN
        bottom_arrow_y = bottom_y
        down_arrow_pts = [
            (slider_x, bottom_arrow_y),
            (slider_x + arrow_w, bottom_arrow_y - arrow_h),
            (slider_x, bottom_arrow_y - arrow_h + notch),
            (slider_x - arrow_w, bottom_arrow_y - arrow_h)
        ]
        pygame.draw.polygon(self.screen, color, down_arrow_pts)

        # Slider bar
        track_top = top_arrow_y + arrow_h - notch + 5
        track_bottom = bottom_arrow_y - arrow_h + notch - 5
        track_length = track_bottom - track_top

        total_items = len(active_list)
        if total_items > MAX_VISIBLE_ITEMS:
            bar_length = max(12, int(track_length * (MAX_VISIBLE_ITEMS / total_items)))
            max_scroll = total_items - MAX_VISIBLE_ITEMS
            scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0

            bar_top = track_top + int(scroll_ratio * (track_length - bar_length))
            bar_bottom = bar_top + bar_length
            pygame.draw.line(self.screen, color, (slider_x, bar_top), (slider_x, bar_bottom), 2)

        # 4. LEFT COLUMN LIST
        visible_items = active_list[scroll_offset : scroll_offset + MAX_VISIBLE_ITEMS]

        for idx_in_view, item in enumerate(visible_items):
            actual_index = scroll_offset + idx_in_view
            y_pos = top_y + (idx_in_view * LINE_HEIGHT)
            is_selected = (actual_index == active_index)

            if is_selected:
                select_rect = pygame.Rect(left_x - 4, y_pos, left_w, LINE_HEIGHT - 1)
                pygame.draw.rect(self.screen, color, select_rect, 1)

            name_surf = main_font.render(item["name"], True, color)
            self.screen.blit(name_surf, (left_x, y_pos + (LINE_HEIGHT - name_surf.get_height()) // 2))

            if self.mode == "GENERAL":
                val_surf = main_font.render(str(item["value"]), True, color)
                val_x = left_x + left_w - 15
                self.screen.blit(val_surf, (val_x, y_pos + (LINE_HEIGHT - val_surf.get_height()) // 2))

        # 5. RIGHT COLUMN DISPLAY
        if self.mode == "GENERAL":
            # --- GENERAL MODE(KARMA) ---
            karma_offset_y = right_offset_y - 15  
            center_x = right_x + (right_w // 2)

            align_surf = sub_font.render(self.karma_alignment, True, color)
            self.screen.blit(align_surf, (center_x - align_surf.get_width() // 2, top_y + 20 + karma_offset_y))

            icon_surf = load_general_icon(self.karma_alignment, "karma_general_nv")
            if icon_surf:
                orig_w, orig_h = icon_surf.get_size()
                scale = min(right_w / orig_w, (available_h * 0.5) / orig_h)
                new_size = (int(orig_w * scale), int(orig_h * scale))

                scaled_img = pygame.transform.smoothscale(icon_surf, new_size)
                colored_img = colorize_surface(scaled_img, color)

                img_x = center_x - (new_size[0] // 2)
                img_y = top_y + 45 + karma_offset_y
                self.screen.blit(colored_img, (img_x, img_y))
                title_y = img_y + new_size[1] + 15
            else:
                title_y = top_y + 120 + karma_offset_y

            title_surf = main_font.render(self.karma_title, True, color)
            self.screen.blit(title_surf, (center_x - title_surf.get_width() // 2, title_y))

        else:
            # --- MODALITÀ REPUTATION ---
            if 0 <= self.selected_rep_index < len(self.reputations):
                selected_rep = self.reputations[self.selected_rep_index]
                center_x = right_x + (right_w // 2)

                icon_surf = load_general_icon(selected_rep["name"], "reputation_general_nv")
                if icon_surf:
                    orig_w, orig_h = icon_surf.get_size()
                    scale = min(right_w / orig_w, (available_h * 0.55) / orig_h)
                    new_size = (int(orig_w * scale), int(orig_h * scale))

                    scaled_img = pygame.transform.smoothscale(icon_surf, new_size)
                    colored_img = colorize_surface(scaled_img, color)

                    img_x = center_x - (new_size[0] // 2)
                    img_y = top_y + 20 + right_offset_y
                    self.screen.blit(colored_img, (img_x, img_y))
                    status_y = img_y + new_size[1] + 15
                else:
                    status_y = top_y + 100 + right_offset_y

                status_surf = main_font.render(selected_rep.get("status", "Neutral"), True, color)
                self.screen.blit(status_surf, (center_x - status_surf.get_width() // 2, status_y))

                faction_surf = main_font.render(selected_rep["name"], True, color)
                self.screen.blit(faction_surf, (center_x - faction_surf.get_width() // 2, status_y + 20))

    def render(self):
        """Render the entire tab UI."""
        if self.is_nv:
            self._render_new_vegas_ui()