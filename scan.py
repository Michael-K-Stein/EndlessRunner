# import the necessary packages
import numpy as np
import cv2
import imutils




def get_surface(box):
    (x, y, w, h)=box
    return w*h
def find_largest(boxes):
    if len(boxes) == 0:
        return boxes
    return [max(boxes, key = get_surface)]
def print_call_back(action):
    print(action)


class Scanner:
    def __init__(self,callback) -> None:
        self.defult_y = 0
        self.defult_height = 0
        self.cur_box = None
        self.jump_thresh = 20
        self.callback = callback
    def calibrate(self):
        (x, y, w, h) = self.cur_box
        self.defult_y = y
        self.defult_height = h
        print("calibrated")

    def test_for_action(self):
        (x, y, w, h) = self.cur_box
        if self.defult_y-y > self.jump_thresh:
            self.callback("JUMP!")
        if y-self.defult_y > self.jump_thresh:
            self.callback("TOOK!")


    def initScanner(self):
        # initialize the HOG descriptor/person detector
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        cv2.startWindowThread()

        # open webcam video stream
        cap = cv2.VideoCapture(0)



        while(True):
            # Capture frame-by-frame
            ret, frame = cap.read()
            frame=cv2.flip(frame, 1)
            # resizing for faster detection
            frame = cv2.resize(frame, (640, 480))
            # using a greyscale picture, also for faster detection
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # detect people in the image
            # returns the bounding boxes for the detected objects
            boxes, weights = hog.detectMultiScale(frame, winStride=(8,8) )
            boxes=find_largest(boxes)
            if len(boxes) != 0:  
                cur_box = boxes[0]
                (x, y, w, h)=cur_box
                cropped_person = frame[y:y+h,x:x+w]
                cropped_person= cv2.resize(cropped_person,(320,520))
                cv2.imshow('person',cropped_person)
                self.cur_box = cur_box
                #finding shoes:
                img = cropped_person
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                lower_gray = np.array([0, 5, 50], np.uint8)
                upper_gray = np.array([200, 200, 200], np.uint8)
                mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)
                img_res = cv2.bitwise_and(img, img, mask = mask_gray)
                cv2.imshow('res',mask_gray)

                #test for actions:
                self.test_for_action()

                





            boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
            for (xA, yA, xB, yB) in boxes:
                # display the detected boxes in the colour picture
                cv2.rectangle(frame, (xA, yA), (xB, yB),
                                  (0, 255, 0), 2)


            # Display the resulting frame

            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if cv2.waitKey(1) & 0xFF == ord(' '):
                self.calibrate()

        # When everything done, release the capture
        cap.release()
        # finally, close the window
        cv2.destroyAllWindows()
        cv2.waitKey(1)

if __name__ == "__main__":
    scan = Scanner(print_call_back)
    scan.initScanner()



