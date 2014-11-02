#!/usr/bin/env bash
# Author: Mihai Tabara
# September 2014
# tabara.mihai@gmail.com

self=$(basename $0)
CLIENT_RUNNER="funsizer.py"
HASH_RUNNER="mar.py"
INPUT="$1"
SERVER_URL="http://funsize-env.elasticbeanstalk.com"

usage(){
    echo "$self partials_info_file"
}

compare_hash(){
  marfile=$1
  correct_hash=$2
  counter=$3

  echo "Check hashes ..."
  local_hash=$(python $HASH_RUNNER --hash $marfile)

  if [ "$local_hash" == "$correct_hash" ]
  then
    echo 'Hashes match!'
    pass "===== Test $counter passed ====="
  else
    echo 'Hashes differ!'
    error "===== Test $counter failed ====="
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

pass(){
    # colored green test-pass information
    str=$@
    echo -e "\e[0;32m${str}\e[0m" >&2
}

clobber() {
  if [ -f $1 ]
  then
    rm $1
    info "Cleaned the file."
  else
    info "Nothing to clean, mving on."
  fi
}

process(){
  echo "Reading partials info line by line from $INPUT ..."
  counter=1
  while read from_url to_url from_hash to_hash channel version partial_path partial_hash
  do
    clobber $partial_path;
    echo -e "Requesting from funsize the partial between \n=> $from_url\n=> $to_url"
    cmd="$CLIENT_RUNNER --server-url $SERVER_URL --from-url $from_url --to-url $to_url --from-hash $from_hash --to-hash $to_hash --channel $channel --version $version --output $partial_path"

    $cmd

    if [ $? -eq 0 ]
    then
      echo "Partial successfully retrieved at "$partial_path
      compare_hash $partial_path $partial_hash $counter;
    else
      echo "Partial unavailable"
      exit 1;
    fi
    counter=$((counter+1))
  done < "$INPUT"
}

if [ $# -lt 1 ]
then
  usage;
  exit 0;
fi

process;
