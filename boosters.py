from basefile import *
from ralph import *
from collision import *
from tunnel import *
import player
import scan
from pandac.PandaModules import WindowProperties

class Booster():
    def __init__(self, game, model_path, boost_call_back):
        self.model = game.loader.loadModel(model_path)
        self.call_back = boost_call_back
    def scale(self, factor):
        self.model.setScale(self.model, factor)
    def collide(self):
        self.call_back()
