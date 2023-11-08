from flask import Flask, request
from flask_cors import CORS
import threading
import json
import logging



def create_app(port):

    app = Flask(f'client_{port}')
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    @app.route('/get_status')
    def get_status():
        with open('cameras_config.json') as config_file:
            config = json.load(config_file)
            Cameras = config['Cameras']
        for cam_info in Cameras:
            cam_port = cam_info['port']
            cam_name = cam_info['name']
            cam_status = cam_info['status']
            if port == cam_port:
                return f"Name: {cam_name}, Port: {port}, Status: {cam_status}"

 
    @app.route('/set_status', methods=['GET'])
    def set_status():
        app.logger.info(request)
        with open('cameras_config.json') as config_file:
            config = json.load(config_file)
            Cameras = config['Cameras']
        new_status = request.args.get('new_status')
        for cam_info in Cameras:
            if cam_info['port'] == port:
                if cam_info['status'] != new_status:
                    cam_info['status'] = new_status
                    
                    with open('cameras_config.json', 'w') as config_file:
                        json.dump(config, config_file, indent=4)
                    response = f"""Status have changed <br>
                                    Name: {cam_info['name']} <br>
                                    Port: {port} <br>
                                    Status: {cam_info['status']}"""
                    return response
                else:
                    response = f"""Status have not changed <br>
                                    Name: {cam_info['name']} <br>
                                    Port: {port} <br>
                                    Status: {cam_info['status']}"""
                    return response
    app.run(debug=False, port=port)


if __name__ == '__main__':
    logging.basicConfig(filename='output.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

    with open('cameras_config.json') as config_file:
        config = json.load(config_file)
        Cameras = config['Cameras']

    threads = []
    for cam_info in Cameras:
        port = cam_info['port']
        thread = threading.Thread(target=create_app, args=(port,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
