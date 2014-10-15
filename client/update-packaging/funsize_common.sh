#!/bin/bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

#
# This tool contains functions that are to be used to handle/enable funsize
# Author: Mihai Tabara
#

SCRIPT_NAME=$(basename $0)
HOOK=""

getsha512(){
    echo "$(openssl sha512 "${1}" | awk '{print $2}')"
}

usage(){
    echo "$SCRIPT_NAME [-g] [-u] PATH-FROM-URL PATH-TO-URL PATH-PATCH SERVER-URL"
    echo "Script that saves/retrieves from cache presumptive patches as args"
    echo ""
    echo "-g pre hook - tests whether patch already in cache"
    echo "-u post hook - upload patch to cache for future use"
    echo ""
    echo "PATH-FROM-URL     : path on disk for source file"
    echo "PATH-TO-URL       : path on disk for destination file"
    echo "PATH-PATCH        : path on disk for patch between source and destination"
    echo "SERVER-URL        : host where to send the files to "
}

upload_patch(){
    sha_from=`getsha512 "$1"`
    sha_to=`getsha512 "$2"`
    path_patch="$3"
    funsize_url="$4"

    # save to local cache first
    mkdir -p "$FUNSIZE_LOCAL_CACHE_DIR/$sha_from"
    cp -af "$path_patch" "$FUNSIZE_LOCAL_CACHE_DIR/$sha_from/$sha_to"
    echo ""$path_patch" saved on local cache!"

    # send it over to funsize
    cmd="curl -sSw %{http_code} -o /dev/null -X POST $funsize_url -F sha_from="$sha_from" -F sha_to="$sha_to" -F patch_file="@$path_patch""
    ret_code=`$cmd`

    if [ $ret_code -eq 200 ]; then
        echo ""$path_patch" Successful uploaded to funsize!"
        return 0;
    fi

    echo ""$path_patch" Failed to be uploaded to funsize!"
    return 1;
}

get_patch(){
    sha_from=`getsha512 "$1"`
    sha_to=`getsha512 "$2"`
    destination_file="$3"
    funsize_url="$4"

    # try to retrieve from local cache first
    if [ -e "$FUNSIZE_LOCAL_CACHE_DIR/$sha_from/$sha_to" ]; then
        cp -af "$FUNSIZE_LOCAL_CACHE_DIR/$sha_from/$sha_to" "$destination_file"
        echo "Successful retrieved $destination_file from local cache!"
        return 0;
    fi

    # if unsuccessful, try to retrieve from funsize
    cmd="curl -sSGw %{http_code} $funsize_url -o "$destination_file" --data-urlencode "sha_from=$sha_from" --data-urlencode "sha_to=$sha_to""
    ret_code=`$cmd`

    if [ $ret_code -eq 200 ]; then
        echo "Successful retrieved $destination_file from funsize!"
        return 0;
    fi

    echo "Failed to retrieve $destination_file from funsize!"
    return 1;
}

if [ $# -lt 5 ]; then
    echo "$@"
    usage;
    exit 1;
fi

OPTIND=1

while getopts ":gu" option; do
    case $option in
        g)
            HOOK="PRE";
            ;;
        u)
            HOOK="POST";
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            ;;
    esac
done
shift $((OPTIND-1))

if [ "$HOOK" == "PRE" ]; then
    get_patch $1 $2 $3 $4;
elif [ "$HOOK" == "POST" ]; then
    upload_patch $1 $2 $3 $4;
fi
