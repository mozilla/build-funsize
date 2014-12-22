"""
funsize.database.cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is currently a stub file that contains function prototypes for the
caching layer core

"""

import os
from boto.s3.connection import S3Connection
from exceptions import Exception


class CacheError(Exception):
    """ Class for generic cache related errors """
    pass


class Cache(object):
    """ Class that provides access to cache
        Assumes all keys are hex-encoded SHA512s
        Internally converts  hex to base64 encoding
    """
    def __init__(self, bucket=os.environ.get('FUNSIZE_S3_UPLOAD_BUCKET')):
        """ _bucket : bucket name to use for S3 resources """
        if not bucket:
            raise CacheError("Amazon S3 bucket not set")
        # open a connection and get the bucket
        self.conn = S3Connection()
        self.bucket = self.conn.get_bucket(bucket)

    def get_cache_path(self, category, identifier):
        """ Method to return cache bucket key based on identifier """
        return "files/%s/%s" % (category, identifier)

    def new_key(self, category, identifier):
        """ Based on identifier and category create a new key in the bucket"""
        key = self.get_cache_path(category, identifier)
        return self.bucket.new_key(key)

    def get_key(self, category, identifier):
        """ Based on identifier and category retrieve key from bucket """
        key = self.get_cache_path(category, identifier)
        return self.bucket.get_key(key)

    def save(self, resource, category, identifier, isfilename=False):
        """ Saves given file to cache.
            resource can be either a local filepath or a file pointer (stream)
            Returns url of the S3 uploaded resource.
        """
        key = self.new_key(category, identifier)
        if isfilename:
            key.set_contents_from_filename(resource)
        else:
            key.set_contents_from_file(resource)

    def save_blank_file(self, category, identifier):
        """ Method to save a blank file to show a partial has been triggered and
            it is being in progress
        """
        key = self.new_key(category, identifier)
        key.set_contents_from_string('')

    def is_blank_file(self, category, identifier):
        """ Function to check if the file is empty or not. To be used to ensure
            no second triggering is done for the same partial
            Returns True is file exists and is blank, False otherwise
        """
        key = self.get_key(category, identifier)
        if not key:
            return False
        return key.size == 0

    def exists(self, category, identifier):
        """ Checks if file with specified key is in cache
            returns True or False depending on whether the file exists
        """
        return bool(self.get_key(category, identifier))

    def retrieve(self, category, identifier, output_file=None):
        """ Retrieve file with the given key
            writes the file to the path specified by output_file if present
            otherwise returns the file as a binary string/file object
        """
        key = self.get_key(category, identifier)
        if output_file:
            key.get_contents_to_filename(output_file)
        else:
            return key.get_contents_as_string()

    def delete(self, category, identifier):
        """ Method to remove a file from cache """
        self.get_key(category, identifier).delete()
