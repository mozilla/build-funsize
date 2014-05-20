#!/usr/bin/env bash

# Author: Anhad Jai Singh
# Download the update packagin tools from hg.m.o


# TODO: Need to integrate downloads of mar and mbsdiff tools aswell.

BASENAME=$(basename $0)
CHANGESET="tip"
OUTPUT_DIR="."

help(){
    echo "Tool to download the latest set of update-packaging tools from hg.m.o"
    #"Needed because there is no narrow clone at the time of writing"
    echo ""
    echo "USAGE: $BASENAME [-c CHANGESET ] [-o OUTPUT_DIR ] "
    echo "-h : Print this help"
    echo "-c : mozilla-central changeset to use for tools; tip be default"
    echo "-o : Output directry where tools are stored; current dir by default"
}

while getopts ho:c: opt
do
    case $opt in
        h)
            help
            ;;
        o)
            OUTPUT_DIR=$OPTARG
            echo "Setting output dir to $OUTPUT_DIR"
            ;;
        c)
            CHANGESET=$OPTARG
            echo "Using Changeset: $CHANGESET"
            ;;
        ?)
            echo "Unrecognized option"
            ;;
    esac
done


file_list=$(curl 'http://hg.mozilla.org/mozilla-central/file/41a54c8add09/tools/update-packaging?style=raw' | awk '{print $3}')
echo $file_list

for FILENAME in $file_list
do
    URL="http://hg.mozilla.org/mozilla-central/raw-file/$CHANGESET/tools/update-packaging/$FILENAME"
    curl -o $OUTPUT_DIR/$FILENAME $URL
done
