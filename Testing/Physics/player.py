"""

"""

from enum import Enum
import logging, sys

TRANSITION_MOVE_COUNT = 30
JUMP_V0_FORCE = 10
GRAVITY_FORCE = -10

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
    target_location_x = -1
    target_location_y = -1

    transition_move_counter = -1

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

    def update(self):
        if pos_world_y != target_location_y:
            if self.pos_y = Player_PositionY_Modes.JUMPED:
                self.pos_world_y = physics_world_jump_function(transition_move_counter, 0, JUMP_V0_FORCE, GRAVITY_FORCE)
            else:
                self.pos_world_y += ((self.pos_world_y - self.target_location_y)/abs(self.pos_world_y - self.target_location_y))

    def physics_world_jump_function(self,time:int, y_0:float, v_0:float, a:float):
        return y_0 + (v_0*time) + ((a*pow(time,2))/2)

    def jump(self):
        if self.pos_y != Player_PositionY_Modes.JUMPED:
            #self.pos_world_y += self.screen_block_heights
            self.pos_y = Player_PositionY_Modes.JUMPED
            self.target_location_y = 2*self.screen_block_heights
            logging.debug('INFO : \t\tPLAYER : jump : ')
        else:
            logging.debug('WARNING : \t\tPLAYER : jump : Player tried to jump while midair! WTF.👺')

    def tuck(self):
        if self.pos_x != Player_PositionX_Modes.TUCKED:
            #self.pos_world_y -= self.screen_block_heights
            self.pos_y = Player_PositionY_Modes.TUCKED
            self.target_location_y = 0
            logging.debug('INFO : \t\tPLAYER : tuck : ')
        else:
            logging.debug('WARNING : \t\tPLAYER : tuck : Player tried to tuck while already tucked!')

    def post_location():
        self.location_post_callback(self.pos_world_x, self.pos_world_y)
