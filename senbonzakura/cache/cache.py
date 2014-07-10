# Stub, structure only
import senbonzakura.utils.oddity as oddity
import senbonzakura.utils.csum as csum

import os
import shutil
import logging

class Cache(object):
    """ Class that provides access to cache
        Assumes all keys are hex-encoded SHA512s
        Internally converts  hex to base64 encoding
    """


# FIXME: Typically caches are given Key-Value pairs, our cache generates the key
#        on it's own, this is not how it should be

    def __init__(self, cache_uri):
        """ cache_uri : URI of the cache for init. 
                        Just a filepath for the time being
        """

        logging.info('Creating cache interface for cache %s' % cache_uri)
        self.cache_dir = cache_uri
        self.cache_complete_dir = os.path.join(self.cache_dir, 'complete') # For complete Mars/files
        self.cache_diffs_dir = os.path.join(self.cache_dir, 'diff') # For diffs
        self.cache_partials_dir = os.path.join(self.cache_dir, 'partial') # for partials

        for directory in (self.cache_dir, self.cache_complete_dir,
                self.cache_diffs_dir, self.cache_partials_dir):
            try:
                os.makedirs(directory)
            except OSError:
                if not os.path.isdir(directory):
                    logging.warning('could not initalize cache')
                    logging.info('could not create required dir %s' % directory)
                    raise oddity.CacheError('Could not initalize Cache')

    def _generate_identifier(self, key):
        # Identifier to convert SHA512-SHA512 hex encoded key to SHA512-SHA512 base64 encoded key
        # Because file systems can only handle up to 255 chars 
        return '-'.join(csum.hexto64(x) if len(x)==128 else x for x in key.split('-'))


    def save(self, string, key, category, isfile=False):
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

        if not key:
            raise oddity.CacheError('Trying to save object to cache without key')

        if isfile:
            try:
                with open(string, 'rb') as f:
                     data = f.read()
            except:
                # Could not read file or is not a file or something
                logging.warning('Could not read file source %s ' %string +
                                'to insert into cache')
                raise oddity.CacheError('Error reading input %s' % string)
        else:
            data = string
        
        identifier = self._generate_identifier(key)
        id_path = os.path.join(*[d for d in identifier[:5]] + [identifier[5:]])

        if category == None:
            file_cache_path = os.path.join(self.cache_dir, id_path)
        elif category == 'complete':
            file_cache_path = os.path.join(self.cache_complete_dir, id_path)
        elif category == 'diff':
            file_cache_path = os.path.join(self.cache_diffs_dir, id_path)
        elif category == 'partial':
            file_cache_path = os.path.join(self.cache_partials_dir, id_path)

        logging.info('Writing to cache in dir %s' % file_cache_path)

        try:
            os.makedirs(os.path.dirname(file_cache_path))
        except OSError:
            if not os.path.isdir(os.path.dirname(file_cache_path)):
                logging.warning('could not create required dir %s' % directory)
                raise oddity.CacheError('Could not insert in Cache')


        if self.find(key, category):
            raise oddity.CacheCollisionError('identifier %s collision' % identifier)

        # We use the write to tempfile then rename to file to
        # prevent file corruption when multiple workers are writing to the cache.
        tmp_location = file_cache_path + str(os.getpid())
        try:
            # Write to tmp first
            with open(tmp_location, 'wb') as f:
                f.write(data)
        except:
            # couldn't open file or other error
            raise oddity.CacheError('Error saving input %s to cache, write failed' % string)
        else:
            try:
                os.link(tmp_location, file_cache_path)
                logging.info('Worker won race to save %s first, file created' % file_cache_path)
            except OSError:
                if os.path.isfile(file_cache_path):
                    logging.info('Worker lost race to save %s first, file already exists' % file_cache_path)
                else:
                    raise oddity.CacheError('Error saving input %s to cache, rename failed' % string)
            else:
                os.unlink(tmp_location)
            return identifier

    def find(self, key, category):
        """ Checks if file with specified key is in cache
            returns True or False depending on whether the file exists
        """
        identifier = self._generate_identifier(key)
        id_path = os.path.join(*[d for d in identifier[:5]] + [identifier[5:]])

        if category == None:
            file_cache_path = os.path.join(self.cache_dir, id_path)
        elif category == 'complete':
            file_cache_path = os.path.join(self.cache_complete_dir, id_path)
        elif category == 'diff':
            file_cache_path = os.path.join(self.cache_diffs_dir, id_path)
        elif category == 'partial':
            file_cache_path = os.path.join(self.cache_partials_dir, id_path)

        #identifier = self._generate_identifier(key)
        #file_cache_path = os.path.join(self.cache_dir, identifier)
        return os.path.isfile(file_cache_path)

    def retrieve(self, key, category, output_file=None):
        """ retrieve file with the given key
            writes the file to the path specified by output_file if present
            otherwise returns the file as a binary string/file object
        """
        # Multiples in case of collisions, might want to handle that

        identifier = self._generate_identifier(key)
        id_path = os.path.join(*[d for d in identifier[:5]] + [identifier[5:]])

        if category == None:
            file_cache_path = os.path.join(self.cache_dir, id_path)
        elif category == 'complete':
            file_cache_path = os.path.join(self.cache_complete_dir, id_path)
        elif category == 'diff':
            file_cache_path = os.path.join(self.cache_diffs_dir, id_path)
        elif category == 'partial':
            file_cache_path = os.path.join(self.cache_partials_dir, id_path)
        
        if output_file:
            try:
                shutil.copyfile(file_cache_path, output_file)
            except:
                logging.warning('could not retrieve file from cache')
                raise oddity.CacheMissError('File with identifier %s not found' 
                                       % identifier)
            else:
                return
        else:
            try:
                with open(file_cache_path, 'rb') as f:
                    data = f.read()
            except:
                logging.warning('could not retrieve file from cache')
                raise oddity.CacheMissError('File with identifier %s not found' 
                                       % identifier)
            else:
                return data
