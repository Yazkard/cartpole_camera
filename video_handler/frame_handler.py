import cv2
import numpy as np


class FrameHandler(): 
    def __init__(self):
        self.clear_frame_list()

    def fill_frames(self):
        frame = self.frames_list[0]
        for _ in range(2):
            self.frames_list.append(frame)

    def add_frame(self, frame):
        self.frames_list.append(frame)
        if len(self.frames_list) > 1:
            self.frames_list.pop(0)
        else:
            self.fill_frames()
    
    def clear_frame_list(self):
        self.frames_list=list()

    def save_frame(self, frame):
        cv2.imwrite("test.png",frame)
        #np.savetxt("foo.csv", np.array(frame), delimiter=",")

    def process_frame(self, frame):
        percent = 10
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        width = int(frame.shape[1] * percent/ 100)
        height = int(frame.shape[0] * percent/ 100)
        dim = (width, height)
        return cv2.resize(gray, dim, interpolation =cv2.INTER_AREA)

    def make_back_big(self, frame):
        percent = 10
        width = int(frame.shape[1] * 100/percent)
        height = int(frame.shape[0] * 100/percent)
        dim = (width, height)
        return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)
