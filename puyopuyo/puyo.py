import pygame
import random
from puyopuyo.constants import *
from puyopuyo.event import *
from puyopuyo.basic import *
from puyopuyo.board import *
from pygame.locals import *

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