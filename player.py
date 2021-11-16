"""
    Crime commiter: Hanich 18
    Fixer: Hanich 17
    Purpose: A class for a player with basic physics functionality.
"""

from enum import Enum
import logging

TRANSITION_MOVE_COUNT = 30
JUMP_V0_FORCE = 0.9
GRAVITY_FORCE = -0.002
MOTION_MULTIPLIER = 0.75
TIME_MULTIPLIER = 1300
PLAYER_HW_RATIO = 2  # Height is 2 * Width


# Renamed from Player_PositionY_Modes
class PlayerPositionYModes(Enum):
    DEFAULT = 0  # Standing
    JUMPED = 1
    TUCKED = 2


# Renamed from Player_PositionX_Modes
class PlayerPositionXModes(Enum):
    # Changed value from 1 to -1
    LEFT = -1
    # Renamed from CENTRE
    CENTER = 0
    # Changed value from 2 to 1
    RIGHT = 1


def physics_world_jump_function(time: int, y_0: float, v_0: float, a: float):
    """
    Your classical moving formula from physics class

    :param time: Time in movement
    :param y_0: Starting position
    :param v_0: Starting speed
    :param a: Acceleration
    :return: Current position
    """
    return y_0 + (v_0 * time) + ((a * pow(time, 2))/2)


