from datetime import timedelta, datetime
from sqlalchemy import func
from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import LoginForm, RegistrationForm, SleepForm, RunForm
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Run, Sleep
from app.reset import reset_data
from app.formulas import run_trend, sleep_trend, item_suggest, sum_function, avg_function


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
    return render_template('registers/register.html', title='Register', form=form)


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
    # NEED CALCULATED FIELDS
    return render_template('user_info.html', user=user)


@app.route('/register_run', methods=['GET', 'POST'])
@login_required
def register_run():
    form = RunForm()

    if form.validate_on_submit():
        run = Run(
            date=form.date.data,
            distance=form.distance.data,
            duration=timedelta(hours=form.hours.data, minutes=form.minutes.data, seconds=form.seconds.data),
            temp=form.temperature.data,
            time_of_day=form.time_of_day.data,
            effort=form.effort.data,
            weather=form.weather.data,
            notes=form.notes.data,
            user_id=current_user.id)
        db.session.add(run)
        db.session.commit()
        flash('Run submitted successfully!')
        return redirect(url_for('main'))
    return render_template('registers/register_run.html', title='Submit Run', form=form)


@app.route('/register_sleep', methods=['GET', 'POST'])
@login_required
def register_sleep():
    form = SleepForm()
    if form.validate_on_submit():
        date_from_form = form.date.data

        # Get time from the form
        bedtime = form.bedtime.data
        wake_up = form.wake_up.data

        # Combine date and time to create datetime objects
        bedtime_datetime = datetime.combine(date_from_form, bedtime)
        wake_up_datetime = datetime.combine(date_from_form, wake_up)

        existing_sleep = Sleep.query.filter(Sleep.user_id == current_user.id,
                                            func.date(Sleep.date) == date_from_form).first()

        if existing_sleep:
            flash('Sleep data for this date already exists. Please choose a different date.')
            return render_template('registers/register_sleep.html', title='Submit Sleep', form=form)

        sleep = Sleep(
            date=form.date.data,
            bedtime=bedtime_datetime,
            wake_up=wake_up_datetime,
            times_awoken=form.times_awoken.data,
            dreams_torf=form.dreams_torf.data,
            notes=form.notes.data,
            user_id=current_user.id)
        db.session.add(sleep)
        db.session.commit()
        flash('Sleep submitted successfully!')
        return redirect(url_for('main'))
    return render_template('registers/register_sleep.html', title='Submit Sleep', form=form)


@app.route('/compareTo/<otherName>')
@login_required
def compare(otherName):
    user = current_user
    user2 = User.query.filter_by(username=otherName).first()
    return render_template('compare.html', user=user, user2=user2)


@app.route('/runs_archive')
@login_required
def runs_archive():
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    runs = Run.query.filter_by(user_id=current_user.id)
    runs_count = runs.count()
    return render_template('runs_archive.html', title='Runs Archive', runs=runs, runs_count=runs_count)


@app.route('/sleep_archive')
@login_required
def sleep_archive():
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    sleeps = Sleep.query.filter_by(user_id=current_user.id)
    sleeps_count = sleeps.count()
    return render_template('sleep_archive.html', title='Sleep Archive', sleeps=sleeps, sleeps_count=sleeps_count)


@app.route('/day_display')
@login_required
def day_display():
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    runs = Run.query.all()
    sleeps = Sleep.query.all()
    return render_template('day_display.html', title='Day Display', run=runs, sleep=sleeps)


@app.route('/run_display/<run_id>')
@login_required
def run_display(run_id):
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    run = Run.query.filter_by(id=run_id).first_or_404()
    score = run_trend(run, current_user)
    pace = run.pace()
    suggestion = item_suggest(run)
    return render_template('run_display.html', title='Run Display', run=run, score=score,
                           pace=pace, suggestion=suggestion)


@app.route('/sleep_display/<sleep_id>')
@login_required
def sleep_display(sleep_id):
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    sleep = Sleep.query.filter_by(id=sleep_id).first_or_404()
    score = sleep_trend(sleep, current_user)
    duration = sleep.duration()
    suggestion = item_suggest(sleep)
    return render_template('sleep_display.html', title='Sleep Display', sleep=sleep, score=score,
                           duration=duration, suggestion=suggestion)


@app.route('/user_info')
@login_required
def user_info():
    user_runs = Run.query.filter_by(user_id=current_user.id).all()
    print(f"Current User ID: {current_user.id}")
    user_sleeps = Sleep.query.filter_by(user_id=current_user.id).all()
    print(f"User Sleeps: {user_sleeps}")
    username = current_user.username
    email = current_user.email
    name = current_user.name
    date_registered = current_user.date_registered
    bio = current_user.bio

    total_miles = sum_function(user_runs, "distance", current_user)
    total_time = sum_function(user_runs, "duration", current_user)
    overall_avg_pace = avg_function(user_runs, "pace", current_user)
    total_sleep_time = sum_function(user_sleeps, "sleep_duration", current_user)
    sum_run_score = sum_function(user_runs, "run_score", current_user)
    sum_sleep_score = sum_function(user_sleeps, "sleep_score", current_user)
    print(total_miles)
    print(total_time)
    print(overall_avg_pace)
    print(total_sleep_time)
    print(sum_run_score)
    print(sum_sleep_score)
    return render_template('user_info.html',user=current_user)
