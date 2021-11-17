from basefile import *
from player import *

# initialize the runner
def init_ralph(self):
    self.ralph = Actor("assets/models/ralph", {"run": "assets/models/ralph-run", "walk": "assets/models/ralph-walk"})
    self.ralph.reparentTo(render)
    self.ralph.setScale(.15, 0.10, 0.15)
    self.ralph.setScale(self.ralph, 1, 1, 1.2)
    self.ralph.setPos(*RALPH_CENTER)
    self.ralph.setHpr(*RALPH_CENTER_ROT)
    self.ralph.setH(self.ralph, 180)
    self.ralph.setTransparency(TransparencyAttrib.MAlpha)
    self.ralph.setAlphaScale(0.35)
    self.ralph.loop('run')
    self.ralph.__dict__['lane'] = 0

    self.ralph.collider = self.ralph.attachNewNode(CollisionNode('ralph'))
    self.ralph.collider.node().addSolid(
        CollisionPolygon(Point3(-0.8, 0, 0),Point3(-0.8,0,7),Point3(0.8,1,7),Point3(0.8,1,0))
        )
    if self.DEBUG:
        self.ralph.collider.show()
    self.cTrav.addCollider(self.ralph.collider, self.notifier)

def set_ralph_pos(self, x, y):
    self.ralph.setPos(self.ralph_base_x + ((y/MAGIC_RALPH_LOCATION_SCALE_FACTOR)*self.ralph_rot_multiplier), (y/MAGIC_RALPH_LOCATION_SCALE_FACTOR) + self.ralph_base_y, 5.5)

def init_ralph_physics(self):
    self.player = Player(self.DEBUG, set_ralph_pos)
    self.player.calibrate(TUNNEL_SEGMENT_LENGTH, TUNNEL_SEGMENT_LENGTH, 3, 3)

def rotate(self, lane):
    if lane == "right":
        self.ralph.lane += 1
        if self.ralph.lane > 1:
            self.ralph.lane = 1
    elif lane == "left":
        self.ralph.lane -= 1
        if self.ralph.lane < -1:
            self.ralph.lane = -1
    else:
        self.ralph.lane = lane

    if self.DEBUG:
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

def tuck(self):
    self.ralph.setScale(RALPH_BASE_SCALE,RALPH_BASE_SCALE,RALPH_BASE_SCALE*0.5)

def tucknt(self):
    self.ralph.setScale(RALPH_BASE_SCALE,0.10,RALPH_BASE_SCALE)
    self.ralph.setScale(self.ralph, 1, 1, 1.2)