class Player:
    """
    A Player class which handles Physics and transition from camera to engine
    """

    def __init__(self, DEBUG, loc_post_callback):
        self.DEBUG = DEBUG
        if self.DEBUG:
            logging.basicConfig(level=logging.DEBUG)
        # Callback function for game engine
        self.location_post_callback = loc_post_callback

        # Screen is divided into 3x3 "blocks"
        # Location of player in 3x3
        self.pos_x = PlayerPositionXModes.CENTER
        self.pos_y = PlayerPositionYModes.DEFAULT

        # Size of each block in pixels (or panda3d units, idk)
        self.screen_block_width = -1
        self.screen_block_height = -1

        # Player size in pixels (Assuming a player is 1x2 blocks)
        self.player_width = -1
        self.player_height = -1

        # Actual location in panda3d units
        self.pos_world_x = -1
        self.pos_world_y = -1

        # Where the player should be in the NEXT tick
        self.target_location_x = -1
        self.target_location_y = -1

        # How much time has passed from the beginning of the movement (t in physics)
        self.transition_move_counter = -1

    def calibrate(self, screen_width: int, screen_height: int, y_levels: int, x_levels: int):
        """
        Calibrate the Player class with game engine dimensions

        :param screen_width: The width of the screen, in pixels
        :param screen_height: The height of the screen, in pixels
        :param y_levels: How many y "lanes" are there in the game
        :param x_levels: How many x "lanes" are there in the game
        :return: None
        """
        # Calculate the block size in pixels
        self.screen_block_width = screen_width / x_levels
        self.screen_block_height = screen_height / y_levels

        # The player size in pixels
        self.player_width = self.screen_block_width
        self.player_height = PLAYER_HW_RATIO * self.screen_block_height

        # Start the player in (0, 0)
        self.pos_world_y = 0
        self.pos_world_x = 0

        # Target location for next tick
        self.target_location_x = self.pos_world_x
        self.target_location_y = self.pos_world_y

    def update(self, delta_time):
        """
        Update the player location

        :param delta_time: The time passed from last tick (something they do in the professional scene)
        :return: None
        """
        self.do_movement(delta_time)

        self.transition_move_counter += (TIME_MULTIPLIER * delta_time)
        self.post_location()

    def do_movement(self, delta_time):
        """
        Do the x,y movement

        :param delta_time: Time passed from last update
        :return: None
        """
        # Do we need to move in the y axis
        if self.pos_world_y != self.target_location_y:
            self.change_y_movement(delta_time)

        # NOT ACTUALLY USED
        # Do we need to move in the x axis
        if self.pos_world_x != self.target_location_x:
            self.pos_world_x += self.calculate_delta_x(delta_time)

    def change_y_movement(self, delta_time):
        """
        Change the Y movement

        :param delta_time: Time passed from last update
        :return: None
        """
        if self.pos_y == PlayerPositionYModes.JUMPED:
            self.jump_movement()
            return

        self.pos_world_y += self.calculate_delta_y(delta_time)

    def calculate_delta_y(self, delta_time):
        """
        Calculate the y movement

        :param delta_time: Time passed from last update
        :return: 1 or -1, depends on y2 > y1
        """
        return (TIME_MULTIPLIER * delta_time) * MOTION_MULTIPLIER * \
               ((self.target_location_y - self.pos_world_y) /
                abs(self.pos_world_y - self.target_location_y))

    def calculate_delta_x(self, delta_time):
        """
        Calculate the x movement, NOT REALLY USED

        :param delta_time: Time passed from last update
        :return: 1 or -1, depends on x2 > x1
        """
        return ((self.target_location_x - self.pos_world_x) /
                abs(self.pos_world_x - self.target_location_x))

    def jump_movement(self):
        """
        Move the player while jumping

        :return: None
        """
        self.pos_world_y = physics_world_jump_function(self.transition_move_counter, 0, JUMP_V0_FORCE, GRAVITY_FORCE)
        if self.transition_move_counter > 1 and self.pos_world_y <= 0:
            self.pos_y = PlayerPositionYModes.DEFAULT
            self.pos_world_y = 0
            self.target_location_y = 0

    def start_jump(self):
        """
        Configure the player to jump

        :return: None
        """
        if self.pos_y == PlayerPositionYModes.JUMPED:
            logging.debug('WARNING: player.py/start_jump(): Player tried to jump while midair! WTF.👺')
            return

        self.pos_y = PlayerPositionYModes.JUMPED
        self.transition_move_counter = 0
        self.target_location_y = PLAYER_HW_RATIO * self.screen_block_height
        logging.debug('INFO: player.py/start_jump(): Started jump!')

    def tuck(self):
        """
        Tuck (or duck or crouch) the player

        :return: None
        """
        if self.pos_y == PlayerPositionYModes.TUCKED:
            logging.debug('WARNING: player.py/tuck(): Player tried to tuck while already tucked!')
            return

        self.pos_y = PlayerPositionYModes.TUCKED
        self.target_location_y = -self.screen_block_height
        logging.debug('INFO: player.py/tuck(): Started tuck!')

    def tucknt(self):
        """
        Stop the tuck (or duck or crouch)

        :return:
        """
        if self.pos_y == PlayerPositionYModes.DEFAULT:
            logging.debug(
                'WARNING: player.py/tucknt(): Player said they are not longer tucked, but they weren\'t tucked.'
                ' They lied. Just like everyone always does. They lie. Never believe anyone.')
            return

        self.target_location_y = 0
        self.pos_y = PlayerPositionYModes.DEFAULT
        logging.debug('INFO: player.py/tucknt(): Ended tuck!')

    def set_center(self):
        """
        Set the player in the center

        :return: None
        """
        self.pos_x = PlayerPositionXModes.CENTER
        self.target_location_x = 0  # self.screen_block_widths
        logging.debug('INFO: player.py/set_center(): Set center')

    def set_right(self):
        """
        Set the player in the right

        :return: None
        """
        self.pos_x = PlayerPositionXModes.RIGHT
        self.target_location_x = self.screen_block_width
        logging.debug('INFO: player.py/set_right(): Set right')

    def set_left(self):
        """
        Set the player in the left

        :return: None
        """
        self.pos_x = PlayerPositionXModes.LEFT
        self.target_location_x = -self.screen_block_width
        logging.debug('INFO: player.py/set_left(): Set left')

    def post_location(self):
        self.location_post_callback(self.pos_world_x, self.pos_world_y)
        # logging.debug('INFO : \t\tPLAYER : Posting location ' + '(' +
        #               str(self.pos_world_x) + ', ' + str(self.pos_world_y) + ')')
