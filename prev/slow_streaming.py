# Import the required modules
from IPython.display import clear_output
import socket
import sys
import cv2
import matplotlib.pyplot as plt
import pickle
import numpy as np
import struct ## new
import zlib
from PIL import Image, ImageOps

from flask import Flask, render_template, Response
import cv2
app = Flask(__name__)

import config

HOST=config.IP_ADDRESS
PORT=1504

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn,addr=s.accept()

data = b""
payload_size = struct.calcsize(">L")
print("payload_size: {}".format(payload_size))


def gen_frames():  
    global data, conn, payload_size
    while True:
        while len(data) < payload_size:
            data += conn.recv(4096)
            if not data:
                cv2.destroyAllWindows()
                conn,addr=s.accept()
                continue
        # receive image row data form client socket
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        # unpack image using pickle 
        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        target_size = (1024,768)
        ratio = target_size[1] / target_size[0] 
        height = frame.shape[0]
        middle_width = frame.shape[1] / 2
        target_width = height * ratio / 2
        roi = frame[:, int(middle_width-target_width/2):int(middle_width+target_width/2), :]
        
        new_frame = cv2.hconcat([roi, roi])

        ret, buffer = cv2.imencode('.jpg', new_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)