# Convert the timestamp to a readable format
import time


def timestamp_to_date(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
