import pytz
from datetime import datetime, timedelta

def convert_local_time_to_utc(timezone_str, local_time_str):
    try:
        # Create a datetime object with the given local time
        local_time = datetime.strptime(local_time_str, '%H:%M:%S')

        # Get the timezone object for the given timezone
        timezone = pytz.timezone(timezone_str)

        # Localize the datetime object with the given timezone
        localized_time = timezone.localize(local_time)

        # Convert the localized time to UTC
        utc_time = localized_time.astimezone(pytz.utc)

        return utc_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    except ValueError as e:
        return str(e)