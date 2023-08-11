import pygame
import sys
from pygame.locals import *
from puyopuyo.constants import * 
from puyopuyo.frame import *
from puyopuyo.board import *
from puyopuyo.core import *
from puyopuyo.event import *

pygame.init()


# set window title
pygame.display.set_caption("puyopuyo")


def main():
    board = Board()
    falling_puyos = FloatingPuyos(display, board)
    # all_sprites.add(falling_puyos.puyos[0], falling_puyos.puyos[1])
    
    frame = Frame(display)
    batsu = Batsu(display)
    window = Window(display, board)
    
    keep_update = True
    
    while True:
        # catch events
        
        reset_floating_puyo = False
        if not keep_update:
            continue
        
        for event in pygame.event.get():
            if event.type == QUIT:
                # Simply using sys.exit() can cause your IDE to hang due to a common bug. 
                pygame.quit()
                sys.exit()
            elif event.type == game_ended:
                keep_update = False
            elif event.type == puyo_landed:
                # reset_floating_puyo = True
                falling_puyos.reset_puyos()
                board.add_puyos(event.__dict__)
            elif event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    falling_puyos.update(event.key)
        
        
        # initiate canvas
        display.fill("white")
        # if keep_update and reset_floating_puyo:
        #     falling_puyos.reset_floating_puyos()

        # update display
        # if keep_update:
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