"""

"""

from enum import Enum
import logging, sys


class Player_PositionY_Modes(Enum):
    DEFAULT = 0
    JUMPED = 1
    TUCKED = 2

class Player_PositionX_Modes(Enum):
    DEFAULT = 0
    LEFT = 1
    RIGHT = 2

class Player:

    player_width = -1
    player_height = -1

    pos_world_x = -1
    pos_world_y = -1
    pos_x = Player_PositionX_Modes.DEFAULT
    pos_y = Player_PositionY_Modes.DEFAULT

    screen_block_heights = -1
    screen_block_widths = -1

    location_post_callback = None

    def __init__(loc_post_callback):
        self.location_post_callback = loc_post_callback

    def callibrate(self, screen_width:int, screen_height:int, y_levels:int, x_levels:int):
        self.screen_block_widths = screen_width / x_levels
        self.screen_block_heights = screen_height / y_levels
        self.player_width = self.screen_block_widths
        self.player_height = 2 * self.screen_block_heights

    def jump(self):
        if self.pos_y != Player_PositionY_Modes.JUMPED:
            self.pos_world_y += self.screen_block_heights
            self.pos_y = Player_PositionY_Modes.JUMPED
            logging.debug('INFO : \t\tPLAYER : jump : ')
        else:
            logging.debug('WARNING : \t\tPLAYER : jump : Player tried to jump while midair! WTF.👺')

    def tuck(self):
        if self.pos_x != Player_PositionX_Modes.TUCKED:
            self.pos_world_y -= self.screen_block_heights
            self.pos_y = Player_PositionY_Modes.TUCKED
            logging.debug('INFO : \t\tPLAYER : tuck : ')
        else:
            logging.debug('WARNING : \t\tPLAYER : tuck : Player tried to tuck while already tucked!')

    def post_location():
        self.location_post_callback(self.pos_world_x, self.pos_world_y, self.pos_y, self.pos_x)
