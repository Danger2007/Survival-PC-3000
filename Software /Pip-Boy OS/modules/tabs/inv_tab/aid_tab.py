import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid
from util_functs import Utils

class AidTab(InvBase):
    def __init__(self, screen, tab_instance, draw_space):
        # Initialize the base class with the 'Aid' category.
        super().__init__(screen, tab_instance, draw_space, category='Aid', enable_turntable=True)
        
        # Initialize the footer for the aid tab.
        self.tab_instance.init_footer(
            self, 
            (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
            self.init_footer_text()
        )
        
        # Load time icon.
        
        self.time_icon = Utils.load_svg(self.small_icon_size, settings.TIME_ICON)
              
        # Initialize the item grid.
        self.item_grid = ItemGrid(
            draw_space=self.calculate_grid_space(),
            font=self.inv_font,
            padding=1
        )
        
        # Prepare and update grid entries for the initially selected aid item.
        entries = self.get_grid_entries(self.inv_items[self.inv_list.selected_index])
        self.item_grid.update(entries)
        
    def init_footer_text(self):
        """
        Combine multiple footer components (weight, defense, and durability) into one footer surface.
        """
        weight_surface = self.init_footer_weight()  # Assumed to be defined in InvBase or elsewhere.
        defense_surface = self.init_footer_caps()
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        footer_surface.blit(weight_surface, (0, 0))
        footer_surface.blit(defense_surface, (0, 0))
        
        return footer_surface


    def get_stats_display_data(self, item):
        """
        Prepare aid stats data for display.
        Returns a list of dictionaries with value and icon for each stat.
        """
        if not item:
            return []
        
        display_data = []
        
        # Health stat.
        if item.health:
            display_data.append({
                "label": "Health",
                "value": item.health
            })
            
        # AP stat.
        if item.ap:
            display_data.append({
                "label": "AP",
                "value": item.ap
            })
            
        # Rads stat.
        if item.rads:
            display_data.append({
                "label": "Rads",
                "value": item.rads
            })
            
            
        # Special bonuses.
        if item.special_bonuses:
            for stat,bonus in item.special_bonuses.items():
                display_data.append({
                    "label": stat,
                    "value": bonus
                })
            
        return display_data
    
    def calculate_grid_space(self):
        return super().calculate_grid_space()
    
    #OG grid calculations
    """
    def calculate_grid_space(self):
        #Calculate the space available for the item grid.
        list_space = self.list_draw_space
        return pygame.Rect(
            list_space.right + settings.GRID_LEFT_MARGIN,  # Horizontal spacing from list.
            list_space.top,                                  # Align top with the list.
            self.draw_space.width - list_space.width - (settings.GRID_RIGHT_MARGIN // 3),  # Use remaining width.
            list_space.height                                # Match the list's height.
        )
    """
    def get_grid_entries(self, item):
        """
        Prepare grid entries for the selected aid item, including aid stats and standard properties.
        """
        entries = []
        
        # Add aid stats entries.
        stats_data = self.get_stats_display_data(item)
        for stat in stats_data:
            entries.append({
                "label": stat["label"],
                "value": stat["value"],
                "icon": self.time_icon
            })
            
        # Add standard entries (e.g., weight and value).
        standard = [
            ("Weight", item.weight),
            ("Value", item.value)
        ]
        for label, value in standard:
            entries.append({"label": label, "value": value})
            
        return entries


    def scroll(self, direction: bool):
        """
        Scroll through the list of aid items and update the grid entries.
        """
        prev_index = self.inv_list.selected_index
        super().scroll(direction)
        if prev_index != self.inv_list.selected_index:
            entries = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(entries)

    def render(self):
        """
        Render the aid tab components.
        """
        super().render()
        self.item_grid.render(self.screen)
