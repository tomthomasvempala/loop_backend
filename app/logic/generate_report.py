from app import app, db
from flask import request, jsonify
import threading
from bson import ObjectId  # Import ObjectId
from app.helpers.time_methods import get_time_and_day_of_week_in_local_time, time_difference_in_minutes, calculate_overlap_minutes, subtract_hours_from_utc, find_overlap, compare_utc_times


def generate_report(count):
    report_id = str(db.reports.insert_one({'status': 'Running'}).inserted_id)
    # we start a thread so that report generation occurs in the background and report id is returned for time being
    report_thread = threading.Thread(
        target=generate_report_thread, args=(report_id, count,))
    report_thread.start()
    return report_id


def generate_report_thread(report_id, count):
    # fetching distinct store ids from the entire list of status reports to perform report generation for each store
    disinct_store_ids = db['store_status'].distinct('store_id')

    # depending on the value of this variable, number of stores considered will be chosen
    # purely for testing
    if count != 0:
        disinct_store_ids = disinct_store_ids[0:int(count)]
    # else:
    #     disinct_store_ids = disinct_store_ids[0:3]
    report = []
    for store_id in disinct_store_ids:
        store_report = generate_store_report(store_id)
        report.append(store_report)
    db.reports.update_one({"_id": ObjectId(report_id)}, {
                          "$set": {'status': 'Completed', 'report': report}})


def generate_store_report(store_id):
    time_now = '2023-01-25 18:13:22.47922 UTC'
    # hard coded current time as max of timestamps

    # fetched all the status reports of single store
    store_status = db.store_status.find({"store_id": store_id})

    report = {}

    # default timezone
    timezone_str = 'America/Denver'
    timezone = db['store_zones'].find_one({'store_id': store_id})

    if not timezone is None:
        timezone_str = timezone['timezone_str']

    store_hour_data = list(db['store_hours'].find({'store_id': store_id}))

    # default business hours
    start_time_local = '00:00:00'
    end_time_local = '23:59:59'

    # converting triggering time in utc to local time for comparison
    time_now_local, day_now_local = get_time_and_day_of_week_in_local_time(
        time_now, timezone_str)

    # this part is important. we sort the list of status reports in reverse with respect to timestamp
    # this is because we make the following assumption
    # suppose report at 7pm says active and 8 pm says inactive and 10 pm says active, (assuming there are no other resports in between)
    # we assume store was active from 7 to 8 and inactive from 8 to 10
    # so if we sort the list, to find this conclusion, we only need to compare consecutive elements
    store_status = sorted(
        store_status, key=lambda x: x["timestamp_utc"], reverse=True)

    # as we iterate through status reports, we go backward in time.
    # and so, we might not need to consider reports beyond sometime
    # these boolean variables will be used to check that.
    isLastHour, isLastDay, isLastWeek = True, True, True

    # the following variables denote the endpoints until when we need to consider
    lastHour = subtract_hours_from_utc(time_now, 1)
    lastDay = subtract_hours_from_utc(time_now, 24)
    lastWeek = subtract_hours_from_utc(time_now, 24*7)
    uptime_lasthour = 0
    downtime_lasthour = 0
    uptime_lastday = 0
    downtime_lastday = 0
    uptime_lastweek = 0
    downtime_lastweek = 0

    # now we iterate through each status report.. starting with the latest report
    for index, status in enumerate(store_status):
        local_time, day = get_time_and_day_of_week_in_local_time(
            status['timestamp_utc'], timezone_str)
        status['timestamp_local'] = local_time
        restaurant_status = status['status']

    # window_end is the two endpoints in time in which a report is valid..
    # for example we have a report at 7 pm and another at 8 pm
    # window_end will be 8 pm
    # window start will be 7 pm
    # in case of the latest report, window_end will be report_trigger time
        window_end = time_now_local
        if index != 0:
            window_end = store_status[index-1]['timestamp_local']
        window_start = local_time
        start_time_local, end_time_local = find_local_business_times(
            store_hour_data, day)

    # we only need to find observation during business hours..
    # so we find the overlapping time period between business hours and the report window
        a, b = find_overlap(window_start, window_end,
                            start_time_local, end_time_local)

    # the following part will be executed if report is within one hour latest
        if isLastHour:
            toAdd = 0
    # we only need uptime and downtime in the past hour
    # so we find the overlap there with report validity window as well
    # then add it to uptime or downtime
    # if report is older than 1 hour mark, then further reports need not be considered here. so we flag it
            if compare_utc_times(lastHour, status['timestamp_utc']) > 0:
                isLastHour = False
                lastHour_local, d = get_time_and_day_of_week_in_local_time(
                    lastHour, timezone_str)
                toAdd = calculate_overlap_minutes(
                    a, b, lastHour_local, time_now_local)
            else:
                toAdd = time_difference_in_minutes(a, b)
            if restaurant_status == 'active':
                uptime_lasthour = uptime_lasthour + toAdd
            else:
                downtime_lasthour = downtime_lasthour + toAdd


# similarly we do it for last one week mark
        if isLastWeek:
            toAdd = 0
            if compare_utc_times(lastWeek, status['timestamp_utc']) > 0:
                isLastWeek = False
                lastHour_local, d = get_time_and_day_of_week_in_local_time(
                    lastWeek, timezone_str)
                toAdd = calculate_overlap_minutes(
                    a, b, lastHour_local, time_now_local)
            else:
                toAdd = time_difference_in_minutes(a, b)
            if restaurant_status == 'active':
                uptime_lastweek = uptime_lastweek + toAdd
            else:
                downtime_lastweek = downtime_lastweek + toAdd

# similarly we do it for last one day mark
        if isLastDay:
            toAdd = 0
            if compare_utc_times(lastDay, status['timestamp_utc']) > 0:
                isLastDay = False
                lastHour_local, d = get_time_and_day_of_week_in_local_time(
                    lastDay, timezone_str)
                toAdd = calculate_overlap_minutes(
                    a, b, lastHour_local, time_now_local)
            else:
                toAdd = time_difference_in_minutes(a, b)
            if restaurant_status == 'active':
                uptime_lastday = uptime_lastday + toAdd
            else:
                downtime_lastday = downtime_lastday + toAdd

# we fill the report dictionary with values and return
    report['store_id'] = store_id
    report['uptime_lasthour'] = round(uptime_lasthour)
    report['downtime_lasthour'] = round(downtime_lasthour)
    report['uptime_lastday'] = round(uptime_lastday/60)
    report['downtime_lastday'] = round(downtime_lastday/60)
    report['uptime_lastweek'] = round(uptime_lastweek/60)
    report['downtime_lastweek'] = round(downtime_lastweek/60)

    return report


def find_local_business_times(array_of_dicts, attribute_value):
    for item in array_of_dicts:
        if item['day'] == attribute_value:
            return item['start_time_local'], item['end_time_local']
    return "00:00:00", "23:59:59"
