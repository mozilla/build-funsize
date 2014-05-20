import hashlib
import redo
import requests

# Self file imports
import csum


def downloadmar(url, checksum, output_file=None):

    """ Downloads the file specified by url, verifies the checksum.
        The file is written to the location specified by output file,
        if not specified, the downloaded file is returned
    """

    print "Starting download for %s with checksum: %s" % (url, checksum)
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        print response.status_code # Should log
        # raise exception
    mar = response.content

    # Verify hash
    if not csum.verify(mar, checksum, algorithm='md5'):
        print "Verification failed"
        # raise exception
    else:
        print "Verified"

    if output_file:
        # write mar to file
        with open(output_file, 'wb') as f:
            f.write(mar)
        print type(mar)

        return None
    else:
        return mar

    # return path of file or return true or false depending on whether 
    # download failed or succeeded


if __name__ == '__main__':
    TEST_URL = "http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/2014-05-12-03-02-02-mozilla-central/firefox-32.0a1.en-US.mac.complete.mar"

    downloadmar(TEST_URL, 'da0ecd3c65f3f333ee42ca332b97e925', 'test.mar')
