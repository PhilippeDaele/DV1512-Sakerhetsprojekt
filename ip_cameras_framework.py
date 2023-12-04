"""Handeling the IP Cameras"""

from time import time
import threading
import logging
import sqlite3
import json
import time as tm
from flask import Flask, request, Response
from flask_cors import CORS
import cv2

logging.basicConfig(filename='output.log',level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

CAMERA_COUNT = 3

camera_frame_pos = [i*0 for i in range(CAMERA_COUNT)]
frame_interval = [None for i in range(CAMERA_COUNT)]
def increase_frame_pos(num, frame_duration):
    """Handles camera stream stuff"""
    camera_frame_pos[num] += frame_duration
    t = threading.Timer(1.0, increase_frame_pos,(num,frame_duration))
    t.start()
    return t
for i in range(CAMERA_COUNT):
    camera = cv2.VideoCapture(f"static/{i}.mp4")
    fps = camera.get(cv2.CAP_PROP_FPS)
    frame_count = int(camera.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    frame_interval[i] = increase_frame_pos(i,duration)

def dict_factory(cursor, row):
    """Returnes the fetched data from DB to json like object"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def fetch_all_camera_from_db():
    """Fetches cameras from DB"""
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.row_factory = dict_factory
    cursor.execute('SELECT * FROM t_cameras')
    cameras = cursor.fetchall()
    connect.close()
    return cameras

def create_app(port):
    """Creates the camera"""
    app = Flask(f'client_{port}')
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Rate limiting configuration
    rate_limit_period = 60
    max_requests = 10
    tokens = max_requests
    last_request_time = time()

    def is_rate_limited(endpoint):
        nonlocal tokens, last_request_time
        if endpoint in ('/reset-rate-limit', '/get_status'):
            return False

        current_time = time()
        elapsed_time = current_time - last_request_time

        if elapsed_time > rate_limit_period:
            # Refill tokens based on elapsed time only if time period elapsed
            tokens += (elapsed_time // rate_limit_period) * max_requests
            tokens = min(max_requests, tokens)
            last_request_time = current_time  # Update last request time

        # Check if there are enough tokens for the request
        if tokens >= 1:
            tokens -= 1
            return False  # Not rate-limited

        return True  # Rate-limited


    def gen_frames():  # generate frame by frame from camera
        #global frame_interval
        #global camera_frame_pos
        #global camera_watching
        video_camera = cv2.VideoCapture(f"static/{port%CAMERA_COUNT}.mp4")
        video_camera.set(cv2.CAP_PROP_POS_FRAMES, camera_frame_pos[port%CAMERA_COUNT])
        while True:
            # Capture frame-by-frame
            success, frame = video_camera.read()  # read the camera frame
            if not success:
                try:
                    video_camera.set(cv2.CAP_PROP_POS_FRAMES,0)
                    camera_frame_pos[port%CAMERA_COUNT] = 0
                    continue
                except ValueError:
                    print(ValueError)
                    break
            else:
                _, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                # concat frame one by one and show result
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  
                camera_frame_pos[port%CAMERA_COUNT] = video_camera.get(cv2.CAP_PROP_POS_FRAMES)
        # camera.release()
        # cv2.destroyAllWindows()
    @app.route('/video_feed')
    def video_feed():
        #Video streaming route. Put this in the src attribute of an img tag
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/reset-rate-limit')
    def reset_rate_limit_route():
        nonlocal tokens, last_request_time
        tokens = max_requests
        last_request_time = time()
        return "Rate limit reset successfully\n", 200

    @app.route('/get_status')
    def get_status():
        # Check rate limit before processing the request
        if is_rate_limited('/get_status'):
            return "Rate limit exceeded. Please try again later.", 429

        for cam_info in fetch_all_camera_from_db():
            cam_port = cam_info['port']
            cam_name = cam_info['cname']
            cam_status = cam_info['status']
            if port == cam_port:
                data = {
                "Name": cam_name,
                "Port": port,
                "Status": cam_status
                }

                # Convert the dictionary to a JSON object
                json_data = json.dumps(data)
                return json_data
                #return f"Name: {cam_name}, Port: {port}, Status: {cam_status}"
    @app.route('/')
    def index():
        for cam_info in fetch_all_camera_from_db():
            if port == cam_info['port']:
                cam_name = cam_info['cname']
        if is_rate_limited('/'):
            connect = sqlite3.connect('database.db')
            cursor = connect.cursor()
            cursor.execute(f"UPDATE t_cameras SET status='Inactive' WHERE port = '{port}'")
            connect.commit()
            connect.close()
            app.logger.warning(
                "Sent from: %s, Rate limit exceeded. %s is set to Inactive.",
                request.remote_addr,
                cam_name
            )
            return "Rate limit exceeded. Please try again later.\n", 429
        app.logger.info("Sent from: %s, %s", request.remote_addr, request)
        return "The path / does not exist or is not handled."
    @app.route('/<path:path>', methods=['GET', 'POST'])  # Catch-all route for undefined paths
    def catch_all(path):
        for cam_info in fetch_all_camera_from_db():
            if port == cam_info['port']:
                cam_name = cam_info['cname']
        if is_rate_limited('/<path:path>'):
            connect = sqlite3.connect('database.db')
            cursor = connect.cursor()
            cursor.execute(f"UPDATE t_cameras SET status='Inactive' WHERE port = '{port}'")
            connect.commit()
            connect.close()
            app.logger.warning(
                "Sent from: %s, Rate limit exceeded. %s is set to Inactive.",
                request.remote_addr,
                cam_name
            )
            return "Rate limit exceeded. Please try again later.\n", 429
        app.logger.info("Sent from: %s, %s", request.remote_addr, request)
        return f"The path '{path}' does not exist or is not handled."
    @app.route('/set_status', methods=['GET'])
    def set_status():
        # Check rate limit before processing the request
        for cam_info in fetch_all_camera_from_db():
            if port == cam_info['port']:
                cam_name = cam_info['cname']
        if is_rate_limited('/set_status'):
            connect = sqlite3.connect('database.db')
            cursor = connect.cursor()
            cursor.execute(f"UPDATE t_cameras SET status='Inactive' WHERE port = '{port}'")
            connect.commit()
            connect.close()
            app.logger.warning(
                "Sent from: %s, Rate limit exceeded. %s is set to Inactive.",
                request.remote_addr,
                cam_name
            )
            return "Rate limit exceeded. Please try again later.\n", 429
        new_status = request.args.get('new_status')
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        cursor.execute(f"UPDATE t_cameras SET status='{new_status}' WHERE port = '{port}'")
        connect.commit()
        connect.close()
        app.logger.info("Sent from: %s, %s", request.remote_addr, request)
        response = (
            f"""\nStatus have changed \nName: {cam_name} \nPort: {port} """
            f"""\nStatus: {new_status} \n"""
        )

        return response

    app.run(debug=False, port=port)

def start_camera(port):
    """Used when a new camera is created during runtime"""
    create_app(port)

if __name__ == '__main__':
    running_camera_ports = set()  # Store running camera ports

    def monitor_database_for_new_cameras():
        """Also used for the camera, serves to functions, starts all the cameras,
            starts new cameras added during runtime"""
        while True:
            cameras = fetch_all_camera_from_db()
            new_cameras = [cam for cam in cameras if cam['port'] not in running_camera_ports]
            for cam_info in new_cameras:
                port = cam_info['port']
                thread = threading.Thread(target=start_camera, args=(port,))
                thread.start()
                running_camera_ports.add(port)

            # Check for new cameras every 10 seconds (adjust as needed)
            tm.sleep(10)

    # Start a thread to monitor the database for new cameras
    db_monitor_thread = threading.Thread(target=monitor_database_for_new_cameras)
    db_monitor_thread.start()

    # Start Flask apps for existing cameras
    #cameras =
    for c_info in fetch_all_camera_from_db():
        start_camera(c_info['port'])
