import logging
import hashlib
import redo
import requests

# Self file imports
import csum
import oddity


#@profile
def downloadmar(url, checksum, cipher='sha512', output_file=None):
    """ Downloads the file specified by url, verifies the checksum.
        The file is written to the location specified by output file,
        if not specified, the downloaded file is returned.
        List of Ciphers supported is the same as those supported by
        `csum.py`
    """

    logging.debug('Starting download for %s with checksum: %s' % (url, checksum))
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        logging.debug('HTTP Request to %s failed with error code %d' % (url, response.status_code))
        raise oddity.DownloadError('server error')
    mar = response.content

    # Verify hash
    if not csum.verify(mar, checksum, cipher='sha512'):
        logging.warning('verification of %s with checksum %s failed' % (url, checksum))
        raise oddity.DownloadError('checksums do not match')
    else:
        logging.info('Verified download of %s' % url)

    if output_file:
        # write mar to file
        try:
            logging.info('Writing download %s to file %s' % (url, output_file))
            with open(output_file, 'wb') as f:
                f.write(mar)
        except:
            raise
            logging.error('Error while downloading %s to file %s on disk' % (url, output_file))
            raise DownloadError('Failed to write file to disk')
        else:
            return None

    else:
        return mar

    # return path of file or return true or false depending on whether 
    # download failed or succeeded

#@profile
#def downloadmar2(url, checksum, output_file=None):
def downloadmar2(url, checksum, output_file):

    """ Downloads the file specified by url, verifies the checksum.
        The file is written to the location specified by output file,
        if not specified, the downloaded file is returned.

        Chunking version
    """

    logging.info('Starting download for %s with checksum: %s' % (url, checksum))

    response = requests.get(url, stream=True)

    if response.status_code != requests.codes.ok:
        logging.debug('HTTP Request to %s failed with error code %d' % (url, response.status_code))
        raise oddity.DownloadError('server error')
    else:
        try:
            logging.info('Writing download %s to file %s' % (url, output_file))
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(1024*1024):
                    f.write(chunk)
        except:
            logging.error('Error while downloading %s to file %s on disk' % (url, output_file))
            raise DownloadError('Failed to write file to disk')
        else:
            if not csum.verify(output_file, checksum, cipher='sha512', isfile=True):
                logging.debug("verification of checksums failed")
                raise oddity.DownloadError('checksums do not match')

        return # Only works with an output_file

if __name__ == '__main__':
    TEST_URL = "http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/2014-05-12-03-02-02-mozilla-central/firefox-32.0a1.en-US.mac.complete.mar"

    downloadmar(TEST_URL, 'da0ecd3c65f3f333ee42ca332b97e925', 'test.mar', cipher='md5')
    downloadmar(TEST_URL, '1a6bec1dd103f8aacbd450ec0787c94ccf07f5e100d7c356bf2'
                'fb75c8181998563e0ded4556c9fb050ee1e7451c1ac765bc1547c8c6ec6bc'
                'ffdf62ae0daf1150', 'test.mar', cipher='sha512')
