from werkzeug.urls import url_parse

from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Run, Sleep
from app.reset import reset_data
from app.formulas import run_trend, sleep_trend, avg_func, avg_pace, rec, sleep_duration


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


@app.route('/runs_archive')
def runs_archive():
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    runs = Run.query.filter_by(user_id=current_user.id)
    runs_count = runs.count()
    return render_template('runs_archive.html', title='Runs Archive', runs=runs, runs_count=runs_count)


@app.route('/sleep_archive')
def sleep_archive():
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    sleeps = Sleep.query.filter_by(user_id=current_user.id)
    sleeps_count = sleeps.count()
    return render_template('sleep_archive.html', title='Sleep Archive', sleeps=sleeps, sleeps_count=sleeps_count)


@app.route('/day_display')
def day_display():
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    runs = Run.query.all()
    sleeps = Sleep.query.all()
    return render_template('day_display.html', title='Day Display', run=runs, sleep=sleeps)


@app.route('/run_display/<run_id>')
def run_display(run_id):
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    run = Run.query.filter_by(id=run_id).first_or_404()
    # score = run_trend()
    # pace = avg_pace()
    # rec = rec()
    score = 100
    pace = "7:50 min/mi"
    rec = "Get 8 hours of sleep tonight!"
    return render_template('run_display.html', title='Run Display', run=run, score=score,
                           pace=pace, rec=rec)


@app.route('/sleep_display/<sleep_id>')
def sleep_display(sleep_id):
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    sleep = Sleep.query.filter_by(id=sleep_id).first_or_404()
    # score = sleep_trend()
    # duration = sleep_duration()
    # rec = rec()
    score = 100
    duration = "8 hours!"
    rec = "run 7 miles today!"
    return render_template('sleep_display.html', title='Sleep Display', sleep=sleep, score=score,
                           duration=duration, rec=rec)

