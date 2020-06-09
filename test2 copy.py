from custom_gym.cartpole import CustomCartPoleEnv
from video_handler.frame_handler import FrameHandler
import time
import cv2

Env = CustomCartPoleEnv(mode=1,render_mode="human")
f = FrameHandler()
x=1
while x:
    frame,_,done,_ = Env.step(1)
    
    gray = f.process_frame(frame)
    #time.sleep(0.02)
    cv2.imshow("test",f.make_back_big(gray))
    if done:
        Env.reset()
    if cv2.waitKey(1) == 27:
        break
 

cv2.destroyAllWindows()
    