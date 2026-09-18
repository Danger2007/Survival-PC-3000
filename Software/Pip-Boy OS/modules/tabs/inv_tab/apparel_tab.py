import os
import pygame
import settings
from tabs.inv_tab.inv_base import InvBase
from ui import ItemGrid
from util_functs import Utils


class ApparelTab(InvBase):
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.footer_font = getattr(tab_instance, 'footer_font', pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10))
        
        # Inizializzazione icone
        self._init_apparel_icons()

        super().__init__(
            screen, 
            tab_instance, 
            draw_space, 
            category='Apparel', 
            enable_turntable=True, 
            enable_dot=True
        )

        self.item_grid = None
        if self.no_items:
            return

        # Inizializzazione ItemGrid per la visualizzazione delle statistiche (Stile FO4)
        if not self.is_nv:
            self.item_grid = ItemGrid(
                draw_space=self.calculate_grid_space(),
                font=self.inv_font,
                padding=1
            )
            if self.unique_items and 0 <= self.active_item_index < len(self.unique_items):
                entries = self.get_grid_entries(self.unique_items[self.active_item_index])
                self.item_grid.update(entries)

    def _init_apparel_icons(self):
        """Inizializza le icone specifiche per l'interfaccia di Apparel."""
        self.big_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 4)
        self.small_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 2)

        self.armor_icon = Utils.load_svg(self.big_icon_size, settings.ARMOR_ICON) if hasattr(settings, 'ARMOR_ICON') else None
        
        defense_icon_path = getattr(settings, 'DEFENSE_ICON', getattr(settings, 'SHIELD_ICON', None))
        if defense_icon_path and os.path.exists(defense_icon_path):
            self.defense_icon = Utils.load_svg(self.small_icon_size, defense_icon_path)
        else:
            self.defense_icon = pygame.Surface((self.small_icon_size, self.small_icon_size), pygame.SRCALPHA)

    def get_defense_display_data(self, active_apparel=None):
        if not hasattr(self, 'defense_icon'):
            self._init_apparel_icons()

        total_dr = 0
        total_dt = 0

        # Se passato un singolo oggetto o tutta la lista
        if active_apparel:
            items_to_check = active_apparel if isinstance(active_apparel, (list, tuple)) else [active_apparel]
            for item in items_to_check:
                # Se valutiamo il totale equipaggiato oppure il singolo oggetto selezionato
                if getattr(item, 'equipped', False) or getattr(item, 'is_equipped', False) or len(items_to_check) == 1:
                    total_dr += getattr(item, 'dr', getattr(item, 'damage_res', getattr(item, 'defense', 0)))
                    total_dt += getattr(item, 'dt', getattr(item, 'damage_threshold', 0))

        text_val = f"{total_dr} / {total_dt}" if total_dt else f"{total_dr}"

        return {
            "icon": self.defense_icon,
            "text": text_val,
            "value": total_dr
        }

    def init_footer_defense(self):
        active_apparel = getattr(self, 'unique_items', [])
        defense_data = self.get_defense_display_data(active_apparel)
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH // 4, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        if defense_data["icon"]:
            icon_y = (settings.BOTTOM_BAR_HEIGHT - defense_data["icon"].get_height()) // 2
            footer_surface.blit(defense_data["icon"], (settings.BOTTOM_BAR_MARGIN, icon_y))
            
            font = getattr(self, 'footer_font', getattr(self, 'inv_font', None))
            if font:
                text_surf = font.render(defense_data["text"], True, settings.PIP_BOY_LIGHT)
                text_y = (settings.BOTTOM_BAR_HEIGHT - text_surf.get_height()) // 2
                footer_surface.blit(text_surf, (defense_data["icon"].get_width() + (settings.BOTTOM_BAR_MARGIN * 2), text_y))

        return footer_surface

    def init_footer_text(self):
        weight_surface = self.init_footer_weight()
        caps_surface = self.init_footer_caps()
        defense_surface = self.init_footer_defense()

        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        footer_surface.blit(weight_surface, (0, 0))
        footer_surface.blit(caps_surface, (0, 0))
        
        # Positioning the defense display in the center of the footer
        start_x = settings.SCREEN_WIDTH // 2
        footer_surface.blit(defense_surface, (start_x, 0))

        return footer_surface

    def get_grid_entries(self, item):
        """Generates a list of entries for the ItemGrid based on the selected apparel item."""
        entries = []
        
        dr_val = getattr(item, 'dr', getattr(item, 'damage_res', getattr(item, 'defense', 0)))
        dt_val = getattr(item, 'dt', getattr(item, 'damage_threshold', 0))

        defense_lines = [{
            "icon": self.defense_icon,
            "value": f"{dr_val} / {dt_val}" if dt_val else dr_val,
            "is_base": True
        }]
        
        entries.append({
            "label": "DMG Resist",
            "lines": defense_lines,
            "highlight": True,
            "split": True
        })
            
        standard = [
            ("Weight", getattr(item, 'weight', 0)),
            ("Value", getattr(item, 'value', 0))
        ]
        for label, value in standard:
            entries.append({"label": label, "value": value})
        
        return entries

    def scroll(self, direction: bool):
        if self.no_items:
            return
        prev_index = self.inv_list.selected_index
        super().scroll(direction)
        
        if not self.is_nv and self.item_grid and prev_index != self.inv_list.selected_index and self.unique_items:
            if 0 <= self.inv_list.selected_index < len(self.unique_items):
                entries = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
                self.item_grid.update(entries)

    def handle_input(self, event: pygame.event.Event):
        """Manages user input events, including item selection and grid updates."""
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if not self.is_nv and self.item_grid and self.unique_items and 0 <= self.active_item_index < len(self.unique_items):
                    entries = self.get_grid_entries(self.unique_items[self.active_item_index])
                    self.item_grid.update(entries)

    def render(self):
        super().render()
        if self.no_items or self.is_nv or self.item_grid is None:
            return
        self.item_grid.render(self.screen)