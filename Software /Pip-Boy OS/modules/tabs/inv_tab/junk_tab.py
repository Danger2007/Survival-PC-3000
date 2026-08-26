import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid

class JunkTab(InvBase):
    def __init__(self, screen, tab_instance, draw_space):
        # Initialize the base class with the 'Junk' category.
        super().__init__(screen, tab_instance, draw_space, category='Junk', enable_turntable=True)
        
        # Initialize the footer for the junk tab.
        self.tab_instance.init_footer(
            self, 
            (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
            self.init_footer_text()
        )
        
        
        # Initialize the item grid.
        self.item_grid = ItemGrid(
            draw_space=self.calculate_grid_space(),
            font=self.inv_font,
            padding=1
        )
        
        # Prepare and update grid entries for the initially selected junk item.
        entries = self.get_grid_entries(self.inv_items[self.inv_list.selected_index])
        self.item_grid.update(entries)
        
    def init_footer_text(self):
        """
        Combine multiple footer components (weight and components) into one footer surface.
        """
        weight_surface = self.init_footer_weight()  # Assumed to be defined in InvBase or elsewhere.
        defense_surface = self.init_footer_caps()
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        footer_surface.blit(weight_surface, (0, 0))
        footer_surface.blit(defense_surface, (0, 0))
        
        return footer_surface
    
    def calculate_grid_space(self):
        return super().calculate_grid_space()
    
    #OG grid calculation
    """"
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
        Prepare grid entries for the selected junk item, including component details and standard properties.
        """
        entries = []
            
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
        Scroll through the list of junk items and update the grid entries.
        """
        prev_index = self.inv_list.selected_index
        super().scroll(direction)
        if prev_index != self.inv_list.selected_index:
            entries = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(entries)

    def render(self):
        """
        Render the junk tab components.
        """
        super().render()
        self.item_grid.render(self.screen)
