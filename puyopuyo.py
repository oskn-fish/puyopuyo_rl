import pygame
import sys
from pygame.locals import *

pygame.init()

IMG_WIDTH = IMG_HEIGHT = 32
BLACK = pygame.Color((0, 0, 0))
DISPLAY_SIZE = (IMG_WIDTH*6, IMG_WIDTH*(12+1+3))
DISPLAY = pygame.display.set_mode(DISPLAY_SIZE)
CLOCK = pygame.time.Clock()
pygame.key.set_repeat(100000,1000)


pygame.display.set_caption("puyopuyo")

# multiple puyos

# user defined events
# sprites group
# sprite collision
# move sprites in the group


# single puyo
class Puyo(pygame.sprite.Sprite):
    to_img = ({"red":"./img/0_0.png", 
               "green":"./img/0_1.png", 
               "blue":"./img/0_2.png", 
               "yellow":"./img/0_3.png", 
               "purple":"./img/0_4.png"})
    def __init__(self, color: str, surface: pygame.surface) -> None:
        super().__init__()
        self.image = pygame.image.load(Puyo.to_img[color])
        self.rect = self.image.get_rect(center = (2*IMG_WIDTH+IMG_WIDTH//2, self.image.get_height()//2))
        self.surface = surface
    
    def fall(self) -> None:
        if self.rect.bottom < self.surface.get_height():
            self.rect.move_ip(0, 5)
        
    def update(self):
        self.fall()
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT] and self.rect.left>IMG_WIDTH//2:
            self.rect.move_ip(-32, 0)
        if pressed_keys[K_RIGHT]and self.rect.right<self.surface.get_width()-IMG_WIDTH//2:
            self.rect.move_ip(32, 0)
        # pass
        
    def draw(self) -> None:
        # pygame.Surface.blit(drawing_surface, destination_surface)
        self.surface.blit(self.image, self.rect)

def draw_grid(surface: pygame.surface) -> None:
    for i in range(1,6):
        pygame.draw.line(surface, BLACK, (i*IMG_WIDTH, 0), (i*IMG_WIDTH, surface.get_height()))
    

def main():
    puyo = Puyo("red", DISPLAY)
    
    
    while True:
        # catch events
        for event in pygame.event.get():
            if event.type == QUIT:
                # Simply using sys.exit() can cause your IDE to hang due to a common bug. 
                pygame.quit()
                sys.exit()
                
        # update display
        DISPLAY.fill("white")
        draw_grid(DISPLAY)
        # puyo.fall()
        puyo.update()
        puyo.draw()
        
        # render
        pygame.display.update()
        CLOCK.tick(60)
    

if __name__ == "__main__":
    main()