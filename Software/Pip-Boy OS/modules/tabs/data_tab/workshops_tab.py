import os
import pygame
import settings
from ui import ItemGrid


class WorkshopsTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        # Font ridimensionati per matchare l'interfaccia principale del Pip-Boy
        self.font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 9)

        # Dati degli insediamenti (Officine)
        self.workshops = [
            {"name": "Greentop Nursery", "warning": True, "stats": {"People": 3, "Food": 12, "Water": 15, "Power": 3, "Defense": 16, "Beds": 12, "Happiness": 40}},
            {"name": "Hangman's Alley", "warning": False, "stats": {"People": 6, "Food": 6, "Water": 10, "Power": 5, "Defense": 28, "Beds": 6, "Happiness": 65}},
            {"name": "Jamaica Plain", "warning": False, "stats": {"People": 4, "Food": 8, "Water": 8, "Power": 2, "Defense": 12, "Beds": 5, "Happiness": 50}},
            {"name": "Lyon Outpost", "warning": False, "stats": {"People": 2, "Food": 4, "Water": 6, "Power": 0, "Defense": 8, "Beds": 2, "Happiness": 45}},
            {"name": "Murkwater Construction Site", "warning": False, "stats": {"People": 0, "Food": 0, "Water": 0, "Power": 0, "Defense": 0, "Beds": 0, "Happiness": 0}},
            {"name": "Nordhagen Beach", "warning": True, "stats": {"People": 5, "Food": 10, "Water": 10, "Power": 3, "Defense": 10, "Beds": 4, "Happiness": 38}},
            {"name": "Nuka World Overpass", "warning": False, "stats": {"People": 3, "Food": 12, "Water": 15, "Power": 3, "Defense": 16, "Beds": 12, "Happiness": 40}},
            {"name": "Oberland Station", "warning": True, "stats": {"People": 4, "Food": 8, "Water": 6, "Power": 2, "Defense": 14, "Beds": 3, "Happiness": 42}},
            {"name": "Parsons State Insane Asylum", "warning": False, "stats": {"People": 1, "Food": 2, "Water": 5, "Power": 10, "Defense": 50, "Beds": 2, "Happiness": 80}},
            {"name": "Sanctuary", "warning": True, "stats": {"People": 14, "Food": 18, "Water": 40, "Power": 20, "Defense": 65, "Beds": 15, "Happiness": 72}},
        ]

        self.selected_index = 0
        self.scroll_offset = 0

        # --- RIDIMENSIONAMENTO E POSIZIONAMENTO PANNELLI CON MARGINI SIMMETRICI ---
        self.left_panel_width = int(self.draw_space.width * 0.55)
        grid_width = int(self.draw_space.width * 0.32)

        margin = int((self.draw_space.width - self.left_panel_width - grid_width) / 2)

        grid_right = self.draw_space.right - margin
        grid_left = grid_right - grid_width
        grid_top = self.draw_space.top + 8
        grid_height = self.draw_space.height - 16
        self.grid_rect = pygame.Rect(grid_left, grid_top, grid_width, grid_height)

        self.item_grid = ItemGrid(
            draw_space=self.grid_rect,
            font=self.font,
            padding=1
        )

        # Caricamento icone per il pannello destro e avviso
        self.icons = {}
        self.warning_icon = None
        self._load_workshop_icons()
        self._update_grid()

    def _load_workshop_icons(self):
        """Carica le immagini PNG/SVG cercando nelle cartelle del progetto."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        possible_dirs = [
            os.path.join(script_dir, "images", "svgs", "icons_workshops"),
            os.path.join(script_dir, "..", "images", "svgs", "icons_workshops"),
            os.path.join(script_dir, "..", "..", "images", "svgs", "icons_workshops"),
            os.path.join(os.getcwd(), "images", "svgs", "icons_workshops")
        ]

        icons_dir = None
        for d in possible_dirs:
            if os.path.exists(d) and os.path.isdir(d):
                icons_dir = d
                break

        icon_mapping = {
            "People": ["population.png", "population.svg"],
            "Food": ["food.png", "food.svg"],
            "Water": ["water.png", "water.svg"],
            "Power": ["power.png", "power.svg"],
            "Defense": ["defense.png", "defense.svg"],
            "Beds": ["bed.png", "bed.svg"],
            "Happiness": ["happiness.png", "happiness.svg"],
        }

        icon_size = (11, 11)

        # Caricamento icona avviso warning.png
        if icons_dir:
            warn_path = os.path.join(icons_dir, "warning.png")
            if os.path.exists(warn_path):
                self.warning_icon = self._try_load_image(warn_path, (10, 10))
        
        if not self.warning_icon:
            surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.polygon(surf, (255, 255, 255), [(5, 1), (1, 9), (9, 9)])
            self.warning_icon = surf

        # Caricamento icone statistiche
        for stat_name, file_candidates in icon_mapping.items():
            loaded_surf = None
            if icons_dir:
                for filename in file_candidates:
                    filepath = os.path.join(icons_dir, filename)
                    if os.path.exists(filepath):
                        loaded_surf = self._try_load_image(filepath, icon_size)
                        if loaded_surf:
                            break

            if not loaded_surf:
                loaded_surf = self._create_procedural_icon(stat_name, icon_size)

            if loaded_surf:
                self.icons[stat_name] = loaded_surf

    def _try_load_image(self, filepath, size):
        """Caricamento e ridimensionamento immagine con Pygame."""
        try:
            img = pygame.image.load(filepath)
            return pygame.transform.smoothscale(img.convert_alpha(), size)
        except Exception:
            return None

    def _create_procedural_icon(self, stat_name, size):
        """Icona geometrica di emergenza."""
        surf = pygame.Surface(size, pygame.SRCALPHA)
        white = (255, 255, 255)

        if stat_name == "People":
            pygame.draw.circle(surf, white, (5, 3), 2)
            pygame.draw.rect(surf, white, (2, 5, 6, 5), border_radius=1)
        elif stat_name == "Food":
            pygame.draw.rect(surf, white, (2, 2, 2, 7))
            pygame.draw.rect(surf, white, (6, 2, 3, 7))
        elif stat_name == "Water":
            pygame.draw.polygon(surf, white, [(5, 1), (2, 6), (5, 10), (8, 6)])
        elif stat_name == "Power":
            pygame.draw.polygon(surf, white, [(6, 1), (2, 5), (5, 5), (3, 10), (9, 4), (5, 4)])
        elif stat_name == "Defense":
            pygame.draw.polygon(surf, white, [(5, 1), (9, 3), (8, 7), (5, 10), (2, 7), (1, 3)])
        elif stat_name == "Beds":
            pygame.draw.rect(surf, white, (1, 4, 9, 4))
            pygame.draw.rect(surf, white, (2, 2, 3, 2))
            pygame.draw.line(surf, white, (1, 8), (1, 10), 1)
            pygame.draw.line(surf, white, (9, 8), (9, 10), 1)
        elif stat_name == "Happiness":
            pygame.draw.circle(surf, white, (5, 5), 4, width=1)
            pygame.draw.circle(surf, white, (3, 4), 1)
            pygame.draw.circle(surf, white, (7, 4), 1)
            pygame.draw.arc(surf, white, (3, 4, 4, 4), 3.14, 0, 1)
        else:
            pygame.draw.rect(surf, white, (2, 2, 7, 7))

        return surf

    def _get_tinted_icon(self, icon_surf, color):
        """Ricolora l'immagine mantenendo la trasparenza."""
        if not icon_surf:
            return None
        tinted = icon_surf.copy().convert_alpha()
        color_surf = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        color_surf.fill(color)
        tinted.blit(color_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted

    def _update_grid(self):
        """Aggiorna le voci della griglia in base all'insediamento selezionato."""
        if 0 <= self.selected_index < len(self.workshops):
            selected_ws = self.workshops[self.selected_index]
            entries = [{"label": k, "value": v} for k, v in selected_ws["stats"].items()]
            if self.item_grid:
                self.item_grid.update(entries)

    def scroll(self, direction: bool):
        """Scroll tra gli insediamenti (True -> Su, False -> Giù)"""
        prev_index = self.selected_index
        if direction:
            if self.selected_index > 0:
                self.selected_index -= 1
        else:
            if self.selected_index < len(self.workshops) - 1:
                self.selected_index += 1

        if prev_index != self.selected_index:
            self._update_grid()

    def select_item(self):
        return True

    def render(self):
        left_margin = self.draw_space.left
        row_h = self.font.get_linesize() + 6
        max_visible = self.draw_space.height // row_h

        # Gestione dello scroll
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + max_visible:
            self.scroll_offset = self.selected_index - max_visible + 1

        pip_light = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))
        pip_dark = getattr(settings, 'PIP_BOY_DARK', (0, 30, 0))

        # --- PANNELLO SINISTRO (Lista Officine) ---
        left_w = self.left_panel_width
        y = self.draw_space.top + 8

        visible_items = self.workshops[self.scroll_offset:self.scroll_offset + max_visible]
        for idx, item in enumerate(visible_items):
            actual_idx = self.scroll_offset + idx
            item_rect = pygame.Rect(left_margin, y, left_w, row_h - 2)

            if actual_idx == self.selected_index:
                pygame.draw.rect(self.screen, pip_light, item_rect)
                text_color = (0, 0, 0)
            else:
                text_color = pip_light

            # Nome Officina (spostato di 5px verso destra con left_margin + 5)
            name_surf = self.font.render(item["name"], True, text_color)
            name_rect = name_surf.get_rect(midleft=(left_margin + 10, item_rect.centery))
            self.screen.blit(name_surf, name_rect)

            # Icona Avviso PNG (warning.png)
            if item.get("warning", False) and self.warning_icon:
                warn_color = (0, 0, 0) if actual_idx == self.selected_index else pip_light
                tinted_warn = self._get_tinted_icon(self.warning_icon, warn_color)

                if tinted_warn:
                    warn_x = name_rect.right + 6
                    max_allowed_x = item_rect.right - 14

                    if warn_x > max_allowed_x:
                        warn_x = max_allowed_x

                    warn_rect = tinted_warn.get_rect(midleft=(warn_x, item_rect.centery))
                    self.screen.blit(tinted_warn, warn_rect)

            y += row_h

        # --- PANNELLO DESTRO (Statistiche) ---
        if 0 <= self.selected_index < len(self.workshops):
            selected_ws = self.workshops[self.selected_index]
            stats = selected_ws["stats"]
            people_cnt = stats.get("People", 0)

            right_y = self.draw_space.top + 8
            stat_row_h = row_h

            for row_idx, (stat_name, stat_value) in enumerate(stats.items()):
                row_rect = pygame.Rect(self.grid_rect.left, right_y, self.grid_rect.width, stat_row_h - 2)

                # Sfondo rettangolo
                pygame.draw.rect(self.screen, pip_dark, row_rect)

                # Verifica avviso singola statistica
                has_stat_warning = False
                if stat_name in ("Beds", "Food", "Water") and stat_value < people_cnt:
                    has_stat_warning = True
                elif stat_name == "Happiness" and stat_value < 50 and people_cnt > 0:
                    has_stat_warning = True

                # 1. Icona PNG ricolorata
                icon_x = row_rect.left + 4
                label_x = icon_x

                if stat_name in self.icons:
                    icon_img = self.icons[stat_name]
                    tinted_icon = self._get_tinted_icon(icon_img, pip_light)
                    if tinted_icon:
                        icon_rect = tinted_icon.get_rect(midleft=(icon_x, row_rect.centery))
                        self.screen.blit(tinted_icon, icon_rect)
                        label_x = icon_rect.right + 5

                # 2. Etichetta Statistica
                label_surf = self.font.render(stat_name, True, pip_light)
                label_rect = label_surf.get_rect(midleft=(label_x, row_rect.centery))
                self.screen.blit(label_surf, label_rect)

                # 3. Valore Statistica (Allineato a destra)
                val_surf = self.font.render(str(stat_value), True, pip_light)
                val_rect = val_surf.get_rect(midright=(row_rect.right - 16 if has_stat_warning else row_rect.right - 4, row_rect.centery))
                self.screen.blit(val_surf, val_rect)

                # 4. Icona avviso accanto al valore nel pannello di destra
                if has_stat_warning and self.warning_icon:
                    tinted_warn = self._get_tinted_icon(self.warning_icon, pip_light)
                    if tinted_warn:
                        warn_rect = tinted_warn.get_rect(midleft=(val_rect.right + 4, row_rect.centery))
                        self.screen.blit(tinted_warn, warn_rect)

                right_y += stat_row_h