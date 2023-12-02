from datetime import timedelta

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField, \
    DateField, SelectMultipleField, DateTimeField, FloatField, TimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, Length
from app.models import User, Run, Sleep


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class RunForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    distance = FloatField('Distance (in miles)', validators=[DataRequired(), NumberRange(min=0)])
    hours = IntegerField('Hours', validators=[DataRequired(), NumberRange(min=0)])
    minutes = IntegerField('Minutes', validators=[DataRequired(), NumberRange(min=0, max=59)])
    seconds = IntegerField('Seconds', validators=[DataRequired(), NumberRange(min=0, max=59)])
    temperature = IntegerField('Temperature', validators=[NumberRange(min=-100, max=130)])
    time_of_day = TimeField('Time of Day', validators=[DataRequired()])
    effort = IntegerField('Effort (1-10)', validators=[NumberRange(min=1, max=10), DataRequired()])
    weather = SelectField('Weather', choices=[('sunny', 'Sunny'), ('cloudy', 'Cloudy'), ('rainy', 'Rainy')])
    notes = TextAreaField('Notes', validators=[Length(max=200)])


class SleepForm(FlaskForm):
    bedtime = DateTimeField('Bedtime', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    wake_up = DateTimeField('Wake Up Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    times_awoken = IntegerField('Times Awoken', validators=[NumberRange(min=0)])
    dreams_torf = SelectField('Dreams', choices=[('t', 'Yes'), ('f', 'No')], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(max=300)])