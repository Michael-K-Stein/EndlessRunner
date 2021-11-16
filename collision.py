from basefile import *
from tunnel import *

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
    self.accept('ralph-into-box', handle_collision)
    self.accept('ralph-into-bird', handle_collision)
    self.accept('bird-into-ralph', handle_collision)

def player_hit(self):
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

    self.session["birds_x_speed"] = min(-BIRD_DEFAULT_SPEED, self.session["birds_x_speed"] // 2)
    self.session["object_spawn_interval_seconds"] = max(STARTING_OBJECTS_SPAWN_INTERVAL_SECONDS,
            self.session["object_spawn_interval_seconds"] // 2)
    self.session["playback_speed"] = max(1, self.session["playback_speed"] - 0.1)

    for node in self.session["birds"] + self.session["boxes"]:
        remove_obj(self, node)
    #self.hit_text.text = 'Hits: ' + str(self.hit)

def is_out_of_frame(self, obj):
    if obj.get_pos()[1] <= -0.7:
        return True
    return False


