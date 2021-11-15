"""
    Author: Hanich 18
    Purpose: A class for a player with basic physics functionality.
"""

from enum import Enum
import logging, sys
logging.basicConfig(level=logging.DEBUG)

TRANSITION_MOVE_COUNT = 30
JUMP_V0_FORCE = 0.9
GRAVITY_FORCE = -0.002
MOTION_MULTIPLIER = 0.75

class Player_PositionY_Modes(Enum):
    DEFAULT = 0
    JUMPED = 1
    TUCKED = 2

class Player_PositionX_Modes(Enum):
    CENTRE = 0
    LEFT = 1
    RIGHT = 2


class Player:

    player_width = -1
    player_height = -1

    pos_world_x = -1
    pos_world_y = -1
    pos_x = Player_PositionX_Modes.CENTRE
    pos_y = Player_PositionY_Modes.DEFAULT
    target_location_x = -1
    target_location_y = -1

    transition_move_counter = -1

    screen_block_heights = -1
    screen_block_widths = -1

    location_post_callback = None

    def __init__(self, loc_post_callback):
        self.location_post_callback = loc_post_callback

    def callibrate(self, screen_width:int, screen_height:int, y_levels:int, x_levels:int):
        self.screen_block_widths = screen_width / x_levels
        self.screen_block_heights = screen_height / y_levels
        self.player_width = self.screen_block_widths
        self.player_height = 2 * self.screen_block_heights
        self.pos_world_y = 0
        self.pos_world_x = 0#self.screen_block_widths
        self.target_location_x = self.pos_world_x
        self.target_location_y = self.pos_world_y

    def update(self, delta_time):
        if self.pos_world_y != self.target_location_y:
            if self.pos_y == Player_PositionY_Modes.JUMPED:
                self.pos_world_y = self.physics_world_jump_function(self.transition_move_counter, 0, JUMP_V0_FORCE, GRAVITY_FORCE)
                if self.transition_move_counter > 1 and self.pos_world_y <= 0:#self.screen_block_heights:
                    self.pos_y = Player_PositionY_Modes.DEFAULT
                    self.pos_world_y = 0
                    self.target_location_y = 0
                    pass
            else:
                self.pos_world_y += (1300 * delta_time)*MOTION_MULTIPLIER*((self.target_location_y-self.pos_world_y)/abs(self.pos_world_y - self.target_location_y))
        if self.pos_world_x != self.target_location_x:
            self.pos_world_x += ((self.target_location_x-self.pos_world_x)/abs(self.pos_world_x - self.target_location_x))
        self.transition_move_counter += (1300 * delta_time)
        self.post_location()

    def physics_world_jump_function(self,time:int, y_0:float, v_0:float, a:float):
        return y_0 + (v_0*time) + ((a*pow(time,2))/2)

    def jump(self):
        if self.pos_y != Player_PositionY_Modes.JUMPED:
            #self.pos_world_y += self.screen_block_heights
            self.pos_y = Player_PositionY_Modes.JUMPED
            self.transition_move_counter = 0
            self.target_location_y = 2*self.screen_block_heights
            logging.debug('INFO : \t\tPLAYER : jump : ')
        else:
            logging.debug('WARNING : \t\tPLAYER : jump : Player tried to jump while midair! WTF.👺')

    def tuck(self):
        if self.pos_y != Player_PositionY_Modes.TUCKED:
            #self.pos_world_y -= self.screen_block_heights
            self.pos_y = Player_PositionY_Modes.TUCKED
            self.target_location_y = -self.screen_block_heights
            logging.debug('INFO : \t\tPLAYER : tuck : ')
        else:
            logging.debug('WARNING : \t\tPLAYER : tuck : Player tried to tuck while already tucked!')

    def tucknt(self):
        if self.pos_y != Player_PositionY_Modes.DEFAULT:
            self.target_location_y = 0
            self.pos_y = Player_PositionY_Modes.DEFAULT
            logging.debug('INFO : \t\tPLAYER : tucknt : ')
        else:
            logging.debug('WARNING : \t\tPLAYER : tucknt : Player said they are not longer tucked, but they weren\'t tucked. They lied. Just like everyone always does. They lie. Never believe anyone.')

    def set_centre(self):
        self.pos_x = Player_PositionX_Modes.CENTRE
        self.target_location_x = 0#self.screen_block_widths
        logging.debug('INFO : \t\tPLAYER : Set centre')

    def set_right(self):
        self.pos_x = Player_PositionX_Modes.RIGHT
        self.target_location_x = self.screen_block_widths
        logging.debug('INFO : \t\tPLAYER : Set right')

    def set_left(self):
        self.pos_x = Player_PositionX_Modes.LEFT
        self.target_location_x = -self.screen_block_widths
        logging.debug('INFO : \t\tPLAYER : Set left')

    def post_location(self):
        self.location_post_callback(self.pos_world_x, self.pos_world_y)
        #logging.debug('INFO : \t\tPLAYER : Posting location ' + '(' + str(self.pos_world_x) + ', ' + str(self.pos_world_y) + ')')
