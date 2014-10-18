"""
funsize.backend.core
~~~~~~~~~~~~~~~~~~

This module contains the brain of the entire funsize project

"""

import ConfigParser
import errno
import logging
import os
import subprocess
import tempfile

import funsize.utils.fetch as fetch
import funsize.cache.cache as cache
import funsize.backend.tools as tools
import funsize.utils.oddity as oddity

__here__ = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(__here__, '../configs/worker.ini')

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE_PATH)

if config.items('tools'):
    TOOLS_DIR = config.get('tools', 'dir')
else:
    raise oddity.ConfigError('Configuration parameters missing')


def get_complete_mar(url, identifier, output_file=None):
    """ Return binary string if no output_file specified """
    cacheo = cache.Cache()
    logging.info('Request for complete MAR %s with Identifer %s in cache',
                 url, identifier)

    if cacheo.find(identifier, 'complete'):
        logging.debug('Found complete MAR %s with Identifer %s in cache',
                      url, identifier)
        logging.info('Retriving MAR from cache')
        mar = cacheo.retrieve(identifier, 'complete', output_file=output_file)
    else:
        logging.info('Downloading complete MAR %s with Identifer %s',
                     url, identifier)
        mar = fetch.downloadmar(url, identifier, output_file=output_file)
        cacheo.save(output_file or mar, identifier, 'complete',
                    isfile=bool(output_file))

    logging.info('Request for complete MAR %s with Identifer %s satisfied',
                 url, identifier)
    return mar


def build_partial_mar(new_cmar_url, new_cmar_hash, old_cmar_url, old_cmar_hash,
                      identifier, channel_id, product_version):
    """ Function that returns the partial MAR file to transition from the mar
        given by old_cmar_url to new_cmar_url
    """
    logging.info('Creating cache connections')
    cacheo = cache.Cache()

    logging.info('Creating temporary working directories')
    TMP_MAR_STORAGE = tempfile.mkdtemp(prefix='cmar_storage_')
    logging.debug('MAR storage: %s', TMP_MAR_STORAGE)
    TMP_WORKING_DIR = tempfile.mkdtemp(prefix='working_dir_')
    logging.debug('Working dir storage: %s', TMP_WORKING_DIR)

    new_cmar_path = os.path.join(TMP_MAR_STORAGE, 'new.mar')
    old_cmar_path = os.path.join(TMP_MAR_STORAGE, 'old.mar')

    logging.info('Looking up the complete MARs required')
    get_complete_mar(new_cmar_url, new_cmar_hash, output_file=new_cmar_path)
    get_complete_mar(old_cmar_url, old_cmar_hash, output_file=old_cmar_path)

    tmo = tools.ToolManager(TOOLS_DIR)
    TMP_TOOL_STORAGE = tmo.get_path()
    logging.info('Tool storage: %s', TMP_TOOL_STORAGE)

    try:
        local_pmar_location = generate_partial_mar(new_cmar_path, old_cmar_path,
                                                   TMP_TOOL_STORAGE,
                                                   channel_id,
                                                   product_version,
                                                   working_dir=TMP_WORKING_DIR)
        logging.debug('Partial MAR generated at %s', local_pmar_location)
    except oddity.ToolError:
        cacheo.delete_from_cache(identifier, 'partial')
        raise

    logging.info('Saving PMAR %s to cache with key %s',
                 local_pmar_location, identifier)
    cacheo.save(local_pmar_location,
                identifier, 'partial', isfile=True)

    #FIXME Cleanup temp directories here ?


def generate_partial_mar(cmar_new, cmar_old, difftools_path, channel_id,
                         product_version, working_dir=None):
    """ cmar_new is the path of the newer complete .mar file
        cmar_old is the path of the older complete .mar file
        difftools_path specifies the path of the directory in which
        the difftools, including mar,mbsdiff exist
    """
    if not working_dir:
        working_dir = '.'

    UNWRAP = os.path.join(difftools_path, 'unwrap_full_update.pl')
    MAKE_INCREMENTAL = os.path.join(difftools_path, 'make_incremental_update.sh')
    MAR = os.path.join(difftools_path, 'mar')
    MBSDIFF = os.path.join(difftools_path, 'mbsdiff')

    my_env = os.environ.copy()
    my_env['MAR'] = MAR
    my_env['MBSDIFF'] = MBSDIFF
    my_env['MOZ_CHANNEL_ID'] = channel_id
    my_env['MOZ_PRODUCT_VERSION'] = product_version
    my_env['LC_ALL'] = 'C'
    my_env['FUNSIZE_URL'] = 'http://127.0.0.1:5000/cache'
    my_env['MBSDIFF_HOOK'] = '/vagrant/src/client/update-packaging/funsize_common.sh'
    my_env['FUNSIZE_LOCAL_CACHE_DIR'] = '/tmp/local_cache'

    try:
        os.mkdir(working_dir)
    except Exception as e:
        if e.errno == errno.EEXIST and os.path.isdir(working_dir):
            pass
        else:
            raise oddity.ToolError('Error while initiating working dir')

    cmn_name = os.path.basename(cmar_new)
    cmn_wd = os.path.join(working_dir, cmn_name)

    try:
        os.mkdir(cmn_wd)
    except Exception as e:
        if e.errno == errno.EEXIST and os.path.isdir(cmn_wd):
            pass
        else:
            raise oddity.ToolError('Error making working dir while unwrapping')

    logging.info('Unwrapping MAR#1')
    logging.debug('subprocess call to %s',
                  str(([UNWRAP, cmar_new], 'cwd:', cmn_wd, 'env:', my_env)))

    subprocess.call([UNWRAP, cmar_new], cwd=cmn_wd, env=my_env)

    cmo_name = os.path.basename(cmar_old)
    cmo_wd = os.path.join(working_dir, cmo_name)

    try:
        os.mkdir(cmo_wd)
    except Exception as e:
        if e.errno == errno.EEXIST and os.path.isdir(cmo_wd):
            pass
        else:
            raise oddity.ToolError('Error while initiating working dir')

    logging.info('Unwrapping MAR#2')
    logging.debug('subprocess call to %s',
                  str(([UNWRAP, cmar_old], 'cwd:', cmo_wd, 'env:', my_env)))

    subprocess.call([UNWRAP, cmar_old], cwd=cmo_wd, env=my_env)

    pmar_name = '-'.join([cmo_name, cmn_name])
    pmar_path = os.path.join(working_dir, pmar_name)

    logging.info('Generating partial mar @ %s', pmar_path)
    logging.debug('subprocess call to %s',
                  str(([MAKE_INCREMENTAL, pmar_path, cmo_wd, cmn_wd],
                       'cwd=', working_dir, 'env=', my_env)))

    subprocess.call(["bash", MAKE_INCREMENTAL, pmar_path, cmo_wd, cmn_wd],
                    cwd=working_dir, env=my_env)
    logging.info('Partial now available at path: %s', pmar_path)

    return pmar_path
