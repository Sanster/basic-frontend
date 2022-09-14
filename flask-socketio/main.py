import time
import cv2
import numpy as np
from flask import Flask, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app, expose_headers=["Content-Disposition"])
MAX_BUFFER_SIZE = 50 * 1000 * 1000  # 50 MB
# async_mode 优先级: eventlet/gevent_uwsgi/gevent/threading
# only threading works on macos
socketio = SocketIO(app, max_http_buffer_size=MAX_BUFFER_SIZE, async_mode='threading')


@app.route("/")
def index():
    return send_file("index.html")

def run():
    for i in range(5):
        time.sleep(1)
        img = np.zeros((512,512, 3), dtype=np.uint8)
        img = cv2.putText(img, str(i),(150,150), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 2, cv2.LINE_AA)
        image_bytes = cv2.imencode('.jpg', img)[1].tobytes()
        print(f'send {i}')
        socketio.emit('image', {'image_bytes': image_bytes})

@socketio.on('start')
def handle_start():
    print('receive start message')
    socketio.start_background_task(run)

@socketio.on('client-image')
def handle_client_image(data):
    raw_bytes = data['image']
    print(f"receive client image: {data.keys()}")
    nparr = np.frombuffer(raw_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite("client_image.jpg", img)

@socketio.on('connected')
def handle_message(data):
    print(f"on [connected]: {data}")

if __name__ == "__main__":
    # app.run(port=6001, debug=True)
    socketio.run(app, port=6001, debug=True)
    # socketio.run(app, port=6001)
