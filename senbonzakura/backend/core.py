# What should go into core and what shouldn't?
import senbonzakura.utils.fetch as fetch
import senbonzakura.cache.cache as cache
import senbonzakura.database.db as db
import senbonzakura.backend.tools as tools

import ConfigParser
import errno
import logging
import os
import subprocess
import tempfile
import time

__here__ = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(__here__, '../configs/worker.ini')
VERIFICATION_FILE = os.path.join(__here__, '../configs/verification_file.csv')

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE_PATH)

if config.items('db') and config.items('cache'):
    #app.config['DB_URI'] = config.get('db', 'uri')
    #app.config['CACHE_URI'] = config.get('cache', 'uri')
    DB_URI = config.get('db', 'uri')
    CACHE_URI = config.get('cache', 'uri')
    TOOLS_DIR = config.get('tools', 'dir')
else:
    raise oddity.ConfigError('Configuration parameters missing')

def get_complete_mar(url, identifier, output_file=None):

    """ Return binary string if no output_file specified """

    cacheo = cache.Cache(CACHE_URI)

    # Check if file is in cache
    # If we find it retrieve it from cache
    logging.info('Request for complete MAR %s with Identifer %s in cache' % (url, identifier))
    if cacheo.find(identifier, 'complete'):
        logging.debug('Found complete MAR %s with Identifer %s in cache' % (url, identifier))
        logging.info('retriving MAR from cache')
        mar = cacheo.retrieve(identifier, 'complete', output_file=output_file)
    # Otherwise we download it and cache it
    else:
        logging.debug('Did not find complete MAR %s with Identifer %s in cache' % (url, identifier))
        logging.info('Downloading complete MAR %s with Identifer %s' % (url, identifier))
        mar = fetch.downloadmar(url, identifier, output_file=output_file)
        # If output_file is specified, use that, else use the mar binary string
        cacheo.save(output_file or mar, identifier, 'complete', isfile=bool(output_file))

    logging.info('Request for complete MAR %s with Identifer %s satisfied' % (url, identifier))
    return mar

def build_partial_mar(new_cmar_url, new_cmar_hash, old_cmar_url, old_cmar_hash,
        identifier, channel_id, product_version):

    #""" Function that returns the partial MAR file to transition from the mar
    #given by old_cmar_url to new_cmar_url
    #"""

    # Don't have to check the cache anymore, do we?
    # Add Tool Fetching logic
    # Setup things for the generate_partial_mar
    # Call partial mar and that's it?
    # Dump into cache
    # Add stuff to the DB as well? Yes? Good idea? not so good?

# Some global config here

# FIXME: Need to move the DBO stuff into celery logic
    logging.info('creating database and cache connections')
    dbo = db.Database(DB_URI)
    cacheo = cache.Cache(CACHE_URI)

    # Create the directories to work in.
    logging.info('creating temporary working directories')
    TMP_MAR_STORAGE = tempfile.mkdtemp(prefix='cmar_storage_')
    logging.debug('MAR storage: %s' % TMP_MAR_STORAGE)
    TMP_WORKING_DIR = tempfile.mkdtemp(prefix='working_dir_')
    logging.debug('Working dir storage: %s' % TMP_WORKING_DIR)

    new_cmar_path = os.path.join(TMP_MAR_STORAGE, 'new.mar')
    old_cmar_path = os.path.join(TMP_MAR_STORAGE, 'old.mar')


# Fetch the complete MARs here. ################################################
    logging.info('Looking up the complete MARs required')
    get_complete_mar(new_cmar_url, new_cmar_hash, output_file=new_cmar_path)
    get_complete_mar(old_cmar_url, old_cmar_hash, output_file=old_cmar_path)

################################################################################

# Tool fetching and related things go in here. #################################

    tmo = tools.ToolManager(TOOLS_DIR, VERIFICATION_FILE)

    TMP_TOOL_STORAGE = tmo.get_path()

    logging.info('Tool storage: %s' % TMP_TOOL_STORAGE)
# If there are very few, might as well dump them all in the cache before hand?
# Keeping it all in the dir statically for now.

################################################################################

# Call generate? ###############################################################

    # If can't generate pmar location properly, then insert ABORTED in DB?
    try: 
        local_pmar_location = generate_partial_mar(new_cmar_path, old_cmar_path,
                                    TMP_TOOL_STORAGE, channel_id, product_version, working_dir=TMP_WORKING_DIR)
        logging.debug('Partial Mar generated at %s' % local_pmar_location)
    except:
        # Something definitely went wrong.
        # Update DB to reflect abortion
        dbo.update(identifier, status=db.status_code['ABORTED'], finish_timestamp=time.time())
        #return None
        raise

