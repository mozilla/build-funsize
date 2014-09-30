"""
Client to ensure accuracy
~~~~~~~~~~~~~~~~~~

This module contains a client side to call for partials the funsize server

"""

import argparse
import requests
import time
try:
    import simplejson as json
except ImportError:
    import json


FUNSIZE_SERVER_SIDE = 'http://127.0.0.1:5000'


class FunsizeClient(object):
    """ Class to hold funsize client methods
    """

    lifecycles = 10 # number of lifecycles to keep polling for results
    cycle_sleep = 30 # number of seconds to sleep in a cycle

    def __init__(self):
        pass

    def _write_to_file(self, ret, output_file):
        """ Private method used to write content from response to file
        """
        with open(output_file, 'a') as fobj:
            fobj.write(ret.content)

    def demand_partial(self, args):
        """ Method to contain th general logic of the module
        """

        trigger_resource_uri = FUNSIZE_SERVER_SIDE + '/partial'
        ret = self.trigger_partial_request(trigger_resource_uri, args)

        if ret.status_code == 500:
            raise Exception('Encoutered error on funsize server side - 500')

        _uri = json.loads(ret.content).get('result', None)
        getter_resource_uri = FUNSIZE_SERVER_SIDE + _uri
        self.poll_for_partial(getter_resource_uri, args.output)

    def trigger_partial_request(self, resource_uri, iargs):
        """ Method used to request partial from funsize server side
        """

        payload = {
            'mar_from': iargs.from_url,
            'mar_to': iargs.to_url,
            'mar_from_hash': iargs.from_hash,
            'mar_to_hash': iargs.to_hash,
            'channel_id': iargs.channel,
            'product_version': iargs.version,
        }

        return requests.post(resource_uri, data=payload)

    def poll_for_partial(self, resource_uri, output_file):
        """ Method to retrieve the partial in max  lifecycles * cycle_sleep time
        """

        ret = requests.get(resource_uri)
        if ret.status_code == 400:
            raise Exception("Bad identifier request!")

        counter = self.lifecycles
        while counter:
            ret = requests.get(resource_uri)
            if ret.status_code == 200:
                self._write_to_file(ret, output_file)
                break
            counter -= 1
            time.sleep(self.cycle_sleep)

        if not counter:
            raise Exception("Timeout, could not retrieve file from funsize.")


def main():
    """ Main method to call for command line arguments
    """

    client = FunsizeClient()
    parser = argparse.ArgumentParser(description='Generate funsize partials!')

    parser.add_argument('--from-url',
                        required=True,
                        help='the complete mar url for `from` version',
                        metavar='from_url')
    parser.add_argument('--to-url',
                        required=True,
                        help='the complete mar url for `to` version',
                        metavar='to_url')
    parser.add_argument('--from-hash',
                        required=True,
                        help='the hash for `from` version mar',
                        metavar='from_hash')
    parser.add_argument('--to-hash',
                        required=True,
                        help='the hash for `to` version mar',
                        metavar='from_hash')
    parser.add_argument('--channel',
                        required=True,
                        help='the channel for the requested partial mar',
                        metavar='channel')
    parser.add_argument('--version',
                        required=True,
                        help='the version of the latter mar',
                        metavar='version')
    parser.add_argument('--output',
                        required=True,
                        help='the file where to write the resulted partial mar',
                        metavar='output')

    args = parser.parse_args()
    client.demand_partial(args)


if __name__=="__main__":
    main()
