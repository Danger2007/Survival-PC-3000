import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid
from util_functs import Utils


class ApparelTab(InvBase):
    def __init__(self, screen, tab_instance, draw_space):
        super().__init__(screen, tab_instance, draw_space, category='Apparel', enable_turntable=True, enable_dot=True)
        self.item_grid = None

        if self.no_items:
            return

        self.armor_icon = Utils.load_svg(self.big_icon_size, settings.ARMOR_ICON) if hasattr(settings, 'ARMOR_ICON') else None
        self.defense_icon = Utils.load_svg(self.small_icon_size, settings.DEFENSE_ICON) if hasattr(settings, 'DEFENSE_ICON') else None
        
        self.item_grid = ItemGrid(
            draw_space=self.calculate_grid_space(),
            font=self.inv_font,
            padding=1
        )
        
        if self.unique_items and 0 <= self.inv_list.selected_index < len(self.unique_items):
            entries = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(entries)

    def init_footer_text(self):
        weight_surface = self.init_footer_weight()
        caps_surface = self.init_footer_caps()
        defense_surface = self.init_footer_defense()
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        footer_surface.blit(weight_surface, (0, 0))
        footer_surface.blit(caps_surface, (0, 0))
        footer_surface.blit(defense_surface, (0, 0))
        
        return footer_surface

    def calculate_defense(self, apparel):
        if not apparel:
            return {"base": 0, "types": {}}
        
        base_defense = getattr(apparel, 'defense', 0) or 0
        
        defense_breakdown = {
            "base": base_defense,
            "types": {}
        }
        
        damage_resist = getattr(apparel, 'damage_resist', []) or []
        for defense_type in damage_resist:
            type_defense = (defense_type.value * base_defense) // 100
            icon = self.icons.get(defense_type.path) if hasattr(self, 'icons') and isinstance(self.icons, dict) else None
            defense_breakdown["types"][defense_type.path] = {
                "value": type_defense,
                "icon": icon
            }
        
        return defense_breakdown

    def get_defense_display_data(self, apparel):
        if not apparel:
            return []
        
        defense_data = self.calculate_defense(apparel)
        display_data = []
        
        base_val = defense_data.get("base", 0) if defense_data.get("base") is not None else 0
        display_data.append({
            "label": "Defense",
            "value": max(0, base_val),
            "icon": self.defense_icon,
            "is_base": True
        })
        
        if "types" in defense_data and defense_data["types"]:
            for _, type_info in defense_data["types"].items():
                display_data.append({
                    "label": "",
                    "value": type_info["value"],
                    "icon": type_info["icon"],
                    "is_base": False
                })
        
        return display_data

    def init_footer_defense(self):
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        if self.no_items or not self.item_selected or self.active_item_index is None or not self.unique_items:
            return footer_surface
        
        if 0 <= self.active_item_index < len(self.unique_items):
            active_apparel = self.unique_items[self.active_item_index]
            defense_data = self.get_defense_display_data(active_apparel)
            
            x_pos = settings.SCREEN_WIDTH - settings.BOTTOM_BAR_MARGIN
            
            if defense_data:
                for entry in reversed(defense_data):
                    value_text = str(entry["value"])
                    value_surface = self.footer_font.render(value_text, True, settings.PIP_BOY_LIGHT)
                    x_pos -= value_surface.get_width()
                    footer_surface.blit(value_surface, (x_pos, 2))
                    
                    if entry.get("icon"):
                        icon = entry["icon"]
                        x_pos -= icon.get_width() + 1
                        y_pos = (settings.BOTTOM_BAR_HEIGHT - icon.get_height()) // 2
                        footer_surface.blit(icon, (x_pos, y_pos))
                        x_pos -= settings.BOTTOM_BAR_MARGIN
            
            if hasattr(self, 'armor_icon') and self.armor_icon:
                x_pos -= self.armor_icon.get_width()
                footer_surface.blit(self.armor_icon, (x_pos, 4))
        
        return footer_surface

    def get_grid_entries(self, item):
        entries = []
        
        defense_data = self.get_defense_display_data(item)
        if defense_data:
            defense_lines = []
            for entry in defense_data:
                defense_lines.append({
                    "icon": entry["icon"],
                    "value": entry["value"],
                    "is_base": entry.get("is_base", False)
                })
            
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

    def select_item(self):
        if self.no_items:
            return
        super().select_item()
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self.init_footer_text())

    def scroll(self, direction: bool):
        if self.no_items or self.item_grid is None:
            return
        prev_index = self.inv_list.selected_index
        super().scroll(direction)
        if prev_index != self.inv_list.selected_index and self.unique_items and 0 <= self.inv_list.selected_index < len(self.unique_items):
            entries = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(entries)

    def render(self):
        super().render()
        if self.no_items or self.item_grid is None:
            return
        self.item_grid.render(self.screen)