import cv2
from darkflow.net.build import TFNet
import numpy as np
import time
from threading import Thread
options = {
    'model':'cfg/tiny-yolo-voc-7c.cfg',
    'load':8500,
    'threshold': 0.1,

}
def turns():
    pass
def distance_to_camera(knownWidth, focalLength, perWidth):
    return (knownWidth * focalLength) / perWidth
#tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]
KNOWN_DISTANCE = 24.0
KNOWN_WIDTH = 11.0
# capture = cv2.VideoCapture(0)
# capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#focalLength=198.75
focalLength=5.5
def turn()
    while True:
        stime = time.time()
        #ret, frame = capture.read()
        #results = tfnet.return_predict(frame)
        break
        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        #print(results)
        if ret:
            for color, result in zip(colors, results):
                tl = (result['topleft']['x'], result['topleft']['y'])
                br = (result['bottomright']['x'], result['bottomright']['y'])
                label = result['label']
                #print("tl ",tl)
               # print("***")
                #print("br",br)
                marker=br[0]-tl[0]
                confidence = result['confidence']
                #inches = distance_to_camera(KNOWN_WIDTH, focalLength, marker)

                rec=['traffic light','car','motercycle','truck','bus','stop sign']
                print(inches)
                if(confidence*100>35 and (label in rec)):
                    #text=label+" "+confidence*100+" distance "+inches
                    #text = '{}: {:.0f}% {}'.format(label, confidence * 100,inches)
                    text = '{}: {:.0f}% {}'.format(label, confidence * 100,inches)

                    frame = cv2.rectangle(frame, tl, br, color, 5)
                    frame = cv2.putText(
                        frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
            cv2.imshow('frame', frame)
            print('FPS {:.1f}'.format(1 / (time.time() - stime)))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()