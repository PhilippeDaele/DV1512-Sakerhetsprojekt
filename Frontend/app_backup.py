from flask import Flask, render_template, url_for, request 
import sqlite3 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

connect = sqlite3.connect('database.db') 
connect.execute('CREATE TABLE IF NOT EXISTS t_users (uname TEXT, password TEXT)') 

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST': 
        uname = request.form['uname'] 
        password = request.form['password'] 

        connect = sqlite3.connect('database.db') 
        cursor = connect.cursor() 
        cursor.execute('SELECT * FROM t_users WHERE `uname` = ? AND `password` = ?',(uname,password)) 
        data = cursor.fetchall()
        if len(data) != 0:
            return render_template('login.html',success = True)
        else:
            return render_template('login.html') 
    else: 
        return render_template('login.html') 

@app.route('/logger')
def logger():
    return render_template('logger.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')

if __name__ == "__main__":
    app.run(debug=True)
