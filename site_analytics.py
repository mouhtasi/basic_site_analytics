#!/usr/local/bin/python3.6

# read nginx access log
# parse and get the ip addresses and times
# match ip addresses to geoip
# possibly ignore bots

import re
from datetime import datetime, timedelta


def get_log_lines(path, time_period_days):
    """Return a list of regex matched log lines from the passed nginx access log path"""
    lines = []
    with open(path) as f:
        r = re.compile("""(?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) \[(?P<time>[^\]]*)\] "(?P<method>\S+)(?: +(?P<path>[^\"]*) +\S*)?" (?P<code>[^ ]*) (?P<size>[^ ]*)(?: "(?P<referer>[^\"]*)" "(?P<agent>[^\"]*)")""")
        for line in f:
            m = r.match(line)
            if m is not None:
                md = m.groupdict()
                if not is_within_time_period(md['time'], time_period_days):
                    break
                lines.append(md)
    print(len(lines)) 
    return lines


def is_within_time_period(log_time, time_period_days):
    line_time = datetime.strptime(log_time, "%d/%b/%Y:%H:%M:%S %z")
    return datetime.now(tz=line_time.tzinfo) - line_time <= timedelta(days=time_period_days)


def get_ip_address_city(ip_address):
    pass


def is_bot(useragent):
    pass


def summarize(data):
    pass


if __name__ == "__main__":
    access_file_path = "/var/log/nginx/imadm.ca.access.log"
    time_period_days = 30

    access_log = get_log_lines(access_file_path, time_period_days)

