from direct.showbase.Loader import Loader
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from math import pi, sin, cos
from direct.actor.Actor import Actor
from panda3d.core import ClockObject

BIRD_SPAWN_INTERVAL_SECONDS = 3

bird_spawner_timer = ClockObject()

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

        self.birds = []

        # Camera setup
        self.taskMgr.add(self.setup_camera, "SetupCamera")

        # Spawn birds
        self.taskMgr.add(self.bird_spawner, "BirdSpawner")

        # Game loop
        self.taskMgr.add(self.game_loop, "GameLoop")

    def game_loop(self, task):
        for bird in self.birds:
            bird.setPos(bird, -0.2, 0, 0)
       
        return Task.cont

    
    def bird_spawner(self, task):
        if (int(bird_spawner_timer.getRealTime()) + 1) % BIRD_SPAWN_INTERVAL_SECONDS == 0:
            self.spawn_bird()
            bird_spawner_timer.reset()
        return Task.cont


    def setupCamera(self, task):
        self.camera.setHpr(90, 0, 0)
        return Task.cont

    # spawn a bird
    def spawn_bird(self):
        print("Spawn")
        bird = self.loader.loadModel("models/birds/12214_Bird_v1max_l3.obj")
        bird.reparentTo(self.scene)
        bird.setPos(0, 0, -100)
        bird.setHpr(90, 0, 90)
        self.birds.append(bird)

    def setup_camera(self, task):
        self.camera.setHpr(90, 0, 0)
        return Task.cont


app = EndlessRunner()
app.run()
app.camera.setHpr(90, 0, 0)