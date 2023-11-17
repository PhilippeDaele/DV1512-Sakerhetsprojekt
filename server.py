from flask import Flask, flash, render_template, request, redirect, session
import sqlite3
import logging

logging.basicConfig(filename='output.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__) 
app.config['SECRET_KEY'] = 'SmartSec'
app.config['PERMANENT_SESSION_LIFETIME'] = 600


connect = sqlite3.connect('database.db') 
connect.execute('CREATE TABLE IF NOT EXISTS t_users (uname TEXT, password TEXT, privilege TEXT)')
connect.execute('CREATE TABLE IF NOT EXISTS t_cameras (cname TEXT, port INTEGER, status TEXT, lat FLOAT, lng FLOAT)') 
# connect.execute('DROP TABLE IF EXISTS t_cameras')
# connect.execute("INSERT INTO t_users VALUES ('admin', 'admin', 'admin'),('user','user','user')")
# connect.execute("INSERT INTO t_cameras VALUES ('Cam1', 5001, 'Inactive', 56.181872002369225, 15.591392032746274),\
#        ('Cam2', 5002, 'Inactive', 56.181298760504475, 15.592301301593377),\
#        ('Cam3', 5003, 'Active', 56.181142013179894, 15.59325616798587),\
#        ('Cam4', 5004, 'Active', 56.18227356514871, 15.590906552911559),\
#        ('Cam5', 5005, 'Inactive', 56.18267661649659, 15.590370111113307),\
#        ('Cam6', 5006, 'Active', 56.18329462033708, 15.5901394411406),\
#        ('Cam7', 5007, 'Active', 56.18285574906873, 15.591367892855724),\
#        ('Cam8', 5008, 'Inactive', 56.18066130753176, 15.590654472780827),\
#        ('Cam9', 5009, 'Active', 56.182109347917304, 15.593304495257986)")
# connect.commit()


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
    return Cameras

@app.route('/')
def redirect_to_home():
    if not session.get('loggedin_as'):
        return redirect('/login')
    return redirect('/camera_hub')

@app.route('/add')
def show_add_page():
    if not session.get('loggedin_as'):
        return redirect('/login')
    Cameras = fetch_all_camera_from_db()
    return render_template('add.html',cameras=Cameras, user=session.get('loggedin_as')[2])

@app.route('/add',methods=['POST'])
def add_camera():
    cname = request.form['cname'] 
    port = request.form['port'] 
    longitude = request.form['longitude'] 
    latitude = request.form['latitude'] 
    connect = sqlite3.connect('database.db') 
    print(f"INSERT INTO t_cameras VALUES ('{cname}', {port}, 'Inactive', {latitude}, {longitude})")
    connect.execute(f"INSERT INTO t_cameras VALUES ('{cname}', {port}, 'Inactive', {latitude}, {longitude})")
    connect.commit()
    connect.close()
    return redirect('/')

@app.route('/camera_hub')
def home(): 
    if not session.get('loggedin_as'):
        return redirect('/login')
    Cameras = fetch_all_camera_from_db()
    return render_template('index.html',cameras=Cameras, user=session.get('loggedin_as')[2])


@app.route('/detailed_view')
def detailed_view():
    if not session.get('loggedin_as'):
        return redirect('/login')
    Cameras = fetch_all_camera_from_db()
    return render_template('detailedView.html',cameras=Cameras, user=session.get('loggedin_as')[2])



@app.route('/log')
def log():
    if not session.get('loggedin_as'):
        return redirect('/login')
    with open('output.log', 'r') as log_file:
        log_content = log_file.readlines()
    return render_template('log.html', log=log_content, user=session.get('loggedin_as')[2])

@app.route('/logout')
def logout():
    if session.get('loggedin_as'):
        session.pop('loggedin_as',None)
    return redirect('/')

@app.route('/login')
def show_login_page():
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def login_user():
    uname = request.form['username'] 
    password = request.form['password'] 
    app.logger.info(f"Username: {uname}, Password: {password}, Sent from: {request.remote_addr}, {request}")
    connect = sqlite3.connect('database.db') 
    cursor = connect.cursor() 
    cursor.execute('SELECT * FROM t_users WHERE `uname` = ? AND `password` = ?',(uname,password))     
    data = cursor.fetchall()
    connect.close()
    if len(data) != 0:
        session['loggedin_as'] = data[0]
        
        return redirect('/')
    else:
        flash("Wrong username or password")
        return show_login_page()

if __name__ == '__main__':
    
    app.run(debug=True)