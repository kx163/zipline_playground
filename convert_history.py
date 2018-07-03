import csv
from datetime import datetime, timedelta


# The file path pattern for each year's raw data
# The time in these files should be the server time from Oanda, which should be GMT+0
history_file_pattern = './history/Record_Pure_Data_GBPUSD_P1_%d.csv'

# The file path for the minute data and the daily data
minute_bundle_file = './custom_history/minute/GBPUSD.csv'
daily_bundle_file = './custom_history/daily/GBPUSD.csv'

# The datetime format strings
datetime_format = '%Y.%m.%d %H:%M:%S'
datetime_dash_format = '%Y-%m-%d %H:%M:%S'

# The one minute time delta to be used in the algorithm
one_minute = timedelta(minutes=1)


# read the datetime from string and apply the calendar offset to comply with the CustomForexCalendar
def recognise_and_offset_datetime(dt_str):
    _dt = datetime.strptime(dt_str, datetime_format)
    return _dt - timedelta(hours=2)


# generate the datetime object for the next trading minute under CustomForexCalendar
# return a tuple of (next_minute, weekend_skipped)
def generate_next_minute(curr: datetime):
    # skipped_weekend = False
    # nt = curr + one_minute
    # # skip the weekend if necessary
    # if nt.isoweekday() > 5:
    #     skipped_weekend = True
    #     nt += ((((7 - nt.isoweekday()) * 24) + 23 - nt.hour) * 60 + 59 - nt.minute + 1) * one_minute
    #     assert nt.hour == 0 and nt.minute == 0
    # assert nt.isoweekday() < 6
    # return nt, skipped_weekend
    nt = curr + one_minute
    # skip the weekend if necessary
    if nt.isoweekday() > 5:
        nt += ((((7 - nt.isoweekday()) * 24) + 23 - nt.hour) * 60 + 59 - nt.minute + 1) * one_minute
        assert nt.hour == 0 and nt.minute == 0
    assert nt.isoweekday() < 6
    return nt


# generate the datetime object representing the start of the current day
def generate_current_day(curr: datetime):
    return datetime(curr.year, curr.month, curr.day)


# create a new minute record
def create_new_minute_record(record, dt, zero_vol):
    OHLC = [float(t) for t in record[3:]]
    vol = 0.0 if zero_vol else float(record[2])
    return [dt.strftime(datetime_dash_format), *OHLC, vol]


# check if a datetime is Christmas
def is_xmas(dt):
    return dt.month == 12 and dt.day == 25


# global variables for the function 'accumulate_and_write_daily_record'
day_open, day_high, day_low, day_vol = 0.0, 0.0, 0.0, 0.0


# accumulate the data through a trading day and write the daily record at the end of day
def accumulate_and_write_daily_record(writer, record, dt, zero_vol):
    global day_open, day_high, day_low, day_vol
    OHLC = [float(t) for t in record[3:]]
    vol = 0.0 if zero_vol else float(record[2])
    if dt.hour == 0 and dt.minute == 0:
        day_open, day_high, day_low = OHLC[0:3]
        day_vol = vol
    else:
        day_vol += vol
        day_high = max(day_high, OHLC[1])
        day_low = min(day_low, OHLC[2])
        if dt.hour == 23 and dt.minute == 59 and not is_xmas(dt):
            daily_new_record = [generate_current_day(dt).strftime(datetime_dash_format),
                                day_open, day_high, day_low, OHLC[3], float(day_vol)]
            writer.writerow(daily_new_record)


# convert one year's raw data and write the results into file
def convert_one_year(year, minute_writer, daily_writer, history_reader):
    curr_dt = generate_next_minute(datetime(year, 1, 2) - one_minute)
    curr_record = next(history_reader, None)
    prev_record = curr_record
    curr_record_dt = recognise_and_offset_datetime(curr_record[1])
    assert curr_dt.month == 1 and curr_dt.day > 1 and curr_dt.hour == 0 and curr_dt.minute == 0
    next_record = False
    while curr_record is not None and curr_dt.year == year:
        while next_record or curr_record_dt.isoweekday() > 5 or is_xmas(curr_record_dt) or curr_record_dt < curr_dt:
            prev_record = curr_record
            curr_record = next(history_reader, None)
            if curr_record is None:
                break
            curr_record_dt = recognise_and_offset_datetime(curr_record[1])
            next_record = False
        if curr_record_dt == curr_dt:
            minute_writer.writerow(create_new_minute_record(curr_record, curr_dt, False))
            accumulate_and_write_daily_record(daily_writer, curr_record, curr_dt, False)
            curr_dt = generate_next_minute(curr_dt)
            next_record = True
        elif curr_record_dt > curr_dt:
            minute_writer.writerow(create_new_minute_record(prev_record, curr_dt, True))
            accumulate_and_write_daily_record(daily_writer, prev_record, curr_dt, True)
            curr_dt = generate_next_minute(curr_dt)
            next_record = False
    while not (curr_dt.hour == 0 and curr_dt.minute == 0):
        minute_writer.writerow(create_new_minute_record(prev_record, curr_dt, True))
        accumulate_and_write_daily_record(daily_writer, prev_record, curr_dt, True)
        curr_dt = generate_next_minute(curr_dt)


if __name__ == '__main__':
    with open(minute_bundle_file, 'w') as minute_bundle, open(daily_bundle_file, 'w') as daily_bundle:
        title_row = ['date', 'open', 'high', 'low', 'close', 'volume']
        minute_writer = csv.writer(minute_bundle)
        minute_writer.writerow(title_row)
        daily_writer = csv.writer(daily_bundle)
        daily_writer.writerow(title_row)
        for year in range(2007, 2018):
            with open(history_file_pattern % year, 'r') as history:
                print(history_file_pattern % year)
                history_reader = csv.reader(history)
                next(history_reader, None)
                convert_one_year(year, minute_writer, daily_writer, history_reader)
