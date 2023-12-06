from datetime import timedelta, datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField, \
    DateField, SelectMultipleField, DateTimeField, FloatField, TimeField, validators
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
    distance = FloatField('Distance (in miles)', validators=[DataRequired(), NumberRange(min=0.01)])
    hours = IntegerField('Hours', validators=[validators.NumberRange(min=0)])
    minutes = IntegerField('Minutes', validators=[validators.NumberRange(min=0)])
    seconds = IntegerField('Seconds', validators=[validators.NumberRange(min=0)])
    temperature = IntegerField('Temperature', validators=[NumberRange(min=-100, max=130)])
    time_of_day = TimeField('Time of Day', validators=[DataRequired()])
    effort = IntegerField('Effort (1-10)', validators=[NumberRange(min=1, max=10), DataRequired()])
    weather = SelectField('Weather', choices=[('sunny', 'Sunny'), ('cloudy', 'Cloudy'), ('rainy', 'Rainy')])
    notes = TextAreaField('Notes', validators=[Length(max=500)])

    def validate_date(self, field):
        if field.data > datetime.now().date():
            raise ValidationError('Date cannot be in the future.')

    def validate_distance(self, field):
        if field.data == 0:
            raise ValidationError('Distance cannot be 0')

    def validate_time_of_day(self, field):
        entered_date = self.date.data
        current_date = datetime.now().date()
        entered_time = field.data
        if entered_date == current_date and entered_time >= datetime.now().time():
            raise ValidationError('Time of day cannot be in the future.')

    def validate_hours(self, field):
        self._validate_duration(field)

    def validate_minutes(self, field):
        self._validate_duration(field)

    def validate_seconds(self, field):
        self._validate_duration(field)

    def _validate_duration(self, field):
        if self.hours.data == self.minutes.data == self.seconds.data == 0:
            raise ValidationError('At least one of hours, minutes, or seconds must be greater than 0.')


class SleepForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    bedtime = TimeField('Bedtime', validators=[DataRequired()])
    wake_up = TimeField('Wake Up Time', validators=[DataRequired()])
    times_awoken = IntegerField('Times Awoken', validators=[NumberRange(min=0)])
    dreams_torf = SelectField('Dreams', choices=[('t', 'Yes'), ('f', 'No')], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(max=300)])

    def validate_date(self, field):
        if field.data >= datetime.now().date():
            raise ValidationError('Date cannot be today or in the future.')

    def validate_bedtime(self, field):
        entered_date = self.date.data
        current_date = datetime.now().date()
        current_time = datetime.now().time()
        entered_time = field.data
        if entered_date == current_date and entered_time > current_time:
            raise ValidationError('Bedtime cannot be in the future.')

    def validate_wake_up(self, field):
        entered_date = self.date.data
        yesterday = datetime.now().date() - timedelta(days=1)
        current_time = datetime.now().time()
        entered_time = field.data
        if entered_date == yesterday and entered_time > current_time:
            raise ValidationError('Wake up time cannot be in the future.')
