def get_humanised_time_str(minutes):
    return "{}:{} hrs".format(int(minutes//60), int(minutes%60)) if minutes is not None else "00:00 hrs"
