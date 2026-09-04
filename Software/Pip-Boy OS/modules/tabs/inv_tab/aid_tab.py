import pygame
import settings
from .inv_base import InvBase
from ui import ItemGrid
from util_functs import Utils


class AidTab(InvBase):
    def __init__(self, screen, tab_instance, draw_space):
        super().__init__(screen, tab_instance, draw_space, category='Aid', enable_turntable=True)
        self.item_grid = None

        if self.no_items:
            return

        self.time_icon = Utils.load_svg(self.small_icon_size, settings.TIME_ICON) if hasattr(settings, 'TIME_ICON') else None
              
        self.item_grid = ItemGrid(
            draw_space=self.calculate_grid_space(),
            font=self.inv_font,
            padding=1
        )
        
        if self.unique_items and 0 <= self.inv_list.selected_index < len(self.unique_items):
            entries = self.get_grid_entries(self.unique_items[self.inv_list.selected_index])
            self.item_grid.update(entries)

    def get_stats_display_data(self, item):
        if not item:
            return []
        
        display_data = []
        
        if getattr(item, 'health', None):
            display_data.append({"label": "Health", "value": item.health})
            
        if getattr(item, 'ap', None):
            display_data.append({"label": "AP", "value": item.ap})
            
        if getattr(item, 'rads', None):
            display_data.append({"label": "Rads", "value": item.rads})
            
        if getattr(item, 'special_bonuses', None):
            for stat, bonus in item.special_bonuses.items():
                display_data.append({"label": stat, "value": bonus})
            
        return display_data

    def get_grid_entries(self, item):
        entries = []
        
        stats_data = self.get_stats_display_data(item)
        for stat in stats_data:
            entry = {"label": stat["label"], "value": stat["value"]}
            if hasattr(self, 'time_icon') and self.time_icon:
                entry["icon"] = self.time_icon
            entries.append(entry)
            
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