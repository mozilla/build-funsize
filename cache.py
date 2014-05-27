# Stub, structure only


def save(string, isfile=False):
    """ Saves given file to cache, treats string as a local filepath if isfile is true.
        returns hash of file
        #returns URI of file on cache?
    """
    return False

def find(filehash):
    """ Checks if file with specified hash is in cache 
        returns True or False depending on whether the file exists
    """

    return False

def retrieve(filehash, output_file=None):
    """ retrieve file with the given hash
        writes the file to the path specified by output_file if present
        otherwise returns the file as a binary string/file object
    """
    # Multiples in case of collisions, might want to handle that
    pass
