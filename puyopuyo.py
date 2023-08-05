import pygame
import sys
from pygame.locals import *
import random

pygame.init()

IMG_WIDTH = IMG_HEIGHT = 32
BLACK = pygame.Color((0, 0, 0))
FALL_SPEED = 3
COLORS = ["red", "green", "blue", "purple", "yellow"]

display_size = (IMG_WIDTH*6, IMG_HEIGHT*(12+1+3))
display = pygame.display.set_mode(display_size)
clock = pygame.time.Clock()

outlet_position = (2*IMG_WIDTH+IMG_WIDTH//2, display.get_height()-11*IMG_HEIGHT-IMG_HEIGHT//2)
above_outlet = (2*IMG_WIDTH+IMG_WIDTH//2, display.get_height()-12*IMG_HEIGHT-IMG_HEIGHT//2)

landed_sprites = pygame.sprite.Group()

game_ended = pygame.event.custom_type()


pygame.key.set_repeat(100000,1000)


pygame.display.set_caption("puyopuyo")

# multiple puyos

# user defined events
# sprites group
# sprite collision
# move sprites in the group

class FallingPuyos(pygame.sprite.Sprite):
    def __init__(self, display: pygame.surface):
        self.display = display
        # self.puyos = [Puyo(self.display, outlet_position, random.choice(COLORS)), Puyo(self.display, above_outlet, random.choice(COLORS))]
        self.reset_puyos()
        
    def reset_puyos(self):
        self.puyos = [Puyo(self.display, outlet_position, random.choice(COLORS)), Puyo(self.display, above_outlet, random.choice(COLORS))]
        # self.landed = False
    
    def fall(self):
        for puyo in self.puyos:
            puyo.fall()
    
    def update(self):
        for puyo in self.puyos:
            puyo.update()
        #   0: sita 1:ue
        if landed_sprites.has(self.puyos[0]): # 1 -> shitamushi 0 -> ue kieru
            landed_sprites.add(self.puyos[1])
            self.reset_puyos()
        elif landed_sprites.has(self.puyos[1]):
            landed_sprites.add(self.puyos[0])
            # self.landed = True
            self.reset_puyos()
    
    def draw(self):
        for puyo in self.puyos:
            puyo.draw()


# single puyo
class Puyo(pygame.sprite.Sprite):
    to_img = ({"red":"./img/0_0.png", 
               "green":"./img/0_1.png", 
               "blue":"./img/0_2.png", 
               "yellow":"./img/0_3.png", 
               "purple":"./img/0_4.png"})
    def __init__(self, display: pygame.surface, center: tuple, color: str) -> None:
        super().__init__()
        self.display = display
        self.image = pygame.image.load(Puyo.to_img[color])
        self.rect = self.image.get_rect(center = center)
        self.landed = False
        
    def fall(self) -> None:
        # if not self.landed and self.rect.bottom < self.display.get_height():
        if self.rect.bottom < self.display.get_height():
            self.rect.move_ip(0, FALL_SPEED)
        else:
            # self.landed = True
            landed_sprites.add(self)
        
    def update(self) -> None:
        # if not self.landed:
        self.fall()
        
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT] and self.rect.left>IMG_WIDTH//2:
            movable = True
            candidate = self.rect.move(-32, 0)
            for puyo in landed_sprites:
                if pygame.Rect.colliderect(puyo.rect, candidate):
                    movable = False
            if movable:
                self.rect.move_ip(-32, 0)
        if pressed_keys[K_RIGHT]and self.rect.right<self.display.get_width()-IMG_WIDTH//2:
            movable = True
            candidate = self.rect.move(32, 0)
            for puyo in landed_sprites:
                if pygame.Rect.colliderect(puyo.rect, candidate):
                    movable = False
            if movable:
                self.rect.move_ip(32, 0)

        if pygame.sprite.spritecollideany(self, landed_sprites):
            # self.landed = True
            landed_sprites.add(self)
        
    def draw(self) -> None:
        # pygame.Surface.blit(drawing_surface, destination_surface)
        self.display.blit(self.image, self.rect)

# def draw_grid(surface: pygame.surface) -> None:
#     for i in range(1,6):
#         pygame.draw.line(surface, BLACK, (i*IMG_WIDTH, surface.get_height()-12*IMG_HEIGHT), (i*IMG_WIDTH, surface.get_height()))
#     for i in range(1,13):
#         pygame.draw.line(surface, BLACK, (0, surface.get_height()-i*IMG_HEIGHT), (surface.get_width(), surface.get_height()-i*IMG_HEIGHT))

class Window():
    def __init__(self, display: pygame.surface):
        self.display = display
        self.left_surface = pygame.Surface((IMG_WIDTH, 2*IMG_HEIGHT))
        self.left_surface.fill((255, 255, 255))
        self.left_rect = self.left_surface.get_rect(topright=(display.get_width()-3*IMG_WIDTH//2, 3*IMG_HEIGHT//2))
        self.right_surface = pygame.Surface((IMG_WIDTH, 2*IMG_HEIGHT))
        self.right_surface.fill((255, 255, 255))
        self.right_rect = self.right_surface.get_rect(topright=(display.get_width()-IMG_WIDTH//2, IMG_HEIGHT//2))

    def draw(self):
        self.display.blit(self.left_surface, self.left_rect)
        self.display.blit(self.right_surface, self.right_rect)


class Frame():
    def __init__(self, surface: pygame.surface):
        self.surface = surface
        self.rect = pygame.Rect((0,0), (self.surface.get_width(), self.surface.get_height()-12*IMG_HEIGHT))

    def draw(self) -> None:
        pygame.draw.rect(self.surface, BLACK, self.rect)
        
class Batsu(pygame.sprite.Sprite):
    def __init__(self, surface: pygame.surface):
        super().__init__()
        self.surface = surface
        self.image = pygame.image.load("./img/batsu_32.png")
        self.rect = self.image.get_rect(center=(2*IMG_WIDTH+IMG_WIDTH//2, self.surface.get_height()-11*IMG_HEIGHT-IMG_HEIGHT//2))
        
    def update(self):
        if pygame.sprite.spritecollideany(self, landed_sprites):
            end_event = pygame.event.Event(game_ended)
            pygame.event.post(end_event)
        
    def draw(self):
        self.surface.blit(self.image, self.rect)

def main():
    falling_puyos = FallingPuyos(display)
    # all_sprites.add(falling_puyos.puyos[0], falling_puyos.puyos[1])
    
    frame = Frame(display)
    batsu = Batsu(display)
    window = Window(display)
    
    keep_update = True
    
    while True:
        # catch events
        for event in pygame.event.get():
            if event.type == QUIT:
                # Simply using sys.exit() can cause your IDE to hang due to a common bug. 
                pygame.quit()
                sys.exit()
            elif event.type == game_ended:
                keep_update = False
                
        # initiate canvas
        display.fill("white")
        
        # update display
        batsu.update()
        if keep_update:
            falling_puyos.update()
        
        # draw
        batsu.draw()
        frame.draw()
        window.draw()
        falling_puyos.draw()
        landed_sprites.draw(display)
        
        # render
        pygame.display.update()
        clock.tick(60)
    

if __name__ == "__main__":
    main()