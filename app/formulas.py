import datetime


def run_trend(run):
    # uses past 2 runs to grade the trend of the run being evaluated
    return 100


def sleep_trend(sleep):
    # uses past 2 sleeps to grade the trend of the sleep being evaluated
    return 100


def avg_func():
    # averages whatever datapoint you are trying to calculate (Distance, Score, Time(..?))
    pass


def avg_pace(duration, time):
    # uses duration and time to create an average pace for the run
    return "7:00 min/mi"


def item_suggest(item, type):
    if item.id > 3000:
        type = "sleep"
    else:
        type = "run"
    # uses a database or some sort of library to recommend sleep or run
    return "A Suggestion will be here!"


def sleep_duration(bedtime, wake_up):
    # calculates duration with start time vs end time
    return "8 hours!"

