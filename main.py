from direct.showbase.Loader import Loader
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from math import pi, sin, cos
from direct.actor.Actor import Actor
from panda3d.core import ClockObject

timer = ClockObject()

class EndlessRunner(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # Load the environment model        
        self.scene = self.loader.loadModel("models/tunnel/tunnel.egg.pz")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the scene.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(0, 0, 0)
        self.scene.setHpr(180, 90, 270)

        # Camera setup
        #self.camera.setHpr(90, 0, 0)
        #self.camera.setPos(100, 100, 0)
        self.accept("space", self.spawn_bird, ["fire", 1])

        # Add the spinCameraTask procedure to the task manager.
        #self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        #self.taskMgr.
        self.taskMgr.add(self.setupCamera, "SetupCamera")

        

    def setupCamera(self, task):
        # if int(task.time) % 3 == 0:
            # print(task.time)
        self.camera.setHpr(90, 0, 0)
        return Task.cont

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 30.0
        print(angleDegrees)
        angleRadians = angleDegrees * (pi / 180.0)
        if int(angleDegrees) % 50 != 0:
            self.camera.setHpr(90, 0, 0)
            return Task.cont
        #self.camera.setPos(20 * sin(angleRadians), -20 * cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        
        return Task.cont


    # spawn a bird
    def spawn_bird(self, key, val):
        print("Spawn")
        bird = self.loader.loadModel("models/birds/12214_Bird_v1max_l3.obj")
        bird.reparentTo(self.scene)
        bird.setPos(0, 0, -100)
        bird.setHpr(90, 0, 0)

app = EndlessRunner()
app.run()
app.camera.setHpr(90, 0, 0)