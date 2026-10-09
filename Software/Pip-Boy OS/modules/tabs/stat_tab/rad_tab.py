import pygame
import random
import math
import settings

class RadSubtab:
    def __init__(self, screen, draw_space: pygame.Rect):
        self.screen = screen
        self.draw_space = draw_space
        
        self.font = pygame.font.Font(settings.MAIN_FONT_PATH, 11)
        self.font_large = pygame.font.Font(settings.MAIN_FONT_PATH, 13)
        self.font_title = pygame.font.Font(settings.MAIN_FONT_PATH, 14)

    def render(self, player_data: dict, ui_style: str):
        if str(ui_style).lower() in ('fallout_nv', 'fallout_new_vegas'):
            self._render_nv(player_data)
        else:
            self._render_fo4(player_data)

    def _get_danger_color(self, base_color):
        """Calcola il colore per la parte di arco tra 800 e 1000 RAD."""
        r, g, b = base_color[:3]
        is_white_or_gray = (max(r, g, b) - min(r, g, b) < 30) and (max(r, g, b) > 170)
        
        # Se il Pip-Boy è verde o bianco/grigio -> Rosso
        if is_white_or_gray or (g > r + 30 and g > b + 30):
            return (255, 30, 30)
        
        # Colore complementare per gli altri colori
        comp_r, comp_g, comp_b = 255 - r, 255 - g, 255 - b
        if (comp_r + comp_g + comp_b) < 120:
            return (255, 30, 30)
        return (comp_r, comp_g, comp_b)

    def _draw_smooth_arc(self, surf, color, center, radius, start_deg, end_deg, width=2):
        """Disegna una fascia ad arco perfettamente liscia e priva di scalini di pixel."""
        cx, cy = center
        steps = max(10, int(abs(end_deg - start_deg) * 4))
        
        points_outer = []
        points_inner = []
        r_out = radius
        r_in = radius - width
        
        for i in range(steps + 1):
            deg = start_deg + (end_deg - start_deg) * (i / steps)
            rad = math.radians(deg)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            
            x_out = cx + r_out * cos_a
            y_out = cy - r_out * sin_a
            x_in = cx + r_in * cos_a
            y_in = cy - r_in * sin_a
            
            points_outer.append((x_out, y_out))
            points_inner.append((x_in, y_in))
            
        poly_pts = points_outer + points_inner[::-1]
        pygame.draw.polygon(surf, color, poly_pts)

    def _get_rad_values(self, player_data: dict):
        base_rads = player_data.get('rads', getattr(settings, 'RADIATION_VALUE', 312))
        fluctuation_mode = str(getattr(settings, 'RADIATION_FLUCTUATION', 'Fixed')).lower()

        JITTER_AMPLITUDE = 8.0
        JITTER_INTERVAL_MS = 50
        MAX_RAD_CHANGE_PER_SEC = 25.0
        TARGET_CHANGE_INTERVAL_MS = 2500

        current_ticks = pygame.time.get_ticks()

        # 1. MODALITÀ 'NONE': Valore fisso
        if fluctuation_mode == 'none':
            if '_rad_state' in player_data:
                del player_data['_rad_state']
            return float(base_rads), float(base_rads)

        # 2. MODALITÀ 'FIXED' / 'STATIC': Media fissa + jitter
        elif fluctuation_mode in ['fixed', 'static']:
            current_mean = float(base_rads)
            if '_rad_state' in player_data:
                del player_data['_rad_state']

        # 3. MODALITÀ 'DYNAMIC': Fluttuazione dinamica + jitter
        else:
            if '_rad_state' not in player_data:
                player_data['_rad_state'] = {
                    'current_mean': float(base_rads),
                    'target_mean': random.uniform(0.0, 1000.0),
                    'last_ticks': current_ticks,
                    'last_target_change': current_ticks
                }

            st = player_data['_rad_state']
            dt = (current_ticks - st['last_ticks']) / 1000.0
            st['last_ticks'] = current_ticks

            if current_ticks - st['last_target_change'] > TARGET_CHANGE_INTERVAL_MS:
                st['target_mean'] = random.uniform(0.0, 1000.0)
                st['last_target_change'] = current_ticks

            diff = st['target_mean'] - st['current_mean']
            if abs(diff) > 0.01:
                max_step = MAX_RAD_CHANGE_PER_SEC * dt
                step = max(-max_step, min(max_step, diff))
                st['current_mean'] += step

            current_mean = st['current_mean']

        # MICRO-JITTER
        jitter_seed = current_ticks // JITTER_INTERVAL_MS
        jitter_rng = random.Random(jitter_seed)
        micro_jitter = jitter_rng.uniform(-JITTER_AMPLITUDE, JITTER_AMPLITUDE)

        display_rads = max(0.0, min(1000.0, current_mean + micro_jitter))
        return display_rads, current_mean

    def _render_nv(self, player_data: dict):
        COLOR_NV = settings.PIP_BOY_LIGHT
        screen_w = self.screen.get_width()

        rad_resist = player_data.get('rad_resist', getattr(settings, 'RAD_RESIST', 6))
        display_rads, current_mean = self._get_rad_values(player_data)
        display_rads_int = int(round(display_rads))

        # 1. RADAWAY / RAD-X
        quick_rad_items = player_data.get('quick_rad_items', ["(1) RadAway A)", "(3) Rad-X X)"])
        item_y = 45
        for item_str in quick_rad_items:
            item_txt = self.font.render(item_str, True, COLOR_NV)
            item_rect = item_txt.get_rect(right=screen_w - 15, top=item_y)
            self.screen.blit(item_txt, item_rect)
            item_y += 25

        center_x = 115
        right_x = screen_w - 10
        eff_top_y = 120
        eff_bottom_y = 170

        # 2. RIQUADRO SUPERIORE "EFF"
        if current_mean >= 800: rad_eff_str = "-3 END, -2 AGL, -2 STR"
        elif current_mean >= 600: rad_eff_str = "-2 END, -2 AGL"
        elif current_mean >= 400: rad_eff_str = "-2 END, -1 AGL"
        elif current_mean >= 200: rad_eff_str = "-1 END"
        else: rad_eff_str = "NONE"

        pygame.draw.line(self.screen, COLOR_NV, (center_x, eff_top_y), (right_x, eff_top_y), 1)
        pygame.draw.line(self.screen, COLOR_NV, (right_x, eff_top_y), (right_x, eff_bottom_y - 17), 1)

        eff_label = self.font_large.render("EFF", True, COLOR_NV)
        eff_val = self.font_large.render(rad_eff_str, True, COLOR_NV)
        self.screen.blit(eff_label, (center_x, eff_top_y + 2))
        self.screen.blit(eff_val, eff_val.get_rect(right=right_x - 15, top=eff_top_y + 2))

        # 3. LINEA DI SEPARAZIONE ORIZZONTALE
        pygame.draw.line(self.screen, COLOR_NV, (0, eff_bottom_y), (center_x - 5, eff_bottom_y), 1)

        # 4. SEZIONE INFERIORE
        bot_y = eff_bottom_y + 2
        pygame.draw.line(self.screen, COLOR_NV, (center_x - 5, eff_bottom_y), (center_x - 5, eff_bottom_y + 20), 1)

        # RAD RESIST
        rr_label = self.font.render("RAD RESIST", True, COLOR_NV)
        rr_val = self.font.render(f"{rad_resist}%", True, COLOR_NV)
        self.screen.blit(rr_label, (10, bot_y))
        self.screen.blit(rr_val, rr_val.get_rect(right=center_x - 10, top=bot_y))

        # RADS
        rads_label = self.font.render("RADS", True, COLOR_NV)
        rads_x = center_x 
        self.screen.blit(rads_label, (rads_x, bot_y))

        # SCALA GRADUATA & INDICATORE
        meter_x1 = rads_x + rads_label.get_width() + 10
        meter_x2 = right_x - 3
        meter_y = eff_bottom_y
        meter_w = max(10, meter_x2 - meter_x1)

        pygame.draw.line(self.screen, COLOR_NV, (center_x, meter_y), (right_x, meter_y), 1)
        pygame.draw.line(self.screen, COLOR_NV, (right_x, eff_bottom_y), (right_x, eff_bottom_y + 20), 1)

        lbl_500 = self.font.render("500", True, COLOR_NV)
        lbl_1000 = self.font.render("1000", True, COLOR_NV)
        self.screen.blit(lbl_500, lbl_500.get_rect(center=(meter_x1 + meter_w // 2, meter_y - 7)))
        self.screen.blit(lbl_1000, lbl_1000.get_rect(right=meter_x2, bottom=meter_y - 2))

        tri_0 = [(meter_x1 - 5, meter_y), (meter_x1, meter_y), (meter_x1, meter_y + 6)]
        pygame.draw.polygon(self.screen, COLOR_NV, tri_0)

        tri_1000 = [(right_x, meter_y), (meter_x2 - 2, meter_y), (meter_x2 - 2, meter_y + 6)]
        pygame.draw.polygon(self.screen, COLOR_NV, tri_1000)

        for val in [200, 400, 600, 800]:
            tx = meter_x1 + int((val / 1000.0) * meter_w)
            pygame.draw.line(self.screen, COLOR_NV, (tx, meter_y), (tx, meter_y + 7), 1)

        for val in [50, 150, 250, 350, 450, 550, 650, 750, 850, 950]:
            tx = meter_x1 + int((val / 1000.0) * meter_w)
            pygame.draw.line(self.screen, COLOR_NV, (tx, meter_y), (tx, meter_y + 4), 1)

        RIGHT_ALIGN_OFFSET = 2  
        effective_x2 = meter_x2 - RIGHT_ALIGN_OFFSET
        effective_w = effective_x2 - meter_x1

        indicator_x = meter_x1 + int((display_rads_int / 1000.0) * effective_w)
        indicator_x = max(meter_x1, min(effective_x2, indicator_x))

        ind_txt = self.font.render(f"{display_rads_int}", True, COLOR_NV)
        self.screen.blit(ind_txt, ind_txt.get_rect(right=indicator_x - 5, top=meter_y + 15))

        arrow_top_y = meter_y + 9
        arrow_bot_y = meter_y + 22
        head_pts = [
            (indicator_x, arrow_top_y), 
            (indicator_x - 4, arrow_top_y + 5), 
            (indicator_x + 4, arrow_top_y + 5)
        ]
        pygame.draw.polygon(self.screen, COLOR_NV, head_pts)
        pygame.draw.line(self.screen, COLOR_NV, (indicator_x, arrow_top_y), (indicator_x, arrow_bot_y + 7), 1)

    def _render_fo4(self, player_data: dict):
        """Interfaccia Radiazioni Fallout 4 con Tacche Graduate Chiare e Ben Definita."""
        COLOR_LIGHT = settings.PIP_BOY_LIGHT
        COLOR_DARK = settings.PIP_BOY_DARK
        DANGER_COLOR = self._get_danger_color(COLOR_LIGHT)

        display_rads, _ = self._get_rad_values(player_data)
        rad_resist = player_data.get('rad_resist', getattr(settings, 'RAD_RESIST', 10))

        # --- QUADRANTE ANALOGICO ---
        margin = 8
        gauge_w = self.draw_space.width - (margin * 2)
        gauge_h = 126
        gauge_box = pygame.Rect(self.draw_space.left + margin, self.draw_space.top + 2, gauge_w, gauge_h)
        
        pygame.draw.rect(self.screen, COLOR_DARK, gauge_box)
        pygame.draw.rect(self.screen, COLOR_LIGHT, gauge_box, 1)

        cx = gauge_box.centerx
        cy = gauge_box.top + 98
        radius = 78

        # --- ARCO CONTINUO LISCIO ---
        self._draw_smooth_arc(self.screen, COLOR_LIGHT, (cx, cy), radius=radius, start_deg=51, end_deg=155, width=2)
        self._draw_smooth_arc(self.screen, DANGER_COLOR, (cx, cy), radius=radius, start_deg=25, end_deg=51.5, width=2)

        # --- TACCHE E VALORI NUMERICI ---
        ticks = [0, 200, 400, 600, 800, 1000]
        for val in ticks:
            frac = val / 1000.0
            angle_deg = 155 - (frac * 130)
            angle_rad = math.radians(angle_deg)
            col = DANGER_COLOR if val >= 800 else COLOR_LIGHT

            # Tacca principale (Lunghezza 12px, sporge leggermente all'esterno)
            x1 = cx + (radius + 1) * math.cos(angle_rad)
            y1 = cy - (radius + 1) * math.sin(angle_rad)
            x2 = cx + (radius - 11) * math.cos(angle_rad)
            y2 = cy - (radius - 11) * math.sin(angle_rad)
            pygame.draw.line(self.screen, col, (int(x1), int(y1)), (int(x2), int(y2)), 2)

            # Numero della scala
            xl = cx + (radius - 24) * math.cos(angle_rad)
            yl = cy - (radius - 24) * math.sin(angle_rad)
            t_surf = self.font.render(str(val), True, col)
            t_rect = t_surf.get_rect(center=(int(xl), int(yl)))
            self.screen.blit(t_surf, t_rect)

        # Tacche intermedie (ogni 50 e 100 RAD) - Ora ben visibili e definite
        for val in range(50, 1000, 50):
            if val in ticks:
                continue
            frac = val / 1000.0
            angle_deg = 155 - (frac * 130)
            angle_rad = math.radians(angle_deg)
            col = DANGER_COLOR if val >= 800 else COLOR_LIGHT

            # Tacche da 100 RAD lunghe 8px, tacche da 50 RAD lunghe 5px
            tick_len = 8 if (val % 100 == 0) else 5
            x1 = cx + (radius + 1) * math.cos(angle_rad)
            y1 = cy - (radius + 1) * math.sin(angle_rad)
            x2 = cx + (radius - tick_len) * math.cos(angle_rad)
            y2 = cy - (radius - tick_len) * math.sin(angle_rad)
            pygame.draw.line(self.screen, col, (int(x1), int(y1)), (int(x2), int(y2)), 1)

        # --- UNITA' DI MISURA (RAD / h) ---
        unit_surf = self.font.render("RAD / h", True, COLOR_LIGHT)
        self.screen.blit(unit_surf, unit_surf.get_rect(center=(cx, cy - 30)))

        # --- AGO ANALOGICO STANDARD ---
        needle_frac = max(0.0, min(1.0, display_rads / 1000.0))
        needle_angle_deg = 155 - (needle_frac * 130)
        needle_angle_rad = math.radians(needle_angle_deg)

        nx = cx + (radius - 3) * math.cos(needle_angle_rad)
        ny = cy - (radius - 3) * math.sin(needle_angle_rad)

        pygame.draw.line(self.screen, COLOR_LIGHT, (cx, cy), (int(nx), int(ny)), 2)
        pygame.draw.circle(self.screen, COLOR_LIGHT, (cx, cy), 4)
        pygame.draw.circle(self.screen, COLOR_DARK, (cx, cy), 2)

        # Lettura Digitale sotto il perno
        readout_surf = self.font_large.render(f"{display_rads:.1f}", True, COLOR_LIGHT)
        self.screen.blit(readout_surf, readout_surf.get_rect(center=(cx, cy + 14)))

        # --- INFORMAZIONI ED EFFETTI INFERIORI ---
        bottom_top = gauge_box.bottom + 6
        box_w = (gauge_w - 8) // 2
        box_h = 44

        # Box 1: Effetti Tossicità
        eff_box = pygame.Rect(gauge_box.left, bottom_top, box_w, box_h)
        pygame.draw.rect(self.screen, COLOR_DARK, eff_box)
        pygame.draw.rect(self.screen, COLOR_LIGHT, eff_box, 1)

        if display_rads >= 800:
            eff_title = "CRITICAL POISON"
            eff_desc = "-3 END, -2 AGI, -2 STR"
        elif display_rads >= 600:
            eff_title = "SEVERE POISON"
            eff_desc = "-2 END, -2 AGI"
        elif display_rads >= 400:
            eff_title = "MODERATE POISON"
            eff_desc = "-2 END, -1 AGI"
        elif display_rads >= 200:
            eff_title = "MINOR POISON"
            eff_desc = "-1 END"
        else:
            eff_title = "NORMAL STATUS"
            eff_desc = "No Rad Effects"

        e_title_surf = self.font.render(eff_title, True, COLOR_LIGHT)
        e_desc_surf = self.font.render(eff_desc, True, COLOR_LIGHT)
        self.screen.blit(e_title_surf, (eff_box.left + 6, eff_box.top + 5))
        self.screen.blit(e_desc_surf, (eff_box.left + 6, eff_box.top + 22))

        # Box 2: Rad Resist & Scorte Aid
        aid_box = pygame.Rect(eff_box.right + 8, bottom_top, box_w, box_h)
        pygame.draw.rect(self.screen, COLOR_DARK, aid_box)
        pygame.draw.rect(self.screen, COLOR_LIGHT, aid_box, 1)

        r_res_surf = self.font.render(f"RAD RESIST: {rad_resist}%", True, COLOR_LIGHT)
        r_aid1 = self.font.render("RadAway: (2)  Rad-X: (1)", True, COLOR_LIGHT)

        self.screen.blit(r_res_surf, (aid_box.left + 6, aid_box.top + 5))
        self.screen.blit(r_aid1, (aid_box.left + 6, aid_box.top + 22))