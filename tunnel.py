from basefile import *
from boosters import *

TUNNELS_COUNT = 8

# Code to initialize the tunnel
def init_tunnel(self):
    self.tunnel = [None] * TUNNELS_COUNT
    init_tunnel_models(self)
    # for x in range(TUNNELS_COUNT):
    #     #self.tunnel[x] = loader.loadModel('assets/models/tunnels/tunnel' + str(0) + '/tunnel')
    #     self.tunnel[x] = loader.loadModel('assets/models/tunnels/tunnel_day/tunnel')
    #     if x == 0:
    #         self.tunnel[x].reparentTo(render)
    #     # The rest of the segments parent to the previous one, so that by moving the front segement, the entire tunnel is moved
    #     else:
    #         self.tunnel[x].reparentTo(self.tunnel[x - 1])
    #     self.tunnel[x].setPos(0, 0, -TUNNEL_SEGMENT_LENGTH)
    #     add_tunnel_props(self, self.tunnel[x])

def remodel_tunnels(self, v=-1):
    if self.tunnel[TUNNELS_COUNT-1] is not None:
        self.tunnel[TUNNELS_COUNT-1].removeNode()
        #self.tunnel[TUNNELS_COUNT-1] = loader.loadModel('assets/models/tunnels/tunnel' + str(v) + '/tunnel')
        self.tunnel[TUNNELS_COUNT-1] = loader.loadModel(f'assets/models/tunnels/tunnel_{v}/tunnel')
        # The rest of the segments parent to the previous one, so that by moving the front segement, the entire tunnel is moved
        self.tunnel[TUNNELS_COUNT-1].reparentTo(self.tunnel[TUNNELS_COUNT-2])
        self.tunnel[TUNNELS_COUNT-1].setPos(0, 0, -TUNNEL_SEGMENT_LENGTH)
        add_tunnel_props(self, self.tunnel[TUNNELS_COUNT-1])

def init_tunnel_models(self):
    create_tunnel_seg(self, 0, render, 'day')#self.session["tunnel_type"]
    for x in range(1, TUNNELS_COUNT):
        create_tunnel_seg(self, x, self.tunnel[x - 1], 'day')

def change_type_grandually(self, type):
    if self.tunnel[TUNNELS_COUNT - 1] is not None:
        self.tunnel[TUNNELS_COUNT - 1].removeNode()
    create_tunnel_seg(self, TUNNELS_COUNT - 1, self.tunnel[TUNNELS_COUNT - 2], type)

def create_tunnel_seg(self, index, parent, type):
    x = index
    #self.tunnel[TUNNELS_COUNT-1] = loader.loadModel('assets/models/tunnels/tunnel' + str(v) + '/tunnel')
    self.tunnel[x] = loader.loadModel(f'assets/models/tunnels/tunnel_{type}/tunnel')
    # The rest of the segments parent to the previous one, so that by moving the front segement, the entire tunnel is moved
    self.tunnel[x].reparentTo(parent)
    self.tunnel[x].setPos(0, 0, -TUNNEL_SEGMENT_LENGTH)
    add_tunnel_props(self, self.tunnel[x])

# This function is called to snap the front of the tunnel to the back to simulate traveling through it
def cont_tunnel(self):
    #self.tunnel_counter += 1
    #if self.tunnel_counter % 16 == 0:
    #    self.tunnel_color = random.randint(0,3)
    if "session" in self.__dict__:
        TUNNEL_VERAETIES = 4  # THATS HOW ITS WRITTEN IDC WHAT YOU SAY
        SCORE_TIME_MULTIPLE = 10000
        time_cycle = self.session["score"] % ((TUNNEL_VERAETIES - 1) * 2 * SCORE_TIME_MULTIPLE)  # For each type, we have 1 day
        
        if time_cycle // SCORE_TIME_MULTIPLE % 2 == 0:
            self.session["tunnel_type"] = "day"
        elif time_cycle <= 1 * SCORE_TIME_MULTIPLE:
            self.session["tunnel_type"] = "night"
        elif time_cycle <= 3 * SCORE_TIME_MULTIPLE:
            self.session["tunnel_type"] = "jungle"
        elif time_cycle <= 5 * SCORE_TIME_MULTIPLE:
            self.session["tunnel_type"] = "modern"
        change_type_grandually(self, self.session["tunnel_type"])
    # remodel_tunnels(self, self.tunnel_color)

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
                    duration=TUNNEL_TIME / (self.session["game_speed"] / -GAME_DEFAULT_SPEED),
                    fromData=0,
                    toData=TUNNEL_SEGMENT_LENGTH * .305), # speed
        Func(cont_tunnel, self)
    )
    self.tunnelMove.start()

    #add_tunnel_props(self)

