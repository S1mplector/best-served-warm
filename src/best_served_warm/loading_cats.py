"""A little cat playground for loading transitions, animated at native resolution."""
from dataclasses import dataclass
import math
import random
import pygame
from .art import load_image

@dataclass
class Cat:
    x: float
    feet: float
    coat: int
    state: str
    timer: float
    facing: int = 1
    target: float = 100.0
    age: float = 0.0
    partner: int = -1

class LoadingCats:
    def __init__(self, seed=None):
        self.rng=random.Random(seed)
        self.age=0.0
        self.cats=[Cat(35,69,0,'chase',5,partner=1), Cat(74,69,1,'run',5,target=157),
                   Cat(143,84,2,'sleep',7), Cat(58,84,3,'play',4)]
        walk=load_image('cat','grey-walk.png')
        rest=load_image('cat','grey-rest.png')
        self.walk=[]; self.rest=[]
        self.sleep=[]
        coats=[(174,177,183),(212,153,93),(240,225,198),(115,126,139)]
        for coat in coats:
            frames=[]; rests=[]
            for source,dest in ((walk,frames),(rest,rests)):
                for n in range(4):
                    frame=source.subsurface((n*16,0,16,16)).copy()
                    for y in range(16):
                        for x in range(16):
                            r,g,b,a=frame.get_at((x,y))
                            if a and max(r,g,b)>75:
                                factor=(r+g+b)/3/200
                                frame.set_at((x,y),(*[min(255,round(c*factor)) for c in coat],a))
                    dest.append(frame)
            self.walk.append(frames); self.rest.append(rests)
            sleeper=load_image('cat','white-sleep.png').copy()
            for y in range(16):
                for x in range(16):
                    r,g,b,a=sleeper.get_at((x,y))
                    if a and max(r,g,b)>75:
                        factor=(r+g+b)/3/230
                        sleeper.set_at((x,y),(*[min(255,round(v*factor)) for v in coat],a))
            self.sleep.append(sleeper)

    def update(self, dt):
        dt=max(0,min(dt,.1)); self.age+=dt
        for i,c in enumerate(self.cats):
            c.age+=dt; c.timer-=dt
            if c.state=='sleep':
                if c.timer<=0: c.state='wake'; c.timer=.8
                continue
            if c.state=='wake':
                if c.timer<=0: c.state='run'; c.timer=self.rng.uniform(3,6); c.target=self.rng.uniform(15,177)
                continue
            if c.timer<=0:
                c.state=self.rng.choice(('run','play','sleep'))
                c.timer=self.rng.uniform(5,9) if c.state=='sleep' else self.rng.uniform(3,6)
                c.target=self.rng.uniform(15,177)
                continue
            if c.state in ('run','chase'):
                if c.state=='chase':
                    other=self.cats[c.partner]
                    c.target=max(12,min(180,other.x-other.facing*19))
                delta=c.target-c.x
                c.facing=1 if delta>=0 else -1
                c.x+=c.facing*min(abs(delta),dt*(30 if c.state=='chase' else 24))
                if abs(delta)<2 and c.state=='run': c.target=18 if c.x>96 else 173
            elif c.state=='play':
                c.facing=1 if math.sin(c.age*2)>0 else -1
        # Invite a nearby awake friend into a chase periodically.
        if int(self.age/8)!=int((self.age-dt)/8):
            awake=[i for i,c in enumerate(self.cats) if c.state not in ('sleep','wake')]
            if len(awake)>1:
                first,second=awake[:2]
                self.cats[first].state='chase'; self.cats[first].partner=second; self.cats[first].timer=5
                self.cats[second].state='run'; self.cats[second].timer=5

    def draw(self, surface):
        surface.fill((0,0,0))
        for c in sorted(self.cats,key=lambda c:c.feet):
            y=c.feet
            if c.state=='sleep':
                frame=self.sleep[c.coat]
            elif c.state=='wake':
                frame=self.rest[c.coat][min(3,max(0,int(c.timer*4)))]
            else:
                frame=self.walk[c.coat][int(c.age*(10 if c.state=='chase' else 7))%4]
                if c.state=='play':
                    y-=max(0,math.sin(c.age*5))*5
                if c.state=='chase': y-=max(0,math.sin(c.age*8))*2
            if c.facing>0: frame=pygame.transform.flip(frame,True,False)
            surface.blit(frame,(round(c.x)-8,round(y)-frame.get_bounding_rect().bottom))
            if c.state=='sleep':
                x=round(c.x)+5; y=round(c.feet)-13-int(c.age%2)
                pygame.draw.lines(surface,(224,198,158),False,[(x,y),(x+3,y),(x,y+3),(x+3,y+3)])
        for i in range(8):
            angle=i*math.pi/4
            brightness=235-((i-int(self.age*9))%8)*23
            pygame.draw.rect(surface,(brightness,brightness,brightness),
                             (round(96+6*math.cos(angle)),round(98+6*math.sin(angle)),2,2))
