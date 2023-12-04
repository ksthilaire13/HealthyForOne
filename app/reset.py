import csv
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Run, Sleep
from datetime import datetime, time, timedelta


def reset_data():
    # with app.app_context():  ## Causes this to run on startup
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()

    print("Made it to users")
    # Reload Users - needed for Foreign Keys
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
                date_registered=datetime.strptime(row['date_registered'], "%m/%d/%Y %H:%M:%S"))
            db.session.add(user)
            db.session.commit()

    print("Made it to Sleep")
    # Reload Sleep
    with open('database_scripts\\sleep.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            print(row)  # used for confirmation
            print(row['bedtime'])
            sleep = Sleep(
                id=row['sleep_id'],
                date=datetime.strptime(row['date'], "%m/%d/%Y"),
                bedtime=datetime.strptime(row['bedtime'], "%I:%M %p"),
                wake_up=datetime.strptime(row['wake_up'], "%I:%M %p"),
                times_awoken=row['times_awoken'],
                dreams_torf=row['dreams_torf'],
                notes=row['sleep_notes'],
                user_id=row['user_id'])
            db.session.add(sleep)
            db.session.commit()

    print("Made it to runs")
    # Reload Runs
    with open('database_scripts\\runs.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            print(row)  # used for confirmation
            duration_parts = row['duration'].split(':')
            duration = timedelta(hours=int(duration_parts[0]), minutes=int(duration_parts[1]),
                                 seconds=int(duration_parts[2]))

            run = Run(
                id=row['run_id'],
                distance=row['distance'],
                duration=duration,
                effort=row['effort'],
                temp=row['temp'],
                time_of_day=datetime.strptime(row['time_of_day'], "%I:%M %p").time(),
                date=datetime.strptime(row['date'], "%m/%d/%Y"),
                weather=row['weather'],
                notes=row['run_notes'],
                user_id=row['user_id'])
            db.session.add(run)
            db.session.commit()
