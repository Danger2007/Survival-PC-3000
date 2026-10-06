import pygame
import settings
from ui import ItemGrid


class StatTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        # Font ridimensionati per matchare l'interfaccia principale del Pip-Boy
        self.font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 9)

        # Categorie e relative statistiche
        self.categories = [
            {
                "name": "General",
                "stats": [
                    ("Locations Discovered", 322),
                    ("Locations Cleared", 191),
                    ("Days Passed", 383),
                    ("Hours Slept", 798),
                    ("Hours Waiting", 1313),
                    ("Caps Found", 309358),
                    ("Most Caps Carried", 224581),
                    ("Junk Collected", 15572),
                    ("Chests Looted", 1361),
                    ("Magazines Found", 69),
                ]
            },
            {
                "name": "Quest",
                "stats": [
                    ("Quests Completed", 45),
                    ("Misc Objectives Completed", 128),
                    ("Main Quests Completed", 12),
                    ("Side Quests Completed", 33),
                ]
            },
            {
                "name": "Combat",
                "stats": [
                    ("People Killed", 542),
                    ("Creatures Killed", 890),
                    ("Robots Destroyed", 120),
                    ("Synths Destroyed", 215),
                    ("Critical Hits", 310),
                    ("Sneak Attacks", 142),
                ]
            },
            {
                "name": "Crafting",
                "stats": [
                    ("Weapons Improved", 84),
                    ("Armor Improved", 112),
                    ("Chems Crafted", 65),
                    ("Food Cooked", 140),
                    ("Objects Built", 512),
                ]
            },
            {
                "name": "Crime",
                "stats": [
                    ("Locks Picked", 156),
                    ("Pockets Picked", 24),
                    ("Items Stolen", 310),
                    ("Trespasses", 15),
                ]
            }
        ]

        self.selected_category = 0

        # --- CALCOLO DIVISIONE E PADDING ORIZZONTALE ---
        left_w = int((self.draw_space.width + 15) / 2)  # Spazio tra elenchi invariato
        
        # Aggiungiamo 5px a sinistra e togliamo 10px totali dalla larghezza (5px a sx + 5px a dx)
        padding_x = 5
        grid_left = self.draw_space.left + left_w + padding_x
        grid_top = self.draw_space.top + 8
        grid_width = (self.draw_space.right - padding_x) - grid_left
        grid_height = self.draw_space.height - 16
        
        grid_rect = pygame.Rect(grid_left, grid_top, grid_width, grid_height)

        self.item_grid = ItemGrid(
            draw_space=grid_rect,
            font=self.font,
            padding=1  # Lasciamo il padding verticale di ItemGrid inalterato
        )
        self._update_grid()

    def _update_grid(self):
        """Aggiorna le voci della griglia in base alla categoria selezionata."""
        if 0 <= self.selected_category < len(self.categories):
            selected_cat = self.categories[self.selected_category]
            entries = [{"label": k, "value": v} for k, v in selected_cat["stats"]]
            if self.item_grid:
                self.item_grid.update(entries)

    def scroll(self, direction: bool):
        """Scroll tra le categorie di statistiche (Invertito: True -> Su, False -> Giù)"""
        prev_index = self.selected_category
        if direction:  # Su
            if self.selected_category > 0:
                self.selected_category -= 1
        else:  # Giù
            if self.selected_category < len(self.categories) - 1:
                self.selected_category += 1

        if prev_index != self.selected_category:
            self._update_grid()

    def select_item(self):
        return True

    def render(self):
        left_margin = self.draw_space.left
        row_h = self.font.get_linesize() + 6

        # --- PANNELLO SINISTRO ---
        left_w = int((self.draw_space.width + 15) / 2)
        y = self.draw_space.top + 8

        pip_light = getattr(settings, 'PIP_BOY_LIGHT', (0, 255, 0))

        for idx, cat in enumerate(self.categories):
            item_rect = pygame.Rect(left_margin, y, left_w, row_h - 2)

            if idx == self.selected_category:
                pygame.draw.rect(self.screen, pip_light, item_rect)
                text_color = (0, 0, 0)
            else:
                text_color = pip_light

            # Scritta elenco sinistro (spostata di 5px verso destra dal margine base 6px -> 11px)
            cat_surf = self.font.render(cat["name"], True, text_color)
            cat_rect = cat_surf.get_rect(midleft=(left_margin + 11, item_rect.centery))
            self.screen.blit(cat_surf, cat_rect)

            y += row_h

        # --- PANNELLO DESTRO (Griglia Statistiche) ---
        if self.item_grid:
            self.item_grid.render(self.screen)


# Alias per garantire retrocompatibilità con TabManager
StatsTab = StatTab