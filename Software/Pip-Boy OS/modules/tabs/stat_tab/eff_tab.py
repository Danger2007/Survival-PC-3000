import pygame
import settings

class EffSubtab:
    def __init__(self, screen, draw_space: pygame.Rect):
        self.screen = screen
        self.draw_space = draw_space
        self.font = pygame.font.Font(settings.MAIN_FONT_PATH, 11)
        self.font_large = pygame.font.Font(settings.MAIN_FONT_PATH, 13)

        self.default_effects = [
            ("Boxing Times", "Unarmed +20 (53s)"),
            ("Buffout", "HP +60 (233s), END +3 (233s)"),
            ("Hoarder Penalty", "STR -1, PER -1, LCK -1, INT -1, END -1, CHR -1, AGL -1"),
            ("Legion Praetorian Armor", "Unarmed +10, Melee Weap. +5, AGL +1"),
            ("Merchant Outfit", "Barter +5"),
            ("Sunset Sarsaparilla", "HP +2 (25s)"),
            ("Weapon Binding Ritual", "Unarm. Dam. +10 (233s), HP -2 (1s)")
        ]

    def render(self, player_data: dict, ui_style: str):
        COLOR_NV = settings.PIP_BOY_LIGHT
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()

        effects = player_data.get('effects', self.default_effects)

        if not effects:
            empty_txt = self.font_large.render("NO ACTIVE EFFECTS", True, COLOR_NV)
            self.screen.blit(empty_txt, empty_txt.get_rect(center=(screen_w // 2 + 20, screen_h // 2)))
            return

        # Posizionamento allineato all'interfaccia originale New Vegas
        start_x = 40
        max_w = screen_w - start_x - 10
        curr_y = 37
        name_col_w = 110

        pygame.draw.line(self.screen, COLOR_NV, (start_x, curr_y), (start_x + max_w, curr_y), 1)
        curr_y += 4

        num_effects = len(effects)
        for idx, (name, desc) in enumerate(effects):
            name_txt = self.font.render(name, True, COLOR_NV)
            self.screen.blit(name_txt, (start_x, curr_y))

            desc_x = start_x + name_col_w
            desc_max_w = max_w - name_col_w
            
            words = desc.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if self.font.size(test_line)[0] <= desc_max_w:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            line_y = curr_y
            for line in lines:
                l_surface = self.font.render(line, True, COLOR_NV)
                self.screen.blit(l_surface, (desc_x, line_y))
                line_y += 14

            item_height = max(18, (line_y - curr_y) + 2)
            curr_y += item_height

            if idx < num_effects - 1:
                pygame.draw.line(self.screen, COLOR_NV, (start_x, curr_y), (start_x + max_w, curr_y), 1)
                curr_y += 3