import pygame

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
FRAME_HEIGHT = WINDOW_UPPER_SPACE+WINDOW_HEIGHT+WINDOW_LOWER_SPACE

# singletons for game logic
display_size = (IMG_WIDTH*6, 12*IMG_HEIGHT+FRAME_HEIGHT)
display = pygame.display.set_mode(display_size)
clock = pygame.time.Clock()
PUYO_RESET_DELAY = 100

outlet_position = (2*IMG_WIDTH+IMG_WIDTH//2, display.get_height()-11*IMG_HEIGHT-IMG_HEIGHT//2)
above_outlet = (2*IMG_WIDTH+IMG_WIDTH//2, display.get_height()-12*IMG_HEIGHT-IMG_HEIGHT//2)


# sprite group
landed_sprites = pygame.sprite.Group()