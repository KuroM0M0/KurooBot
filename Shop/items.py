from dataclasses import dataclass
from enum import Enum

class PriceType(Enum):
    VotePunkt = "VotePunkte"
    StreakPunkt = "StreakPunkte"


@dataclass
class ShopItem:
    itemID: int
    name: str
    description: str
    price: int
    priceType: PriceType 
    image: str