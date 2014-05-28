#!/usr/bin/env bash

# Author: Anhad Jai Singh

################################################################################
# $1 is the major command, $2 is a subcommand. #################################
# Example ######################################################################
# script.sh get [one, two] #####################################################
# script.sh trigger ############################################################
################################################################################
################################################################################

DEFAULT_URL='http://127.0.0.1:5000'
DEFAULT_SRC_MAR='http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/2014-05-12-03-02-02-mozilla-central/firefox-32.0a1.en-US.mac.complete.mar'
DEFAULT_DST_MAR='http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/2014-05-13-03-02-01-mozilla-central/firefox-32.0a1.en-US.mac.complete.mar'
# ftp://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/2014-05-12-03-02-02-mozilla-central/firefox-32.0a1.en-US.mac.checksums
DEFAULT_SRC_HASH='da0ecd3c65f3f333ee42ca332b97e925'
# ftp://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/2014-05-13-03-02-01-mozilla-central/firefox-32.0a1.en-US.mac.checksums
DEFAULT_DST_HASH='c738c5f2d719ef0e00041b6df6a987fe'
DEFAULT_IDENTIFIER="$DEFAULT_SRC_HASH-$DEFAULT_DST_HASH"

FF29="http://ftp.mozilla.org/pub/mozilla.org/firefox/releases/29.0/update/mac/en-US/firefox-29.0.complete.mar"
FF29_HASH=
FF28="http://ftp.mozilla.org/pub/mozilla.org/firefox/releases/28.0/update/mac/en-US/firefox-28.0.complete.mar"
FF28_HASH="d7f65cf5002a1dfda88a33b7a31b65eb"

trigger_partial_build(){
    SRC_MAR=$1
    DST_MAR=$2
    SRC_HASH=$3
    DST_HASH=$4

    #echo curl -X POST "$DEFAULT_URL/partial" -d "mar_from=$SRC_MAR&mar_to=$DST_MAR&mar_from_hash=$SRC_HASH&mar_to_hash=$DST_HASH"
    curl -X POST "$DEFAULT_URL/partial" -d "mar_from=$SRC_MAR&mar_to=$DST_MAR&mar_from_hash=$SRC_HASH&mar_to_hash=$DST_HASH"

}



get_partial_build(){
    echo "got called"
    IDENTIFIER=$1
    #echo curl -X GET "$DEFAULT_URL/partial/$IDENTIFIER"
    curl -X GET "$DEFAULT_URL/partial/$IDENTIFIER"

}

trigger_partial_error(){
    curl -X POST $DEFAULT_URL'/partial'
}

#TODO: Add commandline args and generic testing stuff and so on
case $1 in

    "trigger") 
        trigger_partial_build $DEFAULT_SRC_MAR $DEFAULT_DST_MAR $DEFAULT_SRC_HASH $DEFAULT_DST_HASH
        #echo "Called trigger_partial_build"
        exit 0 ;;

    "trigger-release") 
        trigger_partial_build $FF28 $FF29 $FF28_HASH $FF29_HASH
        #echo "Called trigger_partial_build"
        exit 0 ;;

    "error")
        trigger_partial_error
        #echo "Called trigger_partial_error"
        exit 0;;

    "get")
        get_partial_build $DEFAULT_IDENTIFIER
        #echo "Called get_partial_build"
        exit 0 ;;
esac
