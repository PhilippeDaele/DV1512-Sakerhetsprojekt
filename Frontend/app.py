from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logger')
def logger():
    return render_template('logger.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')

if __name__ == "__main__":
    app.run(debug=True)
