import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid
from util_functs import Utils

class ApparelTab(InvBase):
    def __init__(self, screen, tab_instance, draw_space):
        # Initialize the base class with the 'Apparel' category.
        super().__init__(screen, tab_instance, draw_space, category='Apparel', enable_turntable=False, enable_dot=True)
        
        # Initialize the footer for the apparel tab.
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self.init_footer_text())
        
        # Load icons specific to apparel.
        self.armor_icon = Utils.load_svg(self.big_icon_size, settings.ARMOR_ICON)
        self.defense_icon = Utils.load_svg(self.small_icon_size, settings.DEFENSE_ICON)
        
        # (Assuming self.defense_icons is set elsewhere, e.g., in the parent or during tab initialization)
        
        # Initialize the item grid.
        self.item_grid = ItemGrid(
            draw_space=self.calculate_grid_space(),
            font=self.inv_font,
            padding=1
        )
        
        # Prepare and update grid entries for the initially selected item.
        entries = self.get_grid_entries(self.inv_items[self.inv_list.selected_index])
        self.item_grid.update(entries)
        
    def init_footer_text(self):
        """
        Combine multiple footer components (weight, defense, and durability) into one footer surface.
        """
        weight_surface = self.init_footer_weight()  # Assumed to be defined in InvBase or elsewhere.
        caps_surface = self.init_footer_caps()
        defense_surface = self.init_footer_defense()
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        footer_surface.blit(weight_surface, (0, 0))
        footer_surface.blit(caps_surface, (0, 0))
        footer_surface.blit(defense_surface, (0, 0))
        
        return footer_surface

    def calculate_defense(self, apparel):
        """
        Calculate the defense breakdown for an apparel item.
        Returns a dictionary with base defense and defense type modifiers.
        """
        if not apparel:
            return {}
        
        # Base defense value
        base_defense = apparel.defense
        
        defense_breakdown = {
            "base": base_defense,
            "types": {}
        }
        
        # Process each defense type modifier.
        for defense_type in apparel.damage_resist:
            # Calculate the contribution of this defense type.
            type_defense = (defense_type.value * base_defense) // 100
            defense_breakdown["types"][defense_type.path] = {
                "value": type_defense,
                "icon": self.icons.get(defense_type.path)
            }
        
        return defense_breakdown

    def get_defense_display_data(self, apparel):
        """
        Prepare defense data for display.
        Returns a list of dictionaries with value and icon for each defense component.
        """
        if not apparel:
            return []
        
        defense_data = self.calculate_defense(apparel)
        display_data = []
        # Base defense entry.
        
        if defense_data["base"] <= 0:
            return None
        display_data.append({
            "label": "Defense",
            "value": defense_data["base"],
            "icon": self.defense_icon,
            "is_base": True
        })
            

        
        # Entries for each defense type modifier.
        for _, type_info in defense_data["types"].items():
            display_data.append({
                "label": "",  # No label for modifiers.
                "value": type_info["value"],
                "icon": type_info["icon"],
                "is_base": False
            })
        
        return display_data

    def init_footer_defense(self):
        """
        Render the defense information into a footer surface.
        """
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        if not self.item_selected or self.active_item_index is None:
            return footer_surface
        
        active_apparel = self.unique_items[self.active_item_index]
        defense_data = self.get_defense_display_data(active_apparel)
        
        # Positioning starting from the right.
        x_pos = settings.SCREEN_WIDTH - settings.BOTTOM_BAR_MARGIN
        
        if defense_data:
            # Add defense components (right-to-left).
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
        
        # Blit the apparel icon.
        x_pos -= self.armor_icon.get_width()
        footer_surface.blit(self.armor_icon, (x_pos, 4))
        x_pos -= settings.BOTTOM_BAR_MARGIN
        
        return footer_surface

    def calculate_grid_space(self):
        return super().calculate_grid_space()
    
    #OG grid calculation
    """
    def calculate_grid_space(self):
        #Calculate the space available for the item grid.
        list_space = self.list_draw_space
        return pygame.Rect(
            list_space.right + settings.GRID_LEFT_MARGIN,  # Horizontal spacing from list.
            list_space.top,                                   # Align top with the list.
            self.draw_space.width - list_space.width - settings.GRID_RIGHT_MARGIN,  # Use remaining width.
            list_space.height                                 # Match the list's height.
        )
    """
    def get_grid_entries(self, item):
        """
        Prepare grid entries for the selected apparel item, including defense breakdown and durability.
        """
        entries = []
        
        # Defense entry.
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
            
        
        # Standard entries.
        standard = [
            ("Weight", item.weight),
            ("Value", item.value)
        ]
        for label, value in standard:
            entries.append({"label": label, "value": value})
        
        return entries

    def select_item(self):
        """
        Update the footer when a new apparel item is selected.
        """
        super().select_item()
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), self.init_footer_text())

    def scroll(self, direction: bool):
        """
        Scroll through the list of apparel items and update the grid entries.
        """
        prev_index = self.inv_list.selected_index
        super().scroll(direction)
        if prev_index != self.inv_list.selected_index:
            entries = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(entries)

    def render(self):
        """
        Render the apparel tab components.
        """
        super().render()
        self.item_grid.render(self.screen)
