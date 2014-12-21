#!/bin/bash
# Author: Anhad Jai Singh

set -eu # stricter error checking
set -x
#set -e # stricter error checking

SCRIPT_NAME=$(basename $0)
# General variables
DEFAULT_URL='http://127.0.0.1:5000'

# Release related variables
FROM_MAR="https://ftp.mozilla.org/pub/mozilla.org/firefox/releases/33.1/update/mac/en-US/firefox-33.1.complete.mar"
FROM_MAR_HASH="cb965c32f7fb80546af316804aab8499e2c6a6e6954c95d06d83443a5c05b1869104872761bb8526fa79c6754373cbf4cc250ff8e4fe7d627cb840b22e39ea03"

TO_MAR="https://ftp.mozilla.org/pub/mozilla.org/firefox/releases/34.0/update/mac/en-US/firefox-34.0.complete.mar"
TO_MAR_HASH="fc554499f74670279d58f754ef230ac45f7899aabfdca85ee52b40999cb6b503a9e003584dabc37ecd7f44be55cabaa63308855b2b3e5a2746107071d5aac018"

TO_VERSION="34.0"
REL_CHANNEL_ID="firefox-mozilla-release"
RELEASE_IDENTIFIER="$FROM_MAR_HASH-$TO_MAR_HASH"

trigger_partial_build(){
    SRC_MAR=$1
    DST_MAR=$2
    SRC_HASH=$3
    DST_HASH=$4
    CHANNEL_ID=$5
    PRODUCT_VERSION=$6

    curl -s -S -X POST $DEFAULT_URL/partial \
        -d "mar_from=$SRC_MAR&mar_to=$DST_MAR&sha_from=$SRC_HASH&sha_to=$DST_HASH&channel_id=$CHANNEL_ID&product_version=$PRODUCT_VERSION"
}

get_partial_build(){
    IDENTIFIER=$1
    shift
    curl -s -S $@ $DEFAULT_URL/partial/$IDENTIFIER
}

trigger_partial_error(){
    # Posting with no params should give an error
    curl -s -S -X POST $DEFAULT_URL/partial
}

usage(){
    echo "$SCRIPT_NAME [-h] [-d] [-u SERVER-URL] SUB-COMMAND"
    echo "Script that tests the GET and POST requests"
    echo ""
    echo "SUB-COMMANDS : trigger-release, get, get-release, error"
    echo ""
    echo "trigger-release   : Send a POST to trigger building partial for Firefox Nightly 2014-05-12-03-02-02 -> 2014-05-13-03-02-01"
    echo "trigger-release   : Alternate usage with as params passed to trigger-release [src url] [dst url] [src hash] [dst hash] [channel id] [product version]"
    echo "get-release       : Send a GET to poll/fetch the Nightly partial for Firefox Release v28 -> v29"
    echo "error             : Send a POST to the SERVER-URL without params to trigger an error"
}


if [ $# -lt 1 ]
then
  usage;
  exit 0;
fi

#TODO: Add long form command line args for MAR URLs and Hashes
case $1 in
    "trigger-release")
        shift
        if [ $# -gt 0 ]; then
          if [ $# -eq 6 ]; then
            trigger_partial_build $@
          else
            error "Incorrect number of args";
            exit 1;
          fi
        else
          trigger_partial_build $FROM_MAR $TO_MAR $FROM_MAR_HASH $TO_MAR_HASH \
              $REL_CHANNEL_ID $TO_VERSION
        fi
        ;;
    "error")
        trigger_partial_error
        ;;
    "get-release")
        shift
        get_partial_build $RELEASE_IDENTIFIER $@
        ;;
    *)
        usage
        exit 1
        ;;
esac
