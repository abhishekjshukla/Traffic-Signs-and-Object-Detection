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
	'load':'bin/tiny-yolo.weights',
	'threshold': 0.1,

}
tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]
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

def find_marker(image):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(gray, 35, 125)
	(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	c = max(cnts, key = cv2.contourArea)

	# compute the bounding box of the of the paper region and return it
	return cv2.minAreaRect(c)

def distance_to_camera(knownWidth, focalLength, perWidth):
	return (knownWidth * focalLength) / perWidth

# initialize the known distance from the camera to the object, which
# in this case is 24 inches
KNOWN_DISTANCE = 12.0

# initialize the known object width, which in this case, the piece of
# paper is 11 inches wide
KNOWN_WIDTH = 6.0

# initialize the list of images that we'll be using
#IMAGE_PATHS = ["images/2ft.png", "images/3ft.png", "images/4ft.png"]

# load the furst image that contains an object that is KNOWN TO BE 2 feet
# from our camera, then find the paper marker in the image, and initialize
# the focal length
# image = cv2.imread(IMAGE_PATHS[0])
# marker = find_marker(image)
# focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH

#output_frame = OutputFrame()
webcam_thread = camera("camera thread")
predictor_thread = predictclass("predictclass thread")
webcam_thread.start()
time.sleep(.1)
predictor_thread.start()

cnt=0
while True:
	stime = time.time()
	#ret, frame = cap.read()
	#results = tfnet.return_predict(frame)
	#results=output_frame.boxes
	#print("asdsasz",results)
	if 1:
		for color, result in zip(colors, results):
			tl = (result['topleft']['x'], result['topleft']['y'])
			br = (result['bottomright']['x'], result['bottomright']['y'])
			label = result['label']
			#print(label)
			vech=['car','motercycle','truck','bus']
			confidence = result['confidence']
			rec=['person','traffic light','car','motercycle','truck','bus','stop sign']
			if(confidence*100>35 and (label in rec)):
					#image = cv2.imread(imagePath)
					marker = find_marker(frame)
					inches = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])

					# draw a bounding box around the image and display it
					box = np.int0(cv2.cv.BoxPoints(marker))
					cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
					cv2.putText(image, "%.2fft" % (inches / 12),
						(image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
						2.0, (0, 255, 0), 3)
				text = '{}: {:.0f}%'.format(label, confidence * 100)
				frame = cv2.rectangle(frame, tl, br, color, 5)
				frame = cv2.putText(
					frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
				if label in vech:
					cnt+=1
		cv2.imshow('frame', frame)
		print("Vehicles",cnt)
		print('FPS {:.1f}'.format(1 / (time.time() - stime)))
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
# import the necessary packages
