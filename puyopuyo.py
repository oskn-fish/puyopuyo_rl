import pygame
import sys
from pygame.locals import *
import random

pygame.init()

# constants for rendering
IMG_WIDTH = IMG_HEIGHT = 32
BLACK = pygame.Color((0, 0, 0))
WHITE = pygame.Color((255, 255, 255))
FALL_SPEED = 3
COLORS = ["red", "green", "blue", "purple", "yellow"]

WINDOW_UPPER_SPACE = IMG_HEIGHT//2
WINDOW_LOWER_SPACE = IMG_HEIGHT//2
WINDOW_RIGHT_SPACE = IMG_WIDTH//2
WINDOW_HEIGHT = 4*IMG_HEIGHT
LEFT_WINDOW_GAP = 2*IMG_HEIGHT

# singletons for game logic
display_size = (IMG_WIDTH*6, 12*IMG_HEIGHT+WINDOW_UPPER_SPACE+WINDOW_HEIGHT+WINDOW_LOWER_SPACE)
display = pygame.display.set_mode(display_size)
clock = pygame.time.Clock()

outlet_position = (2*IMG_WIDTH+IMG_WIDTH//2, display.get_height()-11*IMG_HEIGHT-IMG_HEIGHT//2)
above_outlet = (2*IMG_WIDTH+IMG_WIDTH//2, display.get_height()-12*IMG_HEIGHT-IMG_HEIGHT//2)

# sprite group
landed_sprites = pygame.sprite.Group()

# user defined evnets
puyo_landed = pygame.event.custom_type()
game_ended = pygame.event.custom_type()

pygame.display.set_caption("puyopuyo")


class Board():
    def __init__(self):
        self.list_board = [[" "]*6 for i in range(12)]
        self.puyos_queue = [[random.choice(COLORS), random.choice(COLORS)] for i in range(2)]


class FallingPuyos(pygame.sprite.Sprite):
    def __init__(self, display: pygame.surface, board: Board):
        self.display = display
        self.board = board
        self.reset_puyos()
        
    def reset_puyos(self):
        self.board.puyos_queue.append([random.choice(COLORS), random.choice(COLORS)])
        new_puyo_colors = self.board.puyos_queue.pop(0)
        self.puyos = [Puyo(self.display, outlet_position, new_puyo_colors[1]), Puyo(self.display, above_outlet, new_puyo_colors[0])]
        # self.puyos = [Puyo(self.display, outlet_position, random.choice(COLORS)), Puyo(self.display, above_outlet, random.choice(COLORS))]
        
        # self.landed = False
    
    def fall(self):
        for puyo in self.puyos:
            puyo.fall()
            
    def x_movable(self, dx):
        candidates = [self.puyos[i].rect.move(dx, 0) for i in range(2)]
        for candidate in candidates:
            if candidate.left<0 or candidate.right>self.display.get_width():
                return False
            for puyo in landed_sprites:
                if pygame.Rect.colliderect(puyo.rect, candidate):
                    return False
        return True
    
    def y_movable(self, dy):
        candidates = [self.puyos[i].rect.move(0, dy) for i in range(2)]
        for candidate in candidates:
            if candidate.bottom>self.display.get_height():
                return False
            for puyo in landed_sprites:
                if pygame.Rect.colliderect(puyo.rect, candidate):
                    return False
        return True
    
    def adjust_move(self, dx, dy) -> tuple:
        adjusted_dx, adjusted_dy = dx, dy
        if not self.x_movable(dx):
            adjusted_dx = 0
        if not self.y_movable(dy):
            for i in range(FALL_SPEED):
                if self.y_movable(i):
                    adjusted_dy = i
            # adjusted_dy = 0
        return adjusted_dx, adjusted_dy
    
    def update(self, *arrow_key: int):
        dx = 0
        dy = FALL_SPEED
        
        if arrow_key:
            if arrow_key[0] == K_LEFT:
                dx = -IMG_WIDTH
            if arrow_key[0] == K_RIGHT:
                dx = IMG_WIDTH
            
        dx, dy = self.adjust_move(dx, dy)
        
        if (dx, dy) == (0, 0):
            landed_sprites.add(self.puyos[0], self.puyos[1])
            pygame.event.post(pygame.event.Event(puyo_landed))
        
        for puyo in self.puyos:
            puyo.move(dx, dy)
    
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
        self.color = color
        self.image = pygame.image.load(Puyo.to_img[self.color])
        self.rect = self.image.get_rect(center = center)
        self.landed = False
        
    def fall(self) -> None:
        # if not self.landed and self.rect.bottom < self.display.get_height():
        if self.rect.bottom < self.display.get_height():
            self.rect.move_ip(0, FALL_SPEED)
        else:
            # self.landed = True
            landed_sprites.add(self)
            
    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)
        
    def draw(self) -> None:
        # pygame.Surface.blit(drawing_surface, destination_surface)
        self.display.blit(self.image, self.rect)
        
        
class Window():
    def __init__(self, display: pygame.surface, board: Board):
        self.display = display
        self.board = board
        
        right_surface = pygame.Surface((IMG_WIDTH, 2*IMG_HEIGHT))
        right_surface.fill(WHITE)
        right_rect = right_surface.get_rect(topright=(self.display.get_width()-WINDOW_RIGHT_SPACE, WINDOW_UPPER_SPACE))
        
        left_surface = pygame.Surface((IMG_WIDTH, 2*IMG_HEIGHT))
        left_surface.fill(WHITE)
        left_rect = left_surface.get_rect(topright=(right_rect.left, right_rect.top+LEFT_WINDOW_GAP))
        
        self.surfaces = [right_surface, left_surface]
        self.rects = [right_rect, left_rect]
        
        self.puyos = [[Puyo(self.surfaces[0], (IMG_WIDTH//2, IMG_HEIGHT//2), self.board.puyos_queue[0][0]), Puyo(self.surfaces[0], (IMG_WIDTH//2, 3*IMG_HEIGHT//2), self.board.puyos_queue[0][0])], [Puyo(self.surfaces[1], (IMG_WIDTH//2, IMG_HEIGHT//2), self.board.puyos_queue[1][0]), Puyo(self.surfaces[1], (IMG_WIDTH//2, 3*IMG_HEIGHT//2), self.board.puyos_queue[1][1])]]
        
    def update(self):
        self.puyos = [[Puyo(self.surfaces[0], (IMG_WIDTH//2, IMG_HEIGHT//2), self.board.puyos_queue[0][0]), Puyo(self.surfaces[0], (IMG_WIDTH//2, 3*IMG_HEIGHT//2), self.board.puyos_queue[0][0])], [Puyo(self.surfaces[1], (IMG_WIDTH//2, IMG_HEIGHT//2), self.board.puyos_queue[1][0]), Puyo(self.surfaces[1], (IMG_WIDTH//2, 3*IMG_HEIGHT//2), self.board.puyos_queue[1][1])]]

    def draw(self):
        for puyos, surface, rect in zip(self.puyos, self.surfaces, self.rects):
            surface.fill(WHITE)
            for puyo in puyos:
                puyo.draw()
            self.display.blit(surface, rect)
        


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
    board = Board()
    falling_puyos = FallingPuyos(display, board)
    # all_sprites.add(falling_puyos.puyos[0], falling_puyos.puyos[1])
    
    frame = Frame(display)
    batsu = Batsu(display)
    window = Window(display, board)
    
    
    while True:
        # catch events
        keep_update = True
        reset_puyo = False

        for event in pygame.event.get():
            if event.type == QUIT:
                # Simply using sys.exit() can cause your IDE to hang due to a common bug. 
                pygame.quit()
                sys.exit()
            elif event.type == game_ended:
                keep_update = False
            elif event.type == puyo_landed:
                reset_puyo = True
            elif event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    falling_puyos.update(event.key)
                
        # initiate canvas
        display.fill("white")
        if keep_update and reset_puyo:
            falling_puyos.reset_puyos()

        # update display
        
        if keep_update:
            falling_puyos.update()
        batsu.update()
        window.update()
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