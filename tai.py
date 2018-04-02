import numpy as np
import cv2
import os
import sys
import tensorflow as tf
from utils import label_map_util
from utils import visualization_utils as vis_util
import threading

MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = 'models/' + MODEL_NAME + '/frozen_inference_graph.pb'
# List of the strings that is used to add correct label for each box.
CWD_PATH = os.getcwd()
PATH_TO_LABELS = os.path.join(CWD_PATH,'object_detection', 'data', 'mscoco_label_map.pbtxt')
print(PATH_TO_LABELS)
NUM_CLASSES = 90
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

class OutputFrame:
    def __init__(self):
        self.frame = np.zeros((IMAGE_HEIGHT,IMAGE_WIDTH,3))
        self.boxes = ()

def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

class WebcamThread(threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name
   def run(self):
      print("Starting " + self.name)
      get_frame(self.name)
      print("Exiting " + self.name)

def get_frame(threadName):
    while not done:
        _, frame = cap.read()
        output_frame.frame = frame

class PredictorThread(threading.Thread):
   def __init__(self, name):
      threading.Thread.__init__(self)
      self.name = name
   def run(self):
      print("Starting " + self.name)
      predict(self.name)
      print("Exiting " + self.name)

def predict(threadName):
    while not done:
        _, image_np = cap.read()
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
        output_frame.boxes = sess.run(
          [boxes, scores, classes, num_detections],
          feed_dict={image_tensor: image_np_expanded})


if __name__ == "__main__":
    done = False
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc('a', 'v', 'c', '1') # note the lower case
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480), True)
    cap.set(3, IMAGE_WIDTH)
    cap.set(4, IMAGE_HEIGHT)
    sess = tf.Session(graph=detection_graph)
    output_frame = OutputFrame()

    webcam_thread = WebcamThread("Webcam Thread")
    predictor_thread = PredictorThread("Predictor Thread")
    webcam_thread.start()
    predictor_thread.start()

    while True:
        if output_frame.boxes == ():
            to_show = output_frame.frame
        else:
            to_show = output_frame.frame
            vis_util.visualize_boxes_and_labels_on_image_array(
              to_show,
              np.squeeze(output_frame.boxes[0]),
              np.squeeze(output_frame.boxes[2]).astype(np.int32),
              np.squeeze(output_frame.boxes[1]),
              category_index,
              use_normalized_coordinates=True,
              line_thickness=8)

        cv2.imshow('frame', to_show)
        out.write((to_show).astype('u1'))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            done = True
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()