def add_tunnel_props(self, tunnel):
    pipe = self.loader.loadModel("assets\\models\\tunnel_varients\\RustPipe.obj")
    pipe.reparentTo(tunnel)
    alight = AmbientLight('alight')
    alight.setColor((1, 1, 1, 1))
    alnp = pipe.attachNewNode(alight)
    pipe.setLight(alnp)

    if random.randint(0, 3) == 1:
        knife = self.loader.loadModel("assets/models/tunnel_varients/Knife/Knife")
        knife.setScale(0.05)
        knife.setPos(9,-4,0)
        knife.setP(45)
        knife.reparentTo(tunnel)

    if random.randint(0, 4) == 1:
        switch = self.loader.loadModel("assets/models/tunnel_varients/Switch/Switch")
        switch.setScale(3)
        switch.setPos(-9.5,0,0)
        switch.setHpr(90, 180, 90)
        switch.reparentTo(tunnel)

    if random.randint(0, 15) == 1:
        skeleton = self.loader.loadModel("assets/models/tunnel_varients/Skeleton/Skeleton")
        skeleton.setPos(9,0,3)
        skeleton.setHpr(70, 0, 90)
        skeleton.reparentTo(tunnel)

def spawner_timer(self, task):
    if (int(self.bird_spawner_timer.getRealTime()) + 1) % self.session['object_spawn_interval_seconds'] == 0:
        for _ in range(random.randint(1, 4)):
            if random.randint(0,1) % 2 == 0:
                spawner(self, ObsticleType.BIRD, random.randint(0, 2))
            else:
                spawner(self, ObsticleType.BOX, random.randint(0, 2))
        self.bird_spawner_timer.reset()
    if random.randint(0,PRIZE_CHANCE) == 7:
        spawn_prize(self, random.randint(0, 2))
    return Task.cont

def spawner(self, type, lane):
    if type is ObsticleType.BIRD:
        spawn_bird(self, lane)
    elif type is ObsticleType.BOX:
        spawn_box(self, lane)

def spawn_bird(self, lane):
    bird = self.loader.loadModel("assets/models/bluebird/bluebird")
    bird.reparentTo(render)
    bird.setPos(((lane - 1) * MAGIC_POINT_THIRTY_FIVE), -0.10, OBSTACLE_SPWN_DEPTH-2)
    bird.setScale(BIRD_BASE_SCALE)
    bird.setHpr(90, 90, 90)

    col = bird.attachNewNode(CollisionNode('bird'))
    col.node().addSolid(CollisionBox(Point3(0, 0.25, 0.25), 0.75, 0.25, 0.25))
    if self.DEBUG:
        col.show()
    self.cTrav.addCollider(col, self.notifier)
    self.session["birds"].append(bird)

def spawn_box(self, lane):
    box = self.loader.loadModel("assets/models/robot/Robot")
    box.reparentTo(render)
    box.setPos(((lane-1)*0.5), -0.7, OBSTACLE_SPWN_DEPTH)
    box.setScale(BOX_BASE_SCALE)
    box.setHpr(90, 90, 90)

    col = box.attachNewNode(CollisionNode('box'))
    col.node().addSolid(CollisionBox(Point3(0, 0, 0), 2, 2, 2))
    if self.DEBUG:
        col.show()
    self.cTrav.addCollider(col, self.notifier)
    self.session["boxes"].append(box)

def spawn_prize(self, lane):
    prize = None
    extra_scale_factor = 1
    x = random.randint(0,3)
    if  x == 0:
        prize = self.loader.loadModel("assets/models/objects/soccerBall.egg")
    elif x == 1:
        prize = self.loader.loadModel("assets/models/objects/basketball.egg")
    elif x == 2:
        prize = self.loader.loadModel("assets/models/objects/toyball2.egg")
    elif x == 3:
        spawn_boosters(self)
        return
        """prize_light = AmbientLight('alight')
        prize_light.setColor((0.2, 0.2, 0.2, 1))
        plnp = prize.attachNewNode(prize_light)
        prize.setLight(plnp)
        prize.showTightBounds()
        prize.setScale(0.003, 0.003, 0.003)
        prize.setHpr(0, 0, 45)"""


    prize.reparentTo(render)
    prize.setPos(((lane - 1) * 0.7), -0.7, OBSTACLE_SPWN_DEPTH)
    prize.setScale(PRIZE_BASE_SCALE, PRIZE_BASE_SCALE, PRIZE_BASE_SCALE)
    col = prize.attachNewNode(CollisionNode('prize'))
    col.node().addSolid(CollisionSphere(Point3(0,0,0), 0.7))
    if self.DEBUG:
        col.show()
    self.cTrav.addCollider(col, self.notifier)

    self.session["prizes"].append(prize)

def spawn_boosters(self):
    booster = Booster(self, "assets/models/objects/scooter/Scooter2.egg", self.scooter_boost)
    booster.model.setPos(0, -0.7, OBSTACLE_SPWN_DEPTH)
    booster.model.setHpr(0,-90,0)
    booster.scale(0.1)
    booster.model.reparentTo(render)
    self.session["boosters"].append(booster)

def remove_obj(self, obj):
    if type(obj) is not Booster:
        obj.remove_node()
        if obj in self.session["birds"]:
            self.session["birds"].remove(obj)
        elif obj in self.session["boxes"]:
            self.session["boxes"].remove(obj)
        elif obj in self.session["prizes"]:
            self.session["prizes"].remove(obj)
        else:
            pass
    else:
        obj.model.remove_node()
        self.session["boosters"].remove(obj)
