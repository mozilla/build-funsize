import re
import random
import hashlib
import requests
import tempfile
import time
import os
import argparse
from mar.mar import MarFile


partial_mar_re = re.compile(
    r"update/(?P<platform>[\w\d\-]+)/(?P<locale>\w+)/"
    "(?P<product>\w+)-(?P<from>[\d\.]+)-(?P<to>[\d\.]+)\.partial\.mar$")
complete_mar_re = re.compile(
    r"update/(?P<platform>[\w\d\-]+)/(?P<locale>\w+)/"
    "(?P<product>\w+)-(?P<version>[\d\.]+)\.complete\.mar$")

FTP_URL = "https://ftp.mozilla.org/pub/mozilla.org/firefox/releases/{v}"


def mar_internal_sha512(filename):
    m = MarFile(filename)
    digest = hashlib.new("sha512")
    for member in m.members:
        m.fileobj.seek(member._offset)
        digest.update(m.fileobj.read(member.size))
    return str(digest.hexdigest())


def build_update_tree(from_release):
    completes = {}
    partials = {}
    base_url = FTP_URL.format(v=from_release)
    sha512_url = "{}/SHA512SUMS".format(base_url)
    text = requests.get(sha512_url).text
    for line in text.splitlines():
        sha, filename = line.split(None, 1)
        fileurl = "{}/{}".format(base_url, filename)
        m_p = partial_mar_re.match(filename)
        if m_p:
            platform = m_p.group("platform")
            locale = m_p.group("locale")
            product = m_p.group("product")
            from_version = m_p.group("from")
            to_version = m_p.group("to")
            partials[(platform, locale, product, from_version,
                      to_version)] = (fileurl, sha)

        m_c = complete_mar_re.match(filename)
        if m_c:
            platform = m_c.group("platform")
            locale = m_c.group("locale")
            product = m_c.group("product")
            version = m_c.group("version")
            completes[(platform, locale, product, version)] = (fileurl, sha)
    return (completes, partials)


def trigger_partial(api_root, data):
    rv = requests.post("{}/partial".format(api_root), data=data)
    rv.raise_for_status()


def get_file(from_, to, attempt=0, max_attempts=100, interval=5):
    print "Downloading", from_, "to", to
    while True:
        r = requests.get(from_)
        r.raise_for_status()
        if r.status_code == 202:
            attempt += 1
            if attempt >= max_attempts:
                raise Exception("Timed out")
            time.sleep(interval)
        elif r.status_code == 200:
            with open(to, mode="wb") as f:
                f.write(r.content)
            break
        else:
            raise Exception("Unexpected status code: %s", r.status_code)


def build_sample(completes, partials, channel_id):
    sample = []
    for k, v in partials.iteritems():
        try:
            platform, locale, product, from_version, to_version = k
            fileurl, sha = v
            mar_from, sha_from = completes[(platform, locale, product,
                                            from_version)]
            mar_to, sha_to = completes[(platform, locale, product, to_version)]
            data = dict(mar_from=mar_from, mar_to=mar_to, sha_from=sha_from,
                        sha_to=sha_to, channel_id=channel_id,
                        product_version=to_version)
            identifier = "{}-{}".format(sha_from, sha_to)
            sample.append((data, fileurl, identifier))
        except KeyError:
            pass
    return sample


def compare_partials(args):
    data, mar_url, api_root, identifier = args
    trigger_partial(api_root, data)
    _, their_mar = tempfile.mkstemp()
    os.close(_)
    _, our_mar = tempfile.mkstemp()
    os.close(_)
    get_file(mar_url, their_mar)
    get_file("{api_root}partial/{identifier}".format(
        api_root=api_root, identifier=identifier), our_mar)
    assert mar_internal_sha512(their_mar) == mar_internal_sha512(our_mar)
    os.remove(their_mar)
    os.remove(our_mar)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", dest="versions", action="append",
                        help="Version for FROM and TO matrix."
                        " Supply multiple versions")
    parser.add_argument("-A", "--api-root",
                        default="http://localhost:5000/")
    parser.add_argument("-n", "--partial-count", type=int, default=1,
                        help="How many partials to generate")
    parser.add_argument("-c", "--channel-id",
                        default="firefox-mozilla-release",
                        help="MAR channel ID")
    parser.add_argument("-j", "--processes", type=int, default=1,
                        help="How many processes to use")
    args = parser.parse_args()
    versions = args.versions or ["33.1", "34.0"]
    if len(versions) < 2:
        parser.error("Must suplly multiple versions to tests")

    completes = {}
    partials = {}
    for v in versions:
        c, p = build_update_tree(v)
        completes.update(c)
        partials.update(p)

    sample = build_sample(completes, partials, args.channel_id)
    if not len(sample):
        print "No partial to test"
        exit(1)
    print "Testing %s out of %s" % (args.partial_count, len(sample))
    test_args = []
    for data, mar_url, identifier in random.sample(sample, args.partial_count):
        test_args.append([data, mar_url, args.api_root, identifier])
    if args.processes > 1:
        import multiprocessing
        pool = multiprocessing.Pool(processes=min([args.processes,
                                                   len(sample)]))
        pool.map(compare_partials, test_args)
    else:
        for test_arg in test_args:
            compare_partials(test_arg)
