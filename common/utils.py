from datetime import timedelta


def get_humanised_time_str(minutes):
    return "{} hrs".format(str(timedelta(minutes=minutes))[:-3]) if minutes is not None else "0:00 hrs"
