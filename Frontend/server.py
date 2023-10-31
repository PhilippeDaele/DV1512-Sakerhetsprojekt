from flask import Flask, render_template, request, redirect, send_from_directory
from flask_cors import CORS
import json
import logging

app = Flask(__name__)

"""
with open('cameras_config.json') as config_file:
    config = json.load(config_file)
    Cameras = config['Cameras']
    Database = config['Database']
"""
username = ''
password = ''

def authenticate_user(username, password):
    with open('cameras_config.json') as config_file:
        config = json.load(config_file)
        Database = config['Database']
    if username == Database[0]['username'] and password == Database[0]['password']:
        return 'admin', True
    elif username == Database[1]['username'] and password == Database[1]['password']:
        return 'user', True
    return 'neither', False


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def go_to_login():
    return redirect('/login')

@app.route('/logout')
def logout():
    global username
    global password
    username = password = ''
    return redirect('/login')

@app.route('/camera_hub')
def home():
    global username
    global password
    userOrAdmin, allowed = authenticate_user(username, password)
    if allowed:
        with open('cameras_config.json') as config_file:
            config = json.load(config_file)
            Cameras = config['Cameras']
        return render_template('index.html', cameras=Cameras, user=userOrAdmin)
    else:
        return redirect('/login')
    
@app.route('/log')
def log():
    global username
    global password
    userOrAdmin, allowed = authenticate_user(username, password)
    if allowed:
        with open('output.log', 'r') as log_file:
            log_content = log_file.read()
        return render_template('log.html', log=log_content, user=userOrAdmin)
    else:
        return redirect('/login')
    

@app.route('/detailed_view')
def detailed_view():
    global username
    global password
    userOrAdmin, allowed = authenticate_user(username, password)
    if allowed:
        with open('cameras_config.json') as config_file:
            config = json.load(config_file)
            Cameras = config['Cameras']
            print(Cameras)
        return render_template('detailedView.html', cameras=Cameras, user=userOrAdmin)
    else:
        return redirect('/login')


@app.route('/camera_hub', methods=['POST'])
def index():
    global username
    global password
    username = request.form.get('username')
    password = request.form.get('password')
    app.logger.info(f"Username: {username}, Password: {password}, {request}")
    userOrAdmin, allowed = authenticate_user(username, password)
    if allowed:
        with open('cameras_config.json') as config_file:
            config = json.load(config_file)
            Cameras = config['Cameras']
        return render_template('index.html', cameras=Cameras, user=userOrAdmin)
    else:
        return redirect('/login')

if __name__ == '__main__':
    username = password = ''
    logging.basicConfig(filename='output.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    app.run(debug=True)