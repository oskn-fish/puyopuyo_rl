import pygame
import sys
from pygame.locals import *
import random
import copy
import math
import numpy as np

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

# set window title
pygame.display.set_caption("puyopuyo")


class Puyo(pygame.sprite.Sprite):
    """
    simple puyo sprite
    it's movement is defined by FloatingPuyos
    """
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


class Board():
    """
    store infomation of puyos on the screen with 2-dimentinal list
    
    1. puyo queqe of window
    2. already landed puyos (used for quick drop)
    
    """
    def __init__(self):
        self.list_board = [[" "]*6 for i in range(12)]
        self.puyos_queue = [[random.choice(COLORS), random.choice(COLORS)] for i in range(2)]
        
    def pop_chain_puyos(self, *fell_puyos: dict) -> list:
        """
        
        fell_puyos = {(i,j): "yellow", ...}
        
        used when
        1. FloatingPuyo lands
        2. after Pop
        
        when 1., (not when 2.)
        if the color of puyo1 and puyo2 has the same color, 
        search from only puyo1.
        """
        self.list_board_cp = copy.deepcopy(self.list_board)
        for puyo_coordinate, color in fell_puyos:
            if self.list_board_cp[puyo_coordinate[0], puyo_coordinate[1]] != "+":
                longest_chain = self._recursive_chain_search(color, puyo_coordinate)
                if len(longest_chain) >= 4:
                    np.char.replace(self.list_board_cp, "+", " ")

    
    def _recursive_chain_search(self, puyo_color: str,  puyo_coordinate: dict) -> tuple:
        coordinate_chain = []
        
        if self.list_board_cp[puyo_coordinate[0]][puyo_coordinate[1]] != puyo_color:
            return coordinate_chain
        
        # color = self.list_board_cp[puyo_coordinate["x"]][puyo_coordinate["y"]]
        self.list_board_cp[puyo_coordinate[0]][puyo_coordinate[1]] = "+"
        # is_last_call = True
        for next_coordinate in [(puyo_coordinate[0]+round(math.cos(math.radians(90*i))),puyo_coordinate[1]+round(math.sin(math.radians(90*i)))) for i in range(4)]:
            if self.list_board[next_coordinate[0]][next_coordinate[1]] == self.list_board[puyo_coordinate[0]][puyo_coordinate[1]]:
                # coordinate_chain.append(puyo_coordinate)
                coordinate_chain.extend(self._recursive_chain_search(puyo_color, next_coordinate))
                # is_last_call = False
        # if is_last_call:
        return coordinate_chain
    
    def add_puyos(self):
        pass

    # def update():
    #     pass
        
        


class FloatingPuyos(pygame.sprite.Sprite):
    """
    1. contains two falling puyos
    2. defines the movement of containing puyos
    """
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
        
        # when landed
        if (dx, dy) == (0, 0):
            landed_sprites.add(self.puyos[0], self.puyos[1])
            landed_event = pygame.event.Event(puyo_landed)
            # landed_event.__dict__ = 
            pygame.event.post(pygame.event.Event(puyo_landed))
        
        for puyo in self.puyos:
            puyo.move(dx, dy)
    
    def draw(self):
        for puyo in self.puyos:
            puyo.draw()
        
        
class Window():
    """
    class for the puyo stack in window
    it's contents refer to board
    """
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
    """
    frame covering window
    """
    def __init__(self, surface: pygame.surface):
        self.surface = surface
        self.rect = pygame.Rect((0,0), (self.surface.get_width(), self.surface.get_height()-12*IMG_HEIGHT))

    def draw(self) -> None:
        pygame.draw.rect(self.surface, BLACK, self.rect)
        
class Batsu(pygame.sprite.Sprite):
    """
    the 'x' outlet of puyos
    if landed puyo touches this, game_ended event will be sent
    """
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
    falling_puyos = FloatingPuyos(display, board)
    # all_sprites.add(falling_puyos.puyos[0], falling_puyos.puyos[1])
    
    frame = Frame(display)
    batsu = Batsu(display)
    window = Window(display, board)
    
    
    while True:
        # catch events
        keep_update = True
        reset_floating_puyo = False

        for event in pygame.event.get():
            if event.type == QUIT:
                # Simply using sys.exit() can cause your IDE to hang due to a common bug. 
                pygame.quit()
                sys.exit()
            elif event.type == game_ended:
                keep_update = False
            elif event.type == puyo_landed:
                reset_floating_puyo = True
                board.update()
            elif event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    falling_puyos.update(event.key)
                
        # initiate canvas
        display.fill("white")
        if keep_update and reset_floating_puyo:
            falling_puyos.reset_floating_puyos()

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