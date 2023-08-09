import random
from constants.constants import *
import math
import copy
import numpy as np

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