################################################################################
    else:
# Cache related stuff ##########################################################
        try:
            logging.info('Saving PMAR %s to cache with key %s' % (local_pmar_location, identifier))
            pmar_location = cacheo.save(local_pmar_location, identifier, 'partial', isfile=True)
        except:
            # If there are porblems in caching, handle them here.
            raise
################################################################################

# DB Updates and related stuff? ################################################
        logging.info('Updating DB for %s' % identifier)
        dbo.update(identifier, status=db.status_code['COMPLETED'],
                finish_timestamp=time.time())
################################################################################

# Cleanup
    dbo.close()
# Cleanup temp directories here ?###############################################
################################################################################

# What do we want to return?
    return None

def generate_partial_mar(cmar_new, cmar_old, difftools_path, channel_id, product_version, working_dir=None):
    """ cmar_new is the path of the newer complete .mar file
        cmar_old is the path of the older complete .mar file
        difftools_path specifies the path of the directory in which
        the difftools, including mar,mbsdiff exist
    """

    # Set working directory
    if not working_dir:
        working_dir='.' #set pwd as the working dir
    # Setup difftools
    UNWRAP = os.path.join(difftools_path, 'unwrap_full_update.pl')
    MAKE_INCREMENTAL = os.path.join(difftools_path, 'make_incremental_update.sh')
    MAR = os.path.join(difftools_path, 'mar')
    MBSDIFF = os.path.join(difftools_path, 'mbsdiff')

    # Add MAR and MBSDIFF to env we pass down to subprocesses
    my_env = os.environ.copy()
    my_env['MAR'] = MAR
    my_env['MBSDIFF'] = MBSDIFF
    my_env['MOZ_CHANNEL_ID'] = channel_id
    my_env['MOZ_PRODUCT_VERSION'] = product_version

    
    # Create working directory for entire shindig
    # Check if working directory exists, if it doesn't, create it.
    try:
        os.mkdir(working_dir)
    except Exception as e:
        if e.errno == errno.EEXIST and os.path.isdir(working_dir):
            pass
        else:
            raise
    # Move stuff to working dir. # Do we need to? I don't think so.


# Unwrap MAR1 ##################################################################
    cmn_name = os.path.basename(cmar_new)
    cmn_wd = os.path.join(working_dir, cmn_name)

    # Create dir to unwrap newer complete mar into
    try:
        os.mkdir(cmn_wd)
    except Exception as e:
        if e.errno == errno.EEXIST and os.path.isdir(cmn_wd):
            pass
        else:
            raise

    logging.info('unwrapping MAR#1')
    logging.debug('subprocess call to %s', str(([UNWRAP, cmar_new], 'cwd:', cmn_wd, 'env:', my_env)))
    process = subprocess.call([UNWRAP, cmar_new], cwd=cmn_wd, env=my_env)

# Unwrap MAR2 ##################################################################
    cmo_name = os.path.basename(cmar_old)
    cmo_wd = os.path.join(working_dir, cmo_name)

    # Create dir to unwrap older complete mar into
    try:
        os.mkdir(cmo_wd)
    except Exception as e:
        if e.errno == errno.EEXIST and os.path.isdir(cmo_wd):
            pass
        else:
            raise

    logging.info('unwrapping MAR#2')
    logging.debug('subprocess call to %s', str(([UNWRAP, cmar_old], 'cwd:', cmo_wd, 'env:', my_env)))
    subprocess.call([UNWRAP, cmar_old], cwd=cmo_wd, env=my_env)


################################################################################
    # run make_incremental_update.sh on both of them
    pmar_name = cmo_name + '-' + cmn_name # partial mar name
    pmar_path = os.path.join(working_dir, pmar_name)

    logging.info('Generating partial mar @ %s' % pmar_path)
    logging.debug('subprocess call to %s', str(([MAKE_INCREMENTAL, pmar_path, cmo_wd, cmn_wd], 'cwd=', working_dir, 'env=', my_env)))
    subprocess.call([MAKE_INCREMENTAL, pmar_path, cmo_wd, cmn_wd], cwd=working_dir, env=my_env)

    logging.info('Partial now available at path: %s' % pmar_path)
    return pmar_path
