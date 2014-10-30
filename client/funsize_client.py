"""
Client to ensure accuracy
~~~~~~~~~~~~~~~~~~

This module contains a client side to call for partials the funsize server

"""

import argparse
import requests
import time
import logging
import sys

try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class FunsizeClient(object):
    """ Class to hold funsize client methods """
    def __init__(self):
        logger.info("Funsize client successfully initiated.")

    def _write_to_file(self, ret, output_file):
        """ Private method used to write content from response to file """
        with open(output_file, 'a') as fobj:
            fobj.write(ret.content)

    def demand_partial(self, args):
        """ Method to contain th general logic of the module """
        server_url = args.server_url
        ret = self.trigger_partial_request(server_url, args)

        if ret.status_code == 500:
            raise SystemError('Encoutered error on funsize server side - 500')

        logger.info("Server returned. Investigating response ...")
        _uri = json.loads(ret.content).get('result', None)
        getter_resource_uri = server_url + _uri
        self.poll_for_partial(getter_resource_uri, args)

    def trigger_partial_request(self, server_url, iargs):
        """ Method used to request partial from funsize server side """
        trigger_resource_uri = server_url + '/partial'

        payload = {
            'mar_from': iargs.from_url,
            'mar_to': iargs.to_url,
            'sha_from': iargs.from_hash,
            'sha_to': iargs.to_hash,
            'channel_id': iargs.channel,
            'product_version': iargs.version,
        }

        logger.info("Triggering job at %s", trigger_resource_uri)
        return requests.post(trigger_resource_uri, data=payload)

    def poll_for_partial(self, resource_uri, args):
        """ Method to retrieve partial in max  lifecycles * cycle_sleep time """
        logger.info("Polling for the partial at %s", resource_uri)
        ret = requests.get(resource_uri)
        if ret.status_code == 400:
            raise ValueError("Bad identifier request!")

        logger.info("Start querying for the partial resource ...")
        output_file = args.output
        counter = args.timeout
        step = args.window_timeout
        while counter:
            ret = requests.get(resource_uri)
            if ret.status_code == 200:
                logger.info("Partial resource retrieved, writing to file ...")
                self._write_to_file(ret, output_file)
                break
            time.sleep(step)
            counter -= step

        if not counter:
            raise OSError.TimeoutError("Timeout, could not retrieve file.")


def main():
    """ Main method to call for command line arguments """
    client = FunsizeClient()
    parser = argparse.ArgumentParser(description='Generate funsize partials!')

    parser.add_argument('--timeout', default=600,
                        help='timeout (in seconds) to wait for results',
                        metavar='timeout')
    parser.add_argument('--window-timeout', default=5,
                        help='windows timeout sleep between calls',
                        metavar='window_timeout')
    parser.add_argument('--server-url', default='http://127.0.0.1:5000',
                        help='host where to send the files ',
                        metavar='server_url')
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
