import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid
from util_functs import Utils


class WeaponsTab(InvBase):
    def __init__(self, screen, tab_instance, draw_space):
        super().__init__(screen, tab_instance, draw_space, category='Weapon', enable_dot=True)
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self.init_footer_text())
        
        self.ammo_icon = Utils.load_svg(self.small_icon_size, settings.AMMO_ICON)
        self.gun_icon = Utils.load_svg(self.big_icon_size, settings.GUN_ICON)
        self.item_grid = ItemGrid(
            draw_space=self.calculate_grid_space(),
            font=self.inv_font,
            padding=1
        )
        
        entries = self.get_grid_entries(self.inv_items[self.inv_list.selected_index])
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
        """
        Calculate the total damage breakdown for a weapon.
        Returns a dictionary with base damage and damage type modifiers.
        """
        if not weapon:
            return {}

        # Base damage from the weapon
        base_damage = weapon.damage
        

        # Calculate damage type modifiers
        damage_breakdown = {
            "base": base_damage,
            "types": {}
        }

        # Process each damage type
        for damage_type in weapon.damage_types:
            # Calculate the damage contribution for this type
            type_damage = (damage_type.value * base_damage) // 100
            damage_breakdown["types"][damage_type.path] = {
                "value": type_damage,
                "icon": self.damage_icons.get(damage_type.path)
            }

        return damage_breakdown

    def get_damage_display_data(self, weapon):
        """
        Prepare damage data for display in the grid or footer.
        Returns a list of dictionaries with label, value, and icon for each damage component.
        """
        if not weapon:
            return []

        damage_data = self.calculate_damage(weapon)
        display_data = []

        # Base damage entry
        ammo_item = settings.items.get(weapon.ammo_type)
        if ammo_item:
            base_icon = self.damage_icons.get(ammo_item.damage_type)
            display_data.append({
                "label": "Damage",
                "value": damage_data["base"],
                "icon": base_icon,
                "is_base": True
            })

        # Damage type entries
        for dtype_path, type_info in damage_data["types"].items():
            display_data.append({
                "label": "",  # No label for damage types (displayed as modifiers)
                "value": type_info["value"],
                "icon": type_info["icon"],
                "is_base": False
            })

        return display_data

    def init_footer_damage(self):
        """
        Render the damage information in the footer.
        """
        footer_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT),
            pygame.SRCALPHA
        ).convert_alpha()

        if not self.item_selected or self.active_item_index is None:
            return footer_surface

        active_weapon = self.unique_items[self.active_item_index]
        
        damage_data = self.get_damage_display_data(active_weapon)

        # Start positioning from the right edge
        x_pos = settings.SCREEN_WIDTH - settings.BOTTOM_BAR_MARGIN



        # Add damage components (right-to-left)
        for entry in reversed(damage_data):
            
            # Render damage value
            value_text = str(entry["value"])
            value_surface = self.footer_font.render(value_text, True, settings.PIP_BOY_LIGHT)
            x_pos -= value_surface.get_width()
            footer_surface.blit(value_surface, (x_pos, 2))
            
            if entry.get("icon"):
                # Render icon
                icon = entry["icon"]
                x_pos -= icon.get_width() + 1
                y_pos = (settings.BOTTOM_BAR_HEIGHT - icon.get_height()) // 2
                footer_surface.blit(icon, (x_pos, y_pos))
                x_pos -= settings.BOTTOM_BAR_MARGIN



        # Add gun icon
        x_pos -= self.gun_icon.get_width()
        footer_surface.blit(self.gun_icon, (x_pos, 4))
        x_pos -= settings.BOTTOM_BAR_MARGIN

        return footer_surface
 
    def calculate_grid_space(self):
        return super().calculate_grid_space()
    
    def get_grid_entries(self, item):
        """
        Prepare grid entries for the selected weapon, including damage breakdown.
        """
        entries = []

        # Damage entry
        damage_data = self.get_damage_display_data(item)
        damage_lines = []

        for entry in damage_data:
            damage_lines.append({
                "icon": entry["icon"],
                "value": entry["value"],
                "is_base": entry.get("is_base", False)
            })

        entries.append({
            "label": "Damage",
            "lines": damage_lines,
            "highlight": True,
            "split": True
        })

        # Ammo entry
        ammo = settings.TOTAL_AMMO.get(item.ammo_type, 0)
        ammo_type_name = settings.items[item.ammo_type].name
        entries.append({
            "label": ammo_type_name,
            "icon_front": True,
            "icon": self.ammo_icon,
            "value": ammo,
            "highlight": True
        })

        # Standard entries
        standard = [
            ("Fire Rate", item.fire_rate),
            ("Range", item.range),
            ("Accuracy", item.accuracy),
            ("Weight", item.weight),
            ("Value", item.value)
        ]
        for label, value in standard:
            entries.append({"label": label, "value": value})

        return entries
        
    
    def select_item(self):
        super().select_item()
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self.init_footer_text())


    def scroll(self, direction: bool):
        prev_index = self.inv_list.selected_index
        super().scroll(direction)
        if prev_index != self.inv_list.selected_index:
            entries = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(entries)


    def render(self):
        super().render()
        self.item_grid.render(self.screen)