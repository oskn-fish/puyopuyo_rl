import pygame
from puyopuyo.board import Board
from puyopuyo.constants import *
from puyopuyo.puyo import *
from puyopuyo.event import *
from puyopuyo.basic import *

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