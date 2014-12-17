#!/bin/bash
# Author: Anhad Jai Singh

export CELERY_BROKER="amqp://guest@localhost//"
set -e
set -x


script_dir=$(dirname $0)

TRAVIS=false
MD5_OSX='b6d74f5283420d83f788711bdd6722d1' # New hash with channelID and product Version
MD5_LINUX='9da1d36ebcb6473b2cf260f37ddd60e7' # New hash with channelID and product Version
FF28_FF29_PARTIAL_MD5=$MD5_OSX #Default to OSX because that's the dev machine.
tmp_file=$(mktemp)


while getopts "t" opt
do
  case $opt in

    t)
      TRAVIS=true
      FF28_FF29_PARTIAL_MD5=$MD5_LINUX
      ;;
  esac
done

if $TRAVIS
then
  cp $script_dir/../funsize/configs/test.ini $script_dir/../funsize/configs/worker.ini
  cp $script_dir/../funsize/configs/test.ini $script_dir/../funsize/configs/default.ini
fi

echo "Lanching celery"
celery worker --loglevel=INFO -A funsize.backend.tasks &
celery_pid=$!
sleep 5 # Wait for celery to launch

echo "Lanching Flask"
python $script_dir/../funsize/frontend/api.py &
flask_pid=$!
sleep 5 # wait for python and celery to get started.

function cleanup {
    rm -f $tmp_file
    kill $flask_pid || :
    kill $celery_pid || :
}

trap cleanup EXIT

ps --pid $celery_pid || exit 2
ps --pid $flask_pid || exit 3

echo "Starting tests"
bash $script_dir/curl-test.sh trigger-release
echo "Crossed the curl-test call"
start_time=$(date +%s)
sleep 5
echo "Hum drum"
echo $PWD
#bash curl-test.sh get-release
req=0
while true
do
  #POLL=$( bash curl-test.sh -i get-release | head -1 | awk '{print $2}')
  POLL=$( bash $script_dir/curl-test.sh -i get-release | awk '{print $2}' | head -1 )
  req=$(($req + 1))
  if [[ $POLL -eq 200 ]]
  then
    echo "Why the hell does the pipe break"
    break
  fi
  # Timeout within 600 seconds
  if [ $(expr $(date +%s) - $start_time) -gt 600 ]
  then
    break
  fi
  echo "REQUEST #:$req"
  sleep 5
done

# Essentially doing the following, but using files incase we need to confirm headers
#GENERATED_HASH=$(bash $script_dir/curl-test.sh get-release | md5sum | cut -d ' ' -f 1)
bash $script_dir/curl-test.sh get-release > $tmp_file
GENERATED_HASH=$(md5sum $tmp_file | cut -d ' ' -f 1)
echo "Gen Hash: $GENERATED_HASH"
if [ $GENERATED_HASH == $FF28_FF29_PARTIAL_MD5 ]
then
  echo "TEST PASSED, W00t"
else
  echo "Test failed :("
  echo "Expected hash: $FF28_FF29_PARTIAL_MD5"
  exit 1
fi
