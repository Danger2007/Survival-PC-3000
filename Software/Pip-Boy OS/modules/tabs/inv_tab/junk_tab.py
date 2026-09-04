import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid


class JunkTab(InvBase):
    def __init__(self, screen, tab_instance, draw_space):
        super().__init__(screen, tab_instance, draw_space, category='Junk', enable_turntable=True)
        self.item_grid = None

        if self.no_items:
            return
            
        self.item_grid = ItemGrid(
            draw_space=self.calculate_grid_space(),
            font=self.inv_font,
            padding=1
        )
        
        if self.unique_items and 0 <= self.inv_list.selected_index < len(self.unique_items):
            entries = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(entries)

    def get_grid_entries(self, item):
        entries = []
            
        standard = [
            ("Weight", getattr(item, 'weight', 0)),
            ("Value", getattr(item, 'value', 0))
        ]
        for label, value in standard:
            entries.append({"label": label, "value": value})
            
        return entries

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