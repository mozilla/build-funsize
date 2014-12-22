"""
funsize.utils
~~~~~~~~~~~~~~~~~~

This module contains utils functions (e.g. hashing functions)

"""

import hashlib


def get_hash(hash_type, string):
    """ Computes the hash of the string.  """
    digest = hashlib.new(hash_type)
    digest.update(string)
    return str(digest.hexdigest())


def verify(str_, checksum, isfile=False):
    """ Given a string or a filepath and it's expected checksum, verifies if it
        is correct.
        The isfile flag determines whether the string is treated as a filepath.
    """
    return checksum == get_hash("sha512", str_)
