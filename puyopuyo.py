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
    floating_puyos = FloatingPuyos(display, board)
    # all_sprites.add(falling_puyos.puyos[0], falling_puyos.puyos[1])
    
    frame = Frame(display)
    batsu = Batsu(display)
    window = Window(display, board)
    
    # keep_update = True
    keep_update = True
    frame_num = 0
    count_frame = None
    
    while True:
        
        if not keep_update:
            # print("waiting")
            pygame.time.wait(100)
            continue
        
        for event in pygame.event.get():
            # print("eventing ")
            if event.type == QUIT:
                # Simply using sys.exit() can cause your IDE to hang due to a common bug. 
                pygame.quit()
                sys.exit()
                
            # this event loop pops all the events happend the last frame
            # resetting floating puyos depents on both 
            # 1. batsu not colliding to landed puyos
            # 2. floating puyos landed
            # the two conditions can be determined only after the event loop
            elif event.type == game_ended:
                keep_update = False
            elif event.type == puyo_landed:
                pygame.time.set_timer(reset_puyos, 100, 1) 
                board.add_puyos(event.landed_puyos)
            elif event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    floating_puyos.update(event.key)     
            elif event.type == reset_puyos:
                floating_puyos.reset_puyos()
        
        # update
        floating_puyos.update()
        batsu.update()
        window.update()
        
        # check for event occurrence
        floating_puyos.post_events()
        batsu.post_events()
        
        # initiate canvas
        display.fill("white")
        
        # draw
        batsu.draw()
        frame.draw()
        window.draw()
        floating_puyos.draw()
        landed_sprites.draw(display)
        
        # render
        pygame.display.update()
        clock.tick(60)
    

if __name__ == "__main__":
    main()