from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
import eventlet
import socketio
import cv2
import time
from io import BytesIO
import base64
from PIL import Image
import math
import os 
from dotenv import load_dotenv
import os 
import numpy as np

load_dotenv()

# from motor import Motor

# rcdriver = Motor((5, 6, 13), (16, 26, 12))

velocity = 20
# vel_queue = []

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
socketio = SocketIO(app)
camera = cv2.VideoCapture(0) 
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 512)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 384)

map_x_distorted, map_y_distorted = 0, 0

def init():
    global map_x_distorted, map_y_distorted

    ret, image = camera.read()
    if not ret: return 

    height, width = image.shape[:2]
        
    # Calculate the center of the image
    center_x = width // 2
    center_y = height // 2

    # Generate the fisheye mapping
    map_x, map_y = np.meshgrid(np.arange(width), np.arange(height))
    map_x = (map_x - center_x) / width
    map_y = (map_y - center_y) / height
    r = np.sqrt(map_x**2 + map_y**2)
    theta = np.arctan2(map_y, map_x)

    k=0.6
    r_distorted = r * (1 + k*r**2)
    map_x_distorted = r_distorted * np.cos(theta) * width + center_x
    map_y_distorted = r_distorted * np.sin(theta) * height + center_y


@app.route('/')
def index():
	return render_template('improved.html')

@app.route("/live")
def live():
    return render_template("live.html")

@socketio.on('connect', namespace='/socket')
def connect():
    emit("hi", {'data': 'Connected'})

@socketio.on('disconnect', namespace='/socket')
def disconnect():
    print("Disconnected")

def fisheye(image):
    distorted_image = cv2.remap(image, map_x_distorted.astype(np.float32), map_y_distorted.astype(np.float32),
                                interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return distorted_image


@socketio.event(namespace="/socket")
def send():
    # while True:/
    success, frame = camera.read()
    if not success:
        return
    
    # Apply fisheye distortion
    distorted_image = fisheye(frame)

    # flip = cv2.flip(frame, 180)
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),30]
    retval, buffer = cv2.imencode(".jpeg", img=distorted_image, params=encode_param)
    byte_buffer = buffer.tobytes()

    # jpg_as_base64 = base64.b64encode(buffer)
    # image_base64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')

    # color_coverted = cv2.cvtColor(flip, cv2.COLOR_BGR2RGB)
    # # convert from openCV2 to PIL
    # pil_image=Image.fromarray(color_coverted)

    # byte_img = img_to_base64_str(pil_image)

    # print(type(jpg_as_base64))
    emit("video", {"data": byte_buffer}, broadcast=True)
    # time.sleep(0.01)

@socketio.event(namespace="/socket")
def control(data):
    direction = data["dir"]
    angle = int(data["angle"])
    
    x_axis = ["F", "L"]
    y_axis = ["L", "R"]

    t_vel = 0
    if direction in x_axis:
        t_vel = int(velocity + math.log10(angle+10) * 5)
    elif direction in y_axis:
        t_vel = int(velocity + math.log10(angle+10) * 3)

    try: 
        print(direction, t_vel)
        # if direction == "F":
        #     rcdriver.forward(velocity=t_vel)
        # elif direction == "B":
        #     rcdriver.back(velocity=t_vel)
        # elif direction == "L":
        #     rcdriver.left(velocity=t_vel)
        # elif direction == "R":
        #     rcdriver.right(velocity=t_vel)
        # else:
        #     rcdriver.stop_all()
    except: 
        return 

if __name__ == '__main__':
    init()
    socketio.run(app, host="127.0.0.1", port=8000)
