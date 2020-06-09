from video_handler.frame_handler import FrameHandler
import cv2

img = cv2.imread("test.png")
f = FrameHandler()
#f.add_frame(img)
t = f.process_frame(img)
print(t.shape)
percent = 10
width = int(t.shape[1] * percent)
height = int(t.shape[0] * percent)
dim = (width, height)
t=cv2.resize(t, dim, interpolation =cv2.INTER_AREA)
cv2.imshow("test",t)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("test2.png",t)
