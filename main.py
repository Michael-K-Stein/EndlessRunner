from random import random
from direct.showbase.PythonUtil import Enum
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Fog
from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.MetaInterval import Sequence
from direct.interval.LerpInterval import LerpFunc
from direct.interval.FunctionInterval import Func
from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import ClockObject
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerPusher
from panda3d.core import CollisionPolygon, CollisionNode, CollisionHandlerEvent, Point3, CollisionBox
import random
import numpy
import math
import scan
import sys

import scan
from player import Player
from enum import Enum

# Global variables for the tunnel dimensions and speed of travel
TUNNEL_SEGMENT_LENGTH = 50
TUNNEL_TIME = 2  # Amount of time for one segment to travel the
# distance of TUNNEL_SEGMENT_LENGTH
BIRD_SPAWN_INTERVAL_SECONDS = 3

GAME_SPEED_ACCELERATION_INTERVAL_SECONDS = 2
BIRDS_X_ACCELERATION = -0.2

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

OBSTACLE_SPWN_DEPTH = -50

FOG_EXPIRY_DENSITY = 0.045

bird_spawner_timer = ClockObject()
game_speed_timer = ClockObject()


class TYPE(Enum):
    BIRD = 1,
    BOX = 2,
    NULL = 0

class DinoRender(ShowBase):
    # Macro-like function used to reduce the amount to code needed to create the on screen instructions
    def genLabelText(self, i, text):
        return OnscreenText(text=text, parent=base.a2dTopLeft, scale=.05,
                            pos=(0.06, -.065 * i), fg=(1, 1, 1, 1),
                            align=TextNode.ALeft)

    def handle_collision(self, entry):
        #print('=== This is a collision message: ===')
        #print(entry)
        #print('== End collision message ===')
        self.player_hit()
        

    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)

        self.init_collision_detection()

        self.background_music = base.loader.loadSfx('./music.wav')
        self.background_music.setLoop(True)
        self.background_music.play()
        self.playback_speed = 1

        # Standard initialization stuff
        # Standard title that's on screen in every tutorial
        self.title = OnscreenText(text="Ha'ag", style=1,
            fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5), parent=base.a2dBottomRight,
            align=TextNode.ARight, pos=(-0.1, 0.1), scale=.08)

        self.escapeEventText = self.genLabelText(1, "ESC: Quit")

        # disable mouse control so that we can place the camera
        base.disableMouse()
        camera.setPosHpr(0, 0, 10, 0, -90, 0)
        base.setBackgroundColor(0, 0, 0)  # set the background color to black

        # World specific-code
        self.fog = Fog('distanceFog')
        self.fog.setColor(0, 0, 0)
        self.fog.setExpDensity(FOG_EXPIRY_DENSITY)
        # We will set fog on render which means that everything in our scene will
        # be affected by fog. Alternatively, you could only set fog on a specific
        # object/node and only it and the nodes below it would be affected by
        # the fog.
        render.setFog(self.fog)

        # Load the tunel and start the tunnel
        self.initTunnel()
        self.initRalph()
        self.contTunnel()

        self.accept("arrow_left", self.rotate, ["left"])
        self.accept("arrow_right", self.rotate, ["right"])

        self.accept("space", self.jump)
        self.accept("lshift", self.tuck)
        self.accept("rshift", self.tucknt)
        self.accept('enter', self.kill_all)
        self.i = 0

        self.ralph_base_y = self.ralph.getY()
        self.ralph_base_x = self.ralph.getX()
        self.ralph_rot_multiplier = 0

        # Init scanner
        if "debug" not in sys.argv:
            self.scanner = scan.Scanner(self.scanner_callback)
            self.scanner.run_scanner()
            self.accept("c", self.scanner.calibrate)

        self.show_menu()

    def show_menu(self):
        self.pause_game()
        self.gameMenu = DirectDialog(frameSize = (-10, 10, -10, 10), fadeScreen = 0.4, relief = DGG.FLAT)
        DirectLabel(text="Ha'ag", parent=self.gameMenu, scale=0.1, pos = (0,0,0.2))
        DirectButton(text = "Restart",
                   command = self.click_restart,
                   pos = (0, 0, -0.2),
                   parent = self.gameMenu,
                   scale = 0.07)
        DirectButton(text = "Calibrate",
                   command = self.scanner.calibrate,
                   pos = (0, 0, -0.4),
                   parent = self.gameMenu,
                   scale = 0.07)
        DirectButton(text = "Quit",
                   command = self.quit_game,
                   pos = (0, 0, -0.6),
                   parent = self.gameMenu,
                   scale = 0.07)

    def resume_game(self):
        self.tasks_running = True
        self.taskMgr.add(self.spawner_timer, "Spawner")
        self.taskMgr.add(self.game_loop, "GameLoop")
        self.taskMgr.add(self.game_speed_acceleration, "GameSpeedAcceleration")

    def pause_game(self):
        self.tasks_running = False
        self.taskMgr.remove("BirdSpawner")
        self.taskMgr.remove("GameLoop")
        self.taskMgr.remove("GameSpeedAcceleration")
        self.background_music.stop()

    def click_restart(self):
        self.gameMenu.hide()
        self.player = Player(self.set_ralph_pos)
        self.player.callibrate(TUNNEL_SEGMENT_LENGTH, TUNNEL_SEGMENT_LENGTH, 3, 3)
        self.birds_x_speed = -1.5
        for bird in self.birds if hasattr(self, "birds") else []:
            bird.remove_node()
        
        self.birds_x_speed = -1.5 * 10
        self.birds = []
        self.boxes = []

        self.resume_game()
        self.background_music.play()

    def quit_game(self):
        self.scanner.stop()
        sys.exit()

    def exit_game(self):
        self.scanner.release()
        sys.exit(0)


    def init_collision_detection(self):
        self.cTrav = CollisionTraverser()

        self.cTrav.showCollisions(self.render)

        self.notifier = CollisionHandlerEvent()

        self.notifier.addInPattern('%fn-into-%in')

        self.accept('box-into-ralph', self.handle_collision)
        self.accept('ralph-into-box', self.handle_collision)
        self.accept('ralph-into-bird', self.handle_collision)
        self.accept('bird-into-ralph', self.handle_collision)

    def scanner_callback(self, action):
        if action == "JUMP":
            if not self.tasks_running:
                self.click_restart()
            self.jump()
        elif action == "TOOK":
            self.tuck()
        elif action == "CENTER":
            self.rotate(0)
            self.tucknt()
        elif action == "LEFT":
            self.rotate(-1)
            self.tucknt()
        elif action == "RIGHT":
            self.rotate(1)
            self.tucknt()

    def rotate(self, lane):
        self.ralph.lane = lane        

        print(f"Rotate {lane}")
        print(f"Lane: {self.ralph.lane}")
        if self.ralph.lane == -1:
            self.ralph.setPos(*RALPH_LEFT)
            self.ralph.setHpr(*RALPH_LEFT_ROT)
            self.ralph.setH(self.ralph, 180)
            self.ralph_rot_multiplier = 0.5
        elif self.ralph.lane == 0:
            self.ralph.setPos(*RALPH_CENTER)
            self.ralph.setHpr(*RALPH_CENTER_ROT)
            self.ralph.setH(self.ralph, 180)
            self.ralph_rot_multiplier = 0
        elif self.ralph.lane == 1:
            self.ralph.setPos(*RALPH_RIGHT)
            self.ralph.setHpr(*RALPH_RIGHT_ROT)
            self.ralph.setH(self.ralph, 180)
            self.ralph_rot_multiplier = -0.5
        self.ralph_base_y = self.ralph.getY()
        self.ralph_base_x = self.ralph.getX()

    def jump(self, key, value):
        self.ralph.setPos(self.ralph, 0, 0, 2)

    def game_loop(self, task):
        self.player.update(globalClock.getDt())
        for box in self.boxes:
            box.setPos(box, self.birds_x_speed / (7*5), 0, 0)

        for bird in self.birds:
            #  -1.5, -0.05, 0 | right
            #  -1.5, -0.05, 0 | left
            bird.setPos(bird, self.birds_x_speed, 0, -0.0)#-0.1
        
        return Task.cont

    def game_speed_acceleration(self, task):
        if (int(game_speed_timer.getRealTime()) + 1) % GAME_SPEED_ACCELERATION_INTERVAL_SECONDS == 0:
            self.birds_x_speed += BIRDS_X_ACCELERATION
            self.playback_speed += 0.002
            self.background_music.setPlayRate(self.playback_speed)
            # self.birds_y_speed += BIRDS_X_ACCELERATION
            game_speed_timer.reset()
        return Task.cont

    def jump(self):
        self.player.jump()
    
    def tuck(self):
        #self.player.tuck()
        self.ralph.setScale(0.15,0.15,0.15*0.5)
    
    def tucknt(self):
        self.ralph.setScale(0.15,0.15,0.15)

    def set_ralph_pos(self, x, y):
        #print(x,y)
        self.ralph.setPos(self.ralph_base_x + ((y/270)*self.ralph_rot_multiplier), (y/270) + self.ralph_base_y, 5.5)
        #self.ralph.setPos(x*RALPH_POSITION_MULTIPLIER, -1+(y/270), 5.5)

    # Code to initialize the tunnel
    def initTunnel(self):
        self.tunnel = [None] * 4

        for x in range(4):
            # Load a copy of the tunnel
            self.tunnel[x] = loader.loadModel('models/tunnel')
            # The front segment needs to be attached to render
            if x == 0:
                self.tunnel[x].reparentTo(render)
            # The rest of the segments parent to the previous one, so that by moving the front segement, the entire tunnel is moved
            else:
                self.tunnel[x].reparentTo(self.tunnel[x - 1])
            self.tunnel[x].setPos(0, 0, -TUNNEL_SEGMENT_LENGTH)

    # initialize the runner
    def initRalph(self):
        self.ralph = Actor("models/ralph", {"run": "models/ralph-run", "walk": "models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(.15)
        self.ralph.setPos(*RALPH_CENTER)
        self.ralph.setHpr(*RALPH_CENTER_ROT)
        self.ralph.setH(self.ralph, 180)
        self.ralph.loop('run')
        # Hanich 17 - yes it's a crime against humanity, deal with it! btw - -1 left, 0 center, 1 right
        self.ralph.__dict__['lane'] = 0

        self.ralph.collider = self.ralph.attachNewNode(CollisionNode('ralph'))
        self.ralph.collider.node().addSolid(
            #CollisionPolygon(Point3(0, 0, 0),Point3(0,1,1),Point3(1,1,1),Point3(1,0,0))
            CollisionPolygon(Point3(-0.8, 1, 0),Point3(-0.8,1,5),Point3(0.8,1,5),Point3(0.8,1,0))
            )
        self.ralph.collider.show()
        self.cTrav.addCollider(self.ralph.collider, self.notifier)

    # This function is called to snap the front of the tunnel to the back to simulate traveling through it
    def contTunnel(self):
        # This line uses slices to take the front of the list and put it on the back
        self.tunnel = self.tunnel[1:] + self.tunnel[0:1]
        # Set the front segment (which was at TUNNEL_SEGMENT_LENGTH) to 0, which is where the previous segment started
        self.tunnel[0].setZ(0)
        # Reparent the front to render to preserve the hierarchy outlined above
        self.tunnel[0].reparentTo(render)
        # Set the scale to be apropriate (since attributes like scale are inherited, the rest of the segments have a scale of 1)
        self.tunnel[0].setScale(.155, .155, .305)
        # Set the new back to the values that the rest of teh segments have
        self.tunnel[3].reparentTo(self.tunnel[2])
        self.tunnel[3].setZ(-TUNNEL_SEGMENT_LENGTH)
        self.tunnel[3].setScale(1)

        print('hello')

        # Set up the tunnel to move one segment and then call contTunnel again
        # to make the tunnel move infinitely
        self.tunnelMove = Sequence(
            LerpFunc(self.tunnel[0].setZ,
                     duration=TUNNEL_TIME,
                     fromData=0,
                     toData=TUNNEL_SEGMENT_LENGTH * .305), # speed
            Func(self.contTunnel)
        )
        self.tunnelMove.start()

    def spawner_timer(self, task):
        if (int(bird_spawner_timer.getRealTime()) + 1) % BIRD_SPAWN_INTERVAL_SECONDS == 0:
            self.i += 1
            #self.i == 0
            if self.i % 2 == 0:
                self.spawner(TYPE.BIRD, random.randint(0, 2))
                 #self.spawner(TYPE.BIRD, 1)
            else:
                self.spawner(TYPE.BOX, random.randint(0, 2))
            bird_spawner_timer.reset()
        return Task.cont
    
    def spawner(self, type, lane):
        if type is TYPE.BIRD:
            self.spawn_bird(lane)
        elif type is TYPE.BOX:
            self.spawn_box(lane)
    
    def spawn_bird(self, lane):
        bird = self.loader.loadModel("models/birds/12214_Bird_v1max_l3.obj")
        bird.reparentTo(render)
        bird.setPos(((lane-1)*0.35), -0.10, OBSTACLE_SPWN_DEPTH)
        bird.setScale(0.015, 0.015, 0.015)
        bird.setHpr(90, 0, 90)

        col = bird.attachNewNode(CollisionNode('bird'))
        col.node().addSolid(CollisionBox(Point3(0.9, 2.5, 2.5), 0.2, 5, 5)) #nt3(0, 2, 0), 0.2, 5, 2))
        #        col.node().addSolid(CollisionBox(Point3(0.5, 0.4, 0), 0.6, 1, 1))
        col.show()
        self.cTrav.addCollider(col, self.notifier)

        self.birds.append(bird)
    
    def spawn_box(self, lane):
        box = self.loader.loadModel("models/crate")
        box.reparentTo(render)
        box.setPos(((lane-1)*0.35), -0.7, OBSTACLE_SPWN_DEPTH)
        box.setScale(.3)
        box.setHpr(90, 0, 90)

        col = box.attachNewNode(CollisionNode('box'))
        col.node().addSolid(CollisionBox(Point3(0, 0, 0.46), 0.5, 0.5, 0.5))
        col.show()
        self.cTrav.addCollider(col, self.notifier)

        self.boxes.append(box)
    
    def has_coliision(self, obj):
        if obj.get_pos()[1] <= -0.408 and obj.get_pos()[1] > -0.42:
            print("colission!!!")
            return True
        return False
    
    def remove_obj(self, obj):
        obj.remove_node()
        if obj in self.birds:
            self.birds.remove(obj)
        else:
            self.boxes.remove(obj)

    def is_out(self, obj):
        if obj.get_pos()[1] <= -0.7:
            return True
        return False

    def kill_all(self):
        print('Killing all!')
        self.scanner.kill_me()
        exit(0)
    
    def player_hit(self):
        print('Player hit!')
    
demo = DinoRender()
demo.run()
