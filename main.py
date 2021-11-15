from random import random
from direct.showbase.PythonUtil import Enum
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Fog
from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.interval.MetaInterval import Sequence
from direct.interval.LerpInterval import LerpFunc
from direct.interval.FunctionInterval import Func
from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import ClockObject
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerPusher
from panda3d.core import CollisionSphere, CollisionNode
import random

from player import Player
from enum import Enum

# Global variables for the tunnel dimensions and speed of travel
TUNNEL_SEGMENT_LENGTH = 50
TUNNEL_TIME = 2  # Amount of time for one segment to travel the
# distance of TUNNEL_SEGMENT_LENGTH
BIRD_SPAWN_INTERVAL_SECONDS = 3

RALPH_POSITION_MULTIPLIER = 0.05

bird_spawner_timer = ClockObject()

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

    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)

        # Standard initialization stuff
        # Standard title that's on screen in every tutorial
        self.title = OnscreenText(text="Haag", style=1,
            fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5), parent=base.a2dBottomRight,
            align=TextNode.ARight, pos=(-0.1, 0.1), scale=.08)

        # disable mouse control so that we can place the camera
        base.disableMouse()
        camera.setPosHpr(0, 0, 10, 0, -90, 0)
        base.setBackgroundColor(0, 0, 0)  # set the background color to black

        self.birds = []
        self.boxes = []

        self.taskMgr.add(self.spawner_timer, "Spawner")
        self.taskMgr.add(self.game_loop, "GameLoop")

        # World specific-code
        self.fog = Fog('distanceFog')
        self.fog.setColor(0, 0, 0)
        self.fog.setExpDensity(.045)
        # We will set fog on render which means that everything in our scene will
        # be affected by fog. Alternatively, you could only set fog on a specific
        # object/node and only it and the nodes below it would be affected by
        # the fog.
        render.setFog(self.fog)

        # Load the tunel and start the tunnel
        self.initTunnel()
        self.initRalph()
        self.contTunnel()

        self.accept("space", self.jump)
        self.accept("lshift", self.tuck)
        self.accept("rshift", self.tucknt)

        self.player = Player(self.set_ralph_pos)
        self.player.callibrate(TUNNEL_SEGMENT_LENGTH, TUNNEL_SEGMENT_LENGTH, 3, 3)
        self.i = 0
        

    def jump(self):
        self.player.jump()
    def tuck(self):
        #self.player.tuck()
        self.ralph.setScale(0.15,0.15,0.15*0.5)
    def tucknt(self):
        self.ralph.setScale(0.15,0.15,0.15)

    def game_loop(self, task):
        self.player.update(globalClock.getDt())
        for box in self.boxes:
            box.setPos(box, -0.2, 0, 0)
            if self.has_coliision(box) or self.is_out(box):
                self.remove_obj(box)

        for bird in self.birds:
            #  -1.5, -0.05, 0 | right
            #  -1.5, -0.05, 0 | left
            bird.setPos(bird, -1.5, 0, -0.0)#-0.1
            if self.has_coliision(bird) or self.is_out(bird):
                self.remove_obj(bird)
        
        return Task.cont

    def set_ralph_pos(self, x, y):
        self.ralph.setPos(x*RALPH_POSITION_MULTIPLIER, -1+(y/270), 5.5)

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
        self.ralph.setScale(.15, 0.10, 0.15)
        self.ralph.setScale(self.ralph, 1, 1, 1.2)
        self.ralph.setPos(0, -1, 5.5)
        self.ralph.setHpr(0, -90, 0)
        self.ralph.setH(self.ralph, 180)
        self.ralph.loop('run')

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
        self.i += 1
        if (int(bird_spawner_timer.getRealTime()) + 1) % BIRD_SPAWN_INTERVAL_SECONDS == 0:
            if self.i % 2 == 0:
                self.spawner(TYPE.BIRD, random.randint(0, 2))
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
        bird.setPos(((lane-1)*0.35), -0.10, -5)#0.29
        #bird.setPos(0.35, -0.10, -5)#0.29
        bird.setScale(0.015, 0.015, 0.015)
        bird.setHpr(90, 0, 90)
        self.birds.append(bird)
    
    def spawn_box(self, lane):
        box = self.loader.loadModel("models/crate")
        box.reparentTo(render)
        box.setPos(((lane-1)*0.35), -0.7, -5)
        box.setScale(.3)
        box.setHpr(90, 0, 90)
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
    
demo = DinoRender()
demo.run()
