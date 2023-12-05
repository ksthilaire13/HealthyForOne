from datetime import timedelta, datetime
from sqlalchemy import func
from app import app, db
from flask import render_template, redirect, url_for, flash, request, jsonify, render_template_string
from app.forms import LoginForm, RegistrationForm, SleepForm, RunForm
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Run, Sleep
from app.reset import reset_data
from app.formulas import run_trend, sleep_trend, item_suggest, sum_function, avg_function
import requests
import json
import os


@app.route('/')
def startup():
    if current_user.is_authenticated:
        return redirect(url_for('day_display'))
    else:
        return redirect(url_for('main'))


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('day_display'))
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
            next_page = url_for('day_display')
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
    logout_user()
    flash("Resetting database: deleting old data and repopulating with dummy data")
    # clear all data from all tables - in a separate file...
    reset_data()
    return redirect('/')


@app.route('/register_run', methods=['GET', 'POST'])
@login_required
def register_run():
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
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
        return redirect(url_for('day_display'))
    return render_template('registers/register_run.html', title='Submit Run', form=form)


@app.route('/register_sleep', methods=['GET', 'POST'])
@login_required
def register_sleep():
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
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
        return redirect(url_for('day_display'))
    return render_template('registers/register_sleep.html', title='Submit Sleep', form=form)


@app.route('/compare', methods=['GET', 'POST'])
@login_required
def compare():
    if not current_user.is_authenticated:
        return redirect(url_for('main'))

    user = current_user
    user_runs = Run.query.filter_by(user_id=current_user.id).all()
    other_users = User.query.filter(User.username != user.username).all()
    selected_user = None
    selected_date = 'overall'
    selected_user_runs = None
    common_dates = []
    user_dates = []
    selected_user_dates = []

    for run in user_runs:
        if run.date not in user_dates:
            user_dates.append(run.date)

    if request.method == 'POST':
        if 'submit_user' in request.form:
            # Handle user comparison
            print("made it here 3")
            selected_user_id = request.form.get('selected_user')
            selected_user = User.query.get(selected_user_id)
            selected_user_runs = Run.query.filter_by(user_id=selected_user.id).all()
            common_dates = []
            selected_user_dates = []
            for run in selected_user_runs:
                if run.date not in selected_user_dates:
                    selected_user_dates.append(run.date)
            for date in user_dates:
                if date in selected_user_dates:
                    common_dates.append(date)

        if 'submit_date' in request.form:
            selected_date = request.form.get('selected_date')
            print("Selected Date:", selected_date)

    return render_template('compare.html', user=user, other_users=other_users, selected_user=selected_user,
                           common_dates=common_dates, selected_date=selected_date, user_runs=user_runs,
                           selected_user_runs=selected_user_runs, user_dates=user_dates, len=len,
                           selected_user_dates=selected_user_dates, avg_function=avg_function, sum_function=sum_function)


@app.route('/update_content', methods=['POST'])
def update_content():
    selected_date = request.form.get('selected_date')
    compare_dates = "dates compare"
    compare_overall = "compare overall"
    # with open('/app/templates/base.html', 'r') as file:
    #     html_content = file.read()
    #     print(html_content)

    if selected_date == 'overall':
        print("overall stats tempy")
        return jsonify({"content": compare_overall})
    else:
        print("specic stat sempy")
        return jsonify({"content": compare_dates})


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
    today_date = datetime.today().date()
    yesterday_date = datetime.today().date() - timedelta(days=1)
    user_runs = Run.query.filter_by(user_id=current_user.id, date=today_date).all()
    user_sleeps = Sleep.query.filter_by(user_id=current_user.id, date=yesterday_date).all()
    num_sleeps = len(user_sleeps)
    num_runs = len(user_runs)
    if num_runs > 0:
        time = sum_function(user_runs, "duration", current_user)
        distance = sum_function(user_runs, "distance", current_user)
        avg_pace = avg_function(user_runs, "pace", current_user)
        effort = avg_function(user_runs, "effort", current_user)
        temp = avg_function(user_runs, "temp", current_user)
        time_of_day = sum_function(user_runs, "time_of_day", current_user)
        notes = sum_function(user_runs, "notes", current_user)
        score = avg_function(user_runs, "run_scores", current_user)
    else:
        time = None
        distance = None
        avg_pace = None
        effort = None
        temp = None
        time_of_day = None
        notes = None
        score = None

    user_sleep = user_sleeps[0] if num_sleeps > 0 else None

    api_url = "https://zenquotes.io/api/random"
    response = requests.get(api_url)

    if response.status_code == 200:
        quote_data = response.json()[0]
        quote = quote_data['q']
        author = quote_data['a']
        todaysQuote = f'"{quote}" - {author}'
    else:
        return "Failed to fetch a quote"

    return render_template('day_display.html', title='Day Display', user_sleep=user_sleep, time=time,
                           distance=distance, avg_pace=avg_pace, effort=effort, temp=temp, time_of_day=time_of_day,
                           notes=notes, score=score, num_sleeps=num_sleeps, num_runs=num_runs, user=current_user,
                           datetime=datetime, sleep_trend=sleep_trend, quote=todaysQuote)


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
    if not current_user.is_authenticated:
        return redirect(url_for('main'))
    user_runs = Run.query.filter_by(user_id=current_user.id).all()
    user_sleeps = Sleep.query.filter_by(user_id=current_user.id).all()
    total_miles = sum_function(user_runs, "distance", current_user)
    total_time = sum_function(user_runs, "duration", current_user)
    overall_avg_pace = avg_function(user_runs, "pace", current_user)
    total_sleep_time = sum_function(user_sleeps, "sleep_duration", current_user)
    avg_run_score = avg_function(user_runs, "run_score", current_user)
    avg_sleep_score = avg_function(user_sleeps, "sleep_score", current_user)
    return render_template('user_info.html', user=current_user, total_miles=total_miles,
                           total_time=total_time, overall_avg_pace=overall_avg_pace, total_sleep_time=total_sleep_time,
                           avg_run_score=avg_run_score, avg_sleep_score=avg_sleep_score)