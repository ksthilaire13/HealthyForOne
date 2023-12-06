from datetime import datetime, time, timedelta, date
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Time


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    bio = db.Column(db.String(400))
    photo = db.Column(db.String(32))
    date_registered = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    runs = db.relationship("Run", backref="user", lazy="dynamic")
    sleeps = db.relationship("Sleep", backref="user", lazy="dynamic")

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def set_password(self, user_password):
        self.password_hash = generate_password_hash(user_password)

    def check_password(self, user_password):
        return check_password_hash(self.password_hash, user_password)


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distance = db.Column(db.Integer, index=True)
    duration = db.Column(db.Interval, index=True)
    effort = db.Column(db.Integer, index=True)
    temp = db.Column(db.Integer, index=True)
    time_of_day = db.Column(db.Time, index=True, default=time.min)
    date = db.Column(db.Date, index=True, default=date.today)
    weather = db.Column(db.String(32), index=True)
    notes = db.Column(db.String(500), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Run: ({}) {}>'.format(self.id, self.date)

    def pace(self):
        if self.duration and self.distance:
            total_seconds = self.duration.total_seconds()
            pace_seconds = total_seconds / self.distance

            # Convert pace_seconds to timedelta
            pace_timedelta = timedelta(seconds=pace_seconds)

            return pace_timedelta

        return timedelta()


class Sleep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, default=date.today)
    bedtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    wake_up = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    times_awoken = db.Column(db.Integer)
    dreams_torf = db.Column(db.String(1), index=True)
    notes = db.Column(db.String(500), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Sleep: ({}) {}>'.format(self.id, self.date)

    def duration(self):
        if self.wake_up < self.bedtime:
            self.wake_up += timedelta(days=1)
        return self.wake_up - self.bedtime
