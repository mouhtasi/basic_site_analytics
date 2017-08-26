#!/usr/local/bin/python3.6

# read nginx access log
# parse and get the ip addresses and times
# match ip addresses to geoip
# possibly ignore bots

import re


def get_log_lines(path):
    """Return a list of regex matched log lines from the passed nginx access log path"""
    lines = []
    with open(path) as f:
        r = re.compile("""(?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) \[(?P<time>[^\]]*)\] "(?P<method>\S+)(?: +(?P<path>[^\"]*) +\S*)?" (?P<code>[^ ]*) (?P<size>[^ ]*)(?: "(?P<referer>[^\"]*)" "(?P<agent>[^\"]*)")""")
        for line in f:
            m = r.match(line)
            if m is not None:
                md = m.groupdict()
                lines.append(md)
                
    return lines

def get_ip_address_city(ip_address):
    pass

def is_bot(useragent):
    pass

def summarize(data):
    pass

if __name__ == "__main__":
    access_file_path = "/var/log/nginx/imadm.ca.access.log"
    access_log = get_log_lines(access_file_path)

