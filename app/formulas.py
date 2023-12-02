from datetime import datetime
from sqlalchemy import desc
from app.models import Sleep, User, Run


def run_trend(run):
    # uses past 2 runs to grade the trend of the run being evaluated
    return 100


def sleep_trend(sleep, user):
    # uses past 2 sleeps to grade the trend of the sleep being evaluated
    recent_sleeps = Sleep.query.filter(
        Sleep.user_id == user.id,
        Sleep.date < sleep.date).order_by(desc(Sleep.date)).limit(2).all()

    if len(recent_sleeps) >= 2:
        # calculate time score
        avg_sleep_time = (sleep_duration(sleep) + sleep_duration(recent_sleeps[0]) + sleep_duration(recent_sleeps[1]))/3
        if 7 < sleep_duration(sleep) < 10 and 7 < avg_sleep_time < 10:
            time_score = 100
        elif sleep_duration(sleep) < 3:
            time_score = 20
        elif sleep_duration(sleep) < 1:
            time_score = 0
        elif 7 < sleep_duration(sleep) < 10 and (7 > avg_sleep_time or avg_sleep_time > 10):
            time_score = 80
        elif (7 > sleep_duration(sleep) or sleep_duration(sleep) > 10) and 7 < avg_sleep_time < 10:
            time_score = 60
        elif (7 > sleep_duration(sleep) or sleep_duration(sleep) > 10) and (7 > avg_sleep_time or avg_sleep_time > 10):
            time_score = 40

        # calculate consis_score
        if sleep.times_awoken == 0:
            consis_score = 100
        elif 0 < sleep.times_awoken < 2:
            consis_score = 75
        elif 2 < sleep.times_awoken < 5:
            consis_score = 50
        else:
            consis_score = 25

        # calculate dream score
        if sleep.dreams_torf == "t":
            dream_score = 100
        else:
            dream_score = 50

        overall_score = (time_score + time_score + time_score + dream_score + consis_score)/5

        return overall_score
    else:
        return "Cannot be calculated yet"


def avg_pace(run):
    # uses duration and time to create an average pace for the run
    a_pace = run.duration/run.distance
    return a_pace


def item_suggest(item):
    # uses a database or some sort of library to recommend sleep or run
    if item.id > 3000:
        return "Give a Running Suggestion for the sleep!"
    else:
        return "Give a Sleep suggestion for the run!"


def sleep_duration(sleep):
    # calculates duration with start time vs end time
    duration = sleep.wake_up - sleep.bedtime
    return duration

