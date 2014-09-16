"""
funsize.utils
~~~~~~~~~~~~~~~~~~

This module contains utils functions (e.g. hashing functions)

"""

import hashlib
import base64


def hexto64(string):
    """ Encode a hex string to 64-bit string """

    decoded_string = base64.b16decode(string, casefold=True)
    result_string = base64.b64encode(decoded_string, '+@')

    return result_string


def getmd5(string, isfile=False):
    """ Computes the md5 hash of the string.
        If the isfile flag is true, treats string as filepath to a binary file
        and computes the md5 hash of the file.
    """

    md5_digest = hashlib.md5()
    if isfile:
        with open(string, 'rb') as fobj:
            while True:
                chunk = fobj.read(1024*1024)
                if not chunk:
                    break
                md5_digest.update(chunk)
    else:
        md5_digest.update(string)

    return str(md5_digest.hexdigest())


def getsha512(string, isfile=False):
    """ Computes the sha512 hash of the string.
        If the isfile flag is true, treats string as filepath to a binary file
        and computes the sha512 hash of the file.
    """

    sha512_digest = hashlib.sha512()
    if isfile:
        with open(string, 'rb') as fobj:
            while True:
                chunk = fobj.read(1024*1024)
                if not chunk:
                    break
                sha512_digest.update(chunk)
    else:
        sha512_digest.update(string)

    return str(sha512_digest.hexdigest())


def verify(string, checksum, cipher='md5', isfile=False):
    """ Given a string or a filepath and it's expected checksum, verifies if it
        is correct.
        The isfile flag determines whether the string is treated as a filepath.
        Choice of ciphers available: md5, sha256, sha512
    """

    if cipher == 'md5':
        csum = getmd5(string, isfile=isfile)
    elif cipher == 'sha512':
        csum = getsha512(string, isfile=isfile)

    return True if csum == checksum else False
