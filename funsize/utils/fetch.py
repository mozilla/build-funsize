"""
funsize.fetch
~~~~~~~~~~~~~~~~~~

This module contains fetch functions

"""

import logging
import requests
from exceptions import Exception

from .csum import verify


class DownloadError(Exception):
    """ Class for errors raised when downloading a resource fails """
    pass


def downloadmar(url, checksum, output_file, cipher='sha512'):
    """ Downloads the file specified by url, verifies the checksum.
        The file is written to the location specified by output file,
        if not specified, the downloaded file is returned.
        List of Ciphers supported is the same as those supported by
        `csum.py`
    """
    logging.debug('Downloading %s with checksum: %s', url, checksum)

    response = requests.get(url, timeout=120)
    if response.status_code != requests.codes.ok:
        logging.debug('HTTP Request to %s failed with error code %d',
                      url, response.status_code)
        raise DownloadError('HTTP Request response error')
    mar = response.content

    if not verify(mar, checksum, cipher):
        logging.warning('Verification of %s with checksum %s failed',
                        url, checksum)
        raise DownloadError('Checksums do not match')
    else:
        logging.info('Verified download of %s', url)

    try:
        logging.info('Writing download %s to file %s', url, output_file)
        with open(output_file, 'wb') as fobj:
            fobj.write(mar)
    except:
        logging.error('Error while downloading %s to file %s on disk',
                      url, output_file)
        raise DownloadError('Failed to write file to disk')
