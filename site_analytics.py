#!/usr/local/bin/python3.6

# read nginx access log
# parse and get the ip addresses and times
# match ip addresses to geoip
# possibly ignore bots

import re
from datetime import datetime, timedelta
from collections import defaultdict
import geoip2.database


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
    return lines


def is_within_time_period(log_time, time_period_days):
    """Return whether or not the line from the log is within the user specified time period"""
    line_time = datetime.strptime(log_time, "%d/%b/%Y:%H:%M:%S %z")
    return datetime.now(tz=line_time.tzinfo) - line_time <= timedelta(days=time_period_days)


def get_ip_address_city_and_country(geoip_reader, ip_address):
    geo = geoip_reader.city(ip_address)
    city = geo.city.name
    country = geo.country.name
    return city, country


def is_bot(useragent):
    pass


def sort_dict(d):
    """Return sorted list from high count to low count"""
    return sorted(d.items(), key=lambda t: t[1], reverse=True)


def process(data):
    log_count = len(data)
    countries = defaultdict(int)
    cities = defaultdict(int)
    paths = defaultdict(int)
    agents = defaultdict(int)

    geoip_reader = geoip2.database.Reader('/usr/local/share/GeoIP/GeoLite2-City.mmdb')
    for line in data:
        ip_address = line['remote']
        agent = line['agent']
        path = line['path']
        agents[agent] +=1
        paths[path] += 1

        city, country = get_ip_address_city_and_country(geoip_reader, ip_address)
        cities[city] +=1
        countries[country] += 1

    sorted_cities = sort_dict(cities)
    sorted_countries = sort_dict(countries)
    sorted_agents = sort_dict(agents)
    sorted_paths = sort_dict(paths)

    return log_count, sorted_countries, sorted_cities, sorted_agents, sorted_paths

if __name__ == "__main__":
    access_file_path = "/var/log/nginx/imadm.ca.access.log"
    time_period_days = 30

    access_log = get_log_lines(access_file_path, time_period_days)
    log_count, countries, cties, agents, paths = process(access_log)

