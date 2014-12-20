#!/usr/bin/env python
""" Trigger a bunch of MAR jobs to simulate load on the backend.
    Usage: ./generate_load.py | bash
"""
from collections import defaultdict

d = defaultdict(dict)

with open('url_hash.list', 'r') as f:
    # TODO: Dinamically fetch from
    # http://ftp.mozilla.org/pub/mozilla.org/firefox/releases/33.0/SHA512SUMS
    for line in f:
        version, platform, locale, sha, url = [x.strip() for x in
                                               line.split(',')]
        entry = {"version": version, "platform": platform, "locale": locale,
                 "sha512": sha, "url": url}
        d[version][locale] = entry

from_list = [
    ('25.0', 'mac', 'en-US'),
    ('27.0', 'mac', 'en-US'),
]
to_list = ['29.0']

for from_version, platform, locale in from_list:
    for to_version in to_list:
        print " ".join([
            "../curl-test.sh", "trigger-release",
            d[from_version][locale]["url"],
            d[to_version][locale]["url"],
            d[from_version][locale]["sha512"],
            d[to_version][locale]["sha512"],
            'firefox-mozilla-release', to_version])
