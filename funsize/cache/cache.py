"""
funsize.database.cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is currently a stub file that contains function prototypes for the
caching layer core

"""

import os
from boto.s3.connection import S3Connection

import funsize.utils.oddity as oddity


class Cache(object):
    """ Class that provides access to cache
        Assumes all keys are hex-encoded SHA512s
        Internally converts  hex to base64 encoding
    """
    def __init__(self, _bucket=os.environ.get('FUNSIZE_S3_UPLOAD_BUCKET')):
        """ _bucket : bucket name to use for S3 resources """
        if not _bucket:
            raise oddity.CacheError("Amazon S3 bucket not set")
        # open a connection and get the bucket
        self.conn = S3Connection()
        self.bucket = self.conn.get_bucket(_bucket)

    def _get_cache_internals(self, identifier, category):
        """ Method to return cache bucket key based on identifier """
        if not identifier:
            raise oddity.CacheError('Save object failed without identifier')
        if category not in ('partial', 'patch', 'complete'):
            raise oddity.CacheError("Category failed for S3 uploading")
        bucket_key = "files/%s/%s" % (category, identifier)
        return bucket_key

    def _create_new_bucket_key(self, identifier, category):
        """ Based on identifier and category create a new key in the bucket"""
        _key = self._get_cache_internals(identifier, category)
        return self.bucket.new_key(_key)

    def _get_bucket_key(self, identifier, category):
        """ Based on identifier and category retrieve key from bucket """
        _key = self._get_cache_internals(identifier, category)
        return self.bucket.get_key(_key)

    def save(self, resource, identifier, category, isfilename=False):
        """ Saves given file to cache.
            resource can be either a local filepath or a file pointer (stream)
            Returns url of the S3 uploaded resource.
        """
        key = self._create_new_bucket_key(identifier, category)
        if isfilename:
            key.set_contents_from_filename(resource)
        else:
            key.set_contents_from_file(resource)

    def save_blank_file(self, identifier, category):
        """ Method to save a blank file to show a partial has been triggered and
            it is being in progress
        """
        key = self._create_new_bucket_key(identifier, category)
        key.set_contents_from_string('')

    def is_blank_file(self, identifier, category):
        """ Function to check if the file is empty or not. To be used to ensure
            no second triggering is done for the same partial
            Returns True is file exists and is blank, False otherwise
        """
        key = self._get_bucket_key(identifier, category)
        if not key:
            return False
        return key.size == 0

    def find(self, identifier, category):
        """ Checks if file with specified key is in cache
            returns True or False depending on whether the file exists
        """
        key = self._get_bucket_key(identifier, category)
        return bool(key)

    def retrieve(self, identifier, category, output_file=None):
        """ Retrieve file with the given key
            writes the file to the path specified by output_file if present
            otherwise returns the file as a binary string/file object
        """
        key = self._get_bucket_key(identifier, category)
        if output_file:
            key.get_contents_to_filename(output_file)
        else:
            return key.get_contents_as_string()

    def delete_from_cache(self, identifier, category):
        """ Method to remove a file from cache """
        key = self._get_bucket_key(identifier, category)
        key.delete()
