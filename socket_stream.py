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

from motor import Motor

rcdriver = Motor((5, 6, 13), (16, 26, 12))
velocity = 20

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)
camera = cv2.VideoCapture(0) 


@app.route('/')
def index():
	return render_template('improved.html')

def img_to_base64_str(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    img_byte = buffered.getvalue()
    img_str = "data:image/png;base64," + base64.b64encode(img_byte).decode()
    return img_str

# @app.before_request
# def before_request():
#     global user_no
#     if 'session' in session and 'user-id' in session:
#         pass
#     else:
#         session['session'] = os.urandom(24)
#         session['username'] = 'user'+str(user_no)
#         user_no += 1

@socketio.on('connect', namespace='/socket')
def connect():
    emit("hi", {'data': 'Connected'})

@socketio.on('disconnect', namespace='/socket')
def disconnect():
    print("Disconnected")

@socketio.event(namespace="/socket")
def send():
    # while True:/
    success, frame = camera.read()
    if not success:
        return

    flip = cv2.flip(frame, 180)
    retval, buffer = cv2.imencode(".jpeg", img=flip)
    # jpg_as_base64 = base64.b64encode(buffer)
    image_base64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')

    # color_coverted = cv2.cvtColor(flip, cv2.COLOR_BGR2RGB)
    # # convert from openCV2 to PIL
    # pil_image=Image.fromarray(color_coverted)

    # byte_img = img_to_base64_str(pil_image)

    # print(type(jpg_as_base64))
    emit("video", {"data": image_base64})
    # time.sleep(0.01)

@socketio.event(namespace="/socket")
def control(data):
    direction = data.dir
    angle = int(data.angle)
    
    x_axis = ["F", "L"]
    y_axis = ["L", "R"]

    t_vel = 0
    if direction in x_axis:
        t_vel = int(velocity + math.log10(angle+10) * 5)
    elif direction in y_axis:
        t_vel = int(velocity + math.log10(angle+10) * 3)

    try: 
        if direction == "F":
            rcdriver.forward(velocity=t_vel)
        elif direction == "B":
            rcdriver.back(velocity=t_vel)
        elif direction == "L":
            rcdriver.left(velocity=t_vel)
        elif direction == "R":
            rcdriver.right(velocity=t_vel)
        else:
            rcdriver.stop_all()
    except: 
        return 

if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=8000)
