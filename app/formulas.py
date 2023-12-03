from datetime import datetime, timedelta
from sqlalchemy import desc
from app.models import Sleep, User, Run


def run_trend(run, user):
    # uses past 2 runs to grade the trend of the run being evaluated
    recent_runs = Run.query.filter(
        Run.user_id == user.id,
        Run.date < run.date).order_by(desc(Run.date)).limit(2).all()
    if len(recent_runs) >= 2:
        # calculate distance score
        avg_distance = (run.distance + recent_runs[0].distance + recent_runs[1].distance) / 3
        if avg_distance < run.distance + 5:
            distance_score = 100
        if avg_distance <= run.distance:
            distance_score = 80
        if avg_distance < run.distance + 2:
            distance_score = 70
        if avg_distance > run.distance:
            distance_score = 60
        if avg_distance > run.distance + 4:
            distance_score = 50

        # calculate pace score
        pace_avg = avg_pace(run) + avg_pace(recent_runs[0]) + avg_pace(recent_runs[1])
        if pace_avg > avg_pace(run):
            pace_score = 70
        if pace_avg <= avg_pace(run):
            pace_score = 100

        # calculate effort score
        avg_effort = (run.effort + recent_runs[0].effort + recent_runs[1].effort) / 3
        effort_score = run.effort * 5 + avg_effort * 5

        overall_score = distance_score * 0.4 + pace_score * 0.4 + effort_score * 0.2

        return overall_score
    else:
        return "Cannot be calculated yet"


def sleep_trend(sleep, user):
    # uses past 2 sleeps to grade the trend of the sleep being evaluated
    recent_sleeps = Sleep.query.filter(
        Sleep.user_id == user.id,
        Sleep.date < sleep.date).order_by(desc(Sleep.date)).limit(2).all()

    if len(recent_sleeps) >= 2:
        # calculate time score
        avg_sleep_time = (sleep_duration(sleep).total_seconds() / 3600 +
                          sleep_duration(recent_sleeps[0]).total_seconds() / 3600 +
                          sleep_duration(recent_sleeps[1]).total_seconds() / 3600) / 3
        if sleep_duration(sleep).total_seconds() / 3600 < 8:
            sleep1 = (sleep_duration(sleep).total_seconds() / 3600) * 5
        elif 8 <= sleep_duration(sleep).total_seconds() / 3600 <= 10:
            sleep1 = 50
        elif sleep_duration(sleep).total_seconds() / 3600 > 10:
            sleep1 = 50 - (sleep_duration(sleep).total_seconds() / 3600) * 5
        else:
            sleep1 = 50

        if avg_sleep_time < 8:
            sleep2 = avg_sleep_time * 5
        elif 8 <= avg_sleep_time <= 10:
            sleep2 = 50
        elif avg_sleep_time > 10:
            sleep2 = 50 - avg_sleep_time * 5
        else:
            sleep2 = 50

        time_score = sleep1 + sleep2

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

        overall_score = (time_score * 0.75 + dream_score * 0.1 + consis_score * 0.15)

        return overall_score
    else:
        return "Cannot be calculated yet"


def avg_pace(run):
    # uses duration and time to create an average pace for the run
    a_pace = run.duration / run.distance
    return a_pace


def item_suggest(item):
    # uses a database or some sort of library to recommend sleep or run
    if item.id > 3000:
        return "Give a Running Suggestion for the sleep!"
    else:
        return "Give a Sleep suggestion for the run!"


def sleep_duration(sleep):
    # calculates duration with start time vs end time
    if sleep.wake_up < sleep.bedtime:
        sleep.wake_up += timedelta(days=1)

    duration = sleep.wake_up - sleep.bedtime
    return duration


def avg_function(item_list, parameter):
    # pace, sleep_score, run_score
    total = sum_function(item_list, parameter)
    average = total/len(item_list)
    return average


def sum_function(item_list, parameter):
    function_map = {"pace": avg_pace, "sleep_score": sleep_trend, "run_score": run_trend,
                    "sleep_duration": sleep_duration}
    total = 0
    if parameter not in function_map:
        for item in item_list:
            total += item.parameter
    else:
        for item in item_list:
            total += function_map[parameter](item)
    return total


