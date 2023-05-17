import io
import socket
import struct
import time
# import picamera
import cv2
import sys
import threading
import config
import pickle
import numpy as np


class SplitFrames(object):
    def __init__(self, connection):
        self.connection = connection
        self.stream = io.BytesIO()
        self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                self.connection.flush()
                self.connection.seek(0)
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
        self.stream.write(buf)


res = (320, 240)
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])

encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]

# fourcc = cv2.VideoWriter_fourcc(*'MJPG')
# out = cv2.VideoWriter(output, fourcc, 30.0, res)

# client_socket = socket.socket()
# client_socket.connect((config.IP_ADDRESS, 1502))
# connection = client_socket.makefile("wb")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((config.IP_ADDRESS, 1504))

# def send_signal():
#     time.sleep(2)  
#     connection.write(struct.pack('<L', 0))  

# # Start the signal sending thread
# signal_thread = threading.Thread(target=send_signal)
# signal_thread.start()

try:
    # output = SplitFrames(connection)
    # with picamera.PiCamera(resolution=res, framerate=30) as camera:
    #     time.sleep(2)
    #     start = time.time()
    #     camera.start_recording(output, format='mjpeg')
    #     camera.wait_recording(sys.maxint)
    #     camera.stop_recording()

    #     connection.write(struct.pack('<L', 0))
    img_counter = 0
    while True:
        start = time.time()
        ret, frame = capture.read()

        if not ret: break

        frame = cv2.flip(frame,180)
        # out.write(frame)

        result, image = cv2.imencode('.jpg', frame, encode_param)
        data = pickle.dumps(image, 0)

        size = len(data)
        # output.write(data)
        if img_counter%10==0:
            client_socket.sendall(struct.pack(">L", size) + data)
            # cv2.imshow('client',frame)
        img_counter += 1
        if cv2.waitKey(1) == ord('q'):
            break

finally:
    finish = time.time()
    print("aksjfl;asdkjf")
    # print('Sent %d images in %d seconds at %.2ffps' % (
    #     output.count, finish-start, output.count / (finish-start)))
    # connection.close()
    # client_socket.close()