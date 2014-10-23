#!/usr/bin/env bash

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
            exit 0;
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
            exit 1;
            ;;
    esac
done


file_list=$(curl "http://hg.mozilla.org/integration/mozilla-inbound/file/$CHANGESET/tools/update-packaging?style=raw" | awk '{print $3}')
echo $file_list

for FILENAME in $file_list
do
    URL="http://hg.mozilla.org/integration/mozilla-inbound/raw-file/$CHANGESET/tools/update-packaging/$FILENAME"
    curl -s -o $OUTPUT_DIR/$FILENAME $URL
done
