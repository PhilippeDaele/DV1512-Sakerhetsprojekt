from flask import Flask, render_template, request, redirect, session
import sqlite3 

app = Flask(__name__) 
app.config['SECRET_KEY'] = 'SmartSec'

connect = sqlite3.connect('database.db') 
connect.execute('CREATE TABLE IF NOT EXISTS t_users (uname TEXT, password TEXT, privilege TEXT)') 
connect.execute('CREATE TABLE IF NOT EXISTS t_cameras (cname TEXT, port INTEGER, status TEXT)') 
# connect.execute("INSERT INTO t_users VALUES ('admin', 'admin', 'admin'),('user','user','user')")
# connect.execute("INSERT INTO t_cameras VALUES ('Cam1', 5001, 'Inactive'),\
#        ('Cam2', 5002, 'Inactive'),\
#        ('Cam3', 5003, 'Active'),\
#        ('Cam4', 5004, 'Active'),\
#        ('Cam5', 5005, 'Inactive'),\
#        ('Cam6', 5006, 'Active'),\
#        ('Cam7', 5007, 'Active'),\
#        ('Cam8', 5008, 'Inactive'),\
#        ('Cam9', 5009, 'Active'),\
#        ('Cam10', 50010, 'Active'),\
#        ('Cam11', 50011, 'Active'),\
#        ('Cam12', 50012, 'Inactive'),\
#        ('Cam13', 50013, 'Inactive'),\
#        ('Cam14', 50014, 'Inactive'),\
#        ('Cam15', 50015, 'Inactive'),\
#        ('Cam16', 50016, 'Inactive'),\
#        ('Cam17', 50017, 'Inactive'),\
#        ('Cam18', 50018, 'Active')") 
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
def home(): 
    if not session.get('loggedin_as'):
        return show_login_page()
    Cameras = fetch_all_camera_from_db()
    return render_template('index.html',cameras=Cameras, user=session.get('loggedin_as')[2])

@app.route('/detailed_view')
def detailed_view():
    Cameras = fetch_all_camera_from_db()
    return render_template('detailedView.html',cameras=Cameras, user=session.get('loggedin_as')[2])

@app.route('/log')
def log():
    return render_template('log.html')

@app.route('/logout')
def logout():
    if session.get('loggedin_as'):
        session.pop('loggedin_as',None)
    return redirect('/')

def show_login_page():
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def login_user():
    uname = request.form['username'] 
    password = request.form['password'] 

    connect = sqlite3.connect('database.db') 
    cursor = connect.cursor() 
    cursor.execute('SELECT * FROM t_users WHERE `uname` = ? AND `password` = ?',(uname,password))     
    data = cursor.fetchall()
    if len(data) != 0:
        session['loggedin_as'] = data[0]
        return render_template('index.html', user=session.get('loggedin_as')[2])
    else:
        return show_login_page()

if __name__ == '__main__': 
    app.run(debug=True) 