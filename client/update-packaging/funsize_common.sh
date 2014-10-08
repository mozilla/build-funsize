#!/bin/bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

#
# This tool generates incremental update packages for the update system.
# Author: Mihai Tabara

DEFAULT_URL='http://127.0.0.1:5000/cache'

upload_patch(){
    path_from="$1"
    path_to="$2"
    path_patch="$3"

    cmd="curl -sSw %{http_code} -o /dev/null -X POST $DEFAULT_URL -d path_from=$path_from&path_to=$path_to&path_patch=$path_patch"
    ret_code=`$cmd`

    if [ $ret_code -eq 200 ]
    then
        echo "$path_patch successful uploaded to funsize!"
        return 0;
    fi

    echo "$path_patch failed to be uploaded to funsize!"
    return 1;
}

get_patch(){
    path_from="$1"
    path_to="$2"
    path_patch="$3"

    cmd="curl -sSGw %{http_code} $DEFAULT_URL -o $path_patch --data-urlencode "path_from=$path_from" --data-urlencode "path_to=$path_to""
    ret_code=`$cmd`

    if [ $ret_code -eq 200 ]
    then
        echo "successful retrieved $path_patch from funsize!"
        return 0;
    fi

    echo "failed to retrieve $path_patch from funsize!"
    return 1;
}
