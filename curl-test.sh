#!/usr/bin/env bash
# Author: Anhad Jai Singh

SCRIPT_NAME=$(basename $0)

# General variables
DEFAULT_URL='http://127.0.0.1:5000'
DEFAULT_CACHE='/perma/cache'
DEFAULT_DB='./test.db'


# Nightly related variables
DEFAULT_SRC_MAR='http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/2014-05-12-03-02-02-mozilla-central/firefox-32.0a1.en-US.mac.complete.mar'
DEFAULT_DST_MAR='http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/2014-05-13-03-02-01-mozilla-central/firefox-32.0a1.en-US.mac.complete.mar'
DEFAULT_SRC_HASH='da0ecd3c65f3f333ee42ca332b97e925'
DEFAULT_DST_HASH='c738c5f2d719ef0e00041b6df6a987fe'
DEFAULT_IDENTIFIER="$DEFAULT_SRC_HASH-$DEFAULT_DST_HASH"

# Release related variables
FF29="http://ftp.mozilla.org/pub/mozilla.org/firefox/releases/29.0/update/mac/en-US/firefox-29.0.complete.mar"
FF29_HASH="cd757aa3cfed6f0a117fa16f33250f74"
FF28="http://ftp.mozilla.org/pub/mozilla.org/firefox/releases/28.0/update/mac/en-US/firefox-28.0.complete.mar"
FF28_HASH="d7f65cf5002a1dfda88a33b7a31b65eb"
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

    rm $1/*
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
