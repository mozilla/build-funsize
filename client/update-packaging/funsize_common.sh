#!/bin/bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

#
# This tool contains functions that are to be used to handle/enable funsize
# Author: Mihai Tabara
#

DEFAULT_URL='http://127.0.0.1:5000/cache'

getsha512(){
    echo "$(openssl sha512 "${1}" | awk '{print $2}')"
}

upload_patch(){
    sha_from=`getsha512 "$1"`
    sha_to=`getsha512 "$2"`
    path_patch="$3"

    cmd="curl -sSw %{http_code} -o /dev/null -X POST $DEFAULT_URL -F sha_from="$sha_from" -F sha_to="$sha_to" -F patch_file="@$path_patch""
    ret_code=`$cmd`

    if [ $ret_code -eq 200 ]
    then
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

    cmd="curl -sSGw %{http_code} $DEFAULT_URL -o "$destination_file" --data-urlencode "sha_from=$sha_from" --data-urlencode "sha_to=$sha_to""
    ret_code=`$cmd`

    if [ $ret_code -eq 200 ]
    then
        echo "Successful retrieved $destination_file from funsize!"
        return 0;
    fi

    echo "Failed to retrieve $destination_file from funsize!"
    return 1;
}
