from werkzeug.urls import url_parse

from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Run, Sleep
from app.reset import reset_data


@app.route('/')
@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        flash('User Logged in: {}'.format(form.username.data))
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.route('/reset_db')
def reset_db():
    flash("Resetting database: deleting old data and repopulating with dummy data")
    # clear all data from all tables - in a separate file...
    reset_data()
    return redirect('/')

@app.route('/info_page/<name>')
@login_required
def inform(name):
    user = User.query.filter_by(name=name).first()
    return render_template('userInfo.html',user=user)

@app.route('/register_run')
@login_required
def register_run():
    return render_template('register_run.html')

@app.route('/register_sleep')
@login_required
def register_sleep():
    return render_template('register_sleep.html')

@app.route('/compare/<name>To<otherName>')
@login_required
def compare(name,otherName):
    user = User.query.filter_by(name=name).first()
    user2 = User.query.filter_by(name=otherName).first()
    return render_template('compare.html',user=user,user2=user2)


@app.route('/runs_archive')
def runs_archive():
    runs = Run.query.all()
    return render_template('runs_archive.html', title='Runs Archive', runs=runs)


@app.route('/sleep_archive')
def sleep_archive():
    sleeps = Sleep.query.all()
    return render_template('sleep_archive.html', title='Sleep Archive', sleeps=sleeps)


@app.route('/day_display')
def day_display():
    runs = Run.query.all()
    sleeps = Sleep.query.all()
    return render_template('day_display.html', title='Day Display', run=runs, sleep=sleeps)
