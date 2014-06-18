import fetch
import csum
import stat
import os
import shutil
import platform
import logging
import subprocess


class ToolManager(object):
    """ Class to manage the tools required by the service """

    def __init__(self, folder, verification_file, channel='nightly'):
        """ Folder specifies the tools in a given folder
            Verification file is a CSV of <MD5,FILE NAME> pairs
        """
        logging.info('Setting up Tool Manager')
        self.folder = os.path.abspath(folder)
        with open(os.path.abspath(verification_file), 'r') as f:
            self.verification_list = dict(l.split(',')[::-1] for l in f.read().split('\n') if l)
        os.path.isdir(self.folder)
        self.channel = channel

    def check_integrity(self):
        # There is probably a better/more consistent way to do this as well
        logging.info('Checking integrity')
        if not os.path.isdir(self.folder):
            logging.info('Integrity check failed for dir  %s', self.folder)
            return False
        for f, checksum in self.verification_list.items():
            filepath = os.path.join(self.folder, f)
            if not (os.path.isfile(filepath) and csum.getmd5(filepath, isfile=True) == checksum):
                    logging.info('Integrity check failed for file %s', filepath)
                    return False
            else:
                logging.debug('Verfied file %s with checksum %s' % (filepath, checksum))
        logging.info('Integrity check passed')
        return True

    def setup_tools(self):
        # Bomb everything and redownload (there probably is a better way)
        if os.path.isdir(self.folder):
            shutil.rmtree(self.folder)
        os.makedirs(self.folder)
        self.download_tools()

    def download_tools(self):
        # This definitely needs to be changed/fixed.
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
        subprocess.call([os.path.abspath('download-tools.sh'), '-o', self.folder])
        mar = os.path.join(self.folder, 'mar')
        mbsdiff = os.path.join(self.folder, 'mbsdiff')
        subprocess.call(['wget', '-O', mar, mar_tools_url+'mar'])
        subprocess.call(['wget', '-O', mbsdiff, mar_tools_url+'mbsdiff'])
        os.chmod(mar, os.stat(mar).st_mode | stat.S_IEXEC)
        os.chmod(mbsdiff, os.stat(mbsdiff).st_mode | stat.S_IEXEC)

    def get_path(self):
        if not self.check_integrity():
            self.setup_tools()
        return self.folder

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    tm = ToolManager('/perma/tooltest', 'configs/verification_file.csv')
    print tm.get_path()
