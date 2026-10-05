"""Coffee preparation rules, independent of rendering and input devices."""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math

VESSELS = {'demitasse': 'Espresso cup', 'mug': 'Ceramic mug', 'tall': 'Tall glass', 'rocks': 'Low glass'}
BEANS = {'light': 'Light roast', 'medium': 'House blend', 'dark': 'Dark roast'}
MILKS = {'none': 'No milk', 'whole': 'Whole milk', 'oat': 'Oat milk', 'foam': 'Milk foam'}
SYRUPS = {'none': 'No syrup', 'vanilla': 'Vanilla', 'caramel': 'Caramel', 'chocolate': 'Chocolate'}
STRAWS = {'none': 'No straw', 'paper': 'Paper straw', 'steel': 'Steel straw'}
PASTRIES = {'none': 'No pastry', 'croissant': 'Croissant', 'doughnut': 'Choc. doughnut', 'cake': 'Berry cake'}
RECIPES = (
    dict(name='Rainy-day latte', customer='Mila', vessel='mug', beans='medium', milk='whole', ice=False, syrup='none', straw='none', pastry='croissant'),
    dict(name='Iced vanilla oat', customer='Theo', vessel='tall', beans='light', milk='oat', ice=True, syrup='vanilla', straw='paper', pastry='none'),
    dict(name='Little espresso', customer='Jun', vessel='demitasse', beans='dark', milk='none', ice=False, syrup='none', straw='none', pastry='doughnut'),
    dict(name='Caramel on ice', customer='Ada', vessel='rocks', beans='medium', milk='whole', ice=True, syrup='caramel', straw='steel', pastry='cake'),
    dict(name='Cloud cappuccino', customer='Noor', vessel='mug', beans='dark', milk='foam', ice=False, syrup='none', straw='none', pastry='none'),
    dict(name='Chocolate comfort', customer='Leo', vessel='mug', beans='medium', milk='whole', ice=False, syrup='chocolate', straw='none', pastry='croissant'),
)
CHOICES = {'vessel': VESSELS, 'beans': BEANS, 'milk': MILKS, 'syrup': SYRUPS, 'straw': STRAWS, 'pastry': PASTRIES}


@dataclass
class Coffee:
    vessel: str = ''
    beans: str = ''
    grind: float = 0.0
    grind_size: str = 'fine'
    tamp_pressure: float = 0.0
    tamp_quality: bool = False
    tamped: bool = False
    brew: float = 0.0
    milk: str = 'none'
    ice: bool = False
    syrup: str = 'none'
    straw: str = 'none'
    pastry: str = 'none'
    stage: int = 0
    served: int = 0
    earnings: int = 0
    order_index: int = 0
    rating: int = 0
    result: str = ''

    @property
    def order(self) -> dict:
        return RECIPES[self.order_index % len(RECIPES)]

    def choose(self, kind: str, value: str) -> bool:
        if kind not in CHOICES or value not in CHOICES[kind]:
            return False
        if kind == 'vessel' and self.stage == 0:
            self.vessel = value
        elif kind == 'beans' and self.stage == 1:
            self.beans = value
        elif kind in ('milk', 'syrup', 'straw', 'pastry') and self.stage == 4:
            setattr(self, kind, value)
        else:
            return False
        return True

    def next_step(self) -> bool:
        if (self.stage == 0 and self.vessel) or (self.stage == 1 and self.beans):
            self.stage += 1
            return True
        return False

    def work(self, dt: float, action: str) -> None:
        """Progress only while the player holds the machine control."""
        dt = max(0.0, min(dt, 0.1))
        if self.stage == 2 and action == 'grind' and self.grind < 1:
            self.grind = min(1.0, self.grind + dt / 2.0)
        elif self.stage == 2 and action == 'tamp' and self.grind >= 1:
            self.tamp_pressure = min(1.0, self.tamp_pressure + dt / 1.8)
        elif self.stage == 3 and action == 'brew' and self.tamped:
            self.brew = min(1.0, self.brew + dt / 4.0)
            if self.brew >= 1:
                self.stage = 4

    def release(self, action: str) -> None:
        if self.stage == 2 and action == 'tamp' and self.tamp_pressure > 0:
            self.tamped = True
            self.tamp_quality = 0.55 <= self.tamp_pressure <= 0.8
            self.stage = 3
        elif self.stage == 3 and action == 'brew' and self.brew >= 0.15:
            self.stage = 4

    def serve(self) -> bool:
        if self.stage != 4 or self.brew < 0.15:
            return False
        mismatches = [key for key in (*CHOICES, 'ice') if getattr(self, key) != self.order[key]]
        prep = []
        if self.grind_size != 'fine':
            prep.append('use a fine grind')
        if not self.tamp_quality:
            prep.append('tamp in the green zone')
        if not 32 <= self.brew * 48 <= 40:
            prep.append('stop the shot at 32-40g')
        self.rating = max(1, 5 - len(mismatches) - len(prep))
        if not mismatches and not prep:
            self.result = 'Exactly what I needed. Thank you!'
        else:
            labels = {'vessel': 'cup', 'beans': 'roast', 'milk': 'milk', 'ice': 'ice', 'syrup': 'syrup', 'straw': 'straw', 'pastry': 'pastry'}
            notes = [labels[k] for k in mismatches] + prep
            self.result = 'Next time: ' + ', '.join(notes) + '.'
        self.served += 1
        self.earnings += 3 + self.rating
        self.stage = 5
        return True

    def reset_drink(self, *, next_order: bool = False) -> None:
        fresh = Coffee(served=self.served, earnings=self.earnings,
                       order_index=self.order_index + int(next_order))
        self.__dict__.update(fresh.__dict__)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict) -> Coffee:
        """Reject damaged saves instead of creating impossible preparation states."""
        if not isinstance(raw, dict):
            raise ValueError('coffee must be an object')
        values = {}
        for field in fields(cls):
            value = raw.get(field.name, field.default)
            if type(value) is not type(field.default):
                # JSON encoders may write completed progress as 1 instead of 1.0.
                if isinstance(field.default, float) and type(value) in (int, float):
                    value = float(value)
                else:
                    raise ValueError('invalid ' + field.name)
            values[field.name] = value
        coffee = cls(**values)
        for key, options in CHOICES.items():
            if getattr(coffee, key) not in options and not (key in ('vessel', 'beans') and getattr(coffee, key) == ''):
                raise ValueError('unknown ' + key)
        if not 0 <= coffee.stage <= 5 or not 0 <= coffee.rating <= 5:
            raise ValueError('invalid stage or rating')
        if coffee.grind_size not in ('fine', 'medium', 'coarse'):
            raise ValueError('invalid grind size')
        if any(not math.isfinite(v) or not 0 <= v <= 1 for v in (coffee.grind, coffee.brew, coffee.tamp_pressure)):
            raise ValueError('invalid progress')
        if min(coffee.served, coffee.earnings, coffee.order_index) < 0:
            raise ValueError('invalid totals')
        if (coffee.stage >= 1 and not coffee.vessel) or (coffee.stage >= 2 and not coffee.beans):
            raise ValueError('missing supplies')
        if (coffee.stage >= 3 and (coffee.grind < 1 or not coffee.tamped)) or (coffee.stage >= 4 and coffee.brew < 0.15):
            raise ValueError('unfinished preparation')
        return coffee
