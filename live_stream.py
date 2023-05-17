from flask import Flask, render_template, Response, request, jsonify
import cv2
import time
# import paho.mqtt.client as mqtt 

# from motor import Motor

# rcdriver = Motor()
vel = 30

# # Setup callback functions that are called when MQTT events happen like 
# # connecting to the server or receiving data from a subscribed feed. 
# def on_connect(client, userdata, flags, rc): 
#    print("Connected with result code " + str(rc)) 
#    # Subscribing in on_connect() means that if we lose the connection and 
#    # reconnect then subscriptions will be renewed. 
#    client.subscribe("/con/pi") 
# # The callback for when a PUBLISH message is received from the server. 
# def on_message(client, userdata, msg): 
#     print(msg.topic+" "+str( msg.payload)) 
#     if msg.topic == '/con/pi': 
#         direction = msg.topic    
#         if direction == b"F":
#             rcdriver.forward(velocity=vel)
#         elif direction == b"B":
#             rcdriver.back(velocity=vel)
#         elif direction == b"L":
#             rcdriver.left(velocity=vel)
#         elif direction == b"R":
#             rcdriver.right(velocity=vel)
#         elif direction == b"S":
#             rcdriver.stop_all()
#         else:
#             print({"error": "Please select appropriate direction"})
        
# # Create MQTT client and connect to localhost, i.e. the Raspberry Pi running 
# # this script and the MQTT server. 
# client = mqtt.Client() 
# client.on_connect = on_connect 
# client.on_message = on_message 
# client.connect('localhost', 1883, 60) 
# # Connect to the MQTT server and process messages in a background thread. 
# client.loop_start() 

app = Flask(__name__)

@app.route('/live')
def index():
    return render_template('index.html')

@app.route('/live/video_feed')
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
        middle_width = frame.shape[1] / 2
        target_width = height * ratio / 2
        roi = frame[:, int(middle_width-target_width/2):int(middle_width+target_width/2), :]
        
        new_frame = cv2.hconcat([roi, roi])

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 99]
        ret, jpeg = cv2.imencode('.jpg', new_frame, encode_param)
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    camera.release()

if __name__ == '__main__':
    app.run("0.0.0.0", 8080, debug=True)
