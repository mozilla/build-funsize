#!/usr/bin/env bash
# Author: Mihai Tabara
# September 2014
# tabara.mihai@gmail.com

self=$(basename $0)
CLIENT_RUNNER="client.py"
input="$1"
output="$2"

usage(){
    echo "$self INPUT_FILENAME OUTPUT_FILENAME"
}

compare_hash(){
  echo 'TODO mar hash file here'
}

process(){
  from_url=`awk '{ print $1 }' $input`
  to_url=`awk '{ print $2 }' $input`
  from_hash=`awk '{ print $3 }' $input`
  to_hash=`awk '{ print $4 }' $input`
  channel=`awk '{ print $5 }' $input`
  version=`awk '{ print $NF }' $input`
  python $CLIENT_RUNNER --from-url $from_url --to-url $to_url --from-hash $from_hash --to-hash $to_hash --channel $channel --version $version --output $output

  if [ $? -eq 0 ]
  then
      echo "Partial successfully retrieved at "$output
      compare_hash;
  else
      echo "Partial unavailable"
      exit 1;
  fi
}

if [ $# -lt 2 ]
then
  usage;
  exit 0;
fi

process;
