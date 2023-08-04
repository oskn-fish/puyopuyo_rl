import pygame
import sys

pygame.init()

COL_BLAC = pygame.Color((0, 0, 0))
DISPLAY_SIZE = (400, 600)
DISPLAY = pygame.display.set_mode(DISPLAY_SIZE)
CLOCK = pygame.time.Clock()

class Puyo(pygame.sprite.Sprite):
    to_img = ({"red":"./img/0_0.png", 
               "green":"./img/0_1.png", 
               "blue":"./img/0_2.png", 
               "yellow":"./img/0_3.png", 
               "purple":"./img/0_4.png"})
    def __init__(self, color: str) -> None:
        super().__init__()
        self.image = pygame.image.load(Puyo.to_img[color])
        self.rect = self.image.get_rect()
        self.rect.center = (DISPLAY_SIZE[0]/2, DISPLAY_SIZE[1]/2)
        
    def draw(self, surface: pygame.Surface) -> None:
        # pygame.Surface.blit(drawing_surface, destination_surface)
        surface.blit(self.image, self.rect)
        

def main():
    
    CLOCK.tick(60)
    puyo = Puyo("red")
    
    # DISPLAYSURF = pygame.display.set_mode(DISPLAY_SIZE)
    
    while True:
        # catch events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Simply using sys.exit() can cause your IDE to hang due to a common bug. 
                pygame.quit()
                sys.exit()
        # render 
        puyo.draw(DISPLAY)
        
        
        pygame.display.update()
    

if __name__ == "__main__":
    main()