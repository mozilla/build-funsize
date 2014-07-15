#!/usr/bin/env python

from collections import defaultdict as ddict
import pprint

mega_dict = {}

with open('url_hash.list', 'r') as f:
    while True:
        line = f.readline()
        if not line:
            break
        version, platform, locale, sha, url = tuple([x.strip() for x in line.split(',')])
        if not mega_dict.get(version):
            mega_dict[version] = {}
        if not mega_dict[version].get(platform):
            mega_dict[version][platform] = {}
        if not mega_dict[version][platform].get(locale):
            mega_dict[version][platform][locale] = {'hash': sha, 'url': url}

from_list = [
            #('25.0', 'mac', 'fi'),
            #('26.0', 'win32', 'fi'),
            #('28.0', 'linux-i686', 'fi'),
            #('29.0', 'linux-x86_64', 'hi-IN'),
            ('27.0', 'mac', 'en-GB'),
        ]
to_list = [
            ('29.0', 'mac', 'en-GB'),
        ]

for src in from_list:
    for dst in to_list:
        s = mega_dict[src[0]][src[1]][src[2]]
        d = mega_dict[dst[0]][dst[1]][dst[2]]
        #pprint.pprint([s['url'], d['url'], s['hash'], d['hash'], 'firefox-mozilla-release', dst[0]])
        print ','.join([s['url'], d['url'], s['hash'], d['hash'], 'firefox-mozilla-release', dst[0]])
