import pygame
import random
from puyopuyo.constants import *
from puyopuyo.event import *
from puyopuyo.board import Board
from pygame.locals import *
import numpy as np
import copy
import math

# logging
import json
import os
from logging import getLogger, config
with open(os.path.join("util", "log_config.json")) as f:
    log_conf = json.load(f)
config.dictConfig(log_conf)
logger = getLogger(__name__)


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
        self.event_flags = {PUYO_LANDED: False}
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
    
    def _adjust_move(self, dx, dy) -> tuple:
        adjusted_dx, adjusted_dy = dx, dy
        if not self.x_movable(dx):
            adjusted_dx = 0
        if not self.y_movable(dy):
            adjusted_dy = 0
            for i in range(FALL_SPEED):
                if self.y_movable(i):
                    adjusted_dy = i
            # adjusted_dy = 0
        return adjusted_dx, adjusted_dy
    
    def update(self, *arrow_key: int):
        
        if len(self.puyos) == 0:
            return
        
        dx = 0
        dy = FALL_SPEED
        
        if arrow_key:
            if arrow_key[0] == K_LEFT:
                dx = -IMG_WIDTH
            if arrow_key[0] == K_RIGHT:
                dx = IMG_WIDTH
            
        dx, dy = self._adjust_move(dx, dy)
        
        # when landed
        if (dx, dy) == (0, 0):
            landed_sprites.add(self.puyos[0], self.puyos[1])
            # landed_event = pygame.event.Event(puyo_landed, landed_puyos=self.puyos)
            # landed_event.__dict__ = {"landed_puyos":self.puyos}
            self.event_flags[PUYO_LANDED] = True
            self.deleted_puyos = self.puyos
            self.puyos = []
            # pygame.event.post(landed_event)
        
        for puyo in self.puyos:
            puyo.move(dx, dy)
            
    def post_events(self):
        for event, has_occurred in self.event_flags.items():
            if has_occurred:     
                if event == PUYO_LANDED:
                    new_event = pygame.event.Event(event, landed_puyos=self.deleted_puyos)
                    pygame.event.post(new_event)
                    self.event_flags[PUYO_LANDED] = False
    
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
        # self.char_list = np.array([[" "]*6 for i in range(12)])
        self.puyos_queue = [[random.choice(COLORS), random.choice(COLORS)] for i in range(2)]
        self.board = [[None]*6 for i in range(12)]
    
    # for print function
    def __str__(self):
        string = "["
        for i in range(12):
            string = string+list(map(lambda x: " " if x==None else x.color[0] ,self.board[i]))
            if i < 11:
                string += "\n"
        string += "]"
        return string
    
    def pop_chain_puyos(self, landed_puyos: list[Puyo]) -> bool:
        """
        remove puyo chains from self.board: list[Puyo]
        returns if chain pops: bool.        
        """
        puyo_coordinates = [self._coord_to_board_idx(puyo.topleft) for puyo in landed_puyos]
        puyo_colors = [puyo.color for puyo in landed_puyos]
        does_pop = False
        for puyo_coordinate, color in zip(puyo_coordinates, puyo_colors):
            # board for search (searched element will be replaced with "+")
            self.list_board_cp = copy.deepcopy(self.char_list)
            longest_chain = self._recursive_chain_search(color, puyo_coordinate)
            if len(longest_chain) >= 4:
                does_pop = True
                np.char.replace(self.list_board_cp, "+", " ")
                self.char_list = self.list_board_cp
        return does_pop

    
    def _recursive_chain_search(self, puyo_color: str,  puyo_coordinate: dict) -> tuple:
        coordinate_chain = []
        
        if self.list_board_cp[puyo_coordinate[0]][puyo_coordinate[1]] != puyo_color:
            return coordinate_chain
        
        # color = self.list_board_cp[puyo_coordinate["x"]][puyo_coordinate["y"]]
        self.list_board_cp[puyo_coordinate[0]][puyo_coordinate[1]] = "+"
        # is_last_call = True
        for next_coordinate in [(puyo_coordinate[0]+round(math.cos(math.radians(90*i))),puyo_coordinate[1]+round(math.sin(math.radians(90*i)))) for i in range(4)]:
            if self.char_list[next_coordinate[0]][next_coordinate[1]] == self.char_list[puyo_coordinate[0]][puyo_coordinate[1]]:
                # coordinate_chain.append(puyo_coordinate)
                coordinate_chain.extend(self._recursive_chain_search(puyo_color, next_coordinate))
                # is_last_call = False
        # if is_last_call:
        return coordinate_chain
    
    def add_puyos(self, landed_puyos: list[Puyo]):
        
        top_lefts = [puyo.rect.topleft for puyo in landed_puyos]
        puyo_indices = [self._coord_to_board_idx(top_left) for top_left in top_lefts]
        puyo_colors = [puyo.color[0] for puyo in landed_puyos]
        
        for puyo_index, puyo_color, landed_puyo  in zip(puyo_indices,puyo_colors, landed_puyos):
            self.char_list[puyo_index[0] ,puyo_index[1]] = puyo_color
            self.board[puyo_index[0]][puyo_index[1]] = landed_puyo
        # print(self.char_list)
        # logger.debug(self.char_list)

    
    def _coord_to_board_idx(self, top_left):
        i = (top_left[1]-FRAME_HEIGHT)//IMG_WIDTH
        j = top_left[0]//IMG_HEIGHT
        return i, j