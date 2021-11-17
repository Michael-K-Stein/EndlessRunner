from basefile import *

DEFAULT_HEIGHT = 175
DEFAULT_JUMP_THRESH = 15
DEFAULT_CROUCH_THRESH = 30
DEFAULT_LEFT_RIGHT_THRESH = 40
DEFAULT_CALIB_LEFTRIGHT = 40
DEFAULT_CALIB_HEIGHT = 300

BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
               "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
               "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
               "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
               ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
               ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
               ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
               ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]

net = cv2.dnn.readNetFromTensorflow("graph_opt.pb")

threshold = 0.2


class Scanner:
    
    def __init__(self, callback) -> None:
        self.callback = callback
        self.last_action = ""
        self.is_running = True
        self.cur_points = None
        self.overlay = cv2.resize(cv2.imread('./assets/images/outline_body.png'), (720, 480))
        self.is_calibrating = True
        self.time_elapsed_calibration = time.localtime().tm_sec + 3
        self.person_x = 0
        self.person_y = 0
        self.person_height = 0


        self.left_right_thresh = 0
        self.jump_thresh = 0 
        self.frame_center_x = 0
        self.frame_center_y = 0
        self.crouch_thresh = 0
        cv2.startWindowThread()

        # open webcam video stream
        self._cap = cv2.VideoCapture(0)
        
        self.frame = self._cap.read()[1]
        self.frame = cv2.resize(self.frame, (720, 480))
    
    def stop(self):
        self.is_running = False
        self.release()
    
    def find_height_of_person(self):
        try:
            self.person_height = self.cur_points[BODY_PARTS["LAnkle"]][1] - self.cur_points[BODY_PARTS["Neck"]][1]
        except TypeError:
            self.callback("CAMERA")
            self.time_elapsed_calibration = time.localtime().tm_sec
            return False
        return True
    
    def find_center_of_person(self):
        sum_x, sum_y, count = 0, 0, 0
        cur_point = 0
        for each in self.cur_points:
            if cur_point >= 13:
                break
            cur_point+=1
            if each is not None:
                sum_x += each[0]
                sum_y += each[1]
                count += 1
        
        if count == 0:
            self.person_x = 0
            self.person_y = 0
        else:
            sum_x //= count
            sum_y //= count
            self.person_x = sum_x
            self.person_y = sum_y


    def calibrate(self):
        if not self.find_height_of_person():
            return False
        #adjusting thresholds
        self.scale = self.person_height / DEFAULT_HEIGHT
        self.jump_thresh = DEFAULT_JUMP_THRESH * self.scale
        self.crouch_thresh = DEFAULT_CROUCH_THRESH * self.scale
        self.left_right_thresh = DEFAULT_LEFT_RIGHT_THRESH * self.scale
        #finding center of page
        self.frame_center_x = self.person_x
        self.frame_center_y = self.person_y

        action = "CALIBRATED"
        self.callback(action)

        return True

    def get_person_lane(self):
        if self.person_x > self.frame_center_x + self.left_right_thresh:
            return "RIGHT"
        elif self.person_x < self.frame_center_x - self.left_right_thresh:
            return "LEFT"
        else:
            return "CENTER"
    
    def test_for_action(self):
        action = None
        if self.is_calibrating:
            return
        if self.frame_center_y - self.person_y > self.jump_thresh:
            action = "JUMP"
        elif self.person_y - self.frame_center_y > self.crouch_thresh:
            action = self.get_person_lane() + "_TOOK"
        else:
            action = self.get_person_lane()

        if action is not None:
            if self.last_action != action:
                self.last_action = action
                for callback_action in action.split("_"):
                    self.callback(callback_action)
                print(action)

    def is_centered(self):
        frame_y, frame_x , _ = self.frame.shape
        frame_x //= 4
        frame_y //= 4
        res = abs(self.person_x - frame_x) < DEFAULT_CALIB_LEFTRIGHT and\
            abs(self.person_y - frame_y) < DEFAULT_CALIB_HEIGHT
        return res

    def run_scanner(self):
        self.thread = threading.Thread(target=self.scan)
        self.thread.start()
    
    def scan(self):
        while self.is_running:
            # Capture frame-by-frame
            ret, frame = self._cap.read()
            frame=cv2.flip(frame, 1)
            # resizing for faster detection
            try:
                frame = cv2.resize(frame, (360, 240))
                
                #start of openpose:
                net.setInput(cv2.dnn.blobFromImage(frame, 1.0, (360, 240), (127.5, 127.5, 127.5), swapRB=True, crop=False))
                out = net.forward()
                out = out[:, :19, :, :] 
            except cv2.error:
                continue

            assert(len(BODY_PARTS) == out.shape[1])

            points = []
            for i in range(len(BODY_PARTS)):
                    # Slice heatmap of corresponging body's part.
                heatMap = out[0, i, :, :]

                # Originally, we try to find all the local maximums. To simplify a sample
                # we just find a global one. However only a single pose at the same time
                # could be detected this way.
                _, conf, _, point = cv2.minMaxLoc(heatMap)
                x = (360 * point[0]) / out.shape[3]
                y = (240 * point[1]) / out.shape[2]
                # Add a point if it's confidence is higher than threshold.
                points.append((int(x), int(y)) if conf > threshold else None)


            if self.is_centered() and self.is_calibrating:
                color = (255, 255, 255)
            else:
                color = (0, 0, 255)
                
            for pair in POSE_PAIRS:
                partFrom = pair[0]
                partTo = pair[1]
                assert(partFrom in BODY_PARTS)
                assert(partTo in BODY_PARTS)

                idFrom = BODY_PARTS[partFrom]
                idTo = BODY_PARTS[partTo]

                if points[idFrom] and points[idTo]:
                    cv2.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
                    cv2.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, color, cv2.FILLED)
                    cv2.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, color, cv2.FILLED)
            self.cur_points = points
            self.find_center_of_person()
        
            t, _ = net.getPerfProfile()
            cv2.ellipse(frame, (self.person_x, self.person_y), (5, 5), 0, 0, 360, color, cv2.FILLED)
            
            frame_y,frame_x , _ = frame.shape
            

            #right thresh
            cv2.line(frame, (int(self.frame_center_x + self.left_right_thresh),0),\
             (int(self.frame_center_x + self.left_right_thresh),300), (255,255,255), 3)
            #left thresh
            cv2.line(frame, (int(self.frame_center_x - self.left_right_thresh),0),\
             (int(self.frame_center_x - self.left_right_thresh),300), (255,255,255), 3)
            #jump thresh
            cv2.line(frame, (0, int(self.frame_center_y - self.jump_thresh)),\
             (400,int(self.frame_center_y - self.jump_thresh)), (255,255,255), 3)
            #crouch thresh
    
            cv2.line(frame, (0, int(self.frame_center_y + self.crouch_thresh)),\
             (400,int(self.frame_center_y + self.crouch_thresh)), (255,255,255), 3)

            frame = cv2.resize(frame, (720, 480))
            self.frame = frame

            if self.is_calibrating:
                frame = cv2.addWeighted(frame,0.6,self.overlay,0.9,1)
                if self.is_centered():
                    if time.localtime().tm_sec - self.time_elapsed_calibration >= 5:
                        self.is_calibrating = not self.calibrate()
                else:
                    self.time_elapsed_calibration = time.localtime().tm_sec
            self.test_for_action()

            self.frame = frame


    def release(self):
        self._cap.release()
        cv2.destroyAllWindows()


