from data_models import WeaponItem, ApparelItem, AidItem, MiscItem, IconConfig, AmmoItem, JunkItem
from configparser import ConfigParser
from typing import Tuple, Dict



class Inventory:
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Ensures only one instance of Inventory is created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.items = {}  # Initialize the inventory
        return cls._instance

    def add_item(self, item, quantity=1):
        """Add an item to the inventory, incrementing quantity if it exists."""
        if item.name in self.items:
            self.items[item.name] = (item, self.items[item.name][1] + quantity)
        else:
            self.items[item.name] = (item, quantity)

    def get_all_items(self, category=None):
        """Returns a list of item instances, expanded by quantity for existing logic."""
        expanded_list = []
        for item, quantity in self.items.values():
            if category and item.category != category:
                continue
            expanded_list.extend([item] * quantity)
        return expanded_list
    
    
    def get_unique_items(self, category=None):
        """Returns a list of unique item instances."""
        unique_list = []
        for item, _ in self.items.values():
            if category and item.category != category:
                continue
            if item not in unique_list:
                unique_list.append(item)
        return unique_list

    def get_item_names(self, category=None):
        """Returns item names with quantities (e.g., 'RadAway (2)')."""
        item_names = []
        for name, (item, quantity) in self.items.items():
            if category and item.category != category:
                continue
            if quantity > 1:
                item_names.append(f"{name} ({quantity})")
            else:
                item_names.append(name)
        return item_names  # List of formatted names



class ItemLoader:
    def __init__(self, ini_file: str):
        import os
        self.config = ConfigParser()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        ini_path = os.path.join(current_dir, ini_file)
        self.config.read(ini_path)
        self.items = {}

        
    def _parse_icon_configs(self, value: str) -> Tuple[IconConfig]:
        if not value:
            return ()
        return tuple(
            IconConfig(path=ic.split(':')[0], value=int(ic.split(':')[1]))
            for ic in [x.strip() for x in value.split(',')]
        )
    
    def _parse_dicts(self, value: str) -> Dict[str, int]:
        if not value:
            return {}
        return dict(
            (part.split(':')[0].strip(), int(part.split(':')[1]))
            for part in value.split(',')
        )

    def load_items(self):
        for section in self.config.sections():
            data = dict(self.config[section])
            item_type = data.get('category', 'Misc')
            
            base_data = {
                'name': section,
                'weight': float(data.get('weight', 0)),
                'value': int(data.get('value', 0)),
                'icons': data.get('icons', ''),
                'description': data.get('description', ''),
                'category': item_type
            }
            
            if item_type == 'Weapon':
                self.items[section] = WeaponItem(
                    **base_data,
                    damage=int(data.get('damage', 0)),
                    fire_rate=int(data.get('fire_rate', 0)),
                    range=int(data.get('range', 0)),
                    accuracy=int(data.get('accuracy', 0)),
                    ammo_type=data.get('ammo_type', ''),
                    damage_types=self._parse_icon_configs(data.get('damage_types', '')),
                )
            elif item_type == 'Apparel':
                self.items[section] = ApparelItem(
                    **base_data,
                    defense=int(data.get('defense', 0)),
                    damage_resist=self._parse_icon_configs(data.get('damage_resist', '')),
                    special_bonuses=self._parse_dicts(data.get('special_bonuses', ''))
                )
            elif item_type == 'Aid':
                self.items[section] = AidItem(
                    **base_data,
                    health=int(data.get('health', 0)),
                    rads=int(data.get('rads', 0)),
                    ap=int(data.get('ap', 0)),
                    addiction_risk=data.get('addiction_risk', 'None'),
                    special_bonuses=self._parse_dicts(data.get('special_bonuses', ''))
                )
                
            elif item_type == 'Ammo':
                self.items[section] = AmmoItem(
                    **base_data,
                    damage_type=data.get('damage_type', '')
                )
                
            elif item_type == 'Junk':
                self.items[section] = JunkItem(
                    **base_data,
                    components=self._parse_dicts(data.get('components', ''))
                )   
                             
            elif item_type == 'Misc':
                self.items[section] = MiscItem(
                    **base_data,
                    type=data.get('type', '')
                    )
                
            else:
                raise ValueError(f"Unknown item type: {item_type}")
            

        
        return self.items

# Usage example:
if __name__ == "__main__":
    loader = ItemLoader('items.ini')
    items = loader.load_items()