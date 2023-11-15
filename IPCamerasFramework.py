from flask import Flask, request, Response
from flask_cors import CORS
import threading
import logging
import sqlite3
import cv2
from time import sleep, time
from io import BytesIO

logging.basicConfig(filename='output.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def fetch_all_camera_from_db():
    connect = sqlite3.connect('database.db') 
    cursor = connect.cursor() 
    cursor.row_factory = dict_factory
    cursor.execute('SELECT * FROM t_cameras') 
    Cameras = cursor.fetchall()
    connect.close()
    return Cameras

def create_app(port):
    app = Flask(f'client_{port}')
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Rate limiting configuration
    RATE_LIMIT_PERIOD = 60  # 60 seconds
    MAX_REQUESTS = 10  # Maximum requests allowed in the given period
    tokens = MAX_REQUESTS
    last_request_time = time()

    def is_rate_limited(endpoint):
        nonlocal tokens, last_request_time
        if endpoint == '/reset-rate-limit':
            return False

        current_time = time()
        #elapsed_time = current_time - last_request_time

        # Refill tokens based on elapsed time
        #tokens += elapsed_time * (MAX_REQUESTS / RATE_LIMIT_PERIOD)
        #tokens = min(MAX_REQUESTS, tokens)

        # Check if there are enough tokens for the request
        if tokens >= 1:
            tokens -= 1
            last_request_time = current_time
            return False  # Not rate-limited
        else:
            return True  # Rate-limited
        

    # Example usage in Flask route handling the button click
    @app.route('/reset-rate-limit')
    def reset_rate_limit_route():
        nonlocal tokens, last_request_time
        tokens = MAX_REQUESTS
        last_request_time = time()
        return "Rate limit reset successfully", 200
    
    @app.route('/get_status')
    def get_status():
        # Check rate limit before processing the request
        if is_rate_limited('/get_status'):
            return "Rate limit exceeded. Please try again later.", 429

        Cameras = fetch_all_camera_from_db()
        for cam_info in Cameras:
            cam_port = cam_info['port']
            cam_name = cam_info['cname']
            cam_status = cam_info['status']
            if port == cam_port:
                return f"Name: {cam_name}, Port: {port}, Status: {cam_status}" 

    @app.route('/')
    def index():
        Cameras = fetch_all_camera_from_db()
        for cam_info in Cameras:
            if port == cam_info['port']:
                cam_name = cam_info['cname']
        if is_rate_limited('/'):
            connect = sqlite3.connect('database.db')
            cursor = connect.cursor()
            cursor.execute(f"UPDATE t_cameras SET status='Inactive' WHERE port = '{port}'")
            connect.commit()
            connect.close()
            app.logger.warning(f"Sent from: {request.remote_addr}, Rate limit exceeded. {cam_name} is set to Inactive.")
            return "Rate limit exceeded. Please try again later.\n", 429
        app.logger.warning(f"Sent from: {request.remote_addr}, {request}")
        return f"The path / does not exist or is not handled."
    
    @app.route('/<path:path>', methods=['GET', 'POST'])  # Catch-all route for undefined paths
    def catch_all(path):
        Cameras = fetch_all_camera_from_db()
        for cam_info in Cameras:
            if port == cam_info['port']:
                cam_name = cam_info['cname']
        if is_rate_limited('/<path:path>'):
            connect = sqlite3.connect('database.db')
            cursor = connect.cursor()
            cursor.execute(f"UPDATE t_cameras SET status='Inactive' WHERE port = '{port}'")
            connect.commit()
            connect.close()
            app.logger.warning(f"Sent from: {request.remote_addr}, Rate limit exceeded. {cam_name} is set to Inactive.")
            return "Rate limit exceeded. Please try again later.\n", 429
        app.logger.warning(f"Sent from: {request.remote_addr}, {request}")
        return f"The path '{path}' does not exist or is not handled."
            
    

    @app.route('/set_status', methods=['GET'])
    def set_status():
        # Check rate limit before processing the request
        Cameras = fetch_all_camera_from_db()
        for cam_info in Cameras:
            if port == cam_info['port']:
                cam_name = cam_info['cname']
        if is_rate_limited('/set_status'):
            connect = sqlite3.connect('database.db')
            cursor = connect.cursor()
            cursor.execute(f"UPDATE t_cameras SET status='Inactive' WHERE port = '{port}'")
            connect.commit()
            connect.close()
            app.logger.warning(f"Sent from: {request.remote_addr}, Rate limit exceeded. {cam_name} is set to Inactive.")
            return "Rate limit exceeded. Please try again later.\n", 429
        else:
            new_status = request.args.get('new_status')
            #for cam_info in Cameras:
            cam_info['status'] = new_status
            connect = sqlite3.connect('database.db')
            cursor = connect.cursor()
            cursor.execute(f"UPDATE t_cameras SET status='{new_status}' WHERE port = '{port}'")
            connect.commit()
            connect.close()
            app.logger.info(f"Sent from: {request.remote_addr}, {request}")
            response = f"""\nStatus have changed \nName: {cam_name} \nPort: {port} \nStatus: {new_status} \n"""
            return response

    app.run(debug=False, port=port)

if __name__ == '__main__':
    Cameras = fetch_all_camera_from_db()
    threads = []

    for cam_info in Cameras:
        port = cam_info['port']
        thread = threading.Thread(target=create_app, args=(port,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
