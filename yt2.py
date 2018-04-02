import cv2
from darkflow.net.build import TFNet
import numpy as np
import datetime
import threading
import time
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

results=[]
frame=None
done=False
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
options = {
    'model':'cfg/tiny-yolo.cfg',
    'load': 'bin/tiny-yolo.weights',
    'threshold': 0.1,

}
tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]
class camera(threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name
   def run(self):
      #print("Starting " + self.name)
      get_frame(self.name)
      #print("Exiting " + self.name)

def get_frame(threadName):
    global frame,done,cap
    while not done:
        _, frame = cap.read()

class predictclass(threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name
   def run(self):
      #print("Starting " + self.name)
      predict(self.name)
      #print("Exiting " + self.name)
def predict(threadName):
    global results,frame,done
    while not done:
        results = tfnet.return_predict(frame)


#output_frame = OutputFrame()
webcam_thread = camera("camera thread")
predictor_thread = predictclass("predictclass thread")
webcam_thread.start()
time.sleep(1)
predictor_thread.start()

cnt=0
while True:
   stime = time.time()
   if 1:
      for color, result in zip(colors, results):
         tl = (result['topleft']['x'], result['topleft']['y'])
         br = (result['bottomright']['x'], result['bottomright']['y'])
         label = result['label']
         #print(label)
         vech=['car','motercycle','truck','bus']
         confidence = result['confidence']
         rec=['traffic light','car','motercycle','truck','bus','stop sign']
         traffic_symbol = ['stop sign']
         if(label in rec):
             frame = cv2.rectangle(frame, tl, br, color, 5)
             #print(tl, br)
             realHeight = 75
             dist = (5.5*(realHeight)*360)/((br[1] - tl[1])*4.5)
             print(dist)
             text = '{}: {:.0f}% : Dist: {:.0f}inches'.format(label, confidence * 100, dist/25.4)
             
             frame = cv2.putText(
                 frame, text, tl, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
             if label in vech:
                 cnt+=1
   cv2.imshow('frame', frame)
   #print('FPS {:.1f}'.format(1 / (time.time() - stime)))
   if cv2.waitKey(1) & 0xFF == ord('q'):
      break

cap.release()
cv2.destroyAllWindows()
