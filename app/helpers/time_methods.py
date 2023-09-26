from datetime import datetime,timedelta
import pytz

def get_time_and_day_of_week_in_local_time(utc_timestamp_string, timezone_str):
    try:
        # Convert the string to a datetime object in UTC
        utc_datetime = datetime.strptime(utc_timestamp_string, '%Y-%m-%d %H:%M:%S.%f UTC')

        # Specify the time zone
        timezone = pytz.timezone(timezone_str)

        # Convert the UTC time to the local time zone
        local_datetime = utc_datetime.replace(tzinfo=pytz.UTC).astimezone(timezone)

        # Get the time in the format hh:mm:ss
        formatted_time = local_datetime.strftime('%H:%M:%S')

        # Get the day of the week as an integer (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
        day_of_week = local_datetime.weekday()

        return formatted_time, day_of_week
    except (ValueError, pytz.UnknownTimeZoneError):
        return None, None
    

def time_difference_in_minutes(time_str1, time_str2):
    time_format = "%H:%M:%S"

    try:
        time1 = datetime.strptime(time_str1, time_format)
        time2 = datetime.strptime(time_str2, time_format)
    except :
        return 0

    time_difference = (time2 - time1).total_seconds() / 60
    return abs(time_difference)

def days_difference_between_times_UTC(time_str1, time_str2):
    try:
        # Convert the input time strings to datetime objects
        time1 = datetime.strptime(time_str1, '%Y-%m-%d %H:%M:%S.%f UTC')
        time2 = datetime.strptime(time_str2, '%Y-%m-%d %H:%M:%S.%f UTC')

        # Calculate the absolute time difference
        time_difference = abs(time1 - time2)

        # Extract the number of days as a floating-point value
        days_difference = time_difference.days + time_difference.seconds / (60 * 60 * 24)

        return days_difference
    except ValueError:
        return None
    
def hours_difference_between_times_UTC(time_str1, time_str2):
    try:
        # Convert the input time strings to datetime objects
        time1 = datetime.strptime(time_str1, '%Y-%m-%d %H:%M:%S.%f UTC')
        time2 = datetime.strptime(time_str2, '%Y-%m-%d %H:%M:%S.%f UTC')

        # Calculate the absolute time difference
        time_difference = abs(time1 - time2)

        # Extract the number of days as a floating-point value
        days_difference = time_difference.days + time_difference.seconds / (60 * 60 )

        return days_difference
    except ValueError:
        return None
    
def is_time_in_between(start_time_str, end_time_str, check_time_str):
    try:
        # Parse the input time strings into datetime objects with a dummy date
        dummy_date = datetime(2023, 1, 1)
        start_time = datetime.strptime(start_time_str, '%H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%H:%M:%S')
        check_time = datetime.strptime(check_time_str, '%H:%M:%S')

        # Extract the time component from the datetime objects
        start_time = start_time.time()
        end_time = end_time.time()
        check_time = check_time.time()

        # Compare if the check_time is between start_time and end_time
        if ( start_time <= check_time  and check_time <= end_time )  or (start_time > end_time and ( start_time <= check_time  or check_time <= end_time )):
            return True
        else:
            return False
    except ValueError:
        print('error')
        return False
    
def calculate_overlap_minutes(time_frame1_start, time_frame1_end, time_frame2_start, time_frame2_end):
    # Parse the time frames into datetime objects
    try :
        start1 = datetime.strptime(time_frame1_start, "%H:%M:%S")
        end1 = datetime.strptime(time_frame1_end, "%H:%M:%S")
        start2 = datetime.strptime(time_frame2_start, "%H:%M:%S")
        end2 = datetime.strptime(time_frame2_end, "%H:%M:%S")

        # Calculate the overlap duration
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)

        if overlap_start < overlap_end:
            overlap_duration = (overlap_end - overlap_start).total_seconds() / 60  # Convert to minutes
            return overlap_duration
        else:
            return 0
    except :
        return 0

def find_overlap(time_frame1_start, time_frame1_end, time_frame2_start, time_frame2_end):
    try:
    # Parse the time frames into datetime objects
        start1 = datetime.strptime(time_frame1_start, "%H:%M:%S")
        end1 = datetime.strptime(time_frame1_end, "%H:%M:%S")
        start2 = datetime.strptime(time_frame2_start, "%H:%M:%S")
        end2 = datetime.strptime(time_frame2_end, "%H:%M:%S")

        # Find the maximum of the start times and the minimum of the end times
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)

        # Check if there is an overlap
        if overlap_start <= overlap_end:
            return overlap_start.strftime("%H:%M:%S"), overlap_end.strftime("%H:%M:%S")
        else:
            return None,None
    except:
        return None,None
    
def subtract_hours_from_utc(utc_time_str, hours_to_subtract):
    try:
        # Convert the UTC time string to a datetime object
        utc_time = datetime.strptime(utc_time_str, '%Y-%m-%d %H:%M:%S.%f UTC')

        # Subtract the specified number of hours
        result_time = utc_time - timedelta(hours=hours_to_subtract)

        # Convert the result back to a string in the original format
        result_time_str = result_time.strftime('%Y-%m-%d %H:%M:%S.%f UTC')

        return result_time_str
    except ValueError:
        return None  # Return None if there's an error in parsing the input string


def compare_utc_times(time_str1, time_str2):
    try:
        # Convert the time strings to datetime objects
        time1 = datetime.strptime(time_str1, '%Y-%m-%d %H:%M:%S.%f UTC')
        time2 = datetime.strptime(time_str2, '%Y-%m-%d %H:%M:%S.%f UTC')

        if time1 == time2:
            return 0
        elif time1 < time2:
            return -1
        else:
            return 1
    except ValueError:
        return None





# Example usage:
# start_time_str = '23:00:00'
# end_time_str = '08:00:00'
# check_time_str = '2023-01-22 8:09:39.388884 UTC'
# is_between = is_time_in_between(start_time_str, end_time_str, check_time_str)
# print(is_between)