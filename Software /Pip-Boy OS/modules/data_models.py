# data_models.py
from dataclasses import dataclass
from typing import NamedTuple, Dict, Tuple


@dataclass
class LimbPosition:
    x_offset: int
    y_position: int
    name: str

class IconConfig(NamedTuple):
    path: str
    value: int

class DamageType(NamedTuple):
    type: str
    value: int


@dataclass
class ItemBase:
    name: str
    weight: float
    value: int
    icons: str
    description: str = ""
    category: str = "Misc"

@dataclass
class WeaponItem(ItemBase):
    damage: int = 0
    fire_rate: int = 0
    range: int = 0
    accuracy: int = 0
    ammo_type: str = ""
    damage_types: Tuple[DamageType] = ()

@dataclass
class ApparelItem(ItemBase):
    defense: int = 0
    damage_resist: Tuple[DamageType] = ()
    special_bonuses: Dict[str, int] = None

@dataclass
class AidItem(ItemBase):
    health: int = 0
    ap: int = 0
    rads: int = 0
    addiction_risk: str = "None"
    special_bonuses: Dict[str, int] = None

@dataclass
class AmmoItem(ItemBase):
    damage_type: str = ""

@dataclass
class JunkItem(ItemBase):
    components: Dict[str, int] = None

@dataclass
class MiscItem(ItemBase):
    type: str = "Misc"
