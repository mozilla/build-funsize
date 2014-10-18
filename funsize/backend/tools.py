"""
funsize.backend.tools
~~~~~~~~~~~~~~~~~~

This module contains all funsize related tool things

"""

import stat
import os
import shutil
import platform
import logging
import subprocess

import funsize.utils.oddity as oddity

__here__ = os.path.dirname(os.path.abspath(__file__))


class ToolManager(object):
    """ Class to manage the tools required by the service """

    def __init__(self, folder, channel='nightly'):
        """ Folder specifies the tools in a given folder """
        logging.info('Setting up Tool Manager in folder %s on channel %s',
                     folder, channel)
        self.folder = os.path.abspath(folder)
        self.channel = channel
        self.mar = os.path.join(self.folder, 'mar')
        self.mbsdiff = os.path.join(self.folder, 'mbsdiff')
        self.unwrap = os.path.join(self.folder, 'unwrap_full_update.pl')
        self.make_incremental = os.path.join(self.folder,
                                             'make_incremental_update.sh')

    def setup_tools(self):
        """ Bomb everything and redownload (there probably is a better way) """
        if os.path.isdir(self.folder):
            shutil.rmtree(self.folder)
        os.makedirs(self.folder)
        self.download_tools()

    def download_tools(self):
        """ Method to call the downloading of the mar and mbsdiff files """
        OS = platform.system()
        if OS == 'Linux':
            platform_version = 'linux64'
        elif OS == 'Darwin':
            platform_version = 'macosx64'
        elif OS in ['Windows', 'Microsoft']:
            platform_version = 'win32'
        else:
            raise oddity.ToolError('Could not determine platform')
        mar_tools_url = "http://ftp.mozilla.org/pub/mozilla.org/firefox/%s/latest-mozilla-central/mar-tools/%s/" % (self.channel, platform_version)
        logging.info('Downloading tools from %s', mar_tools_url)
        subprocess.call([os.path.abspath(os.path.join(__here__, 'download-copy-tools.sh')), '-o', self.folder])
        subprocess.call(['wget', '-O', self.mar, mar_tools_url+'mar'])
        subprocess.call(['wget', '-O', self.mbsdiff, mar_tools_url+'mbsdiff'])

        os.chmod(self.mar, os.stat(self.mar).st_mode | stat.S_IEXEC)
        os.chmod(self.mbsdiff, os.stat(self.mbsdiff).st_mode | stat.S_IEXEC)
        os.chmod(self.unwrap, os.stat(self.unwrap).st_mode | stat.S_IEXEC)
        os.chmod(self.make_incremental, os.stat(self.make_incremental).st_mode | stat.S_IEXEC)

    def get_path(self):
        """ Caller method for the redownloading """
        self.setup_tools()
        return self.folder
