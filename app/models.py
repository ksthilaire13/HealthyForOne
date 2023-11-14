from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

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
    date_registered = db.Column(db.String(32))

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def set_password(self, user_password):
        self.password_hash = generate_password_hash(user_password)

    def check_password(self, user_password):
        return check_password_hash(self.password_hash, user_password)


class Run(db.Model):
    run_id = db.Column(db.Integer, primary_key=True)
    distance = db.Column(db.Integer, index=True)
    duration = db.Column(db.String(64), index=True)
    effort = db.Column(db.Integer, index=True)
    temp = db.Column(db.Integer, index=True)
    time_of_day = db.Column(db.String(32), index=True)
    date = db.Column(db.String(32), index=True)
    weather = db.Column(db.String(32), index=True)
    notes = db.Column(db.String(200), index=True)
    user_id = db.Column(db.Integer, foreign_key=True)

    def __repr__(self):
        return '<Run: ({}) {}>'.format(self.run_id, self.date)


class Venue(db.Model):
    venue_id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String(64), index=True, unique=True)
    venue_address = db.Column(db.String(64), index=True)
    venue_city = db.Column(db.String(64), index=True)
    venue_state = db.Column(db.String(2), index=True)
    venue_description = db.Column(db.String(128), index=True)
    max_capacity = db.Column(db.Integer, index=True)
    events = db.relationship('Event', backref='venue', lazy='dynamic')

    def __repr__(self):
        return '<Venue: ({}) {}>'.format(self.venue_id,self.venue_name)