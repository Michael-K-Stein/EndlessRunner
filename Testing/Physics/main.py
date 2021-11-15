"""

"""

import pygame
from player import Player

pygame.init()
screen = pygame.display.set_mode([500, 500])



circ_x = 0
circ_y = 0

def location_callback(x,y):
    global circ_x
    global circ_y
    circ_x = x
    circ_y = y

player = Player(location_callback)

def player_jump_callback():
    player.jump()


def player_tuck_callback():
    player.tuck()


def player_tucknt_callback():
    player.tucknt()


def player_move_right_callback():
    pass


def player_move_left_callback():
    pass



def main():

    player.callibrate(500,500,3,3)

    # Run until the user asks to quit
    running = True
    while running:

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player_jump_callback()
                if event.key == pygame.K_LSHIFT:
                    player_tuck_callback()
                if event.key == pygame.K_RSHIFT:
                    player_tucknt_callback()

        player.update()

        # Fill the background with white
        screen.fill((0, 0, 0))

        # Draw a solid blue circle in the center
        pygame.draw.circle(screen, (255, 0, 0), (circ_x, (500/(3/2))-circ_y -30), 30)

        # Flip the display
        pygame.display.flip()

    # Done! Time to quit.
    pygame.quit()

if __name__ == '__main__': 
    main()
