"""Handles the server"""

import sqlite3
import logging
from flask import Flask, render_template, request, redirect, session, flash


logging.basicConfig(filename='output.log', level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')
log_level = logging.getLogger('werkzeug')
log_level.setLevel(logging.ERROR)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SmartSec'
app.config['PERMANENT_SESSION_LIFETIME'] = 600


connect = sqlite3.connect('database.db')
#connect.execute('DROP TABLE IF EXISTS t_cameras')
#connect.execute('DROP TABLE IF EXISTS t_userrs')
CREATE_USER_TABLE = '''
    CREATE TABLE IF NOT EXISTS t_users (
        uname TEXT,
        password TEXT,
        privilege TEXT
    )
'''
CREATE_CAMERAS_TABLE = '''
    CREATE TABLE IF NOT EXISTS t_cameras (
        cname TEXT,
        port INTEGER,
        status TEXT,
        lat FLOAT,
        lng FLOAT
    )
'''
connect.execute(CREATE_USER_TABLE)
connect.execute(CREATE_CAMERAS_TABLE)
#connect.execute('CREATE TABLE IF NOT EXISTS t_users
# (uname TEXT, password TEXT, privilege TEXT)')
#connect.execute('CREATE TABLE IF NOT EXISTS t_cameras
# (cname TEXT, port INTEGER, status TEXT, lat FLOAT, lng FLOAT)')
#connect.execute("INSERT INTO t_users VALUES
# ('user','user','user'),('admin', 'admin', 'admin')")
#connect.execute("INSERT INTO t_cameras VALUES
#        ('Cam1', 5001, 'Inactive', 56.181872002369225, 15.591392032746274),\
#        ('Cam2', 5002, 'Inactive', 56.181298760504475, 15.592301301593377),\
#        ('Cam3', 5003, 'Active', 56.181142013179894, 15.59325616798587),\
#        ('Cam4', 5004, 'Active', 56.18227356514871, 15.590906552911559),\
#        ('Cam5', 5005, 'Inactive', 56.18267661649659, 15.590370111113307),\
#        ('Cam6', 5006, 'Active', 56.18329462033708, 15.5901394411406),\
#        ('Cam7', 5007, 'Active', 56.18285574906873, 15.591367892855724),\
#        ('Cam8', 5008, 'Inactive', 56.18066130753176, 15.590654472780827),\
#        ('Cam9', 5009, 'Active', 56.182109347917304, 15.593304495257986)")
#connect.commit()


def dict_factory(cursor, row):
    """Returnes the fetched data from DB to json like object"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def fetch_all_camera_from_db():
    """Fetches cameras from DB"""
    new_connect = sqlite3.connect('database.db')
    cursor = new_connect.cursor()
    cursor.row_factory = dict_factory
    cursor.execute('SELECT * FROM t_cameras')
    return cursor.fetchall()

@app.route('/')
def redirect_to_home():
    """Redirects to home page"""
    if not session.get('loggedin_as'):
        return redirect('/login')
    return redirect('/camera_hub')

@app.route('/delete_camera',methods=['POST'])
def delete_camera():
    """Deletes the given camera from DB"""
    cname = request.form['cname']
    delete_connect = sqlite3.connect('database.db')
    delete_connect.execute("DELETE FROM t_cameras WHERE cname = ?", (cname,))
    delete_connect.commit()
    delete_connect.close()
    return redirect('/')


@app.route('/add')
def show_add_page():
    """Shows the add page"""
    if not session.get('loggedin_as'):
        return redirect('/login')
    cameras = fetch_all_camera_from_db()
    return render_template('add.html',cameras=cameras, user=session.get('loggedin_as'))

@app.route('/add',methods=['POST'])
def add_camera():
    """Adds the camera to DB"""
    cname = request.form['cname']
    port = request.form['port']
    longitude = request.form['longitude']
    latitude = request.form['latitude']
    add_connect = sqlite3.connect('database.db')
    insert_camera_query = '''
        INSERT INTO t_cameras (cname, port, status, lat, lng)
        VALUES (?, ?, 'Inactive', ?, ?)
    '''
    camera_values = (cname, port, latitude, longitude)
    add_connect.execute(insert_camera_query, camera_values)
    #connect.execute(f"INSERT INTO t_cameras VALUES('{cname}',
    # {port}, 'Inactive', {latitude}, {longitude})")
    connect.commit()
    connect.close()
    return redirect('/')

@app.route('/camera_hub')
def home():
    """Shows home page"""
    if not session.get('loggedin_as'):
        return redirect('/login')
    cameras = fetch_all_camera_from_db()
    return render_template('index.html',cameras=cameras, user=session.get('loggedin_as'))


@app.route('/detailed_view')
def detailed_view():
    """Shows the detailed view, not sure if still needed"""
    if not session.get('loggedin_as'):
        return redirect('/login')
    cameras = fetch_all_camera_from_db()
    return render_template('detailedView.html',cameras=cameras, user=session.get('loggedin_as'))



@app.route('/log')
def log():
    """Shows the logger page"""
    if not session.get('loggedin_as'):
        return redirect('/login')
    with open('output.log', 'r', encoding='utf-8') as log_file:
        log_content = log_file.readlines()
    return render_template('log.html', log=log_content, user=session.get('loggedin_as'))

@app.route('/logout')
def logout():
    """Handles logut"""
    if session.get('loggedin_as'):
        session.pop('loggedin_as',None)
    return redirect('/')

@app.route('/login')
def show_login_page():
    """Shows login page"""
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def login_user():
    """Handles login"""
    uname = request.form['username']
    password = request.form['password']
    login_connect = sqlite3.connect('database.db')
    cursor = login_connect.cursor()
    cursor.execute(f"SELECT * FROM t_users WHERE `uname` = '{uname}' AND `password` = '{password}'")
    data = cursor.fetchall()
    login_connect.close()
    if len(data) != 0:
        if len(password) == 0 or "'" in uname:
            log_message = \
                f"Possible SQL Attack: Username: {uname}, " \
                f"Password: {password}, " \
                f"Sent from: {request.remote_addr}"

            app.logger.warning(log_message)

        else:
            log_message = (
                f"Username: {uname}, "
                f"Password: {password}, "
                f"Sent from: {request.remote_addr}"
            )
            app.logger.info(log_message)

        session['loggedin_as'] = data[0]
        return redirect('/')
    log_message = (
        f"Username: {uname}, "
        f"Password: {password}, "
        f"Sent from: {request.remote_addr}"
    )
    app.logger.warning(log_message)
    flash("Wrong username or password")
    return show_login_page()


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
