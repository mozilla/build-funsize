"""
funsize.backend.core
~~~~~~~~~~~~~~~~~~

This module contains the brain of the entire funsize project

"""

import logging
import os
import tempfile
import sh

import funsize.utils.fetch as fetch
from funsize.cache import cache

log = logging.getLogger(__name__)

TOOLS_DIR = "/perma/tools"  # TODO: pass or keep them under the tree?
UNWRAP = os.path.join(TOOLS_DIR, 'unwrap_full_update.pl')
MAKE_INCREMENTAL = os.path.join(TOOLS_DIR, 'make_incremental_update.sh')
MAR = os.path.join(TOOLS_DIR, 'mar')
MBSDIFF = os.path.join(TOOLS_DIR, 'mbsdiff')


def get_complete_mar(url, mar_hash, output_file):
    """ Return binary string if no output_file specified """
    log.info('Downloading complete MAR %s with mar_hash %s', url, mar_hash)

    if url.startswith('http://') or url.startswith('https://'):
        fetch.download_mar(url, mar_hash, output_file)
        cache.save(output_file, 'complete', mar_hash, isfilename=True)
    else:
        cache.retrieve('complete', mar_hash, output_file=output_file)

    log.info('Satisfied request for complete MAR %s with mar_hash %s', url,
             mar_hash)


def build_partial_mar(to_mar_url, to_mar_hash, from_mar_url, from_mar_hash,
                      identifier, channel_id, product_version):
    """ Function that returns the partial MAR file to transition from the mar
        given by from_mar_url to to_mar_url
    """
    log.debug('Creating temporary working directories')
    TMP_MAR_STORAGE = tempfile.mkdtemp(prefix='mar_')
    TMP_WORKING_DIR = tempfile.mkdtemp(prefix='wd_')
    log.debug('MAR storage: %s', TMP_MAR_STORAGE)
    log.debug('Working dir storage: %s', TMP_WORKING_DIR)

    to_mar = os.path.join(TMP_MAR_STORAGE, 'new.mar')
    from_mar = os.path.join(TMP_MAR_STORAGE, 'old.mar')

    log.info('Looking up the complete MARs required')
    get_complete_mar(to_mar_url, to_mar_hash, to_mar)
    get_complete_mar(from_mar_url, from_mar_hash, from_mar)

    log.info('Creating cache connections')
    try:
        partial_file = generate_partial_mar(
            to_mar, from_mar, channel_id, product_version,
            working_dir=TMP_WORKING_DIR)
        log.debug('Partial MAR generated at %s', partial_file)
    except:
        cache.delete('partial', identifier)
        raise

    log.info('Saving partial MAR %s to cache with key %s', partial_file,
             identifier)
    cache.save(partial_file, 'partial', identifier, isfilename=True)


def generate_partial_mar(to_mar, from_mar, channel_id, product_version,
                         working_dir):
    """ to_mar is the path of the newer complete .mar file
        from_mar is the path of the older complete .mar file
    """
    my_env = os.environ.copy()
    my_env['MAR'] = MAR
    my_env['MBSDIFF'] = MBSDIFF
    my_env['MOZ_CHANNEL_ID'] = channel_id
    my_env['MOZ_PRODUCT_VERSION'] = product_version
    my_env['LC_ALL'] = 'C'

    to_mar_name = os.path.basename(to_mar)
    to_mar_wd = os.path.join(working_dir, to_mar_name)
    os.mkdir(to_mar_wd)

    log.info('Unwrapping "to" MAR')
    unwrap_cmd = sh.Command(UNWRAP)
    out = unwrap_cmd(to_mar, _cwd=to_mar_wd, _env=my_env, _timeout=120,
                     _err_to_out=True)
    log.debug("Command returned:\n%s", out)

    from_mar_name = os.path.basename(from_mar)
    from_mar_wd = os.path.join(working_dir, from_mar_name)
    os.mkdir(from_mar_wd)

    log.info('Unwrapping "from" MAR')
    out = unwrap_cmd(from_mar, _cwd=from_mar_wd, _env=my_env, _timeout=120,
                     _err_to_out=True)
    log.debug("Command returned:\n%s", out)

    partial_name = '-'.join([from_mar_name, to_mar_name])
    partial_mar = os.path.join(working_dir, partial_name)

    log.info('Generating partial mar @ %s', partial_mar)
    out = sh.bash(MAKE_INCREMENTAL, partial_mar, from_mar_wd, to_mar_wd,
                  _cwd=working_dir, _env=my_env, _timeout=300, _err_to_out=True)
    log.debug("Command returned: %s", out)
    log.info('Partial now available at path: %s', partial_mar)

    return partial_mar
