from flask import Flask, request
from flask_cors import CORS
import threading
import logging
import sqlite3

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
    #app.config['SECRET_KEY'] = 'SmartSec'
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    @app.route('/get_status')
    def get_status():
        Cameras = fetch_all_camera_from_db()
        for cam_info in Cameras:
            cam_port = cam_info['port']
            cam_name = cam_info['cname']
            cam_status = cam_info['status']
            if port == cam_port:
                return f"Name: {cam_name}, Port: {port}, Status: {cam_status}"

    @app.route('/set_status', methods=['GET'])
    def set_status():
        Cameras = fetch_all_camera_from_db()
        new_status = request.args.get('new_status')
        for cam_info in Cameras:
            cam_info['status'] = new_status
            connect = sqlite3.connect('database.db')
            cursor = connect.cursor()
            cursor.execute(f"UPDATE t_cameras SET status='{new_status}' WHERE port = '{port}'")
            connect.commit()
            connect.close()
            app.logger.info(f"Sent from: {request.remote_addr}, {request}")
            response = f"""\nStatus have changed \n Name: {cam_info['cname']} \n Port: {port} \n Status: {cam_info['status']} \n"""
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
