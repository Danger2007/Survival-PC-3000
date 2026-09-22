import os
from datetime import datetime
import pygame
import settings
from ui import GenericList


class QuestsTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        self.ui_style = str(getattr(settings, 'UI_STYLE', 'Fallout_4')).lower()
        self.is_nv = any(k in self.ui_style for k in ['nv', 'new_vegas', 'newvegas', 'fnv'])

        # Font (+2px per lo stile Fallout 4)
        self.font_main = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10 if self.is_nv else 11)
        self.font_header = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 11 if self.is_nv else 14)
        self.font_small = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 8 if self.is_nv else 11)

        self.selected_index = 0
        self.selected_step_index = 0
        self.desc_scroll_offset = 0
        self.obj_scroll_offset = 0
        self.quest_scroll_offset = 0
        
        self.focus_on_desc = False
        self.vault_boy_frame = None

        self.quests = [
            {
                "title": "Jewel of the Commonwealth",
                "active": True,
                "completed": False,
                "location": "Diamond City",
                "objectives": [
                    {"text": "Go to Valentine's Detective Agency", "done": False, "current": True},
                    {"text": "Find information about Shaun", "done": True, "current": False},
                    {"text": "Go to Diamond City", "done": True, "current": False}
                ]
            },
            {
                "title": "The First Step",
                "active": False,
                "completed": False,
                "location": "Radiant settlement",
                "objectives": [
                    {"text": "Talk to Preston Garvey", "done": False, "current": False},
                    {"text": "Report your success to settlers", "done": False, "current": False},
                    {"text": "Kill the raiders", "done": False, "current": False},
                    {"text": "Talk to the settlers", "done": False, "current": True}
                ]
            },
            {
                "title": "Call to Arms",
                "active": False,
                "completed": False,
                "location": "ArcJet Systems",
                "objectives": [
                    {"text": "Speak to Paladin Danse", "done": False, "current": False},
                    {"text": "Exit ArcJet Systems", "done": False, "current": False},
                    {"text": "Clear the control room", "done": False, "current": False},
                    {"text": "(Optional) Assess Paladin Danse's condition", "done": False, "current": False},
                    {"text": "(Optional) Activate the engine core's rocket", "done": False, "current": False},
                    {"text": "Locate DRT", "done": False, "current": False},
                    {"text": "Door opened, trigger synth ambush", "done": False, "current": True},
                    {"text": "Found synth evidence", "done": False, "current": False},
                    {"text": "Arrive at ArcJet - Get inside", "done": False, "current": False},
                    {"text": "Follow Paladin Danse", "done": False, "current": False},
                    {"text": "Speak to Paladin Danse", "done": False, "current": True}
                ]
            },
            {
                "title": "Fire Support",
                "active": False,
                "completed": True,
                "location": "Commonwealth",
                "objectives": [
                    {"text": "Speak to Paladin Danse", "done": True, "current": False},
                    {"text": "Proceed to Cambridge Police Station", "done": True, "current": False},
                    {"text": "Listen to Military Frequency AF95", "done": True, "current": False}
                ]
            },
            {
                "title": "Reveille",
                "active": False,
                "completed": True,
                "location": "Fort Hagen",
                "objectives": [
                    {"text": "Proceed to Cambridge Police Station", "done": True, "current": False},
                    {"text": "Investigate the Brotherhood of Steel airship", "done": True, "current": False}
                ]
            },
            {
                "title": "When Freedom Calls",
                "active": False,
                "completed": True,
                "location": "Concord",
                "objectives": [
                    {"text": "Join Preston Garvey in Sanctuary", "done": True, "current": False},
                    {"text": "Report back to Preston", "done": True, "current": False},
                    {"text": "Clear Concord of hostiles", "done": True, "current": False},
                    {"text": "Enter the power armor - Grab the minigun", "done": True, "current": False},
                    {"text": "Get the fusion core - Put the fusion core in the power armor", "done": True, "current": False},
                    {"text": "Unlock the security gate", "done": True, "current": False},
                    {"text": "Talk to Preston Garvey", "done": True, "current": False},
                    {"text": "Kill the Raiders", "done": True, "current": False},
                    {"text": "Locate the trapped settlers", "done": True, "current": False},
                    {"text": "Enter the Museum", "done": True, "current": False},
                    {"text": "Find the Last Minutemen", "done": True, "current": False}
                ]
            },
            {
                "title": "Out of Time",
                "active": False,
                "completed": True,
                "location": "Vault 111",
                "objectives": [
                    {"text": "Investigate Concord", "done": True, "current": False},
                    {"text": "Kill the Insects", "done": True, "current": False},
                    {"text": "Search the Neighborhood with Codsworth", "done": True, "current": False},
                    {"text": "Talk to Codsworth", "done": True, "current": False},
                    {"text": "Go Home", "done": True, "current": False},
                    {"text": "Exit Vault 111", "done": True, "current": False}
                ]
            }

#-------------------------------------------------------------------------
#                          Fallout New Vegas Quests
#-------------------------------------------------------------------------

        ] if not self.is_nv else [
            {
                "title": "Ring-a-Ding-Ding!",
                "active": True,
                "completed": False,
                "location": "Mojave",
                "objectives": [
                    {"text": "Search Benny's suite.", "done": False, "current": False},
                    {"text": "Survive the ambush (or recover the platinum chip).", "done": False, "current": False},
                    {"text": "Go to the presidential suite (or kill Benny).", "done": False, "current": False},
                    {"text": "Confront Benny at The Tops casino.", "done": False, "current": True},
                    {"text": "Search The Strip for the man who shot you.", "done": True, "current": False}
                ]
            },
            {
                "title": "They Went That-A-Way",
                "active": False,
                "completed": True,
                "location": "Mojave",
                "objectives": [
                    {"text": "Intercept the Great Khans at Boulder City.", "done": True, "current": False},
                    {"text": "Find out from Manny Vargas where the Khans were headed.", "done": True, "current": False},
                    {"text": "Head to Novac through Nipton. Ask around Novac about your attackers.", "done": True, "current": False},
                    {"text": "Find Primm's lawman to get information on where your attackers went.", "done": True, "current": False},
                    {"text": "Inquire about your delivery assignment with the administrator of the Mojave Express in Primm.", "done": True, "current": False},
                    {"text": "[Optional] Talk to Victor about your rescue", "done": True, "current": False},
                    {"text": "Find the men who tried to kill you.", "done": True, "current": False},
                ]
            },
            {
                "title": "Ain't That a Kick in the Head",
                "active": False,
                "completed": True,
                "location": "Goodsprings",
                "objectives": [
                    {"text": "Follow Doc Mitchell to the exit.", "done": True, "current": False},
                    {"text": "Sit down on the couch in Doc Mitchell's living room.", "done": True, "current": False},
                    {"text": "Use the Vit-o-matic Vigor Tester.", "done": True, "current": False},
                    {"text": "Walk to the Vit-o-matic Vigor Tester.", "done": True, "current": False}
                ]
            }
        ]

        self._init_layout()
        self._load_vaultboy_frame()

    def _get_visible_objectives(self, quest):
        """Restituisce solo gli obiettivi completati (done) o correnti (current)."""
        return [
            obj for obj in quest.get("objectives", [])
            if obj.get("done", False) or obj.get("current", False)
        ]

    def _load_vaultboy_frame(self):
        """Loads the Vault Boy frame from the boot sequence"""
        target_size = (46, 60)

        if hasattr(self.tab_instance, 'boot_screen') and hasattr(self.tab_instance.boot_screen, 'frames'):
            frames = self.tab_instance.boot_screen.frames
            if len(frames) >= 8:
                self.vault_boy_frame = pygame.transform.smoothscale(frames[7], target_size)
                return

        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_file_dir, "..", "..", ".."))
        target_path = os.path.join(project_root, "images", "boot", "8.png")

        if os.path.exists(target_path):
            try:
                img = pygame.image.load(target_path).convert_alpha()
                self.vault_boy_frame = pygame.transform.smoothscale(img, target_size)
                return
            except Exception as e:
                print(f"[QuestsTab] Quest tab Error: {e}")

        fallback_paths = [
            os.path.join(project_root, "images", "boot", "frame_8.png"),
            os.path.join(current_file_dir, "8.png")
        ]
        for path in fallback_paths:
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.vault_boy_frame = pygame.transform.smoothscale(img, target_size)
                    return
                except Exception:
                    pass

    def _init_layout(self):
        left_margin = 18 if self.is_nv else 10
        left_w = int(self.draw_space.width * 0.44) - (8 if self.is_nv else 0)
        right_w = self.draw_space.width - left_w - left_margin - 20

        self.list_rect = pygame.Rect(
            self.draw_space.left + left_margin,
            self.draw_space.top + settings.LIST_TOP_MARGIN,
            left_w,
            self.draw_space.height - settings.LIST_TOP_MARGIN * 2
        )

        self.details_rect = pygame.Rect(
            self.list_rect.right + 12,
            self.draw_space.top + settings.LIST_TOP_MARGIN,
            right_w,
            self.draw_space.height - settings.LIST_TOP_MARGIN * 2
        )

        items_display = [q['title'] for q in self.quests]

        self.quest_list = GenericList(
            draw_space=self.list_rect,
            font=self.font_main,
            items=items_display,
            enable_dot=False
        )

    def toggle_focus(self):
        self.focus_on_desc = not self.focus_on_desc
        self.selected_step_index = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                self.toggle_focus()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.scroll(True)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll(False)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.select_item()

    def _is_quest_fully_visible(self, target_idx, offset):
        """Verifica se la quest target_idx viene renderizzata interamente con l'offset fornito."""
        y_cursor = self.list_rect.top + (0 if self.is_nv else 8)
        line_height = self.font_main.get_height() + (2 if self.is_nv else 1)
        padding = 4 if self.is_nv else 2
        max_y = self.list_rect.bottom - (5 if self.is_nv else 12)
        
        text_offset_x = 17 if self.is_nv else 0
        max_text_w = self.list_rect.width - text_offset_x - 5 if self.is_nv else self.list_rect.width - 20
        has_drawn_line = False

        for i in range(offset, len(self.quests)):
            q = self.quests[i]
            is_completed = q.get("completed", False)

            if is_completed and not has_drawn_line:
                if self.is_nv:
                    if any(not self.quests[k].get("completed", False) for k in range(i)):
                        y_cursor += 7
                elif i > offset:
                    y_cursor += 7
                has_drawn_line = True

            lines = self._wrap_text(q['title'], self.font_main, max_text_w)
            item_h = (len(lines) * line_height) + (padding * 2)

            if i == target_idx:
                return (y_cursor + item_h) <= max_y

            y_cursor += item_h + (4 if self.is_nv else 2)
            if y_cursor >= max_y:
                return False

        return False

    def _is_step_fully_visible(self, objectives, target_idx, offset):
        """Verifica se lo step target_idx viene renderizzato interamente con l'offset fornito."""
        if self.is_nv:
            y_top = self.draw_space.top + 2
            start_steps_y = y_top + 36
            y_cursor = start_steps_y
            max_bottom = self.details_rect.bottom - 5
            max_text_w = self.details_rect.width - 32 - 12
            font = self.font_main
            line_h = font.get_height() + 2
            
            for i in range(offset, len(objectives)):
                obj = objectives[i]
                lines = self._wrap_text(obj["text"], font, max_text_w)
                step_h = (len(lines) * line_h) + 4
                if i == target_idx:
                    return (y_cursor + step_h) <= max_bottom
                y_cursor += step_h + 4
                if y_cursor >= max_bottom:
                    return False
            return False
        else:
            line_height = self.font_small.get_height() + 1
            padding = 2
            spacing = 3
            max_bottom = self.details_rect.bottom - 12
            
            vb_y = self.details_rect.top
            current_y = vb_y + 75

            for i in range(offset, len(objectives)):
                obj = objectives[i]
                check_str = "✓ " if obj.get("done", False) else ""
                check_w = self.font_small.size(check_str)[0] if check_str else 0
                max_text_w = self.details_rect.width - 20 - check_w
                lines = self._wrap_text(obj["text"], self.font_small, max_text_w)

                step_h = (len(lines) * line_height) + (padding * 2)

                if i == target_idx:
                    return (current_y + step_h) <= max_bottom

                current_y += step_h + spacing
                if current_y >= max_bottom:
                    return False

            return False

    def scroll(self, direction: bool):
        step = -1 if direction else 1

        if self.focus_on_desc:
            if 0 <= self.selected_index < len(self.quests):
                objectives = self._get_visible_objectives(self.quests[self.selected_index])
                if objectives:
                    self.selected_step_index = max(0, min(len(objectives) - 1, self.selected_step_index + step))

                    if self.selected_step_index < self.obj_scroll_offset:
                        self.obj_scroll_offset = self.selected_step_index
                    else:
                        while not self._is_step_fully_visible(objectives, self.selected_step_index, self.obj_scroll_offset):
                            self.obj_scroll_offset += 1
                            if self.obj_scroll_offset >= len(objectives):
                                break
        else:
            self.desc_scroll_offset = 0
            self.obj_scroll_offset = 0
            self.selected_step_index = 0
            self.selected_index = max(0, min(len(self.quests) - 1, self.selected_index + step))

            if self.selected_index < self.quest_scroll_offset:
                self.quest_scroll_offset = self.selected_index
            else:
                while not self._is_quest_fully_visible(self.selected_index, self.quest_scroll_offset):
                    self.quest_scroll_offset += 1
                    if self.quest_scroll_offset >= len(self.quests):
                        break

            if hasattr(self, 'quest_list'):
                self.quest_list.selected_index = self.selected_index
                self.quest_list.update_list()

    def select_item(self):
        if 0 <= self.selected_index < len(self.quests):
            self.quests[self.selected_index]["active"] = not self.quests[self.selected_index]["active"]
            self.quest_list.items[self.selected_index] = self.quests[self.selected_index]['title']
            self.quest_list.update_list()

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

    def _draw_nv_scrollbar(self, x, top_y, bottom_y, total_items, visible_items, current_offset, color):
        arrow_w = 4
        arrow_h = 6
        notch = 2

        up_arrow_pts = [
            (x, top_y),
            (x + arrow_w, top_y + arrow_h),
            (x, top_y + arrow_h - notch),
            (x - arrow_w, top_y + arrow_h)
        ]
        pygame.draw.polygon(self.screen, color, up_arrow_pts)

        down_arrow_pts = [
            (x, bottom_y),
            (x + arrow_w, bottom_y - arrow_h),
            (x, bottom_y - arrow_h + notch),
            (x - arrow_w, bottom_y - arrow_h)
        ]
        pygame.draw.polygon(self.screen, color, down_arrow_pts)

        track_top = top_y + arrow_h + 2
        track_bottom = bottom_y - arrow_h - 2
        track_length = track_bottom - track_top

        if track_length > 0:
            pygame.draw.line(self.screen, color, (x, track_top), (x, track_bottom), 1)

            if total_items > visible_items and total_items > 0:
                bar_length = max(10, int(track_length * (visible_items / total_items)))
                max_scroll = max(1, total_items - visible_items)
                scroll_ratio = min(1.0, max(0.0, current_offset / max_scroll))
                bar_top = track_top + int(scroll_ratio * (track_length - bar_length))
                bar_bottom = bar_top + bar_length
                pygame.draw.line(self.screen, color, (x, bar_top), (x, bar_bottom), 3)
            else:
                pygame.draw.line(self.screen, color, (x, track_top), (x, track_bottom), 3)

    def render(self):
        color_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
        color_middle = getattr(settings, "PIP_BOY_MIDDLE", (0, 191, 0))

        if self.is_nv:
            self._render_nv_list(color_light, color_middle)
            if 0 <= self.selected_index < len(self.quests):
                self._render_nv_details(self.quests[self.selected_index], color_light, color_middle)
        else:
            self._render_fo4_list(color_light, color_middle)
            if 0 <= self.selected_index < len(self.quests):
                self._render_fo4_details(self.quests[self.selected_index], color_light, color_middle)

        self._render_system_datetime(color_light)

    def _render_system_datetime(self, color_light):
        now = datetime.now()
        date_str = now.strftime("%m.%d.%Y")
        time_str = now.strftime("%I:%M %p")

        date_surf = self.font_small.render(date_str, True, color_light)
        time_surf = self.font_small.render(time_str, True, color_light)

        bottom_bar_h = getattr(settings, 'BOTTOM_BAR_HEIGHT', 25)
        footer_top = settings.SCREEN_HEIGHT - bottom_bar_h
        cell_width = settings.SCREEN_WIDTH // 3

        pos_y = footer_top + (bottom_bar_h - date_surf.get_height()) // 2
        
        date_x = 6
        time_x = cell_width + 6

        if self.is_nv:
            pos_y -= 20
        else:
            time_x -= 30

        self.screen.blit(date_surf, (date_x, pos_y))
        self.screen.blit(time_surf, (time_x, pos_y))

    def _draw_fo4_double_arrow(self, x, y, pointing_up, color):
        """Disegna una freccia doppia (chevron doppio) in stile Fallout 4 orientata correttamente."""
        if pointing_up:
            pts1 = [(x, y + 3), (x + 4, y), (x + 8, y + 3)]
            pts2 = [(x, y + 7), (x + 4, y + 4), (x + 8, y + 7)]
        else:
            pts1 = [(x, y), (x + 4, y + 3), (x + 8, y)]
            pts2 = [(x, y + 4), (x + 4, y + 7), (x + 8, y + 4)]

        pygame.draw.lines(self.screen, color, False, pts1, 2)
        pygame.draw.lines(self.screen, color, False, pts2, 2)

    # ==========================================
    # LOGICA FALLOUT 4
    # ==========================================
    def _render_fo4_list(self, color_light, color_middle):
        """Renderizza la lista quest FO4 usando la scroll offset e frecce doppie."""
        y_cursor = self.list_rect.top + 8
        padding = 2
        line_height = self.font_main.get_height() + 1
        max_y = self.list_rect.bottom - 12

        # Freccia Superiore Doppia Quest (Punta verso l'alto)
        if self.quest_scroll_offset > 0:
            arrow_x = self.list_rect.left + 15
            arrow_y = self.list_rect.top - 10
            self._draw_fo4_double_arrow(arrow_x, arrow_y, pointing_up=True, color=color_light)

        text_x = self.list_rect.left + 14
        max_text_w = self.list_rect.width - 20
        has_drawn_line = False

        rendered_count = 0
        visible_slice = list(enumerate(self.quests))[self.quest_scroll_offset:]

        for original_idx, q in visible_slice:
            is_completed = q.get("completed", False)

            if is_completed and not has_drawn_line:
                if rendered_count > 0:
                    y_cursor += 2
                    pygame.draw.line(self.screen, color_light, (self.list_rect.left, y_cursor), (self.list_rect.right - 5, y_cursor), 1)
                    y_cursor += 5
                has_drawn_line = True

            lines = self._wrap_text(q['title'], self.font_main, max_text_w)
            item_h = (len(lines) * line_height) + (padding * 2)

            if y_cursor + item_h > max_y:
                break

            is_selected = (original_idx == self.selected_index and not self.focus_on_desc)

            # Il rettangolo di selezione parte da x=0 e copre l'ampiezza fino al bordo destro della lista
            item_rect = pygame.Rect(0, y_cursor, self.list_rect.left + self.list_rect.width, item_h)

            if is_selected:
                pygame.draw.rect(self.screen, color_light, item_rect)
                text_col = (0, 0, 0)
            else:
                text_col = color_middle if is_completed else color_light

            if q.get("active", False) and not is_completed:
                sq_size = 7
                sq_x = self.list_rect.left + 2
                sq_y = item_rect.top + padding + ((line_height - sq_size) // 2)
                pygame.draw.rect(self.screen, text_col, (sq_x, sq_y, sq_size, sq_size))

            line_y = item_rect.top + padding
            for line in lines:
                txt_surf = self.font_main.render(line, True, text_col)
                self.screen.blit(txt_surf, (text_x, line_y))
                line_y += line_height

            y_cursor += item_h + 2
            rendered_count += 1

        # Freccia Inferiore Doppia Quest (Punta verso il basso)
        if self.quest_scroll_offset + rendered_count < len(self.quests):
            arrow_x = self.list_rect.left + 15
            arrow_y = self.list_rect.bottom - 4
            self._draw_fo4_double_arrow(arrow_x, arrow_y, pointing_up=False, color=color_light)

    def _render_fo4_details(self, quest, color_light, color_middle):
        """Renderizza Vault Boy e gli obiettivi FO4 con frecce doppie allineate a sinistra."""
        vb_center_x = self.details_rect.left + (self.details_rect.width // 2) - 10
        vb_y = self.details_rect.top

        if self.vault_boy_frame:
            tinted_vb = self.vault_boy_frame.copy()
            tinted_vb.fill(color_light, special_flags=pygame.BLEND_RGBA_MULT)
            vb_rect = tinted_vb.get_rect(center=(vb_center_x, vb_y + 28))
            self.screen.blit(tinted_vb, vb_rect)

        start_y = vb_y + 75
        line_height = self.font_small.get_height() + 1
        padding = 2
        spacing = 3
        max_bottom = self.details_rect.bottom - 12

        objectives = self._get_visible_objectives(quest)

        # Posiziona la freccia a sinistra
        arrow_x = self.details_rect.left + 2

        # Freccia Superiore Objectives (Punta verso l'alto)
        if self.obj_scroll_offset > 0:
            arrow_y = start_y - 12
            self._draw_fo4_double_arrow(arrow_x, arrow_y, pointing_up=True, color=color_light)

        y_cursor = start_y
        rendered_count = 0

        for i in range(self.obj_scroll_offset, len(objectives)):
            obj = objectives[i]
            actual_idx = i
            is_current = obj.get("current", False)
            is_step_selected = self.focus_on_desc and (actual_idx == self.selected_step_index)

            check_str = "✓ " if obj.get("done", False) else ""
            check_w = self.font_small.size(check_str)[0] if check_str else 0

            max_text_w = self.details_rect.width - 20 - check_w
            lines = self._wrap_text(obj["text"], self.font_small, max_text_w)

            step_h = (len(lines) * line_height) + (padding * 2)

            if y_cursor + step_h > max_bottom:
                break

            row_rect = pygame.Rect(self.details_rect.left, y_cursor, self.details_rect.width - 15, step_h)

            if is_current and not is_step_selected:
                bg_surf = pygame.Surface((row_rect.width, row_rect.height))
                bg_surf.fill(color_middle)
                self.screen.blit(bg_surf, row_rect.topleft)
                text_col = (0, 0, 0)
            elif is_step_selected:
                pygame.draw.rect(self.screen, color_light, row_rect)
                text_col = (0, 0, 0)
            else:
                bg_surf = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
                bg_surf.fill((10, 25, 10, 190))
                self.screen.blit(bg_surf, row_rect.topleft)
                text_col = color_light

            text_x_offset = row_rect.left + 6
            if check_str:
                check_surf = self.font_small.render(check_str, True, text_col)
                self.screen.blit(check_surf, (text_x_offset, row_rect.top + padding))
                text_x_offset += check_w

            line_y = row_rect.top + padding
            for line in lines:
                txt_surf = self.font_small.render(line, True, text_col)
                self.screen.blit(txt_surf, (text_x_offset, line_y))
                line_y += line_height

            y_cursor += step_h + spacing
            rendered_count += 1

        # Freccia Inferiore Objectives (Punta verso il basso)
        if self.obj_scroll_offset + rendered_count < len(objectives):
            arrow_y = max_bottom + 2
            self._draw_fo4_double_arrow(arrow_x, arrow_y, pointing_up=False, color=color_light)

    # ==========================================
    # LOGICA NEW VEGAS
    # ==========================================
    def _render_nv_list(self, color_light, color_middle):
        left_scrollbar_x = self.draw_space.left + 6
        top_y = self.list_rect.top
        bottom_y = self.list_rect.bottom - 5

        y_cursor = self.list_rect.top
        text_offset_x = 17
        max_width = self.list_rect.width - text_offset_x - 5
        line_height = self.font_main.get_height() + 2
        padding = 4

        visible_indices = list(range(self.quest_scroll_offset, len(self.quests)))
        has_drawn_line = False
        rendered_count = 0

        for original_idx in visible_indices:
            q = self.quests[original_idx]
            is_completed = q.get("completed", False)

            if is_completed and not has_drawn_line:
                any_active_before = any(not self.quests[i].get("completed", False) for i in range(original_idx))
                if any_active_before:
                    y_cursor += 2
                    pygame.draw.line(self.screen, color_middle, (self.list_rect.left + 5, y_cursor), (self.list_rect.right - 5, y_cursor), 1)
                    y_cursor += 5
                has_drawn_line = True

            lines = self._wrap_text(q["title"], self.font_main, max_width)
            item_h = (len(lines) * line_height) + (padding * 2)

            if y_cursor + item_h > self.list_rect.bottom:
                break

            item_rect = pygame.Rect(self.list_rect.left, y_cursor, self.list_rect.width, item_h)
            item_text_color = color_middle if is_completed else color_light

            if original_idx == self.selected_index:
                box_color = color_light if not self.focus_on_desc else color_middle
                pygame.draw.rect(self.screen, box_color, item_rect, 1)

            if q.get("active", False) and not is_completed:
                sq_size = 5
                sq_x = item_rect.left + 6
                sq_y = y_cursor + padding + (line_height // 2) - (sq_size // 2)
                pygame.draw.rect(self.screen, color_light, (sq_x, sq_y, sq_size, sq_size))

            text_x = item_rect.left + text_offset_x
            text_y = y_cursor + padding
            for l in lines:
                txt_surf = self.font_main.render(l, True, item_text_color)
                self.screen.blit(txt_surf, (text_x, text_y))
                text_y += line_height

            y_cursor += item_h + 4
            rendered_count += 1

        self._draw_nv_scrollbar(
            x=left_scrollbar_x,
            top_y=top_y,
            bottom_y=bottom_y,
            total_items=len(self.quests),
            visible_items=max(1, rendered_count),
            current_offset=self.quest_scroll_offset,
            color=color_light
        )

    def _render_nv_details(self, quest, color_light, color_middle):
        objectives = self._get_visible_objectives(quest)

        y_top = self.draw_space.top + 2
        y_actions = y_top + 1
        act1 = self.font_main.render("Show Active Quest Notes X", True, color_light)
        act2 = self.font_main.render("Challenges Y", True, color_light)
        
        right_x = self.draw_space.right - 20
        self.screen.blit(act1, (right_x - act1.get_width(), y_actions))
        self.screen.blit(act2, (right_x - act2.get_width(), y_actions + 15))

        start_steps_y = y_actions + 35

        right_scrollbar_x = self.details_rect.right - 8
        top_y = start_steps_y
        bottom_y = self.details_rect.bottom - 5

        y_cursor = start_steps_y
        max_text_w = self.details_rect.width - 32

        visible_objectives = objectives[self.obj_scroll_offset:]
        rendered_count = 0

        for idx, obj in enumerate(visible_objectives):
            actual_idx = self.obj_scroll_offset + idx
            is_done = obj.get("done", False)

            step_color = color_middle if is_done else color_light

            box_size = 6
            box_margin_right = 6

            lines = self._wrap_text(obj["text"], self.font_main, max_text_w - (box_size + box_margin_right))
            line_h = self.font_main.get_height() + 2
            step_h = (len(lines) * line_h) + 4

            if y_cursor + step_h > self.details_rect.bottom:
                break

            step_rect = pygame.Rect(self.details_rect.left, y_cursor, self.details_rect.width - 15, step_h)

            is_step_selected = self.focus_on_desc and (actual_idx == self.selected_step_index)
            if is_step_selected:
                pygame.draw.rect(self.screen, color_light, step_rect, 1)

            box_x = step_rect.left + 4
            box_y = y_cursor + 4
            box_rect = pygame.Rect(box_x, box_y, box_size, box_size)

            if is_done:
                pygame.draw.rect(self.screen, color_middle, box_rect)
            else:
                pygame.draw.rect(self.screen, color_light, box_rect, 1)

            text_x = box_x + box_size + box_margin_right
            text_y = y_cursor + 2
            for line in lines:
                txt_surf = self.font_main.render(line, True, step_color)
                self.screen.blit(txt_surf, (text_x, text_y))
                text_y += line_h

            y_cursor += step_h + 4
            rendered_count += 1

        self._draw_nv_scrollbar(
            x=right_scrollbar_x,
            top_y=top_y,
            bottom_y=bottom_y,
            total_items=len(objectives),
            visible_items=max(1, rendered_count),
            current_offset=self.obj_scroll_offset,
            color=color_light
        )

        if self.focus_on_desc:
            outline_rect = pygame.Rect(
                self.details_rect.left - 4,
                start_steps_y - 4,
                self.details_rect.width + 2,
                (self.details_rect.bottom - start_steps_y) + 4
            )
            pygame.draw.rect(self.screen, color_middle, outline_rect, 1)