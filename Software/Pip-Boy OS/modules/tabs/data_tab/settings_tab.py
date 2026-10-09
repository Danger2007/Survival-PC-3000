# settings_tab.py
import os
import sys
import pygame
import ast
import subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = current_dir
while root_dir and not os.path.exists(os.path.join(root_dir, 'settings.py')):
    parent = os.path.dirname(root_dir)
    if parent == root_dir:
        break
    root_dir = parent

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from ui import GenericList
import settings
from util_functs import Utils

EDITABLE_SETTINGS = [
    'PLAYER_NAME', 'HP_MAX', 'HP_CURRENT', 'AP_MAX', 'AP_CURRENT', 'LEVEL',
    'RADIATION_VALUE', 'RADIATION_FLUCTUATION',
    'PIP_BOY_LIGHT', 'PIP_BOY_MID', 'PIP_BOY_DARK', 'PIP_BOY_DARKER',
    'SCREEN_WIDTH', 'SCREEN_HEIGHT', 'FPS', 'SOUND_ON', 'SHOW_CRT', 'BLOOM_EFFECT',
    'REAL_MAP', 'FM_RADIO', 'FAKE_LOCATION', 'UI_STYLE', 'SHOW_ALL_MARKERS', 'DATE_MODE'
]

CYCLE_OPTIONS = {
    'UI_STYLE': ['Fallout_4', 'Fallout_NV'],
    'FAKE_LOCATION': ['Commonwealth', 'Mojave'],
    'DATE_MODE': ['Game', 'Real'],
    'RADIATION_FLUCTUATION': ['Fixed', 'Dynamic', 'None']
}

# Definizione Limiti Min/Max per i valori interi
INT_LIMITS = {
    'RADIATION_VALUE': (0, 1000),
    'HP_MAX': (1, 999),
    'HP_CURRENT': (0, 999),
    'AP_MAX': (1, 999),
    'AP_CURRENT': (0, 999),
    'LEVEL': (1, 99),
    'FPS': (15, 144),
    'SCREEN_WIDTH': (320, 3840),
    'SCREEN_HEIGHT': (240, 2160)
}

class SettingsTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.category = "Settings"
        
        self.inv_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 11)
        self.modal_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        
        self.config_path = os.path.join(root_dir, 'user_config.py')
        if not os.path.exists(self.config_path):
            self.config_path = os.path.join(root_dir, 'modules', 'user_config.py')
        
        self.needs_restart = False
        self.show_confirm_modal = False
        self.modal_selection = 0  # 0: YES, 1: NO
        
        # Stato Editor Popup
        self.editing_mode = None  # None, 'INT', 'RGB', 'STRING'
        self.editing_var = None
        self.editing_value = None
        
        # Dati specifici per l'editor
        self.rgb_index = 0  # 0: R, 1: G, 2: B
        self.str_char_index = 0
        self.str_ascii_chars = []
        
        # Gestione Key Repeat (Pressione prolungata dei tasti)
        self.pressed_key = None
        self.key_press_time = 0
        self.last_repeat_time = 0
        self.is_holding = False
        self.hold_delay = 350      # ms prima che inizi l'autorepeat
        self.hold_interval = 45    # ms tra ciascuno scatto continuo

        self._load_settings()
        self._init_list()

    def _load_settings(self):
        self.settings = []
        user_vars = {}

        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if ' = ' in line and not line.startswith('#'):
                    var_name, value = line.split(' = ', 1)
                    var_name = var_name.strip()
                    raw_value = value.split('#')[0].strip()
                    try:
                        parsed_val = ast.literal_eval(raw_value)
                    except (ValueError, SyntaxError):
                        parsed_val = raw_value
                    
                    comment = value.split('#')[1].strip() if '#' in value else ''
                    user_vars[var_name] = (parsed_val, comment)

        for var_name in EDITABLE_SETTINGS:
            if var_name in user_vars:
                val, comment = user_vars[var_name]
            else:
                val = getattr(settings, var_name, None)
                comment = ""

            if val is not None:
                self.settings.append({
                    'var_name': var_name,
                    'display_name': ' '.join(var_name.split('_')).title(),
                    'value': val,
                    'type': type(val),
                    'comment': comment
                })

        self.settings.append({
            'var_name': 'SAVE_CHANGES',
            'display_name': 'Save Changes',
            'value': 'ACTION',
            'type': str,
            'comment': ''
        })

    def _init_list(self):
        self.scroll_offset = 0
        self.visible_count = 9
        self.selected_index = 0
        self._update_list_items()

    def _format_value(self, value):
        if value == 'ACTION':
            return ""
        elif isinstance(value, bool):
            return "[ ON ]" if value else "[ OFF ]"
        elif isinstance(value, (tuple, list)):
            return f"RGB{list(value)}"
        elif isinstance(value, str):
            return f"< {value.replace('_', ' ')} >"
        return str(value)

    def _update_list_items(self):
        all_items = [
            f"{s['display_name']}{(': ' + self._format_value(s['value'])) if s['value'] != 'ACTION' else ''}" 
            for s in self.settings
        ]

        max_text_w = 0
        for item_text in all_items:
            w = self.inv_font.size(item_text)[0]
            if w > max_text_w:
                max_text_w = w

        margin_bottom = 15
        
        ui_style = str(getattr(settings, 'UI_STYLE', 'Fallout_4')).lower()
        is_nv = ('nv' in ui_style or 'vegas' in ui_style)

        left_margin = 25
        left_x = self.draw_space.left + left_margin
        right_margin = 10

        max_available_width = self.draw_space.width - left_margin - right_margin

        if is_nv:
            box_width = min(max_text_w + 20, max_available_width)
        else:
            box_width = max_available_width

        self.list_draw_space = pygame.Rect(
            left_x,
            self.draw_space.top + settings.LIST_TOP_MARGIN,
            box_width,
            self.draw_space.height - settings.LIST_TOP_MARGIN - margin_bottom
        )

        visible_items = all_items[self.scroll_offset : self.scroll_offset + self.visible_count]
        rel_index = self.selected_index - self.scroll_offset

        self.settings_list = GenericList(
            draw_space=self.list_draw_space,
            font=self.inv_font,
            items=visible_items,
            enable_dot=True
        )
        self.settings_list.selected_index = max(0, min(rel_index, len(visible_items) - 1))

    def is_editing(self):
        """Restituisce True se un popup è aperto."""
        return self.editing_mode is not None or self.show_confirm_modal

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return False

        if not self.is_editing():
            if event.key in [pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN, pygame.K_KP_ENTER]:
                return False

        self._dispatch_key(event.key)
        return True
    
    def _dispatch_key(self, key):
        """Esegue l'azione del tasto premuto."""
        if self.is_editing():
            if key in [pygame.K_LEFT, pygame.K_a]:
                return self.handle_horizontal_scroll(is_left=True)
            elif key in [pygame.K_RIGHT, pygame.K_d]:
                return self.handle_horizontal_scroll(is_left=False)
            elif key in [pygame.K_UP, pygame.K_w]:
                return self.handle_vertical_scroll(is_up=True)
            elif key in [pygame.K_DOWN, pygame.K_s]:
                return self.handle_vertical_scroll(is_up=False)
            elif key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_x]:
                if key == pygame.K_x:
                    return self.handle_x_press()
                else:
                    return self.select_item()
            return True

        if key in [pygame.K_UP, pygame.K_w]:
            return self.handle_vertical_scroll(is_up=True)
        elif key in [pygame.K_DOWN, pygame.K_s]:
            return self.handle_vertical_scroll(is_up=False)
        elif key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            return self.select_item()
        elif key == pygame.K_x:
            return self.handle_x_press()

        return False
    
    def _activate_selected_item(self):
        if not self.settings:
            return True
        
        current_setting = self.settings[self.selected_index]
        var_name = current_setting['var_name']
        val = current_setting['value']

        if var_name == 'SAVE_CHANGES':
            if self.needs_restart:
                self.show_confirm_modal = True
                self.modal_selection = 0
            else:
                self._apply_and_save()
            return True

        if isinstance(val, bool):
            current_setting['value'] = not val
            self._check_restart_required(var_name)
            self._update_list_items()

        elif var_name in CYCLE_OPTIONS:
            opts = CYCLE_OPTIONS[var_name]
            next_idx = (opts.index(val) + 1) % len(opts) if val in opts else 0
            current_setting['value'] = opts[next_idx]
            self._check_restart_required(var_name)
            self._update_list_items()

        elif isinstance(val, int):
            self.editing_mode = 'INT'
            self.editing_var = current_setting
            self.editing_value = val

        elif isinstance(val, (tuple, list)) and len(val) == 3:
            self.editing_mode = 'RGB'
            self.editing_var = current_setting
            self.editing_value = list(val)
            self.rgb_index = 0

        elif isinstance(val, str):
            self.editing_mode = 'STRING'
            self.editing_var = current_setting
            self.str_ascii_chars = [ord(c) for c in val] if val else [65]
            self.str_char_index = 0

        return True

    def handle_x_press(self):
        if self.show_confirm_modal:
            return True

        if self.editing_mode is not None:
            self._save_and_close_editor()
            return True

        return self._activate_selected_item()

    def select_item(self):
        if self.show_confirm_modal:
            if self.modal_selection == 0:  # YES
                self._apply_and_save()
                self._restart_pipboy()
            else:  # NO
                self.show_confirm_modal = False
            return True

        if self.editing_mode is not None:
            self._save_and_close_editor()
            return True

        return self._activate_selected_item()

    def _save_and_close_editor(self):
        if self.editing_mode == 'INT':
            self.editing_var['value'] = self.editing_value
        elif self.editing_mode == 'RGB':
            self.editing_var['value'] = tuple(self.editing_value)
        elif self.editing_mode == 'STRING':
            clean_str = "".join([chr(c) for c in self.str_ascii_chars if 32 <= c <= 126]).strip()
            self.editing_var['value'] = clean_str if clean_str else "Player"

        self._check_restart_required(self.editing_var['var_name'])
        self.editing_mode = None
        self.editing_var = None
        self._update_list_items()

    def handle_horizontal_scroll(self, is_left: bool):
        if not self.is_editing():
            return False

        if self.show_confirm_modal:
            self.modal_selection = 1 - self.modal_selection
            return True

        if self.editing_mode == 'RGB':
            delta = -1 if is_left else 1
            self.rgb_index = (self.rgb_index + delta) % 3
            return True

        if self.editing_mode == 'STRING':
            if is_left:
                if self.str_char_index > 0:
                    self.str_char_index -= 1
            else:
                if self.str_char_index < len(self.str_ascii_chars) - 1:
                    self.str_char_index += 1
                elif len(self.str_ascii_chars) < 20:
                    self.str_ascii_chars.append(65)
                    self.str_char_index = len(self.str_ascii_chars) - 1
            return True

        return True

    def handle_vertical_scroll(self, is_up: bool):
        if self.show_confirm_modal:
            self.modal_selection = 1 - self.modal_selection
            return True

        if self.editing_mode == 'INT':
            var_name = self.editing_var['var_name']
            step = 10 if any(k in var_name for k in ['WIDTH', 'HEIGHT', 'RADIATION']) else 1
            min_val, max_val = INT_LIMITS.get(var_name, (0, 9999))

            new_val = self.editing_value + (step if is_up else -step)

            # Wrap-around degli estremi (se va sopra il max torna al min, e viceversa)
            if new_val > max_val:
                new_val = min_val
            elif new_val < min_val:
                new_val = max_val

            self.editing_value = new_val
            return True

        if self.editing_mode == 'RGB':
            delta = 5 if is_up else -5
            curr = self.editing_value[self.rgb_index]
            new_curr = curr + delta

            # Wrap-around da 0 a 255 per ciascun canale RGB
            if new_curr > 255:
                new_curr = 0
            elif new_curr < 0:
                new_curr = 255

            self.editing_value[self.rgb_index] = new_curr
            return True

        if self.editing_mode == 'STRING':
            curr_code = self.str_ascii_chars[self.str_char_index]
            new_code = (curr_code + 1) if is_up else (curr_code - 1)

            # Wrap-around caratteri ASCII stampabili (32 - 126)
            if new_code > 126:
                new_code = 32
            elif new_code < 32:
                new_code = 126

            self.str_ascii_chars[self.str_char_index] = new_code
            return True

        if is_up:
            self.selected_index = max(0, self.selected_index - 1)
        else:
            self.selected_index = min(len(self.settings) - 1, self.selected_index + 1)

        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_count:
            self.scroll_offset = self.selected_index - self.visible_count + 1

        self._update_list_items()
        return True

    def scroll(self, direction: bool):
        self.handle_vertical_scroll(is_up=direction)

    def _check_restart_required(self, var_name):
        if var_name in ['UI_STYLE', 'FAKE_LOCATION', 'REAL_MAP', 'DATE_MODE']:
            self.needs_restart = True

    def _apply_and_save(self):
        for setting in self.settings:
            var_name = setting['var_name']
            if var_name == 'SAVE_CHANGES':
                continue
            val = setting['value']
            setattr(settings, var_name, val)

        self.save_settings()
        self.needs_restart = False
        self._update_list_items()

    def _restart_pipboy(self):
        target = None
        if hasattr(self.tab_instance, 'pipboy'):
            target = self.tab_instance.pipboy
        elif hasattr(self.tab_instance, 'tab_base') and hasattr(self.tab_instance.tab_base, 'pipboy'):
            target = self.tab_instance.tab_base.pipboy

        if target:
            target.should_restart = True
        else:
            python_exe = sys.executable
            main_script = os.path.abspath(sys.argv[0])
            subprocess.Popen([python_exe, main_script], cwd=root_dir)
            os._exit(0)

    def save_settings(self):
        output = ["# User Configuration (Auto-generated)\n", "# Overrides settings.py\n\n"]
        for setting in self.settings:
            var_name = setting['var_name']
            if var_name == 'SAVE_CHANGES':
                continue
            val = setting['value']
            comment = f"  # {setting['comment']}" if setting['comment'] else ""
            output.append(f"{var_name} = {repr(val)}{comment}\n")

        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            f.writelines(output)

    def _render_scrollbar(self):
        if not self.settings:
            return

        color_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
        x = self.draw_space.left + 15
        top_y = self.list_draw_space.top
        bottom_y = self.list_draw_space.bottom - 5

        arrow_w, arrow_h, notch = 2, 4, 1
        pygame.draw.polygon(self.screen, color_light, [(x, top_y), (x + arrow_w, top_y + arrow_h), (x, top_y + arrow_h - notch), (x - arrow_w, top_y + arrow_h)])
        pygame.draw.polygon(self.screen, color_light, [(x, bottom_y), (x + arrow_w, bottom_y - arrow_h), (x, bottom_y - arrow_h + notch), (x - arrow_w, bottom_y - arrow_h)])

        track_top = top_y + arrow_h + 2
        track_bottom = bottom_y - arrow_h - 2
        track_length = track_bottom - track_top

        total = len(self.settings)
        if track_length > 0 and total > self.visible_count:
            bar_length = max(8, int(track_length * (self.visible_count / total)))
            max_scroll = max(1, total - self.visible_count)
            scroll_ratio = min(1.0, max(0.0, self.scroll_offset / max_scroll))
            bar_top = track_top + int(scroll_ratio * (track_length - bar_length))
            pygame.draw.line(self.screen, color_light, (x, bar_top), (x, bar_top + bar_length), 1)

    def _render_editor_modal(self):
        if self.editing_mode is None and not self.show_confirm_modal:
            return

        color_light = getattr(settings, "PIP_BOY_LIGHT", (0, 255, 0))
        color_mid = getattr(settings, "PIP_BOY_MID", (0, 150, 0))

        modal_w, modal_h = 240, 100
        modal_x = self.draw_space.left + (self.draw_space.width - modal_w) // 2
        modal_y = self.draw_space.top + (self.draw_space.height - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        pygame.draw.rect(self.screen, (0, 0, 0), modal_rect)
        pygame.draw.rect(self.screen, color_light, modal_rect, 2)

        if self.show_confirm_modal:
            title_surf = self.modal_font.render("RESTART REQUIRED", True, color_light)
            self.screen.blit(title_surf, (modal_x + (modal_w - title_surf.get_width()) // 2, modal_y + 12))

            msg_surf = self.modal_font.render("Apply changes and restart?", True, color_light)
            self.screen.blit(msg_surf, (modal_x + (modal_w - msg_surf.get_width()) // 2, modal_y + 35))

            yes_col = color_light if self.modal_selection == 0 else color_mid
            no_col = color_light if self.modal_selection == 1 else color_mid

            yes_surf = self.inv_font.render("[ YES ]" if self.modal_selection == 0 else "  YES  ", True, yes_col)
            no_surf = self.inv_font.render("[ NO ]" if self.modal_selection == 1 else "  NO  ", True, no_col)

            self.screen.blit(yes_surf, (modal_x + 40, modal_y + 65))
            self.screen.blit(no_surf, (modal_x + modal_w - 40 - no_surf.get_width(), modal_y + 65))
            return

        title_str = f"EDIT: {self.editing_var['display_name']}"
        title_surf = self.modal_font.render(title_str, True, color_light)
        self.screen.blit(title_surf, (modal_x + (modal_w - title_surf.get_width()) // 2, modal_y + 10))

        center_y = modal_y + 42

        def draw_up_down_arrows(cx, top_y, bottom_y):
            arrow_w = 4
            arrow_h = 5
            notch = 3
            gap = 5

            top_base_y = top_y - gap
            top_tip_y = top_base_y - arrow_h
            pygame.draw.polygon(self.screen, color_light, [
                (cx, top_tip_y),
                (cx + arrow_w, top_base_y),
                (cx, top_base_y - notch),
                (cx - arrow_w, top_base_y)
            ])

            bot_base_y = bottom_y + gap
            bot_tip_y = bot_base_y + arrow_h
            pygame.draw.polygon(self.screen, color_light, [
                (cx, bot_tip_y),
                (cx + arrow_w, bot_base_y),
                (cx, bot_base_y + notch),
                (cx - arrow_w, bot_base_y)
            ])

        if self.editing_mode == 'INT':
            val_surf = self.inv_font.render(str(self.editing_value), True, color_light)
            val_x = modal_x + (modal_w - val_surf.get_width()) // 2
            self.screen.blit(val_surf, (val_x, center_y))

            cx = val_x + val_surf.get_width() // 2
            draw_up_down_arrows(cx, center_y, center_y + val_surf.get_height())

        elif self.editing_mode == 'RGB':
            labels = ["R", "G", "B"]
            spacing = 60
            start_x = modal_x + (modal_w - (spacing * 2)) // 2

            for i in range(3):
                cx = start_x + (i * spacing)
                is_sel = (i == self.rgb_index)
                txt = f"{labels[i]}:{self.editing_value[i]}"
                col = color_light if is_sel else color_mid

                surf = self.modal_font.render(txt, True, col)
                surf_x = cx - surf.get_width() // 2
                self.screen.blit(surf, (surf_x, center_y))

                if is_sel:
                    box_rect = pygame.Rect(surf_x - 3, center_y - 2, surf.get_width() + 6, surf.get_height() + 4)
                    pygame.draw.rect(self.screen, color_light, box_rect, 1)
                    draw_up_down_arrows(cx, box_rect.top, box_rect.bottom)

        elif self.editing_mode == 'STRING':
            chars = [chr(c) for c in self.str_ascii_chars]
            char_surfs = [self.modal_font.render(c, True, color_light) for c in chars]
            
            char_w = 12
            total_w = len(chars) * char_w
            start_x = modal_x + (modal_w - total_w) // 2

            for i, c_surf in enumerate(char_surfs):
                cx = start_x + (i * char_w) + char_w // 2
                cy = center_y
                is_sel = (i == self.str_char_index)

                self.screen.blit(c_surf, (cx - c_surf.get_width() // 2, cy))

                if is_sel:
                    box_rect = pygame.Rect(cx - char_w // 2, cy - 2, char_w, c_surf.get_height() + 4)
                    pygame.draw.rect(self.screen, color_light, box_rect, 1)
                    draw_up_down_arrows(cx, box_rect.top, box_rect.bottom)

        footer_surf = self.modal_font.render("[Enter/X] Save   [<- ->] Select   [^ v] Change", True, color_light)
        self.screen.blit(footer_surf, (modal_x + (modal_w - footer_surf.get_width()) // 2, modal_y + modal_h - 18))

    def render(self):
        self.settings_list.render(self.screen)
        self._render_scrollbar()
        self._render_editor_modal()