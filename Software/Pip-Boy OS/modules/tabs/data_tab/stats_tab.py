import pygame
import settings


class StatsTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        self.font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 14)
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 12)

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

    def scroll(self, direction: bool):
        """Scroll tra le categorie di statistiche"""
        if direction:  # Giù
            if self.selected_category < len(self.categories) - 1:
                self.selected_category += 1
        else:  # Su
            if self.selected_category > 0:
                self.selected_category -= 1

    def select_item(self):
        return True

    def render(self):
        left_margin = self.draw_space.left - 10
        item_h = 24

        # --- PANNELLO SINISTRO (Categorie Statistiche) ---
        left_w = int(self.draw_space.width * 0.40)
        y = self.draw_space.top

        for idx, cat in enumerate(self.categories):
            item_rect = pygame.Rect(left_margin, y, left_w, item_h)

            if idx == self.selected_category:
                pygame.draw.rect(self.screen, settings.PIP_BOY_LIGHT, item_rect)
                text_color = settings.BACKGROUND
            else:
                text_color = settings.PIP_BOY_LIGHT

            cat_surf = self.font.render(cat["name"], True, text_color)
            self.screen.blit(cat_surf, (left_margin + 8, y + 3))

            y += item_h + 2

        # --- PANNELLO DESTRO (Dettaglio Statistiche) ---
        selected_cat = self.categories[self.selected_category]
        right_x = left_margin + left_w + 20
        right_y = self.draw_space.top

        for stat_name, stat_val in selected_cat["stats"]:
            lbl_surf = self.font.render(stat_name, True, settings.PIP_BOY_LIGHT)
            val_surf = self.font.render(str(stat_val), True, settings.PIP_BOY_LIGHT)

            self.screen.blit(lbl_surf, (right_x, right_y))

            # Allineamento valore a destra
            val_x = self.draw_space.right + 10 - val_surf.get_width()
            self.screen.blit(val_surf, (val_x, right_y))

            right_y += 20

        # Freccetta di indicazione scorrimento in basso a destra
        if len(selected_cat["stats"]) > 8:
            arrow_surf = self.font_small.render("v", True, settings.PIP_BOY_LIGHT)
            self.screen.blit(arrow_surf, (self.draw_space.right, self.draw_space.bottom - 15))