import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid

class AmmoTab(InvBase):
    def __init__(self, screen, tab_instance, draw_space):
        super().__init__(screen, tab_instance, draw_space, category='Ammo', enable_turntable=True)
        
        self.tab_instance.init_footer(
            self, 
            (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
            self.init_footer_text()
        )
        
        if self.no_items:
            return
            
        # Initialize the item grid
        self.item_grid = ItemGrid(
            draw_space=self.calculate_grid_space(),
            font=self.inv_font,
            padding=1
        )
        
        # Prepare grid entries for initially selected ammo item
        entries = self.get_grid_entries(self.inv_items[self.inv_list.selected_index])
        self.item_grid.update(entries)
        
    def init_footer_text(self):
        """Combine weight and capacity info into footer surface"""
        weight_surface = self.init_footer_weight()
        capacity_surface = self.init_footer_caps()
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        footer_surface.blit(weight_surface, (0, 0))
        footer_surface.blit(capacity_surface, (0, 0))
        
        return footer_surface

    def calculate_grid_space(self):
        return super().calculate_grid_space()
    
    #OG grid calculation
    """
    def calculate_grid_space(self):
        #Calculate available space for item grid (same as MiscTab)
        list_space = self.list_draw_space
        return pygame.Rect(
            list_space.right + settings.GRID_LEFT_MARGIN,
            list_space.top,
            self.draw_space.width - list_space.width - (settings.GRID_RIGHT_MARGIN // 3),
            list_space.height
        )
    """
    def get_grid_entries(self, item):
        """Add ammo-specific entries including damage type"""
        entries = []
            
        # Standard item properties
        standard = [
            ("Weight", item.weight),
            ("Value", item.value)
        ]
        for label, value in standard:
            entries.append({"label": label, "value": value})
            
            
        return entries

    def scroll(self, direction: bool):
        """Update grid when scrolling through ammo items"""
        if self.no_items:
            return
        prev_index = self.inv_list.selected_index
        super().scroll(direction)
        if prev_index != self.inv_list.selected_index:
            entries = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(entries)

    def render(self):
        """Draw ammo tab components"""
        super().render()
        if self.no_items:
            return
        self.item_grid.render(self.screen)