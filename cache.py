# Stub, structure only
import csum
import os
import shutil
import logging

class Cache(object):
    """ Class that provides access to cache """

# FIXME: Typically caches are given Key-Value pairs, our cache generates the key
#        on it's own, this is not how it should be

    def __init__(self, cache_uri):
        """ cache_uri : URI of the cache for init. 
                        Just a filepath for the time being
        """

        try:
            os.makedirs(cache_uri)
        except OSError:
            if not os.path.isdir(cache_uri):
                logging.warning('could not initalize cache')
                raise

        self.cache_dir = cache_uri

    def save(self, string, isfile=False):
        # FIXME: How do we deal with the race condition where the file is still
        # being written to cache, but since it exists is returned as is (most
        # likely corrupted).

        # Possible solution - Write file as id.tmp and then rename to id when
        # done

        # FIXME: What should the behaviour be when we try to save to a
        # pre-existing key?
        """ Saves given file to cache, treats string as a local filepath if isfile is true.
            returns hash of file
            #returns URI/Identifier for cache
        """

        if isfile:
            try:
                with open(string, 'rb') as f:
                     data = f.read()
            except:
                # Could not read file or is not a file or something
                raise
        else:
            data = string

        identifier = csum.getmd5(data)
        file_cache_path = os.path.join(self.cache_dir, identifier)

        try:
            with open(file_cache_path, 'wb') as f:
                f.write(data)
        except:
            # couldn't open file or other error
            raise
        else:
            return identifier

    def find(self, identifier):
        """ Checks if file with specified hash is in cache 
            returns True or False depending on whether the file exists
        """

        file_cache_path = os.path.join(self.cache_dir, identifier)
        return os.path.isfile(file_cache_path)

    def retrieve(self, identifier, output_file=None):
        """ retrieve file with the given identifier
            writes the file to the path specified by output_file if present
            otherwise returns the file as a binary string/file object
        """
        # Multiples in case of collisions, might want to handle that
        
        file_path = os.path.join(self.cache_dir, identifier)
        if output_file:
            try:
                shutil.copyfile(file_path, output_file)
            except:
                logging.warning('could not retrieve file from cache')
                raise
            else:
                return
        else:
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
            except:
                logging.warning('could not retrieve file from cache')
                raise
            else:
                return data