def overlay(self):
    dr = self.win.makeDisplayRegion()
    dr.setSort(20)

    myCamera2d = NodePath(Camera('myCam2d'))
    lens = OrthographicLens()
    lens.setFilmSize(2, 2)
    lens.setNearFar(-1000, 1000)
    myCamera2d.node().setLens(lens)

    myRender2d = NodePath('myRender2d')
    myRender2d.setDepthTest(False)
    myRender2d.setDepthWrite(False)
    myCamera2d.reparentTo(myRender2d)
    dr.setCamera(myCamera2d)

    h, w, _ = self.scanner.frame.shape  # accessing the width and height of the frame
    # setup panda3d scripting env (render, taskMgr, camera etc)
    # set up a texture for (h by w) rgb image
    self.tex = Texture()
    self.tex.setup2dTexture(w, h, Texture.T_unsigned_byte,
                    Texture.F_rgb)
    # set up a card to apply the numpy texture
    cm = CardMaker('card')
    self.card = myRender2d.attachNewNode(cm.generate())
    #self.card = cm.generate().reParent(self.render)

    WIDTHRATIO = 1
    HEIGHTRATIO = h/w
    DEPTH = 1

    self.card.setScale(WIDTHRATIO/2, DEPTH, HEIGHTRATIO)

    self.card.setPos(-1, 0, -1)

    self.card.setBin("fixed", 0)
    self.card.setDepthTest(False)
    self.card.setDepthWrite(False)

    return self.taskMgr.add(lambda task: update_tex(self, task), 'video frame update')

def update_tex(self, task):
    # positive y goes down in openCV, so we must flip the y coordinates
    flipped_frame = cv2.flip(self.scanner.frame, 0)
    # overwriting the memory with new frame
    self.tex.setRamImage(flipped_frame)
    self.card.setTexture(self.tex)  # now apply it to the card

    return task.cont

if __name__ == "__main__":
    scan = Scanner(lambda action: print(action))
    scan.run_scanner()
