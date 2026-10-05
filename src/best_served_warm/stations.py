"""Asset-independent station mechanics. A view only sends actions and draws state."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
import math
from .coffee import Coffee, VESSELS, BEANS, SYRUPS, STRAWS, PASTRIES

STATIONS = ('shelf', 'grinder', 'tamp', 'espresso', 'milk', 'finish', 'serve', 'sink')
STATION_NAMES = dict(zip(STATIONS, ('Cup shelf', 'Grinder', 'Tamp mat', 'Espresso', 'Milk station', 'Finishing', 'Serve', 'Sink')))
LOCATIONS = (*STATIONS, 'hand')
ALLOWED = {'cup': {'espresso', 'milk', 'finish', 'serve', 'sink'},
           'filter': {'grinder', 'tamp', 'espresso', 'sink'},
           'pitcher': {'milk', 'sink'}}

class StationError(ValueError):
    """A player-readable reason an action cannot currently happen."""

@dataclass
class Portafilter:
    location: str = 'grinder'
    beans: str = 'medium'
    grind_size: str = 'fine'
    dose: float = 0.0
    pressure: float = 0.0
    tamped: bool = False
    dirty: bool = False

@dataclass
class Pitcher:
    location: str = 'milk'
    milk: str = 'none'
    temperature: float = 20.0
    dirty: bool = False

@dataclass
class Cup:
    location: str
    drink: Coffee
    milk_temperature: float = 20.0
    style: str = ''
    size: str = ''

@dataclass
class Kitchen:
    cups: dict[str, Cup] = field(default_factory=dict)
    filter: Portafilter = field(default_factory=Portafilter)
    pitcher: Pitcher = field(default_factory=Pitcher)
    served: int = 0
    earnings: int = 0
    order_index: int = 0
    next_id: int = 1
    active: str = ''
    pending: str = ''
    feedback: str = 'Pick a cup. Move tools between stations.'

    @property
    def order(self):
        return Coffee(order_index=self.order_index).order

    def item(self, item_id):
        if item_id == 'filter': return self.filter
        if item_id == 'pitcher': return self.pitcher
        if item_id in self.cups: return self.cups[item_id]
        raise StationError('That item is no longer on the counter.')

    @property
    def carrying(self):
        return next((key for key in ('filter', 'pitcher', *self.cups) if self.item(key).location == 'hand'), None)

    def cup_at(self, station):
        return next((cup for cup in self.cups.values() if cup.location == station), None)

    def take_cup(self, vessel):
        self.require(vessel in VESSELS, 'Choose a known cup.')
        self.require(not self.carrying, 'Put down the item you are holding first.')
        self.require(len(self.cups) < 3, 'Serve or discard a drink to clear counter space.')
        key = 'cup_' + str(self.next_id)
        self.next_id += 1
        self.cups[key] = Cup('hand', Coffee(vessel=vessel))
        return key

    @staticmethod
    def require(ok, message):
        if not ok: raise StationError(message)

    def pickup(self, item_id):
        self.require(not self.active and not self.pending, 'Finish the paused machine action before moving tools.')
        self.require(not self.carrying, 'Put down the item you are holding first.')
        self.item(item_id).location = 'hand'

    def place(self, station):
        self.require(not self.active and not self.pending, 'Finish the machine action before moving items.')
        key = self.carrying
        self.require(key is not None, 'Pick up a cup or tool first.')
        kind = 'cup' if key in self.cups else key
        self.require(station in ALLOWED[kind], 'This item does not belong at that station.')
        if kind == 'cup':
            self.require(self.cup_at(station) is None, 'There is already a cup here.')
        self.item(key).location = station

    def select_beans(self, beans, grind_size=None):
        self.require(self.filter.location == 'grinder', 'Place the portafilter at the grinder.')
        self.require(not self.filter.dirty and self.filter.dose == 0, 'Rinse the portafilter before changing beans.')
        self.require(not self.active and not self.pending, 'Finish grinding first.')
        self.require(beans in BEANS, 'Choose a known roast.')
        self.require(grind_size is None or grind_size in ('fine','medium','coarse'), 'Choose a grind size.')
        self.filter.beans = beans
        if grind_size: self.filter.grind_size = grind_size

    def begin(self, action):
        self.require(not self.active, 'Finish the current action first.')
        if self.pending:
            self.require(action == self.pending, 'Resume the paused ' + self.pending + ' action first.')
            self.active, self.pending = action, ''
            return
        f = self.filter
        if action == 'grind':
            self.require(f.location == 'grinder' and not f.dirty and not f.tamped, 'Place a clean portafilter at the grinder.')
            self.require(f.dose < 22, 'The basket is full.')
        elif action == 'tamp':
            self.require(f.location == 'tamp' and f.dose > 0 and not f.dirty, 'Bring ground coffee to the tamp mat.')
            f.pressure = 0.0
        elif action == 'brew':
            cup = self.cup_at('espresso')
            self.require(f.location == 'espresso' and f.tamped and not f.dirty, 'Fit a freshly tamped portafilter to the machine.')
            self.require(cup is not None, 'Put a cup under the machine.')
            self.require(cup.drink.brew == 0, 'This cup already contains coffee.')
        elif action == 'steam':
            self.require(self.pitcher.location == 'milk' and self.pitcher.milk != 'none', 'Fill the pitcher at the milk station first.')
            self.require(not self.pitcher.dirty, 'Rinse the empty pitcher first.')
        else:
            raise StationError('Unknown station action.')
        self.active = action

    def suspend(self):
        if self.active:
            self.pending, self.active = self.active, ''

    def update(self, dt):
        if not math.isfinite(dt) or dt < 0: return
        dt = min(dt, .1)
        if self.active == 'grind': self.filter.dose = min(22.0, self.filter.dose + dt*7)
        elif self.active == 'tamp': self.filter.pressure = min(1.0, self.filter.pressure + dt/1.8)
        elif self.active == 'steam': self.pitcher.temperature = min(90.0, self.pitcher.temperature + dt*14)
        elif self.active == 'brew':
            cup = self.cup_at('espresso')
            cup.drink.brew = min(1.0, cup.drink.brew + dt/4)
            if cup.drink.brew >= 1: self.end()

    def end(self):
        action, self.active = self.active, ''
        f = self.filter
        if action == 'tamp' and f.pressure > 0: f.tamped = True
        if action == 'brew':
            d = self.cup_at('espresso').drink
            if d.brew > 0:
                d.beans = f.beans
                d.grind_size = f.grind_size
                d.grind = 1.0
                d.tamped = True
                d.tamp_quality = 17 <= f.dose <= 19 and .55 <= f.pressure <= .8
                d.stage = 4
                f.dirty = True
        return action

    def fill_milk(self, milk):
        p = self.pitcher
        self.require(p.location == 'milk' and not self.active and not self.pending, 'Put the pitcher at the milk station and finish the machine action.')
        self.require(p.milk == 'none' and not p.dirty, 'Empty and rinse the pitcher first.')
        self.require(milk in ('whole','oat'), 'Choose whole or oat milk.')
        p.milk, p.temperature = milk, 20.0

    def pour_milk(self, foam=False):
        p, cup = self.pitcher, self.cup_at('milk')
        self.require(not self.active and not self.pending, 'Finish steaming before pouring.')
        self.require(p.location == 'milk' and p.milk != 'none' and cup is not None, 'Bring the cup and a filled pitcher to the milk station.')
        self.require(cup.drink.milk == 'none', 'This cup already contains milk.')
        self.require(not foam or p.temperature >= 50, 'Steam the milk before adding foam.')
        cup.drink.milk = 'foam' if foam else p.milk
        # Scorched milk reduces preparation quality; cold milk is valid for iced drinks.
        cup.milk_temperature = p.temperature
        p.milk, p.dirty = 'none', True

    def add(self, kind, value):
        cup = self.cup_at('finish')
        self.require(cup is not None, 'Put a cup at the finishing station.')
        options = {'syrup': SYRUPS, 'straw': STRAWS, 'pastry': PASTRIES, 'ice': (True,False)}
        self.require(kind in options and value in options[kind], 'Choose a valid finishing ingredient.')
        setattr(cup.drink, kind, value)

    def rinse(self, item_id):
        self.require(not self.active and not self.pending, 'Finish the machine action first.')
        self.require(self.item(item_id).location == 'sink', 'Bring the item to the sink.')
        if item_id == 'filter': self.filter = Portafilter(location='sink',beans=self.filter.beans,grind_size=self.filter.grind_size)
        elif item_id == 'pitcher': self.pitcher = Pitcher(location='sink')
        else: del self.cups[item_id]

    def serve(self):
        cup = self.cup_at('serve')
        self.require(cup is not None and cup.drink.brew >= .15, 'Bring a brewed drink to the serving counter.')
        d = cup.drink
        d.order_index = self.order_index
        d.stage = 4
        d.serve()
        if d.milk != 'none' and (cup.milk_temperature > 75 or (not d.ice and cup.milk_temperature < 50)):
            d.rating = max(1,d.rating-1)
            d.result = 'Check the milk temperature; aim for 55-65C for hot drinks.'
        self.served += 1
        self.earnings += 3+d.rating
        self.order_index += 1
        self.feedback = f'{d.rating}/5 stars. ' + d.result
        key = next(k for k,v in self.cups.items() if v is cup)
        del self.cups[key]
        return d.rating

    def to_dict(self):
        # A held control is never replayed automatically on load.
        return dict(version=1, cups={k:dict(location=c.location,drink=c.drink.to_dict() | {'stage': 0},milk_temperature=c.milk_temperature,style=c.style,size=c.size) for k,c in self.cups.items()},
                    filter=asdict(self.filter),pitcher=asdict(self.pitcher),served=self.served,
                    earnings=self.earnings,order_index=self.order_index,next_id=self.next_id,feedback=self.feedback,
                    pending=self.active or self.pending)

    @classmethod
    def from_dict(cls, raw):
        if not isinstance(raw,dict) or raw.get('version') != 1: raise ValueError('invalid station save')
        k=cls()
        for name in ('served','earnings','order_index','next_id'):
            value=raw[name]
            if type(value) is not int or value<0: raise ValueError('invalid counter')
            setattr(k,name,value)
        k.filter=Portafilter(**raw['filter']); k.pitcher=Pitcher(**raw['pitcher'])
        f,p=k.filter,k.pitcher
        if f.beans not in BEANS or f.grind_size not in ('fine','medium','coarse') or p.milk not in ('none','whole','oat'): raise ValueError('invalid supplies')
        for value,limit in ((f.dose,22),(f.pressure,1),(p.temperature,90)):
            if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=limit: raise ValueError('invalid progress')
        if any(type(v) is not bool for v in (f.tamped,f.dirty,p.dirty)): raise ValueError('invalid tool state')
        if not isinstance(raw['cups'],dict) or len(raw['cups'])>3: raise ValueError('invalid cups')
        for key,value in raw['cups'].items():
            if not key.startswith('cup_') or not key[4:].isdigit() or int(key[4:])>=k.next_id: raise ValueError('invalid cup id')
            # Station drinks can be assembled in any order, unlike the legacy wizard.
            data=value['drink'].copy(); data['stage']=0
            drink=Coffee.from_dict(data)
            temperature=value.get('milk_temperature',20.0)
            if type(temperature) not in (int,float) or not math.isfinite(temperature) or not 0<=temperature<=90: raise ValueError('invalid milk temperature')
            style,size=value.get('style',''),value.get('size','')
            if (style,size)!=('','') and (style not in ('takeaway','cold','mug') or size not in ('S','M','L')):
                raise ValueError('invalid cup art')
            k.cups[key]=Cup(value['location'],drink,temperature,style,size)
        for key in ('filter','pitcher',*k.cups):
            location=k.item(key).location; kind='cup' if key in k.cups else key
            if location!='hand' and location not in ALLOWED[kind]: raise ValueError('invalid item location')
        if sum(k.item(key).location=='hand' for key in ('filter','pitcher',*k.cups))>1: raise ValueError('hands full')
        locations=[c.location for c in k.cups.values()]
        if len(locations)!=len(set(locations)): raise ValueError('occupied station')
        k.feedback=str(raw.get('feedback','Welcome back.'))[:200]
        pending=raw.get('pending','')
        if pending not in ('','grind','tamp','brew','steam'): raise ValueError('invalid paused action')
        if pending:
            expected={'grind':'grinder','tamp':'tamp','brew':'espresso','steam':'milk'}[pending]
            tool=p if pending=='steam' else f
            if tool.location!=expected or (pending=='brew' and k.cup_at('espresso') is None): raise ValueError('missing paused tool')
        k.pending=pending
        return k
