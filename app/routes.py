from app import app
from flask import render_template
from flask_login import login_user, logout_user, current_user, login_required

@app.route('/')
@app.route('/main')
def main():
    return render_template('base.html')


@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')