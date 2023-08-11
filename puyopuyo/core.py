import pygame
import random
from puyopuyo.constants import *
from puyopuyo.event import *
from puyopuyo.basic import *
from puyopuyo.board import Board
from pygame.locals import *
import numpy as np
import copy
import math

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
            landed_event.__dict__ = {"landed_puyos":self.puyos}
            pygame.event.post(pygame.event.Event(puyo_landed))
        
        for puyo in self.puyos:
            puyo.move(dx, dy)
    
    def draw(self):
        for puyo in self.puyos:
            puyo.draw()

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
    
    def add_puyos(self, event_dict: list[Puyo]):
        
        bottom_lefts = [puyo.rect.bottomleft for puyo in event_dict["landed_puyos"]]
        puyo_indices = [self._coord_to_board_idx(bottom_left) for bottom_left in bottom_lefts]
        puyo_colors = [puyo.color[0] for puyo in event_dict]
        
        for puyo_index, puyo_color  in zip(puyo_indices,puyo_colors):
            self.list_board[puyo_index[0]][puyo_index[1]] == puyo_color

    
    def _coord_to_board_idx(self, bottom_left):
        x = bottom_left[0]%IMG_WIDTH
        y = (display.get_height()-bottom_left[1])%IMG_HEIGHT
        return x, y