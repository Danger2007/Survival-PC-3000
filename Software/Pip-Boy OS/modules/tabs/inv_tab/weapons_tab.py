import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid
from util_functs import Utils


class WeaponsTab(InvBase):
    def __init__(self, screen, tab_instance, draw_space):
        super().__init__(screen, tab_instance, draw_space, category='Weapon', enable_dot=True)
        self.item_grid = None

        if self.no_items:
            return

        self.ammo_icon = Utils.load_svg(self.small_icon_size, settings.AMMO_ICON) if hasattr(settings, 'AMMO_ICON') else None
        self.gun_icon = Utils.load_svg(self.big_icon_size, settings.GUN_ICON) if hasattr(settings, 'GUN_ICON') else None
        
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
        damage_surface = self.init_footer_damage()
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        footer_surface.blit(weight_surface, (0, 0))
        footer_surface.blit(caps_surface, (0, 0))
        footer_surface.blit(damage_surface, (0, 0))
        
        return footer_surface

    def calculate_damage(self, weapon):
        if not weapon:
            return {"base": 0, "types": {}}

        base_damage = getattr(weapon, 'damage', 0) or 0

        damage_breakdown = {
            "base": base_damage,
            "types": {}
        }

        damage_types = getattr(weapon, 'damage_types', []) or []
        for damage_type in damage_types:
            type_damage = (damage_type.value * base_damage) // 100
            icon = self.damage_icons.get(damage_type.path) if hasattr(self, 'damage_icons') and isinstance(self.damage_icons, dict) else None
            damage_breakdown["types"][damage_type.path] = {
                "value": type_damage,
                "icon": icon
            }

        return damage_breakdown

    def get_damage_display_data(self, weapon):
        if not weapon:
            return []

        damage_data = self.calculate_damage(weapon)
        display_data = []

        ammo_type = getattr(weapon, 'ammo_type', None)
        base_icon = None
        if ammo_type and hasattr(settings, 'items') and ammo_type in settings.items:
            ammo_item = settings.items[ammo_type]
            if hasattr(ammo_item, 'damage_type') and hasattr(self, 'damage_icons') and isinstance(self.damage_icons, dict):
                base_icon = self.damage_icons.get(ammo_item.damage_type)

        display_data.append({
            "label": "Damage",
            "value": damage_data.get("base", 0),
            "icon": base_icon,
            "is_base": True
        })

        if "types" in damage_data and damage_data["types"]:
            for _, type_info in damage_data["types"].items():
                display_data.append({
                    "label": "",
                    "value": type_info["value"],
                    "icon": type_info["icon"],
                    "is_base": False
                })

        return display_data

    def init_footer_damage(self):
        footer_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT),
            pygame.SRCALPHA
        ).convert_alpha()

        if self.no_items or not self.item_selected or self.active_item_index is None or not self.unique_items:
            return footer_surface

        if 0 <= self.active_item_index < len(self.unique_items):
            active_weapon = self.unique_items[self.active_item_index]
            damage_data = self.get_damage_display_data(active_weapon)

            x_pos = settings.SCREEN_WIDTH - settings.BOTTOM_BAR_MARGIN

            for entry in reversed(damage_data):
                value_text = str(entry["value"])
                value_surface = self.footer_font.render(value_text, True, settings.PIP_BOY_LIGHT)
                x_pos -= value_surface.get_width()
                footer_surface.blit(value_surface, (x_pos, 2))
                
                if entry.get("icon") is not None:
                    icon = entry["icon"]
                    x_pos -= icon.get_width() + 1
                    y_pos = (settings.BOTTOM_BAR_HEIGHT - icon.get_height()) // 2
                    footer_surface.blit(icon, (x_pos, y_pos))
                    x_pos -= settings.BOTTOM_BAR_MARGIN

            if hasattr(self, 'gun_icon') and self.gun_icon:
                x_pos -= self.gun_icon.get_width()
                footer_surface.blit(self.gun_icon, (x_pos, 4))

        return footer_surface

    def get_grid_entries(self, item):
        entries = []

        damage_data = self.get_damage_display_data(item)
        damage_lines = []

        for entry in damage_data:
            line_data = {
                "value": entry["value"],
                "is_base": entry.get("is_base", False)
            }
            if entry.get("icon") is not None:
                line_data["icon"] = entry["icon"]
            damage_lines.append(line_data)

        entries.append({
            "label": "Damage",
            "lines": damage_lines,
            "highlight": True,
            "split": True
        })

        ammo_type = getattr(item, 'ammo_type', None)
        if ammo_type and hasattr(settings, 'items') and ammo_type in settings.items:
            ammo_count = settings.TOTAL_AMMO.get(ammo_type, 0) if hasattr(settings, 'TOTAL_AMMO') else 0
            ammo_type_name = settings.items[ammo_type].name
            
            ammo_entry = {
                "label": ammo_type_name,
                "icon_front": True,
                "value": ammo_count,
                "highlight": True
            }
            if hasattr(self, 'ammo_icon') and self.ammo_icon is not None:
                ammo_entry["icon"] = self.ammo_icon

            entries.append(ammo_entry)

        standard = [
            ("Fire Rate", getattr(item, 'fire_rate', 0)),
            ("Range", getattr(item, 'range', 0)),
            ("Accuracy", getattr(item, 'accuracy', 0)),
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