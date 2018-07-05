# Traffic Sign and Object Detection using YOLO Algorithm

We attempt to make Traffic Sign and Object detection using YOLO(You-Only-Look-Once) Algorithm. The reason behind choosing of YOLO is because of the high speed of detection with reasonable amount of accuracy(~74%). YOLO Algorithm is popular due to its Real-Time Object detection capability.

- More About YOLO: [Darknet/YOLO](https://pjreddie.com/darknet/yolo/)
- GitHub: [thtrieu/darkflow](https://github.com/thtrieu/darkflow)

This Project was submitted in **Smart India Hackathon 2018** under team name: 6_Pixels.

Along with Object Detection our model has been designed with easy to use and navigate interface (User Interface) using PYGAME library of Python. The Model also has the capability to notify user about the Traffic Signs and Vehicles using Speech. The speech is available in 4 Languages at the moment namely: English, Hindi, Bangali, Marathi.

Also we have attempted to add the feature of Fatigue detection of the driver based on closing of eye using HaarCascades of OpenCV. If the driver's eyes remain closed for a long time, the alarm starts to ring to wake the driver up.

The model also has the capability to estimate the distance of vehicle in front of it thus setting a stepping stone towards self-driving cars. Also you can view Map and Weather Condition in the User Interface. Below are some results and Screenshots of the  final project.

# Usage

Clone the repository to your local machine

`git clone https://github.com/jatinmandav/Traffic-Signs-and-Object-Detection`

Navigate to the Directory

`cd Traffic-Signs-and-Object-Detection`

Install all the Requirements given below.

Download pre-trained `weights` or train your own and add them to `main.py` and also add the `cfg` file to your `main.py` file.

Execute main.py file!


# Requirements

* Darkflow - https://github.com/thtrieu/darkflow
* Tensorflow - https://tensorflow.org
* Numpy - https://numpy.org
* OpenCV - https://opencv.org
* Pygame - https://pygame.org
* Geocoder: 
`pip3 install geocoder`
* playsound: 
`pip3 install playsound`
* GooMPy: 
`git clone https://github.com/simondlevy/GooMPy`
* PyOwm Weather API: 
`pip3 install pyowm`

After instllation of pyowm, You would require an API Key which can be generated from the [Official Website](https://home.openweathermap.org/users/sign_up) For more information on PyOwm check out [csparpa/pyown](https://github.com/csparpa/pyowm). Paste the generated API Key in Line 127 of `main.py`

# ScreenShots
![Stop Sign Detection](https://github.com/dark-archerx/Traffic-Signs-and-Object-Detection/blob/master/images/Screen%20Shot%202018-03-31%20at%205.08.08%20pm.png)
![Traffic Light](https://github.com/dark-archerx/Traffic-Signs-and-Object-Detection/blob/master/images/Screen%20Shot%202018-03-31%20at%205.55.32%20pm.png)
![Car Detection](https://github.com/dark-archerx/Traffic-Signs-and-Object-Detection/blob/master/images/Screen%20Shot%202018-03-31%20at%205.56.00%20pm.png)
