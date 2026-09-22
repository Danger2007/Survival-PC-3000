import pygame
import settings


class NotesTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        self.font_main = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.font_header = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 11)

        self.selected_index = 0
        self.desc_scroll_offset = 0
        self.focus_on_desc = False

        self.notes = [
            {
                "title": "Mojave Express Delivery Order (6 of 6)",
                "active": True,
                "instructions": "Deliver the package at the north entrance to the Vegas Strip. Receiver is Benjamin Maney."
            },
            {
                "title": "Doc Mitchell's Supplies",
                "active": False,
                "instructions": "Recover medicine and equipment before heading out to the wasteland."
            }
        ]

        self._init_layout()

    def _init_layout(self):
        left_w = int(self.draw_space.width * 0.44)
        right_w = self.draw_space.width - left_w - 20

        self.list_rect = pygame.Rect(
            self.draw_space.left + 10,
            self.draw_space.top + settings.LIST_TOP_MARGIN,
            left_w,
            self.draw_space.height - settings.LIST_TOP_MARGIN * 2
        )

        self.details_rect = pygame.Rect(
            self.list_rect.right + 10,
            self.draw_space.top + settings.LIST_TOP_MARGIN,
            right_w,
            self.draw_space.height - settings.LIST_TOP_MARGIN * 2
        )

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                self.focus_on_desc = not self.focus_on_desc
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.scroll(True)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll(False)

    def scroll(self, direction: bool):
        step = -1 if direction else 1

        if self.focus_on_desc:
            if 0 <= self.selected_index < len(self.notes):
                lines = self._wrap_text(self.notes[self.selected_index]["instructions"], self.font_main, self.details_rect.width - 25)
                max_scroll = max(0, len(lines) - 8)
                self.desc_scroll_offset = max(0, min(max_scroll, self.desc_scroll_offset + step))
        else:
            self.desc_scroll_offset = 0
            self.selected_index = max(0, min(len(self.notes) - 1, self.selected_index + step))

    def _wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            if font.size(test_line)[0] <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line.strip())
                line = word + " "
        if line:
            lines.append(line.strip())
        return lines

    def render(self):
        color_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
        color_middle = getattr(settings, "PIP_BOY_MIDDLE", (0, 191, 0))

        self._render_nv_list(color_light, color_middle)
        if 0 <= self.selected_index < len(self.notes):
            self._render_nv_details(self.notes[self.selected_index], color_light, color_middle)

    def _render_nv_list(self, color_light, color_middle):
        y_cursor = self.list_rect.top
        text_offset_x = 17
        max_width = self.list_rect.width - text_offset_x - 5
        line_height = self.font_main.get_height() + 2
        padding = 4

        for i, note in enumerate(self.notes):
            lines = self._wrap_text(note["title"], self.font_main, max_width)
            item_h = (len(lines) * line_height) + (padding * 2)

            if y_cursor + item_h > self.list_rect.bottom:
                break

            item_rect = pygame.Rect(self.list_rect.left, y_cursor, self.list_rect.width, item_h)

            if i == self.selected_index:
                border_color = color_light if not self.focus_on_desc else color_middle
                pygame.draw.rect(self.screen, border_color, item_rect, 1)

            if note.get("active", False):
                pygame.draw.rect(self.screen, color_light, (item_rect.left + 7, y_cursor + padding + 4, 5, 5))

            text_y = y_cursor + padding
            for l in lines:
                txt_surf = self.font_main.render(l, True, color_light)
                self.screen.blit(txt_surf, (item_rect.left + text_offset_x, text_y))
                text_y += line_height

            y_cursor += item_h + 4

    def _render_nv_details(self, note, color_light, color_middle):
        y_top = self.draw_space.top + 2
        right_x = self.draw_space.right - 20

        act1 = self.font_main.render("Show Active Quest Notes X", True, color_light)
        self.screen.blit(act1, (right_x - act1.get_width(), y_top + 1))

        y_instr = y_top + 35
        title_surf = self.font_header.render("INSTRUCTIONS", True, color_light)
        self.screen.blit(title_surf, (self.details_rect.left, y_instr))

        lines = self._wrap_text(note["instructions"], self.font_main, self.details_rect.width - 25)
        line_height = self.font_main.get_height() + 3
        visible_lines = lines[self.desc_scroll_offset : self.desc_scroll_offset + 8]

        current_y = y_instr + 22
        for l in visible_lines:
            surf = self.font_main.render(l, True, color_light)
            self.screen.blit(surf, (self.details_rect.left, current_y))
            current_y += line_height

        if self.focus_on_desc:
            desc_box = pygame.Rect(self.details_rect.left - 4, y_instr - 4, self.details_rect.width - 15, (self.details_rect.bottom - y_instr) + 2)
            pygame.draw.rect(self.screen, color_light, desc_box, 1)