"""Temporary station layout for exercising mechanics before final scene art arrives."""
import textwrap
import pygame
from .paths import asset_path
from .workbench import Workbench, SIZE, INK, PAPER, CREAM, SAGE, MUTED, PALE
from .stations import STATIONS, STATION_NAMES, StationError
from .coffee import VESSELS, BEANS, SYRUPS, STRAWS, PASTRIES, MILKS

class StationView(Workbench):
    def __init__(self, app):
        super().__init__(app)
        self.station='shelf'
        for path in asset_path('cups').glob('*.png'):
            self.sprites[path.stem] = pygame.image.load(str(path)).convert_alpha()
        self.note='Click an item to carry it; click a station to put it down.'

    @property
    def kitchen(self): return self.app.kitchen

    def cancel_hold(self):
        self.holding=None
        self.kitchen.suspend()

    def release(self):
        if self.holding:
            self.kitchen.end()
        self.holding=None

    def update(self, dt, pointer):
        self.time+=dt
        if self.holding:
            rect=next((r for action,r in self.controls if action=='hold:'+self.holding),None)
            if rect and rect.collidepoint(pointer): self.kitchen.update(dt)
        target=self.target(pointer)
        if target and target!=self.hovered: self.app.sfx.play('hover')
        self.hovered=target

    def press(self, point):
        action=self.target(point)
        if not action: return
        k=self.kitchen
        self.app.sfx.play('click')
        try:
            if action=='pause':
                self.cancel_hold(); self.app.paused_from='coffee'; self.app.state='pause'; self.app.message=''; return
            kind,_,value=action.partition(':')
            if kind=='station':
                self.station=value
                if k.carrying: k.place(value)
            elif kind=='pick': k.pickup(value)
            elif kind=='cup': k.take_cup(value)
            elif kind=='hold': k.begin(value); self.holding=value
            elif kind=='beans':
                keys=list(BEANS); k.select_beans(keys[(keys.index(k.filter.beans)+1)%len(keys)])
            elif kind=='size':
                keys=['fine','medium','coarse']; k.select_beans(k.filter.beans,keys[(keys.index(k.filter.grind_size)+1)%3])
            elif kind=='fill': k.fill_milk(value)
            elif kind=='pour': k.pour_milk(value=='foam')
            elif kind=='add':
                cup=k.cup_at('finish'); k.require(cup is not None,'Put a cup at the finishing station.')
                if value=='ice': k.add('ice',not cup.drink.ice)
                else:
                    options=list({'syrup':SYRUPS,'straw':STRAWS,'pastry':PASTRIES}[value]); current=getattr(cup.drink,value)
                    k.add(value,options[(options.index(current)+1)%len(options)])
            elif kind=='rinse': k.rinse(value)
            elif kind=='serve': k.serve()
            self.note=k.feedback if kind=='serve' else 'Pick up items to move them. Hold machine controls to work.'
        except StationError as exc:
            self.note=str(exc)

    def actions(self):
        k=self.kitchen; f=k.filter; p=k.pitcher
        if self.station=='shelf': return [('cup:'+v,label) for v,label in VESSELS.items()]
        if self.station=='grinder': return [('beans:',BEANS[f.beans]),('size:','Grind: '+f.grind_size),('hold:grind','Hold to grind')]
        if self.station=='tamp': return [('hold:tamp','Hold to tamp')]
        if self.station=='espresso': return [('hold:brew','Hold to brew')]
        if self.station=='milk': return [('fill:whole','Whole milk'),('fill:oat','Oat milk'),('hold:steam','Hold to steam'),('pour:milk','Pour milk'),('pour:foam','Pour foam')]
        if self.station=='finish':
            cup=k.cup_at('finish'); d=cup.drink if cup else None
            return [('add:ice','Ice: '+('yes' if d and d.ice else 'no')),('add:syrup',SYRUPS[d.syrup] if d else 'Syrup'),('add:straw',STRAWS[d.straw] if d else 'Straw'),('add:pastry',PASTRIES[d.pastry] if d else 'Pastry')]
        if self.station=='serve': return [('serve:','Serve drink')]
        return [('rinse:'+key,'Discard drink' if key in k.cups else 'Rinse '+key) for key in ('filter','pitcher',*k.cups) if k.item(key).location=='sink']

    def draw(self, pointer):
        k=self.kitchen; self.controls=[]; s=self.surface; s.fill((219,200,165))
        pygame.draw.rect(s,SAGE,(0,0,640,35))
        self.text('BEST SERVED WARM',16,18,title=True,color=PAPER)
        self.text(f'{k.served} served / {k.earnings} coins',387,18,color=PAPER)
        self.button('pause',(554,7,72,21),'PAUSE Esc',pointer)
        self.panel((12,48,151,243))
        self.text('ORDER %02d'%(k.order_index+1),24,64,color=SAGE)
        self.text(k.order['customer'],24,85,title=True)
        self.text(k.order['name'],24,108)
        order=k.order
        for i,label in enumerate([VESSELS[order['vessel']],BEANS[order['beans']],MILKS[order['milk']], 'With ice' if order['ice'] else 'Served hot', SYRUPS[order['syrup']],STRAWS[order['straw']],PASTRIES[order['pastry']]]):
            self.text(label,24,137+i*19)
        self.text('STATION PROTOTYPE',181,47,color=SAGE)
        for i,name in enumerate(STATIONS):
            r=pygame.Rect(180+i%4*112,59+i//4*94,102,83)
            self.panel(r, PALE if self.station==name else PAPER)
            self.controls.append(('station:'+name,r))
            self.text(STATION_NAMES[name],r.centerx,r.y+12,center=True)
            items=[key for key in ('filter','pitcher',*k.cups) if k.item(key).location==name]
            for n,key in enumerate(items):
                icon=(f'{k.cups[key].style}_{k.cups[key].size.lower()}' if k.cups[key].style else k.cups[key].drink.vessel) if key in k.cups else 'portafilter' if key=='filter' else 'milk_foam'
                cx=r.x+22+n*32; cy=r.y+40
                self.icon(icon,(cx,cy))
                self.controls.append(('pick:'+key,pygame.Rect(cx-15,cy-16,30,34)))
                if key=='filter': detail='Used' if k.filter.dirty else f'{k.filter.dose:.0f}g'
                elif key=='pitcher': detail='Rinse' if k.pitcher.dirty else k.pitcher.milk
                else: detail='Coffee' if k.cups[key].drink.brew else 'Empty'
                self.text(detail,cx,r.y+67,center=True,color=MUTED)
        self.panel((180,250,438,65))
        self.text(STATION_NAMES[self.station],190,260,color=SAGE)
        for i,(action,label) in enumerate(self.actions()):
            self.button(action,(190+i%3*139,270+i//3*21,132,18),label,pointer)
        if k.carrying:
            key=k.carrying
            self.text('Carrying: '+('cup' if key in k.cups else key),24,308,color=SAGE)
        else: self.text('Hands free',24,308,color=MUTED)
        metric={'grinder':f'Dose {k.filter.dose:.1f}g / aim 17-19g',
                'tamp':f'Pressure {k.filter.pressure:.0%} / aim 55-80%',
                'espresso':f'Yield {(k.cup_at("espresso").drink.brew*48 if k.cup_at("espresso") else 0):.0f}g / aim 32-40g',
                'milk':f'Milk {k.pitcher.temperature:.0f}C / aim 55-65C'}
        if self.station in metric: self.text(metric[self.station],350,260,color=INK)
        for i,line in enumerate(textwrap.wrap(self.note,99)[:2]): self.text(line,15,333+i*13)
        pygame.transform.scale(s,self.app.window.get_size(),self.app.window)
