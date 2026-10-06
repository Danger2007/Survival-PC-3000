import pygame
import settings


class WorkshopsTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        self.font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 14)
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 12)

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

    def scroll(self, direction: bool):
        """Scroll verso l'alto (False) o verso il basso (True)"""
        if direction:  # Giù
            if self.selected_index < len(self.workshops) - 1:
                self.selected_index += 1
        else:  # Su
            if self.selected_index > 0:
                self.selected_index -= 1

    def select_item(self):
        return True

    def render(self):
        left_margin = self.draw_space.left - 10
        item_h = 22
        max_visible = self.draw_space.height // item_h

        # Gestione scroll offset visibile
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + max_visible:
            self.scroll_offset = self.selected_index - max_visible + 1

        # --- PANNELLO SINISTRO (Lista Officine) ---
        left_w = int(self.draw_space.width * 0.52)
        y = self.draw_space.top

        visible_items = self.workshops[self.scroll_offset:self.scroll_offset + max_visible]
        for idx, item in enumerate(visible_items):
            actual_idx = self.scroll_offset + idx
            item_rect = pygame.Rect(left_margin, y, left_w, item_h)

            if actual_idx == self.selected_index:
                pygame.draw.rect(self.screen, settings.PIP_BOY_LIGHT, item_rect)
                text_color = settings.BACKGROUND
            else:
                text_color = settings.PIP_BOY_LIGHT

            # Nome Officina
            name_surf = self.font.render(item["name"], True, text_color)
            self.screen.blit(name_surf, (left_margin + 8, y + 2))

            # Icona Avviso (Triangolo ▲)
            if item.get("warning", False):
                warn_surf = self.font_small.render("▲", True, text_color)
                self.screen.blit(warn_surf, (left_margin + left_w - 18, y + 3))

            y += item_h

        # --- PANNELLO DESTRO (Statistiche Insediamento Selezionato) ---
        selected_ws = self.workshops[self.selected_index]
        right_x = left_margin + left_w + 25
        right_y = self.draw_space.top + 10

        stats = selected_ws["stats"]
        for key, val in stats.items():
            label_surf = self.font.render(key, True, settings.PIP_BOY_LIGHT)
            val_surf = self.font.render(str(val), True, settings.PIP_BOY_LIGHT)

            self.screen.blit(label_surf, (right_x, right_y))
            val_x = right_x + 130 - val_surf.get_width()
            self.screen.blit(val_surf, (val_x, right_y))

            right_y += 24