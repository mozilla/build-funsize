#!/usr/bin/env bash
# Author: Anhad Jai Singh

SCRIPT_NAME=$(basename $0)

# General variables
DEFAULT_URL='http://127.0.0.1:5000'
DEFAULT_CACHE='/perma/cache'
DEFAULT_DB='./test.db'


# Nightly related variables
DEFAULT_SRC_MAR='http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/2014/05/2014-05-12-03-02-02-mozilla-central/firefox-32.0a1.en-US.mac.checksums'
DEFAULT_DST_MAR='http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/2014/05/2014-05-13-03-02-01-mozilla-central/firefox-32.0a1.en-US.mac.complete.mar'
DEFAULT_SRC_HASH_MD5='da0ecd3c65f3f333ee42ca332b97e925'
DEFAULT_DST_HASH_MD5='c738c5f2d719ef0e00041b6df6a987fe'
DEFAULT_SRC_HASH='1a6bec1dd103f8aacbd450ec0787c94ccf07f5e100d7c356bf2fb75c8181998563e0ded4556c9fb050ee1e7451c1ac765bc1547c8c6ec6bcffdf62ae0daf1150'
DEFAULT_DST_HASH='2d7fb432484f2b0354b7f1df503b329cc3063b44d894a06606b6ee692d3b22679dc0c80eb29426d2a6e6dba3e34242ca1bf0a5e6d6dc6c159092cb0becc7e80f'
DEFAULT_IDENTIFIER="$DEFAULT_SRC_HASH-$DEFAULT_DST_HASH"

# Release related variables
FF29="http://ftp.mozilla.org/pub/mozilla.org/firefox/releases/29.0/update/mac/en-US/firefox-29.0.complete.mar"
FF29_HASH_MD5="cd757aa3cfed6f0a117fa16f33250f74"
FF29_HASH="3933dc4b3abe6e07fc62bf4821d52fc87e442dadf84aed9a28e2671fc60f3a85232d84a529d4089058d9ad3fd9af98d0b9d8482c9ca9a585770c0dcd288b0937"
FF28="http://ftp.mozilla.org/pub/mozilla.org/firefox/releases/28.0/update/mac/en-US/firefox-28.0.complete.mar"
FF28_HASH_MD5="d7f65cf5002a1dfda88a33b7a31b65eb"
FF28_HASH="4d5bcce9c29f04daae9af1868997ce26c71bc836fc0f403d4800746379610a5ef83a390eb3037d356033b4bf627e922a71c9fba5ee645b70b980aef90e6c8ff9"
RELEASE_IDENTIFIER="$FF28_HASH-$FF29_HASH"


# Coloured output
error(){
    # Red
    str=$1
    echo -e "\e[0;31m"$str"\e[0m" >&2
}

info(){
    # Yellow
    str=$1
    echo -e "\e[0;33m"$str"\e[0m" >&2
}

debug(){
    # Purple
    str=$1
    if [ $DEBUG ]
    then
        echo -e "\e[0;35m"$str"\e[0m" >&2
    fi
}

usage(){
    echo "$SCRIPT_NAME [-h] [-d] [-u SERVER-URL] SUB-COMMAND"
    echo "Script that tests the GET and POST requests"
    echo ""
    echo "-h: This help"
    echo "-d: Enable debug logging"
    echo "-u: Base server URL to use for all requests"
    echo ""
    echo "SUB-COMMANDS : trigger, trigger-release, get, get-release, clobber, error"
    echo ""
    echo "trigger           : Send a POST to trigger building partial for Firefox Release v28 -> v29"
    echo "trigger-release   : Send a POST to trigger building partial for Firefox Nightly 2014-05-12-03-02-02 -> 2014-05-13-03-02-01"
    echo "get               : Send a GET to poll/fetch the partial for Firefox Nightly 2014-05-12-03-02-02 -> 2014-05-13-03-02-01"
    echo "get-release       : Send a GET to poll/fetch the Nightly partial for Firefox Release v28 -> v29"
    echo "clobber           : Wipe Cache and Database to for a clean start"
    echo "error             : Send a POST to the SERVER-URL without params to trigger an error"
}


count=0
while getopts ":u:hd" option
do
    case $option in
        d)
            DEBUG=true;
            debug "Debug logging enabled";
            count=$(expr $count + 1);
            ;;

        u)
            echo "OPTARG" $OPTARG
            #DEFAULT_URL=
            count=$(expr $count + 2);
            ;;

        h)
            usage;
            exit 0;
            ;;
        ?)
            usage;
            exit 1;
            ;;
    esac
done
shift $count

trigger_partial_build(){
    SRC_MAR=$1
    DST_MAR=$2
    SRC_HASH=$3
    DST_HASH=$4

    debug "CMD: curl -X POST" "$DEFAULT_URL/partial" -d "mar_from=$SRC_MAR&mar_to=$DST_MAR&mar_from_hash=$SRC_HASH&mar_to_hash=$DST_HASH"
    curl -X POST "$DEFAULT_URL/partial" -d "mar_from=$SRC_MAR&mar_to=$DST_MAR&mar_from_hash=$SRC_HASH&mar_to_hash=$DST_HASH" && echo
    if [ $? -eq 0 ]
    then
        debug "Trigger succeeded"
    else
        error "Trigger Failed"
    fi

}

get_partial_build(){
    IDENTIFIER=$1
    debug "CMD: curl -X GET ""$DEFAULT_URL/partial/""$IDENTIFIER"
    curl -X GET "$DEFAULT_URL/partial/$IDENTIFIER" && echo
    if [ $? -eq 0 ]
    then
        debug "GET succeeded"
    else
        error "GET Failed"
    fi

}

trigger_partial_error(){
    # Posting with no params should give an error
    debug "curl -X POST $DEFAULT_URL/partial"
    curl -X POST $DEFAULT_URL'/partial' && echo
    if [ $? -eq 0 ]
    then
        debug "Trigged"
    else
        error "Trigger Failed"
    fi
}

clobber(){
    # Wipe ALL the things
    CACHE=$1
    DB=$2


    debug "clobber function called with $@"

    rm -rf $1/* #Hope this doesn't mess things up. Fingers crossed.
    if [ $? -eq 0 ]
    then
        info "Cache Cleaned"
    else
        error "Cache could not be cleaned"
    fi

    rm $2
    if [ $? -eq 0 ]
    then
        info "Database Cleaned"
    else
        error "Could not remove database"
    fi
}

#TODO: Add long form command line args for MAR URLs and Hashes
case $1 in

    "trigger") 
        trigger_partial_build $DEFAULT_SRC_MAR $DEFAULT_DST_MAR $DEFAULT_SRC_HASH $DEFAULT_DST_HASH
        debug "Called trigger_partial_build"
        exit 0 ;;

    "trigger-release") 
        trigger_partial_build $FF28 $FF29 $FF28_HASH $FF29_HASH
        debug "Called: trigger_partial_build"
        exit 0 ;;

    "error")
        trigger_partial_error
        debug "Called: trigger_partial_error"
        exit 0;;

    "get")
        get_partial_build $DEFAULT_IDENTIFIER
        debug "Called: get_partial_build $DEFAULT_IDENTIFIER"
        exit 0 ;;

    "get-release")
        get_partial_build $RELEASE_IDENTIFIER
        debug "Called: get_partial_build $RELEASE_IDENTIFIER"
        exit 0 ;;

    "clobber")
        clobber $DEFAULT_CACHE $DEFAULT_DB
        debug "Called: clobber $DEFAULT_CACHE $DEFAULT_DB"
        exit 0 ;;

    *)
        usage
        exit 1 ;;
esac
