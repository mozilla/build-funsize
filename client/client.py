"""
Client to ensure accuracy
~~~~~~~~~~~~~~~~~~

This module contains a client side to call for partials the funsize server

"""

import argparse
import requests


class IncrementalAction(argparse.Action):
    """ Action class to ensure incremental version partial requesting
    """

    def __call__(self, parser, namespace, values, option_string=None):
        if values < namespace.from_version:
            parser.error("Must have an incremental version request!")

        setattr(namespace, self.dest, values)


class FunsizeClient(object):
    """ Class to hold funsize client methods
    """

    catalogue = {}

    def __init__(self, input_file):
        self._process(input_file)

    @property
    def platform_choices(self):
        return self.catalogue.get('25.0').keys()

    @property
    def locale_choices(self):
        return sorted(self.catalogue.get('25.0')['mac'].keys())

    @property
    def version_choices(self):
        return self.catalogue.keys()

    def _process(self, input_file):
        """ Internal method used to populate catalogue with data from file
        """

        with open(input_file, 'r') as fobj:
            while True:
                line = fobj.readline()
                if not line:
                    break
                version, platform, locale, sha, url = tuple([x.strip() for x in line.split(',')])
                if not self.catalogue.get(version):
                    self.catalogue[version] = {}
                if not self.catalogue[version].get(platform):
                    self.catalogue[version][platform] = {}
                if not self.catalogue[version][platform].get(locale):
                    self.catalogue[version][platform][locale] = {
                        'hash': sha, 'url': url
                    }

    def request_partial(self, iargs):
        """ Method used to request partial from funsize server side
            e.g. Namespace(from_version='25.0', locale='en-US',
                           platform='mac', to_version='26.0', funsize_url=...)
        """
        source = self.catalogue[iargs.from_version][iargs.platform][iargs.locale]
        dest = self.catalogue[iargs.to_version][iargs.platform][iargs.locale]
        url = iargs.funsize_url + '/partial'

        payload = {
            'mar_from': source['url'],
            'mar_to': dest['url'],
            'mar_from_hash': source['hash'],
            'mar_to_hash': dest['hash'],
            'channel_id': 'firefox-mozilla-release',
            'product_version': iargs.to_version,
        }

        ret = requests.post(url, data=payload)
        print (ret.text)


def main():
    client = FunsizeClient('url_hash.list')

    parser = argparse.ArgumentParser(description='Generate partials with funsize!')
    parser.add_argument('platform', choices=client.platform_choices,
                        help='platform for the triggered partial', metavar='platform')
    parser.add_argument('locale', choices=client.locale_choices,
                        help='locale for the triggered partial', metavar='locale')
    parser.add_argument('from_version', choices=client.version_choices,
                        help='source version to call a partial from',
                        metavar='from_version')
    parser.add_argument('to_version', action=IncrementalAction,
                        choices=client.catalogue.keys(),
                        help='destination version to call a partial to',
                        metavar='to_version')
    parser.add_argument('funsize_url',
                        help='funsize server side url',
                        metavar='funsize_url')
    args = parser.parse_args()

    client.request_partial(args)


if __name__=="__main__":
    main()
