from basefile import *
from ralph import *
from collision import *
from tunnel import *
import player
import scan
from pandac.PandaModules import WindowProperties

SPEED_BOOST_TIME = 5
SPEED_BOOST_MULTIPLIER = 3


class Booster():
    def __init__(self, game, model_path, boost_call_back):
        self.model = game.loader.loadModel(model_path)
        self.real_model = game.loader.loadModel(model_path)
        self.real_model.setPos(0,0,0)
        self.real_model.reparentTo(self.model)
        self.call_back = boost_call_back
    def scale(self, factor):
        self.model.setScale(self.model, 0.001)
        self.model.setScale(self.real_model, 1/0.001)
        self.model.setScale(self.model, factor)
        self.scale_factor = factor
    def get_scale(self):
        return self.scale_factor
    def collide(self):
        self.real_model.setH(0)
        self.call_back(self)
    def update(self):
        self.real_model.setH(self.real_model, 3)
