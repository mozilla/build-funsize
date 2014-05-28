# What should go into core and what shouldn't?
import fetch
import cache
import db

import errno
import os
import subprocess
import tempfile

def get_complete_mar(url, checksum, output_file=None):

    """ Return binary string if no output_file specified """

    # Check if file is in cache
    # If we find it retrieve it from cache
    if cache.find(checksum):
        mar = cache.retrieve(checksum, output_file=output_file)
    # Otherwise we download it and cache it
    else:
        mar = fetch.downloadmar(url, checksum, output_file=output_file)
        # If output_file is specified, use that, else use the mar binary string
        cache.save(output_file or mar, isfile=bool(output_file))

    return mar

def something():
# What did I even make this for?!
    pass

def build_partial_mar(new_cmar_url, new_cmar_hash, old_cmar_url, old_cmar_hash,
        identifier):

    #import pdb
    #pdb.set_trace()
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

# Do we really need this? Why not use python's inbuilt Random folder generator?
# Unless we have better reason, we probably should, but lets keep the option
# open to configuration
#TMP_MAR_STORAGE='/tmp/something/'
#TMP_TOOL_STORAGE='tmp/tools/'
#TMP_WORKING_DIR='/tmp/working/'

    # Create the directories to work in.
    TMP_MAR_STORAGE = tempfile.mkdtemp(prefix='cmar_storage_')
    TMP_TOOL_STORAGE='/tmp/tools/' # Using static location, till we figure out tooling.
    TMP_WORKING_DIR = tempfile.mkdtemp(prefix='working_dir_')

    print "Locals:", '*'*50
    print locals()
    print '*'*50

    print "Working directories:"
    print TMP_MAR_STORAGE
    print TMP_TOOL_STORAGE
    print TMP_WORKING_DIR
    print "*"*80

    new_cmar_path = os.path.join(TMP_MAR_STORAGE, 'new.mar')
    old_cmar_path = os.path.join(TMP_MAR_STORAGE, 'old.mar')


    # Fetch the complete MARs here. ################################################

    get_complete_mar(new_cmar_url, new_cmar_hash, output_file=new_cmar_path)
    get_complete_mar(old_cmar_url, old_cmar_hash, output_file=old_cmar_path)

################################################################################

# Tool fetching and related things go in here. #################################
# Nothing here, right now, TODO: Tooling after issue resolved

# If there are very few, might as well dump them all in the cache before hand?
# Keeping it all in the dir statically for now.


################################################################################

# Call generate? ###############################################################

    # If can't generate pmar location properly, then insert ABORTED in DB?
    try: 
        local_pmar_location = generate_partial_mar(new_cmar_path, old_cmar_path,
                                    TMP_TOOL_STORAGE, working_dir=TMP_WORKING_DIR)
    except:
        # Something definitely went wrong.
        # Update DB to reflect abortion
        db.update(identifier, status=db.status_code['ABORTED'])
        return None

################################################################################
    else:
# Cache related stuff ##########################################################
        try:
            pmar_location = cache.save('somelocation', isfile=True)
        except:
            # If there are porblems in caching, handle them here.
            raise
################################################################################

# DB Updates and related stuff? ################################################
        db.update(identifier, status=db.status_code['COMPLETED'],
                location=pmar_location)
################################################################################

# Cleanup temp directories here ?###############################################
################################################################################

# What do we want to return?
    return None

def generate_partial_mar(cmar_new, cmar_old, difftools_path, working_dir=None):
    """ cmar_new is the path of the newer complete .mar file
        cmar_old is the path of the older complete .mar file
        difftools_path specifies the path of the directory in which
        the difftools, including mar,mbsdiff exist
    """

    # Setup defaults and ENV vars
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

################################################################################

##generate_partial_mar('/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/current.mar',
##                      '/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/previous.mar',
##                      '/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/',
##                      working_dir='/tmp/testing-work')

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

    print "unwrapping mar1"
    subprocess.call([UNWRAP, cmar_new], cwd=cmn_wd, env=my_env)
    print "Crossed subprocess"

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

    print "unwrapping mar2"
    subprocess.call([UNWRAP, cmar_old], cwd=cmo_wd, env=my_env)


################################################################################
    # run make_incremental_update.sh on both of them
    pmar_name = cmo_name + '-' + cmn_name # partial mar name
    pmar_path = os.path.join(working_dir, pmar_name)

    print "Generating partial mar @ %s" % pmar_path
    subprocess.call([MAKE_INCREMENTAL, pmar_path, cmo_wd, cmn_wd], cwd=working_dir, env=my_env)

    print "Path:",pmar_path
    return pmar_path


if __name__ == '__main__':
    # Why does this break with relative paths? probably cwd arg
    ##generate_partial_mar('/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/current.mar',
    ##                     '/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/previous.mar',
    ##                     '/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/',
    ##                     working_dir='/tmp/testing-work')
    generate_partial_mar('/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/current.mar',
                         '/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/previous.mar',
                         '/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/',
                         working_dir='/tmp/testing-work')

