#Calling this oddity because we don't want to override the built-in expcetions module
import exceptions
from exceptions import Exception

class DownloadError(Exception):
    """ Class for errors raised when downloading a resource fails """
    pass

class DBError(Exception):
    """ Class for all Database related Errors """
    pass
