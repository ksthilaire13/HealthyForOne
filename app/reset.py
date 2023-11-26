import csv
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Run, Sleep

def reset_data():
    # with app.app_context():  ## Causes this to run on startup
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()

    ## Reload Users - needed for Foreign Keys
    with open('database_scripts\\users.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            print(row)  # used for confirmation
            user = User(
                id=row['user_id'],
                username=row['username'],
                email=row['email'],
                password_hash=generate_password_hash(row['password']),
                name=row['name'],
                bio=row['bio'],
                photo=row['photo'],
                date_registered=row['date_registered'])
            db.session.add(user)
            db.session.commit()

    ## Reload Sleep
    with open('database_scripts\\sleep.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            print(row)  # used for confirmation
            sleep = Sleep(
                id=row['sleep_id'],
                date=row['date'],
                bedtime=row['bedtime'],
                wake_up=row['wake_up'],
                times_awoken=row['times_awoken'],
                dreams_torf=row['dreams_torf'],
                notes=row['sleep_notes'],
                user_id=row['user_id'])
            db.session.add(sleep)
            db.session.commit()

    ## Reload Runs
    with open('database_scripts\\runs.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            print(row)  # used for confirmation
            run = Run(
                id=row['run_id'],
                distance=row['distance'],
                duration=row['duration'],
                effort=row['effort'],
                temp=row['temp'],
                time_of_day=row['time_of_day'],
                date=row['date'],
                weather=row['weather'],
                notes=row['run_notes'],
                user_id=row['user_id'])
            db.session.add(run)
            db.session.commit()