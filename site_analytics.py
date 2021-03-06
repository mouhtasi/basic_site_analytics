#!/usr/local/bin/python3.6

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
    known_bots = ['bingbot', 'Googlebot', 'Baiduspider', 'YandexBot', 'SemrushBot', 'Mail.RU_Bot', 'CSS Certificate Spider', 'Ruby']
    for bot in known_bots:
        if bot in useragent:
            return True
    return False


def sort_dict(d):
    """Return sorted list from high count to low count"""
    return sorted(d.items(), key=lambda t: t[1], reverse=True)


def process(data, geoip_file_path):
    log_count = 0
    ip_addresses = defaultdict(int)
    countries = defaultdict(int)
    cities = defaultdict(int)
    paths = defaultdict(int)
    agents = defaultdict(int)

    geoip_reader = geoip2.database.Reader(geoip_file_path)
    for line in data:
        agent = line['agent']
        code = line['code']
        if not is_bot(agent) and code != '301':  # ignore HTTP->HTTPS redirects
            log_count += 1
            ip_address = line['remote']
            path = line['path']
            agents[agent] +=1
            if path is not None:
                paths[path] += 1

            ip_addresses[ip_address] += 1

            city, country = get_ip_address_city_and_country(geoip_reader, ip_address)
            if city is not None:
                cities[city] +=1
            if country is not None:
                countries[country] += 1

    sorted_ip_addresses = sort_dict(ip_addresses)
    sorted_cities = sort_dict(cities)
    sorted_countries = sort_dict(countries)
    sorted_agents = sort_dict(agents)
    sorted_paths = sort_dict(paths)

    return log_count, sorted_ip_addresses, sorted_countries, sorted_cities, sorted_agents, sorted_paths


def print_summary(log_count, ip_addresses, countries, cities, agents, paths):
    print(str(log_count) + ' events logged after filtering.')
    print('Top countries are:')
    for country in countries[:5]:
        print('\t' + country[0] + '\t' + str(country[1]))

    print('Top cities are:')
    for city in cities[:5]:
        print('\t' + city[0] + '\t' + str(city[1]))

    print('Top IP addresses are:')
    for ip_address in ip_addresses[:5]:
        print('\t' + ip_address[0] + '\t' + str(ip_address[1]))

    print('Top paths are:')
    for path in paths[:5]:
        print('\t' + path[0] + '\t' + str(path[1]))

if __name__ == "__main__":
    access_file_path = '/var/log/nginx/imadm.ca.access.log'
    geoip_file_path = '/usr/local/share/GeoIP/GeoLite2-City.mmdb'
    time_period_days = 30

    access_log = get_log_lines(access_file_path, time_period_days)
    log_count, ip_addresses, countries, cities, agents, paths = process(access_log, geoip_file_path)
    print_summary(log_count, ip_addresses, countries, cities, agents, paths)

