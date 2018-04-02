import cv2
from darkflow.net.build import TFNet
from yolov2 import run,predicty
import numpy as np
import datetime
import threading
import time
from playsound import playsound
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
HI=0
EN=1
MH=2
BN=3
lang=1
results=[]
frame=None
done=False
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
options = {
    'model':'cfg/tiny-yolo.cfg',
    'load':'bin/tiny-yolo.weights',
    'threshold': 0.3,
}
tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]
def speak(label,veh):
  global lang
  if(veh==1):
    if(lang==0):
      playsound("./sounds/vehicle_ahead_hi.mp3")
    elif(lang==1):
      playsound("./sounds/vehicle_ahead_en.mp3")
    elif(lang==2):
      playsound("./sounds/vehicle_ahead_mh.mp3")
    elif(lang==3):
      playsound("./sounds/vehicle_ahead_bn.mp3")
  else:
    if(label=="stop sign"):
      if(lang==0):
        playsound("./sounds/stop_hi.mp3")
      elif(lang==1):
        playsound("./sounds/stop_en.mp3")
      elif(lang==2):
        playsound("./sounds/stop_mh.mp3")
      elif(lang==3):
        playsound("./sounds/stop_bn.mp3")
    elif(label=="turn left"):
      if(lang==0):
        playsound("./sounds/tl_hi.mp3")
      elif(lang==1):
        playsound("./sounds/tl_en.mp3")
      elif(lang==2):
        playsound("./sounds/tl_mh.mp3")
      elif(lang==3):
        playsound("./sounds/tl_bn.mp3")
    elif(label=="turn right"):
      if(lang==0):
        playsound("./sounds/tr_hi.mp3")
      elif(lang==1):
        playsound("./sounds/tr_en.mp3")
      elif(lang==2):
        playsound("./sounds/tr_mh.mp3")
      elif(lang==3):
        playsound("./sounds/tr_bn.mp3")
class camera(threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name
   def run(self):
      print("Starting " + self.name)
      get_frame(self.name)
      print("Exiting " + self.name)

def get_frame(threadName):
    global frame,done,cap
    while not done:
        _, frame = cap.read()

class predictclass(threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name
   def run(self):
      print("Starting " + self.name)
      predict(self.name)
      print("Exiting " + self.name)
def predict(threadName):
    global results,frame,done
    while not done:
        results = tfnet.return_predict(frame)

def detection_graph():
    while True:
      ret, image_np = cap.read()
      # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
      image_np_expanded = np.expand_dims(image_np, axis=0)
      image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
      # Each box represents a part of the image where a particular object was detected.
      boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
      # Each score represent how level of confidence for each of the objects.
      # Score is shown on the result image, together with the class label.
      scores = detection_graph.get_tensor_by_name('detection_scores:0')
      classes = detection_graph.get_tensor_by_name('detection_classes:0')
      num_detections = detection_graph.get_tensor_by_name('num_detections:0')
      # Actual detection.
      (boxes, scores, classes, num_detections) = sess.run(
          [boxes, scores, classes, num_detections],
          feed_dict={image_tensor: image_np_expanded})
      # Visualization of the results of a detection.
      vis_util.visualize_boxes_and_labels_on_image_array(
          image_np,
          np.squeeze(boxes),
          np.squeeze(classes).astype(np.int32),
          np.squeeze(scores),
          category_index,
          use_normalized_coordinates=True,
          line_thickness=8)
#output_frame = OutputFrame()
webcam_thread = camera("camera thread")
predictor_thread = predictclass("predictclass thread")
webcam_thread.start()
time.sleep(.1)
predictor_thread.start()

cnt=0
while True:
    stime = time.time()
    a=run(frame)
    veh=0
    #print(a)
    #ret, frame = cap.read()
    #results = tfnet.return_predict(frame)
    #results=output_frame.boxes
    #print("asdsasz",results)
    if 1:
        for color, result in zip(colors, results):
            tl = (result['topleft']['x'], result['topleft']['y'])
            br = (result['bottomright']['x'], result['bottomright']['y'])
            label = result['label']
            #print("tl is ",tl)
            vech=['car','motercycle','truck','bus']
            confidence = result['confidence']
            rec=['traffic light','car','motercycle','truck','bus','stop sign']
            #confidence*100>35 and (label in rec)
            if(a!=None):
              if(a[0]!=None):
                txt2='{}: {}'.format(a[0], a[2])
                speak(a[0],0)
                frame = cv2.putText(
                       frame, txt2,tuple(a[1]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            if(confidence*100>0 and (label in rec) ):
                if(label in vech):
                  veh=1
                speak(label,veh)
                text = '{}: {:.0f}%'.format(label, confidence * 100)
                #text = '{}'.format(detectedTrafficSign)
                #print("*** ",tuple(a[1]))
                #a[1]=tuple(a[1])
                # if(a[0]!=None):
                #   txt2='{}: {}'.format(a[0], a[2])
                #   frame = cv2.putText(
                #      frame, txt2,tuple(a[1]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                frame = cv2.rectangle(frame, tl, br, color, 5)
                frame = cv2.putText(
                    frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                if label in vech:
                    cnt+=1

                realHeight = 100
                dist = (6*(realHeight)*480)/((br[1] - tl[1])*4.5)
                #print(dist)
                text = cv2.putText(frame, str("Dist: {:.01f} cm".format(dist/10)), (tl[0], tl[1] + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)


        cv2.imshow('frame', frame)
        #print("Vehicles",cnt)
       # print('FPS {:.1f}'.format(1 / (time.time() - stime)))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()