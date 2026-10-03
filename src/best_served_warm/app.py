"""Pygame application: menu, first playable cafe day, and options."""
import math
import pygame
from .art import AnimatedButton, load_image
from .music import Music
from .visualizer import Visualizer
from .storage import DRINKS, load_game, load_options, new_game, save_game, save_options

WIDTH, HEIGHT = 1280, 720
INK = (89, 47, 30)
CREAM = (255, 239, 213)
AMBER = (184, 91, 53)


def label(surface, font, value, center, color=INK):
    text = font.render(value, True, color)
    surface.blit(text, text.get_rect(center=center))


class App:
    def __init__(self):
        pygame.init()
        self.options = load_options()
        flags = pygame.RESIZABLE | (pygame.FULLSCREEN if self.options["fullscreen"] else 0)
        self.window = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        pygame.display.set_caption("Best Served Warm")
        self.canvas = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("georgia", 30)
        self.small = pygame.font.SysFont("georgia", 23)
        self.big = pygame.font.SysFont("georgia", 48, bold=True)
        self.background = pygame.transform.smoothscale(load_image("images", "background.png"), (WIDTH, HEIGHT))
        logo = load_image("images", "logo.png")
        self.logo = pygame.transform.smoothscale(logo, (600, round(logo.get_height()*600/logo.get_width())))
        self.buttons = {
            "new": AnimatedButton("new-game", (640, 286)),
            "load": AnimatedButton("load-game", (640, 382)),
            "options": AnimatedButton("options", (640, 478)),
            "exit": AnimatedButton("exit-game", (640, 574)),
        }
        self.music = Music()
        self.music.set_volume(self.options["volume"])
        self.visualizer = Visualizer()
        self.state = "menu"
        self.game = None
        self.message = ""
        self.message_until = 0.0
        self.elapsed = 0.0
        self.running = True

    def notify(self, message: str):
        self.message = message
        self.message_until = self.elapsed + 3

    def pointer(self, screen_pos):
        ww, wh = self.window.get_size()
        scale = min(ww/WIDTH, wh/HEIGHT)
        ox, oy = (ww-WIDTH*scale)/2, (wh-HEIGHT*scale)/2
        return ((screen_pos[0]-ox)/scale, (screen_pos[1]-oy)/scale)

    def click(self, pos):
        x,y = pos
        if self.state == "menu":
            for action, button in self.buttons.items():
                if button.rect.collidepoint(x,y):
                    if action == "new":
                        self.game = new_game();self.state = "game"
                    elif action == "load":
                        self.game = load_game()
                        if self.game is None:self.notify("No saved game yet. Choose New Game.")
                        else:self.state = "game"
                    elif action == "options":self.state = "options"
                    else:self.running = False
                    return
        elif self.state == "options":
            if pygame.Rect(360,275,560,75).collidepoint(x,y):
                self.options["volume"] = round(max(0,min(1,(x-420)/440)),2)
                self.music.set_volume(self.options["volume"])
            elif pygame.Rect(360,360,560,75).collidepoint(x,y):
                self.options["visualizer"] = not self.options["visualizer"]
            elif pygame.Rect(360,450,560,75).collidepoint(x,y):
                self.options["fullscreen"] = not self.options["fullscreen"]
                flags = pygame.RESIZABLE | (pygame.FULLSCREEN if self.options["fullscreen"] else 0)
                self.window = pygame.display.set_mode((WIDTH,HEIGHT),flags)
            elif pygame.Rect(480,580,320,64).collidepoint(x,y):
                save_options(self.options);self.state="menu"
        elif self.state == "game":
            if pygame.Rect(60,46,220,60).collidepoint(x,y):
                save_game(self.game);self.state="menu"
            for index, drink in enumerate(DRINKS):
                if pygame.Rect(280+index*250,360,220,95).collidepoint(x,y):
                    self.game["selected"]=drink
            if pygame.Rect(475,500,330,90).collidepoint(x,y):
                self.game["score"]+=10
                self.game["served"]+=1
                self.game["day"]=1+self.game["served"]//5
                save_game(self.game)
                self.notify(f"One warm {self.game['selected'].lower()} served!")

    def panel(self, rect, fill=(255,238,210,225)):
        box = pygame.Surface((rect.width,rect.height),pygame.SRCALPHA)
        pygame.draw.rect(box,fill,box.get_rect(),border_radius=24)
        pygame.draw.rect(box,(110,62,41,230),box.get_rect(),width=4,border_radius=24)
        self.canvas.blit(box,rect.topleft)

    def draw_menu(self):
        self.canvas.blit(self.logo,self.logo.get_rect(center=(640,106)))
        mouse = self.pointer(pygame.mouse.get_pos())
        for button in self.buttons.values():
            button.draw(self.canvas,self.elapsed,button.rect.collidepoint(mouse))
        label(self.canvas,self.small,"A small cafe, a warm cup, a quiet moment.",(640,662))
        label(self.canvas,self.small,"Music: Moon Unit / HoliznaCC0 (CC0)",(640,695))

    def draw_options(self):
        self.panel(pygame.Rect(310,150,660,520))
        label(self.canvas,self.big,"Options",(640,220))
        label(self.canvas,self.font,f"Music volume   {round(self.options['volume']*100)}%",(640,310))
        pygame.draw.line(self.canvas,INK,(420,345),(860,345),6)
        pygame.draw.circle(self.canvas,AMBER,(420+round(440*self.options["volume"]),345),15)
        label(self.canvas,self.font,"Visualizer: " + ("On" if self.options["visualizer"] else "Off"),(640,405))
        label(self.canvas,self.font,"Fullscreen: " + ("On" if self.options["fullscreen"] else "Off"),(640,495))
        self.panel(pygame.Rect(480,580,320,64))
        label(self.canvas,self.font,"Save & Back",(640,612))

    def draw_game(self):
        self.panel(pygame.Rect(45,36,1190,610))
        self.panel(pygame.Rect(60,46,220,60));label(self.canvas,self.small,"Save & Menu",(170,76))
        label(self.canvas,self.big,"A warm order",(640,167))
        label(self.canvas,self.font,f"Day {self.game['day']}  -  Cups served {self.game['served']}  -  Score {self.game['score']}",(640,232))
        label(self.canvas,self.font,"Choose a drink, then serve it:",(640,300))
        for index,drink in enumerate(DRINKS):
            rect=pygame.Rect(280+index*250,360,220,95)
            self.panel(rect,(255,222,177,245) if drink==self.game["selected"] else (255,238,210,225))
            label(self.canvas,self.font,drink,rect.center)
        self.panel(pygame.Rect(475,500,330,90),(255,222,177,245))
        label(self.canvas,self.font,"Serve warm  +10",(640,545))

    def draw(self):
        self.canvas.blit(self.background,(0,0))
        if self.state=="menu":self.draw_menu()
        elif self.state=="options":self.draw_options()
        else:self.draw_game()
        if self.state=="menu":
            self.visualizer.draw(self.canvas,907,640,self.elapsed,self.options["visualizer"])
        if self.message and self.elapsed<self.message_until:
            label(self.canvas,self.small,self.message,(640,660))
        if self.elapsed<2.0:
            veil=pygame.Surface((WIDTH,HEIGHT));veil.fill((32,17,13));veil.set_alpha(round(255*(1-self.elapsed/2)**2));self.canvas.blit(veil,(0,0))
        ww,wh=self.window.get_size();scale=min(ww/WIDTH,wh/HEIGHT)
        w,h=round(WIDTH*scale),round(HEIGHT*scale)
        self.window.fill((35,19,13))
        self.window.blit(pygame.transform.smoothscale(self.canvas,(w,h)),((ww-w)//2,(wh-h)//2))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt=min(self.clock.tick(60)/1000,0.1);self.elapsed+=dt
            for event in pygame.event.get():
                if event.type==pygame.QUIT:self.running=False
                elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:self.click(self.pointer(event.pos))
                elif event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:
                        if self.state=="menu":self.running=False
                        elif self.state=="game":save_game(self.game);self.state="menu"
                        else:save_options(self.options);self.state="menu"
            self.visualizer.update(self.music.levels(),dt)
            self.draw()
        self.music.close();pygame.quit()


def main():
    App().run()
