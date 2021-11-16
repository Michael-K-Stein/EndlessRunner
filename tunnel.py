from basefile import *

# Code to initialize the tunnel
def init_tunnel(self):
    self.tunnel = [None] * 4

    for x in range(4):
        self.tunnel[x] = loader.loadModel('assets/models/tunnels/tunnel' + str(x) + '/tunnel')
        if x == 0:
            self.tunnel[x].reparentTo(render)
        # The rest of the segments parent to the previous one, so that by moving the front segement, the entire tunnel is moved
        else:
            self.tunnel[x].reparentTo(self.tunnel[x - 1])
        self.tunnel[x].setPos(0, 0, -TUNNEL_SEGMENT_LENGTH)

# This function is called to snap the front of the tunnel to the back to simulate traveling through it
def cont_tunnel(self):
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

    # Set up the tunnel to move one segment and then call contTunnel again to make the tunnel move infinitely
    self.tunnelMove = Sequence(
        LerpFunc(self.tunnel[0].setZ,
                    duration=TUNNEL_TIME,
                    fromData=0,
                    toData=TUNNEL_SEGMENT_LENGTH * .305), # speed
        Func(cont_tunnel, self)
    )
    self.tunnelMove.start()

def spawner_timer(self, task):
    if (int(self.bird_spawner_timer.getRealTime()) + 1) % BIRD_SPAWN_INTERVAL_SECONDS == 0:
        if random.randint(0,1) % 2 == 0:
            spawner(self, ObsticleType.BIRD, random.randint(0, 2))
        else:
            spawner(self, ObsticleType.BOX, random.randint(0, 2))
        self.bird_spawner_timer.reset()
    if random.randint(0,1000) == 7:
        spawn_prize(self, random.randint(0, 2))
    return Task.cont

def spawner(self, type, lane):
    if type is ObsticleType.BIRD:
        spawn_bird(self, lane)
    elif type is ObsticleType.BOX:
        spawn_box(self, lane)

def spawn_bird(self, lane):
    bird = self.loader.loadModel("assets/models/birds/12214_Bird_v1max_l3.obj")
    bird.reparentTo(render)
    bird.setPos(((lane-1)*MAGIC_POINT_THIRTY_FIVE), -0.10, OBSTACLE_SPWN_DEPTH)
    bird.setScale(BIRD_BASE_SCALE, BIRD_BASE_SCALE, BIRD_BASE_SCALE)
    bird.setHpr(90, 0, 90)

    col = bird.attachNewNode(CollisionNode('bird'))
    col.node().addSolid(CollisionBox(Point3(0, 2.5, 2.5), 8, 5, 5))
    if self.DEBUG:
        col.show()
    self.cTrav.addCollider(col, self.notifier)
    self.session["birds"].append(bird)

def spawn_box(self, lane):
    box = self.loader.loadModel("assets/models/crate")
    box.reparentTo(render)
    box.setPos(((lane-1)*MAGIC_POINT_THIRTY_FIVE), -0.7, OBSTACLE_SPWN_DEPTH)
    box.setScale(.3)
    box.setHpr(90, 0, 90)

    col = box.attachNewNode(CollisionNode('box'))
    col.node().addSolid(CollisionBox(Point3(0, 0, 0.46), 0.5, 0.5, 0.5))
    if self.DEBUG:
        col.show()
    self.cTrav.addCollider(col, self.notifier)
    self.session["boxes"].append(box)

def spawn_prize(self, lane):
    prize = None
    x = random.randint(0,2)
    if  x == 0:
        prize = self.loader.loadModel("assets/models/objects/soccerBall.egg")
    elif x == 1:
        prize = self.loader.loadModel("assets/models/objects/basketball.egg")
    elif x == 2:
        prize = self.loader.loadModel("assets/models/objects/toyball2.egg")
        
    prize.reparentTo(render)
    #prize.setPos(((lane-1)*MAGIC_POINT_THIRTY_FIVE), -1.3, OBSTACLE_SPWN_DEPTH)
    prize.setPos(0, -1.3, OBSTACLE_SPWN_DEPTH)
    prize.setScale(PRIZE_BASE_SCALE, PRIZE_BASE_SCALE, PRIZE_BASE_SCALE)
    col = prize.attachNewNode(CollisionNode('prize'))
    col.node().addSolid(CollisionSphere(Point3(0,2,0), 0.7))
    if self.DEBUG:
        col.show()
    self.cTrav.addCollider(col, self.notifier)

    self.session["prizes"].append(prize)

def remove_obj(self, obj):
    obj.remove_node()
    if obj in self.session["birds"]:
        self.session["birds"].remove(obj)
    elif obj in self.session["boxes"]:
        self.session["boxes"].remove(obj)
    elif obj in self.session["prizes"]:
        self.session["prizes"].remove(obj)
