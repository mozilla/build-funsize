import fetch
import cache

import errno
import os
import subprocess

def get_complete_mar(url, checksum, output_file=None):

    """ Return binary string if no output_file specified """

    # Check if file is in cache
    # If we find it retrieve it from cache
    if cache.find(checksum):
        mar = cache.retrieve(checksum, output_file=output_file)
    # Otherwise we download it and cache it
    else:
        mar = fetch.downloadmar(url, checksum, output_file=output_file)
        cache.save(outputfile, isfile=bool(outputfile))

    return mar

def get_partial_mar(new_cmar_url, new_cmar_hash, old_cmar_url, old_cmar_hash):
    """ Function that returns the partial MAR file to transition from the mar
    given by old_cmar_url to new_cmar_url
    """

    pass

    # Check if this exists in cache

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
    subprocess.call([UNWRAP, cmar_new], cwd=cmo_wd, env=my_env)


################################################################################
    # run make_incremental_update.sh on both of them
    pmar_name = cmo_name + '--' + cmn_name # partial mar name
    pmar_path = os.path.join(working_dir, pmar_name)

    print "Generating partial mar @ %s" % pmar_path
    subprocess.call([MAKE_INCREMENTAL, pmar_path, cmo_wd, cmn_wd], cwd=working_dir, env=my_env)


##generate_partial_mar('/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/current.mar',
##                      '/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/previous.mar',
##                      '/Users/mozilla/Work/Senbonzakura/senbonzakura/dump/',
##                      working_dir='/tmp/testing-work')

# Why does this break with relative paths? probably cwd arg
