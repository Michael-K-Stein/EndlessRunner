from basefile import *
from tunnel import *

def handle_prize_collision(self, entry):
    self.session["score"] += PRIZE_REWARD

def handle_boost_collision(self, boost):
    boost.collide()

def init_collision_detection(self):
    self.cTrav = CollisionTraverser()

    if self.DEBUG:
        self.cTrav.showCollisions(self.render)

    self.notifier = CollisionHandlerEvent()

    self.notifier.addInPattern('%fn-into-%in')
    self.notifier.addAgainPattern('%fn-again-%in')

    def handle_collision(entry):
        player_hit(self)

    # magic. Do not touch!
    self.accept('box-into-ralph', handle_collision)
    #self.accept('ralph-into-box', handle_collision)
    #self.accept('ralph-into-bird', handle_collision)
    self.accept('bird-into-ralph', handle_collision)
    #self.accept('prize-into-ralph', handle_prize_collision)
    #self.accept('ralph-into-prize', handle_prize_collision)

def player_hit(self):
    if self.session["player_immune"]:
        return

    self.hit_soundeffect.play()

    self.session["hit"] += 1
    if self.DEBUG:
        print(self.session["hit"])
    self.hit_text.text = 'Hits: ' + str(self.session["hit"])
    if self.session["hearts_counter"] > 1:
        self.session["hearts_obj"][self.session["hearts_counter"] - 1].setImage('assets/images/broken_heart.png')
        self.session["hearts_obj"][self.session["hearts_counter"] - 1].setTransparency(1)
    else:
        self.show_menu()
    self.session["hearts_counter"] -= 1

    #self.session["game_speed"] = min(-GAME_DEFAULT_SPEED, self.session["game_speed"] // 2)
    self.session["object_spawn_interval_seconds"] = max(STARTING_OBJECTS_SPAWN_INTERVAL_SECONDS,
            self.session["object_spawn_interval_seconds"] // 2)
    self.session["playback_speed"] = max(1, self.session["playback_speed"] - 0.1)

    self.start_immune(3)

def prize_collision(self, prize):
<<<<<<< HEAD
    if self.ralph.getX() == prize.getX() \
            and math.ceil(prize.getZ()) == math.ceil(self.ralph.getZ()): # Dirty collision check
        handle_prize_collision(self, None)
        remove_obj(self, prize)
        self.prize_soundeffect.play()
=======
    if prize.getZ() >= self.ralph.getZ():
        if self.ralph.getX() == 0:
            if self.ralph.getY() < 0:
                handle_prize_collision(self, None)
                remove_obj(self, prize)
                self.prize_soundeffect.play()
>>>>>>> e2b6866ef8853e719b2d58f589f15964b97150ca

def boost_collision(self, boost):
    if boost.model.getZ() >= self.ralph.getZ(): 
        if self.ralph.getX() == 0:
            if self.ralph.getY() < 0:
                handle_boost_collision(self, boost)
                remove_obj(self, boost)
                self.prize_soundeffect.play()

def is_out_of_frame(self, obj):
    if obj not in self.session["prizes"]:
        if obj.get_pos()[1] <= -0.7:
            return True
    else:
        if obj.get_pos()[2] >= 10:
            return True
    return False


