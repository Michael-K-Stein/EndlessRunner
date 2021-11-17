from direct.showbase.PythonUtil import Enum
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.MetaInterval import Sequence
from direct.interval.LerpInterval import LerpFunc
from direct.interval.FunctionInterval import Func
from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import Fog
from panda3d.core import TextNode
from panda3d.core import Texture, CardMaker
from panda3d.core import NodePath
from panda3d.core import Camera
from panda3d.core import OrthographicLens
from panda3d.core import ClockObject
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionPolygon, CollisionNode, CollisionHandlerEvent, Point3, CollisionBox, CollisionSphere, AmbientLight
from panda3d.core import NodePath
from panda3d.core import Camera
from panda3d.core import OrthographicLens
from panda3d.core import TransparencyAttrib
import random
import math
import sys
from enum import Enum
import numpy as np
import cv2
import threading
import time

# Global variables for the tunnel dimensions and speed of travel
TUNNEL_SEGMENT_LENGTH = 50
TUNNEL_TIME = 2  # Amount of time for one segment to travel the
# distance of TUNNEL_SEGMENT_LENGTH

GAME_SPEED_ACCELERATION_INTERVAL_SECONDS = 2

RALPH_START_X = 0
RALPH_START_Y = -1
RALPH_START_Z = 5.5

RALPH_CENTER = (0, -1, 5.5)
RALPH_LEFT = (-0.7, -0.7, 5.5)
RALPH_RIGHT = (0.7, -0.7, 5.5)

RALPH_CENTER_ROT = (0, -90, 0)
RALPH_LEFT_ROT = (0, -90, 30)
RALPH_RIGHT_ROT = (30, -90, 0)
RALPH_POSITION_MULTIPLIER = 0.05
RALPH_BASE_SCALE = 0.15

OBSTACLE_SPWN_DEPTH = -50

FOG_EXPIRY_DENSITY = 0.045

MAX_GAME_SPEED = 0.02
GAME_DEFAULT_SPEED = 0.150
GAME_ACCELERATION = -0.020

BIRD_BASE_SCALE = 0.2
BOX_BASE_SCALE = 0.07


MAX_BACKGROUND_MUSIC_SPEED = 1.2

BIRD_SPAWN_INTERVAL_SECONDS = 3

STARTING_OBJECTS_SPAWN_INTERVAL_SECONDS = 3
PRIZE_REWARD = 777
PRIZE_BASE_SCALE = 0.3
PRIZE_CHANCE = 700

FOG_LUMINECENSE = 0.2

# Pure magic
MAGIC_RALPH_LOCATION_SCALE_FACTOR = 270
MAGIC_POINT_THIRTY_FIVE = 0.35

class ObsticleType(Enum):
    BIRD = 1,
    BOX = 2,
    NULL = 0
