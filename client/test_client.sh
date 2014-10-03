#!/usr/bin/env bash
# Author: Mihai Tabara
# September 2014
# tabara.mihai@gmail.com

self=$(basename $0)
CLIENT_RUNNER="client.py"
HASH_RUNNER="client_mar.py"
input="$1"
output="$2"

usage(){
    echo "$self INPUT_FILENAME OUTPUT_FILENAME"
}

compare_hash(){
  marfile=$1
  correct_hash=$2

  echo "Chech hashings ..."
  local_hash=$(python $HASH_RUNNER --hash $marfile)

  if [ "$local_hash" == "$correct_hash" ]
  then
    echo "[OK] Test passed"
  else
    echo "[Fail] Test failed"
    exit 1;
  fi
}

error(){
    # colored red errors
    str=$@
    echo -e "\e[0;31m${str}\e[0m" >&2
}

info(){
    # colored yellow information
    str=$@
    echo -e "\e[0;33m${str}\e[0m" >&2
}

clobber() {
    rm $output
    if [ $? -eq 0 ]
    then
        info "Cleaned the file."
    else
        error "Nothing to clean, mving on."
    fi
}

process(){
  clobber

  from_url=`awk '{ print $1 }' $input`
  to_url=`awk '{ print $2 }' $input`
  from_hash=`awk '{ print $3 }' $input`
  to_hash=`awk '{ print $4 }' $input`
  channel=`awk '{ print $5 }' $input`
  version=`awk '{ print $NF }' $input`
  ok_hash="887c50eb11e92e6ea4b515596b23e59f4fdf85d6783920060f0d8bac3c954354333aa9a7575a0c73bb72548b33f213ec079c616a9e8a88041046e894a5245a95"
  cmd="python $CLIENT_RUNNER --from-url $from_url --to-url $to_url --from-hash $from_hash --to-hash $to_hash --channel $channel --version $version --output $output"

  echo 'Request partial from funsize ...'
  $cmd

  if [ $? -eq 0 ]
  then
      echo "Partial successfully retrieved at "$output
      compare_hash $output $ok_hash;
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
