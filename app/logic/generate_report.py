from app import app, db
from flask import request, jsonify
import threading
from bson import ObjectId  # Import ObjectId
from app.helpers.time_methods import get_time_and_day_of_week_in_local_time, time_difference_in_minutes, calculate_overlap_minutes, subtract_hours_from_utc, find_overlap, compare_utc_times


def generate_report(count):
    report_id = str(db.reports.insert_one({'status': 'Running'}).inserted_id)
    report_thread = threading.Thread(
        target=generate_report_thread, args=(report_id,count,))
    report_thread.start()
    return report_id


def generate_report_thread(report_id,count):
    disinct_store_ids = db['store_status'].distinct('store_id')
    if count != 0 :
        disinct_store_ids = disinct_store_ids[0:int(count)]
    # else:
    #     disinct_store_ids = disinct_store_ids[0:3]
    report = []
    for store_id in disinct_store_ids:
        store_report = generate_store_report(store_id)
        report.append(store_report)
    db.reports.update_one({"_id": ObjectId(report_id)}, {
                          "$set": {'status': 'Completed', 'report': report}})


def generate_store_report( store_id):
    time_now = '2023-01-25 18:13:22.47922 UTC'
    store_status = db.store_status.find({"store_id": store_id})

    report = {}

    timezone_str = 'America/Denver'
    timezone = db['store_zones'].find_one({'store_id': store_id})

    if not timezone is None:
        timezone_str = timezone['timezone_str']

    store_hour_data = list(db['store_hours'].find({'store_id': store_id}))
    start_time_local = '00:00:00'
    end_time_local = '23:59:59'
    time_now_local, day_now_local = get_time_and_day_of_week_in_local_time(
        time_now, timezone_str)
    store_status = sorted(
        store_status, key=lambda x: x["timestamp_utc"], reverse=True)
    isLastHour, isLastDay, isLastWeek = True, True, True
    lastHour = subtract_hours_from_utc(time_now, 1)
    lastDay = subtract_hours_from_utc(time_now, 24)
    lastWeek = subtract_hours_from_utc(time_now, 24*7)
    uptime_lasthour = 0
    downtime_lasthour = 0
    uptime_lastday = 0
    downtime_lastday = 0
    uptime_lastweek = 0
    downtime_lastweek = 0
    for index, status in enumerate(store_status):
        local_time, day = get_time_and_day_of_week_in_local_time(
            status['timestamp_utc'], timezone_str)
        status.pop('_id')
        status['timestamp_local'] = local_time
        restaurant_status = status['status']

        window_end = time_now_local
        if index != 0:
            window_end = store_status[index-1]['timestamp_local']
        window_start = local_time
        start_time_local, end_time_local = find_local_business_times(
            store_hour_data, day)
        a, b = find_overlap(window_start, window_end,
                            start_time_local, end_time_local)
        if isLastHour:
            toAdd = 0
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
