from flask import Flask, render_template, Response, request, jsonify
import cv2
import time
import math

from motor import Motor

rcdriver = Motor((5, 6, 13), (16, 26, 12))
velocity = 20

app = Flask(__name__)

@app.route("/dir/<param>", methods=["GET"])
def direction(param):
    direction = param
    angle = int(request.args.get('angle'))
    
    x_axis = ["F", "L"]
    y_axis = ["L", "R"]

    t_vel = 0
    if direction in x_axis:
        t_vel = int(velocity + math.log10(int) * 5)
    elif direction in y_axis:
        t_vel = int(velocity + math.log10(angle) * 3)

    try: 
        if direction == "F":
            rcdriver.forward(velocity=t_vel)
        elif direction == "B":
            rcdriver.back(velocity=velocity)
        elif direction == "L":
            rcdriver.left(velocity=velocity)
        elif direction == "R":
            rcdriver.right(velocity=velocity)
        else:
            rcdriver.stop_all()

        return jsonify({"status": "Niceeee!!"})
    except: 
        return jsonify({"status": "Internal Server Error"})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(stream_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

def stream_video():
    camera = cv2.VideoCapture(0) 

    while True:
        success, frame = camera.read()
        if not success:
            break

        frame = cv2.flip(frame,180)

        target_size = (1024,768)
        ratio = target_size[1] / target_size[0] 
        height = frame.shape[0]
        target_width = height * ratio
        new_frame = frame[:, int(frame.shape[1] / 2 - target_width / 2):int(frame.shape[1] / 2 + target_width / 2) , :]

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 99]
        ret, jpeg = cv2.imencode('.jpg', new_frame, encode_param)
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    camera.release()

if __name__ == '__main__':
    app.run("127.0.0.1", 8000, debug=True)
