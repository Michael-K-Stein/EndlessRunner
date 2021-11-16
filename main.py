from basefile import *
from ralph import *
from collision import *
from tunnel import *
import player
import scan

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.DEBUG = False
        if "debug" in sys.argv:
            self.DEBUG = True

        init_collision_detection(self)
        self.init_music()

        self.title = OnscreenText(text="Haag", style=1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5), parent=base.a2dBottomRight, align=TextNode.ARight, pos=(-0.05, 0.05), scale=.08)
        self.hit_text = OnscreenText(text="Hits: 0", style=1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5), parent=base.a2dTopLeft, align=TextNode.ALeft, pos=(0.008, -0.09), scale=.08)

        base.disableMouse()
        camera.setPosHpr(0, 0, 10, 0, -90, 0)
        base.setBackgroundColor(0, 0, 0)
        
        init_tunnel(self)
        self.init_fog()
        init_ralph(self)
        init_ralph_physics(self)
        cont_tunnel(self)

        self.bird_spawner_timer = ClockObject()
        self.game_speed_timer = ClockObject()

        self.register_keys()

        # Where ralph is if he were standing (for laning)
        self.ralph_base_y = self.ralph.getY()
        self.ralph_base_x = self.ralph.getX()
        self.ralph_rot_multiplier = 0

        # Init scanner
        if not self.DEBUG:
            self.scanner = scan.Scanner(self.scanner_callback)
            self.scanner.run_scanner()
            task = scan.overlay(self)
            self.accept("c", self.scanner.calibrate)

        self.show_menu()

    def create_game_session(self):
        self.session = {
            "birds": [],
            "boxes": [],
            "time": 0,
            "score": 0,
            "score_last_update_time": 0,
            "hearts_counter": 3,
            "birds_x_speed": 0,
            "playback_speed": 1,
            "hearts_obj": [
                OnscreenImage(image='assets/images/heart.png', pos=(-0.08, 0, -0.08), scale=0.08, parent=base.a2dTopRight),
                 OnscreenImage(image='assets/images/heart.png', pos=(-0.23, 0, -0.08), scale=0.08, parent=base.a2dTopRight),
                  OnscreenImage(image='assets/images/heart.png', pos=(-0.38, 0, -0.08), scale=0.08, parent=base.a2dTopRight)][::-1]}

    def register_keys(self):
        self.accept("arrow_left", rotate, [self, "left"])
        self.accept("arrow_right", rotate, [self, "right"])
        self.accept("space", self.player.start_jump)
        self.accept("lshift", tuck, [self])
        self.accept("rshift", tucknt, [self])
        self.accept("r", self.quit_game)
        self.accept("p", self.scanner_callback, ["JUMP"])
        self.accept("l", self.show_menu)

    def show_menu(self):
        self.stop_tasks()
        self.scanner = scan.Scanner(self.scanner_callback)
        self.scanner.run_scanner()
        self.gameMenu = DirectDialog(frameSize = (-10, 10, -10, 10), fadeScreen = 0.4, relief = DGG.FLAT)
        DirectFrame(parent=self.gameMenu, image = "assets/models/background.jpg", sortOrder = (-1), pos=(0.076,0,0), scale=3.7)
        # OnscreenText(text="Jump To Start...", parent=self.gameMenu, scale=0.1, pos = (0,-0.2))
        self.labels = [OnscreenText(text="Keep camera aligned with the ceiling", fg=(0,0,0,255), bg=(255,255,255,255), parent=self.gameMenu, scale=0.08, pos = (0,-0.19)),
                  OnscreenText(text="Wait to calibrating...", parent=self.gameMenu, scale=0.07, pos = (0,-0.29))]
        OnscreenImage(parent=self.gameMenu, image = 'assets/models/title2.PNG', pos = (0,0,0.3), scale=0.3)

        DirectButton(text = "Calibrate",
                   command = self.scanner.calibrate,
                   pos = (0, 0, -0.4),
                   parent = self.gameMenu,
                   scale = 0.07)
        DirectButton(text = "Quit",
                   command = self.quit_game,
                   pos = (0, 0, -0.6),
                   parent = self.gameMenu,
                   scale = 0.07)

    def start_tasks(self):
        self.tasks_running = True
        self.taskMgr.add(lambda task: spawner_timer(self, task), "Spawner")
        self.taskMgr.add(self.game_loop, "GameLoop")
        self.taskMgr.add(self.game_speed_acceleration, "GameSpeedAcceleration")
        self.background_music.play()

    def stop_tasks(self):
        self.tasks_running = False
        self.taskMgr.remove("Spawner")
        self.taskMgr.remove("GameLoop")
        self.taskMgr.remove("GameSpeedAcceleration")
        self.scanner.stop()
        self.background_music.stop()

    def start_game(self):
        self.create_game_session()
        self.gameMenu.hide()
        self.session["birds_x_speed"] = (-BIRD_DEFAULT_SPEED * 10) if self.DEBUG else -BIRD_DEFAULT_SPEED 
        for node in self.session["birds"] + self.session["boxes"]:
            node.remove_node()

        for x in self.session["hearts_obj"]:
            x.setTransparency(1)

        self.start_tasks()
        self.init_music()
        self.session["playback_speed"] = 1
        self.session["hit"] = 0

    def quit_game(self):
        self.scanner.stop()
        sys.exit(0)

    def init_music(self):
        self.background_music = base.loader.loadSfx('assets/music/music.wav')
        self.background_music.setLoop(True)
        self.playback_speed = 1
    
    def init_fog(self):
        self.fog = Fog('distanceFog')
        self.fog.setColor(0, 0, 0)
        self.fog.setExpDensity(FOG_EXPIRY_DENSITY)
        render.setFog(self.fog)

    def scanner_callback(self, action):
        if action == "JUMP":
            if not self.tasks_running:
                self.start_game()
            self.player.start_jump()
        elif action == "TOOK":
            tuck(self)
        elif action == "CENTER":
            rotate(self, 0)
            tucknt(self)
        elif action == "LEFT":
            rotate(self, -1)
            tucknt(self)
        elif action == "RIGHT":
            rotate(self, 1)
            tucknt(self)
        elif action == "CALIBRATED":
            self.labels[0].setText("Jump to start...")
            self.labels[0].setPos((0,-0.2))
            self.labels[0].setScale(0.1)
            self.labels[1].setText("")

    def game_loop(self, task):
        self.player.update(self, globalClock.getDt())
        for box in self.session["boxes"]:
            box.setPos(box, self.session["birds_x_speed"] / (7*5), 0, 0)
            if is_out_of_frame(self, box):
                remove_obj(self, box)

        for bird in self.session["birds"]:
            bird.setPos(bird, self.session["birds_x_speed"], 0, math.sin(bird.getZ()) / 10)#-0.1
            if is_out_of_frame(self, bird):
                remove_obj(self, bird)
            #TODO - Michael: bird.setHpr(0, math.sin(bird.getZ()) / 5, 0)
        

        self.session["time"] += globalClock.getDt()
        if self.session["time"] > self.session["score_last_update_time"] + 0.2:
            self.session["score_last_update_time"] = self.session["time"]
            self.session["score"] += -self.session["birds_x_speed"] * 0.2
        self.hit_text.text = 'Score: ' + str(int(self.session["score"]))

        return Task.cont

    def game_speed_acceleration(self, task):
        if (int(self.game_speed_timer.getRealTime()) + 1) % GAME_SPEED_ACCELERATION_INTERVAL_SECONDS == 0:
            self.session["birds_x_speed"] += BIRDS_X_ACCELERATION
            self.session["playback_speed"] += 0.002
            self.background_music.setPlayRate(self.playback_speed)
            # self.birds_y_speed += BIRDS_X_ACCELERATION
            self.game_speed_timer.reset()
        return Task.cont
    
game = Game()
game.run()
