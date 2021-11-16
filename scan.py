import numpy as np
import cv2
import threading
import time

DEFAULT_HEIGHT = 175

DEFAULT_JUMP_THRESH = 10
DEFAULT_CROUCH_THRESH = 20
DEFAULT_LEFT_RIGHT_THRESH = 30

DEFAULT_CALIB_LEFTRIGHT = 50
DEFAULT_CALIB_HEIGHT = 300

class Scanner:

    def __init__(self, callback) -> None:
        self.defult_y = 0
        self.defult_height = 0
        self.largest_box = None
        self.jump_thresh = DEFAULT_JUMP_THRESH
        self.crouch_thresh = DEFAULT_CROUCH_THRESH
        self.center = 0
        self.left_right_thresh = DEFAULT_LEFT_RIGHT_THRESH
        self.callback = callback
        self.last_action = ""
        self.is_running = True
        self.overlay = cv2.resize(cv2.imread('Outline-body.png'), (720, 480))
        self.is_calibrating = True
        self.time_elapsed_calibration = time.localtime().tm_sec - 3

        # initialize the HOG descriptor/person detector
        self._hog = cv2.HOGDescriptor()
        self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        cv2.startWindowThread()

        # open webcam video stream
        self._cap = cv2.VideoCapture(0)
        self.frame = self._cap.read()[1]
        self.frame = cv2.resize(self.frame, (720, 480))
    
    def stop(self):
        self.is_running = False

        self._cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def calibrate(self):
        x, y, w, h = self.largest_box

        self.scale = h / DEFAULT_HEIGHT
        self.jump_thresh = DEFAULT_JUMP_THRESH * self.scale
        self.crouch_thresh = DEFAULT_CROUCH_THRESH * self.scale
        self.left_right_thresh = DEFAULT_LEFT_RIGHT_THRESH * self.scale

        self.defult_y = y + h // 2
        self.defult_height = h
        self.center = x + w // 2
        print("calibrated")

    def test_for_action(self):
        action = None
        (x, y, w, h) = self.largest_box
        if self.defult_y - (y + h // 2) > self.jump_thresh:
            action = "JUMP"
        elif h + self.crouch_thresh < self.defult_height:
            action = "TOOK"
        elif x + w // 2 > self.center + self.left_right_thresh:
            action = "RIGHT"
        elif x + w // 2 < self.center - self.left_right_thresh:
            action = "LEFT"
        else:
            action = "CENTER"

        if action is not None:
            if self.last_action != action:
                self.last_action = action
                self.callback(action)

    def is_centered(self):
        if self.largest_box is None:
            return False
        (x, y, w, h) = self.largest_box
        frame_x, frame_y, _ = self.frame.shape
        frame_x //= 2
        frame_y //= 2
        return abs(x + w // 2 - frame_x // 2) < DEFAULT_CALIB_LEFTRIGHT and\
            abs(y + h // 2 - frame_y // 2) < DEFAULT_CALIB_HEIGHT
    
    def run_scanner(self):
        self.thread = threading.Thread(target=self.scan)
        self.thread.start()
    
    def scan(self):
        while self.is_running:
            # Capture frame-by-frame
            _, frame = self._cap.read()
            frame=cv2.flip(frame, 1)
            # resizing for faster detection
            frame = cv2.resize(frame, (320, 240))

            # detect people in the image
            # returns the bounding boxes for the detected objects
            boxes, weights = self._hog.detectMultiScale(frame, winStride=(2,2))
            boxes = Scanner.find_largest(boxes, weights)
            if boxes:
                largest_box = boxes[0]

                self.largest_box = largest_box

                # test for actions:
                self.test_for_action()
            else:
                self.largest_box = None
            boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

            for (xA, yA, xB, yB) in boxes:
                # display the detected box in the colour picture
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)


            # Display the resulting frame
            frame = cv2.resize(frame, (720, 480))
            self.frame = frame

            if self.is_calibrating:
                frame = cv2.addWeighted(frame, 0.4, self.overlay, 0.1, 0)
                if self.is_centered():
                    if time.localtime().tm_sec - self.time_elapsed_calibration >= 10:  
                        self.is_calibrating = False
                        self.calibrate()
                else:
                    self.time_elapsed_calibration = time.localtime().tm_sec

            self.frame = frame



    def release(self):
        self._cap.release()
        cv2.destroyAllWindows()


    @staticmethod
    def find_largest(boxes, weights):
        if len(boxes) == 0:
            return boxes
        return [max(zip(boxes, weights), key = lambda x:x[1])[0]]


if __name__ == "__main__":
    scan = Scanner(lambda action: print(action))
    scan.run_scanner()
