from basefile import *
from ralph import *
from collision import *
from tunnel import *
import player
import scan
import queue
from pandac.PandaModules import WindowProperties

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
        self.highscore_text = OnscreenText(text="Highscore: 0", style=1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5), parent=base.a2dTopLeft, align=TextNode.ALeft, pos=(0.008, -0.18), scale=.08)
        self.lastscore_text = 0

        self.tunnel_color = 0
        self.tunnel_counter = 0
        self.tunnels_moving = False

        props = WindowProperties()
        props.setTitle('Haag Simulator')
        base.win.requestProperties(props)

        base.disableMouse()
        camera.setPosHpr(0, 0, 10, 0, -90, 0)
        base.setBackgroundColor(FOG_LUMINECENSE, FOG_LUMINECENSE, FOG_LUMINECENSE)

        init_tunnel(self)
        self.init_fog()
        init_ralph(self)
        init_ralph_physics(self)

        self.bird_spawner_timer = ClockObject()
        self.game_speed_timer = ClockObject()

        self.register_keys()

        # Where ralph is if he were standing (for laning)
        self.ralph_base_y = self.ralph.getY()
        self.ralph_base_x = self.ralph.getX()
        self.ralph_rot_multiplier = 0

        self.high_score = 0

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
            "prizes": [],
            "boosters": [],
            "time": 0,
            "last_tunnel_remodel_time": 0,
            "score": 0,
            "score_last_update_time": 0,
            "object_spawn_interval_seconds": STARTING_OBJECTS_SPAWN_INTERVAL_SECONDS,
            "hearts_counter": 3,
            "game_speed": GAME_DEFAULT_SPEED,
            "tmp_accelerate": 0,
            "speed_boost": False,
            "score_boost": False,
            "sleep_boost": False,
            "playback_speed": 1,
            "hearts_obj": [
                OnscreenImage(image='assets/images/heart.png', pos=(-0.38, 0, -0.08), scale=0.08, parent=base.a2dTopRight),
                 OnscreenImage(image='assets/images/heart.png', pos=(-0.23, 0, -0.08), scale=0.08, parent=base.a2dTopRight),
                 OnscreenImage(image='assets/images/heart.png', pos=(-0.08, 0, -0.08), scale=0.08, parent=base.a2dTopRight)],
            "player_immune": False,
            "player_immune_start": 0,
            "immune_duration": 3,
            "tunnel_type": "day"
        }
        if not self.tunnels_moving:
            cont_tunnel(self)
            self.tunnels_moving = True

    def register_keys(self):
        self.accept("arrow_left", rotate, [self, "left"])
        self.accept("arrow_right", rotate, [self, "right"])
        self.accept("space", self.player.start_jump)
        self.accept("lshift", tuck, [self])
        self.accept("rshift", tucknt, [self])
        for exit_key in ['r', 'esc']:
            self.accept(exit_key, self.quit_game)
        self.accept("p", self.scanner_callback, ["JUMP"])
        self.accept("l", self.show_menu)

    def show_menu(self):
        self.stop_tasks()
        if not self.DEBUG:
            self.scanner = scan.Scanner(self.scanner_callback)
            self.scanner.run_scanner()
        self.gameMenu = DirectDialog(frameSize = (-10, 10, -10, 10), fadeScreen = 0.4, relief = DGG.FLAT)
        DirectFrame(parent=self.gameMenu, image = "assets/models/background.jpg", sortOrder = (-1), pos=(0.076,0,0), scale=3.7)
        # OnscreenText(text="Jump To Start...", parent=self.gameMenu, scale=0.1, pos = (0,-0.2))
        self.labels = [OnscreenText(text="Keep camera aligned with the ceiling", fg=(0,0,0,255), bg=(255,255,255,255), parent=self.gameMenu, scale=0.08, pos = (0,-0.19)),
                  OnscreenText(text="Wait for calibration...", parent=self.gameMenu, scale=0.07, pos = (0,-0.29)),
                  OnscreenText(text="(White Circle => Good | Red Circle => Bad)", parent=self.gameMenu, scale=0.04, pos = (0,-0.39)),
                  OnscreenText(text=f"High score: {int(self.high_score)}\t Score: {int(self.lastscore_text)}" , parent=self.gameMenu, scale=0.07, pos = (-0.1,-0.50))]
        OnscreenImage(parent=self.gameMenu, image = 'assets/models/title2.PNG', pos = (0,0,0.3), scale=0.3)

    def start_tasks(self):
        self.tasks_running = True
        self.taskMgr.add(lambda task: spawner_timer(self, task), "Spawner")
        self.taskMgr.add(self.game_loop, "GameLoop")
        self.taskMgr.add(self.game_speed_acceleration, "GameSpeedAcceleration")
        self.taskMgr.add(self.manage_music, "MusicTrackManager")

    def stop_tasks(self):
        self.tasks_running = False
        self.taskMgr.remove("Spawner")
        self.taskMgr.remove("GameLoop")
        self.taskMgr.remove("GameSpeedAcceleration")
        if not self.DEBUG:
            self.scanner.stop()
        self.taskMgr.remove("MusicTrackManager")
        self.current_playing_music.stop()

    def start_game(self):
        if "session" in dir(self):
            for node in self.session["birds"] + self.session["boxes"] + self.session["prizes"] + self.session["boosters"]:
                node.remove_node()
        self.create_game_session()
        self.gameMenu.hide()
        self.session["game_speed"] = (-GAME_DEFAULT_SPEED * 1) if self.DEBUG else -GAME_DEFAULT_SPEED

        for x in self.session["hearts_obj"]:
            x.setTransparency(1)

        self.start_tasks()
        self.init_soundeffects()
        self.session["playback_speed"] = 1
        self.session["hit"] = 0

    def quit_game(self):
        if not self.DEBUG:
            self.scanner.stop()
        sys.exit(0)

    def init_soundeffects(self):
        self.hit_soundeffect   = base.loader.loadSfx('assets/soundeffects/hit.mp3')
        self.prize_soundeffect = base.loader.loadSfx('assets/soundeffects/prize_soundeffect.mp3')

    def init_music(self):
        music_files = [os.path.join(MUSIC_FILES_PATH, file) for file in os.listdir(MUSIC_FILES_PATH) if os.path.isfile(os.path.join(MUSIC_FILES_PATH, file))]
        print(music_files)
        
        self.music_queue = queue.Queue()
        for file in music_files:
            self.music_queue.put(base.loader.loadSfx(file))
        
        # For now, let's take the first track in the queue and just play it, although it's a bit dirty
        self.current_playing_music = self.music_queue.get()
        self.current_playing_music.setLoopCount(random.randint(2, 4))
        self.current_playing_music.play()
    
    def manage_music(self, task):
        if self.current_playing_music.status() == AudioSound.READY: # Checks if the sound track has ended
            next_track = self.music_queue.get()
            self.music_queue.put(self.current_playing_music)
            next_track.setLoopCount(random.randint(2, 4))
            self.current_playing_music = next_track
            self.current_playing_music.play()
        return Task.cont
   
    def init_fog(self):
        self.fog = Fog('distanceFog')
        self.fog.setColor(FOG_LUMINECENSE, FOG_LUMINECENSE, FOG_LUMINECENSE)
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
            if "labels" in dir(self):
                self.labels[0].setText("Jump to start...")
                self.labels[0].setPos(0,-0.2)
                self.labels[0].setScale(0.1)
                self.labels[1].setText("")
        elif action == "CAMERA":
            if "labels" in dir(self):
                self.labels[0].setText("Camera can't fully see you")


    def game_loop(self, task):
        self.player.update(self, globalClock.getDt())
        for box in self.session["boxes"]:
            box.setPos(box, 0, -self.session["game_speed"] / BOX_BASE_SCALE, 0)
            if is_out_of_frame(self, box):
                remove_obj(self, box)

        for bird in self.session["birds"]:
            #bird.setPos(bird, self.session["birds_x_speed"], 0, math.sin(bird.getZ()) / 10)#-0.1
            bird.setPos(bird, 0, -self.session["game_speed"] / BIRD_BASE_SCALE, math.sin(bird.getZ()) / 40)#-0.1
            if is_out_of_frame(self, bird):
                remove_obj(self, bird)
            #TODO - Michael: bird.setHpr(0, math.sin(bird.getZ()) / 5, 0)

        for prize in self.session["prizes"]:
            prize.setPos(prize, 0, 0, -self.session["game_speed"] / PRIZE_BASE_SCALE)
            if is_out_of_frame(self, prize) or prize_collision(self, prize):
                remove_obj(self, prize)

        for boost in self.session["boosters"]:
            boost.model.setPos(boost.model, 0, self.session["game_speed"] / boost.get_scale(), 0)
            boost.update()
            if is_out_of_frame(self, boost.model) or boost_collision(self, boost):
                remove_obj(self, boost)

        self.session["time"] += globalClock.getDt()
        if self.session["time"] > self.session["score_last_update_time"] + 0.2:
            self.session["score_last_update_time"] = self.session["time"]
            self.session["score"] += -self.session["game_speed"] * 20
            score_addr = -self.session["game_speed"] * 20
            if self.session["score_boost"]:
                score_addr *= SCORE_BOOST_MULTIPLIER
            self.session["score"] += score_addr
        
        self.hit_text.text = f'Score: {int(self.session["score"])}'
        self.highscore_text.text = f'Highscore: {int(self.high_score)}'
        
        if self.session["score"] > self.high_score:
            self.high_score = self.session["score"]

        if self.session["player_immune"]:
            self.ralph.setAlphaScale(0.35 + math.sin(self.session["time"] * 10)/2)

        return Task.cont

    def game_speed_acceleration(self, task):
        if (int(self.game_speed_timer.getRealTime()) + 1) % GAME_SPEED_ACCELERATION_INTERVAL_SECONDS == 0:
            if self.session["game_speed"] > -MAX_GAME_SPEED:
                self.session["game_speed"] += GAME_ACCELERATION
            if self.session["playback_speed"] < MAX_BACKGROUND_MUSIC_SPEED:
                self.session["playback_speed"] += 0.002
            # self.background_music.setPlayRate(self.playback_speed)
            self.current_playing_music.setPlayRate(self.session["playback_speed"])
            # self.birds_y_speed += BIRDS_X_ACCELERATION
            self.game_speed_timer.reset()
        return Task.cont

    def scooter_boost(self, boost):
        if not self.session["speed_boost"]:
            boost.real_model.reparentTo(self.ralph)
            boost.real_model.setPos(0,0,0)
            self.session["game_speed"] = SPEED_BOOST_MULTIPLIER*self.session["game_speed"]
            self.session["speed_boost"] = True
            #self.session["tmp_accelerate"] = self.getRealTime() + 5

            self.start_immune(5)

            myTask = self.taskMgr.doMethodLater(SPEED_BOOST_TIME, self.stop_scooter_boost, 'stop_speed_boost', extraArgs = [boost], appendTask=True)

    def stop_scooter_boost(self, boost, task):
        self.session["game_speed"] /= SPEED_BOOST_MULTIPLIER
        boost.real_model.remove_node()
        self.session["speed_boost"] = False

    def dragon_boost(self, boost):
        boost.real_model.reparentTo(self.ralph)
        boost.real_model.setPos(0,0,5)
        boost.real_model.setH(45)
        boost.real_model.setScale(0.1)
        self.session["score_boost"] = True
        myTask = self.taskMgr.doMethodLater(SPEED_BOOST_TIME, self.stop_dragon_boost, 'stop_dragon_boost', extraArgs = [boost], appendTask=True)
    def stop_dragon_boost(self, boost, task):
        boost.real_model.remove_node()
        self.session["score_boost"] = False

    def sleep_boost(self, boost):
        boost.real_model.reparentTo(self.ralph)
        boost.real_model.setPos(0,0,5)
        boost.real_model.setH(45)
        boost.real_model.setScale(0.5)
        self.session["sleep_boost"] = True
        myTask = self.taskMgr.doMethodLater(SPEED_BOOST_TIME * 2, self.stop_sleep_boost, 'stop_sleep_boost', extraArgs = [boost], appendTask=True)
    def stop_sleep_boost(self, boost, task):
        boost.real_model.remove_node()
        self.session["sleep_boost"] = False

    def surprise_boost(self, boost):
        y = random.randint(0,2)
        if y == 0:
            for x in range(20):
                myTask = self.taskMgr.doMethodLater(0.3*x, self.bomb_birds, 'bomb_boost')
        elif y == 1:
            j = random.randint(0,2)
            for x in range(20):
                myTask = self.taskMgr.doMethodLater(0.3*x, self.bomb_boxes, 'bomb_boost', extraArgs=[j], appendTask=True)
        elif y == 2:
            self.session["score"] *= 2
    def bomb_birds(self, task):
        for x in range(3):
                spawner(self, ObsticleType.BIRD, x)
    def bomb_boxes(self, j, task):
        spawner(self, ObsticleType.BOX, j)

    def start_immune(self, durration):
        self.session["player_immune"] = True
        myTask = self.taskMgr.doMethodLater(SPEED_BOOST_TIME, self.stop_immune, 'stop_immune')
    def stop_immune(self, task):
        self.session["player_immune"] = False
        self.ralph.setAlphaScale(0.35)
    
game = Game()
game.run()
