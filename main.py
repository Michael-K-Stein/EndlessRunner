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
from panda3d.core import Texture, CardMaker
from panda3d.core import WindowProperties
from panda3d.core import NodePath
from panda3d.core import Camera
from panda3d.core import OrthographicLens

from panda3d.core import ClockObject
import scan
import cv2
from player import Player

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

bird_spawner_timer = ClockObject()
game_speed_timer = ClockObject()


class DinoRender(ShowBase):

    # Macro-like function used to reduce the amount to code needed to create the
    # on screen instructions
    def genLabelText(self, i, text):
        return OnscreenText(text=text, parent=base.a2dTopLeft, scale=.05,
                            pos=(0.06, -.065 * i), fg=(1, 1, 1, 1),
                            align=TextNode.ALeft)

    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)

        background_music = base.loader.loadSfx('./music.wav')
        background_music.setLoop(True)
        background_music.play()

        # Standard initialization stuff
        # Standard title that's on screen in every tutorial
        self.title = OnscreenText(text="Ha'ag", style=1,
            fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5), parent=base.a2dBottomRight,
            align=TextNode.ARight, pos=(-0.1, 0.1), scale=.08)

        # disable mouse control so that we can place the camera
        base.disableMouse()
        camera.setPosHpr(0, 0, 10, 0, -90, 0)
        base.setBackgroundColor(0, 0, 0)  # set the background color to black

        self.birds_x_speed = -1.5

        self.birds = []
        self.taskMgr.add(self.bird_spawner, "BirdSpawner")
        self.taskMgr.add(self.game_loop, "GameLoop")
        self.taskMgr.add(self.game_speed_acceleration, "GameSpeedAcceleration")

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

        self.accept("arrow_left", self.rotate, ["left"])
        self.accept("arrow_right", self.rotate, ["right"])

        self.accept("space", self.jump)
        self.accept("lshift", self.tuck)
        self.accept("rshift", self.tucknt)

        self.player = Player(self.set_ralph_pos)
        self.player.callibrate(TUNNEL_SEGMENT_LENGTH, TUNNEL_SEGMENT_LENGTH, 3, 3)

        self.ralph_base_y = self.ralph.getY()
        self.ralph_base_x = self.ralph.getX()
        self.ralph_rot_multiplier = 0

        # Init scanner
        self.scanner = scan.Scanner(self.scanner_callback)
        self.scanner.run_scanner()
        task = self.overlay()
        self.accept("c", self.scanner.calibrate)

    def overlay(self):
        dr = self.win.makeDisplayRegion()
        dr.setSort(20)

        myCamera2d = NodePath(Camera('myCam2d'))
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        myCamera2d.node().setLens(lens)

        myRender2d = NodePath('myRender2d')
        myRender2d.setDepthTest(False)
        myRender2d.setDepthWrite(False)
        myCamera2d.reparentTo(myRender2d)
        dr.setCamera(myCamera2d)

        h, w, _ = self.scanner.frame.shape  # accessing the width and height of the frame
        # setup panda3d scripting env (render, taskMgr, camera etc)
        # set up a texture for (h by w) rgb image
        self.tex = Texture()
        self.tex.setup2dTexture(w, h, Texture.T_unsigned_byte,
                        Texture.F_rgb)
        # set up a card to apply the numpy texture
        cm = CardMaker('card')
        self.card = myRender2d.attachNewNode(cm.generate())
        #self.card = cm.generate().reParent(self.render)
        
        WIDTHRATIO = 1
        HEIGHTRATIO = h/w
        DEPTH = 1

        self.card.setScale(WIDTHRATIO/2, DEPTH, HEIGHTRATIO)
        
        self.card.setPos(-1, 0, -1)

        self.card.setBin("fixed", 0)
        self.card.setDepthTest(False)
        self.card.setDepthWrite(False)

        return self.taskMgr.add(self.updateTex, 'video frame update')
    
    def updateTex(self, task):
        # positive y goes down in openCV, so we must flip the y coordinates
        flipped_frame = cv2.flip(self.scanner.frame, 0)
        # overwriting the memory with new frame
        self.tex.setRamImage(flipped_frame)
        self.card.setTexture(self.tex)  # now apply it to the card

        return task.cont

        

    def scanner_callback(self, action):
        if action == "JUMP":
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
        # if direction == "left":
        #     self.ralph.lane -= 1
        #     if self.ralph.lane < -1:
        #         self.ralph.lane = -1
        # elif direction == "right":
        #     self.ralph.lane += 1
        #     if self.ralph.lane > 1:
        #         self.ralph.lane = 1

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
        for bird in self.birds:
            #  -1.5, -0.05, 0 | right
            #  -1.5, -0.05, 0 | left
            bird.setPos(bird, self.birds_x_speed, 0, 0)
            if bird.getPos()[1] <= -0.408:
                print("colission!!!")
                self.birds.remove(bird)
                bird.remove_node()
        return Task.cont
    

    def game_speed_acceleration(self, task):
        if (int(game_speed_timer.getRealTime()) + 1) % GAME_SPEED_ACCELERATION_INTERVAL_SECONDS == 0:
            self.birds_x_speed += BIRDS_X_ACCELERATION
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
            # The rest of the segments parent to the previous one, so that by moving
            # the front segement, the entire tunnel is moved
            else:
                self.tunnel[x].reparentTo(self.tunnel[x - 1])
            # We have to offset each segment by its length so that they stack onto
            # each other. Otherwise, they would all occupy the same space.
            self.tunnel[x].setPos(0, 0, -TUNNEL_SEGMENT_LENGTH)
            # Now we have a tunnel consisting of 4 repeating segments with a
            # hierarchy like this:
            # render<-tunnel[0]<-tunnel[1]<-tunnel[2]<-tunnel[3]

    def initRalph(self):
        self.ralph = Actor("models/ralph",
                           {"run": "models/ralph-run",
                            "walk": "models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(.15)
        self.ralph.setPos(*RALPH_CENTER)
        self.ralph.setHpr(*RALPH_CENTER_ROT)
        self.ralph.setH(self.ralph, 180)
        self.ralph.loop('run')
        # Hanich 17 - yes it's a crime against humanity, deal with it! btw - -1 left, 0 center, 1 right
        self.ralph.__dict__['lane'] = 0

    # This function is called to snap the front of the tunnel to the back
    # to simulate traveling through it
    def contTunnel(self):
        # This line uses slices to take the front of the list and put it on the
        # back. For more information on slices check the Python manual
        self.tunnel = self.tunnel[1:] + self.tunnel[0:1]
        # Set the front segment (which was at TUNNEL_SEGMENT_LENGTH) to 0, which
        # is where the previous segment started
        self.tunnel[0].setZ(0)
        # Reparent the front to render to preserve the hierarchy outlined above
        self.tunnel[0].reparentTo(render)
        # Set the scale to be apropriate (since attributes like scale are
        # inherited, the rest of the segments have a scale of 1)
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

    def bird_spawner(self, task):
        if (int(bird_spawner_timer.getRealTime()) + 1) % BIRD_SPAWN_INTERVAL_SECONDS == 0:
            self.spawn_bird()
            bird_spawner_timer.reset()
        return Task.cont

    def spawn_bird(self):
        print("Spawn")
        bird = self.loader.loadModel("models/birds/12214_Bird_v1max_l3.obj")
        bird.reparentTo(render)
        bird.setPos(0, -0.4, -5)
        bird.setScale(.03)
        bird.setHpr(90, 0, 90)
        self.birds.append(bird)

demo = DinoRender()
demo.run()
