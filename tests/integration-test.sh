#!/bin/bash
# Author: Anhad Jai Singh

req=0

TRAVIS=false
MD5_OSX='7db10de649864c45d2da6559cf2ca766'
MD5_LINUX='97c403cc1d7375f2f1efee3731f85f4c'
FF28_FF29_PARTIAL_MD5=$MD5_OSX #Default to OSX because that's the dev machine.


cleanup() {
  killall python2.7
  killall python
}

killeverything(){
  killall -9 python
  killall -9 python2.7
}

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
  cp ../configs/test.ini ../configs/worker.ini
  cp ../configs/test.ini ../configs/default.ini
fi

cleanup

celery -A senbonzakura.backend.tasks worker &
celery_pid=$!
python ../frontend/api.py &
flask_pid=$!

sleep 2 # wait for python and celery to get started.

bash curl-test.sh trigger-release
start_time=$(date +%s)
sleep 5
echo "Hum drum"
echo $PWD
#bash curl-test.sh get-release
while true
do
  #POLL=$( bash curl-test.sh -i get-release | head -1 | awk '{print $2}')
  POLL=$( bash curl-test.sh -i get-release | awk '{print $2}' | head -1 )
  req=$(($req + 1))
  if [[ $POLL -eq 200 ]]
  then
    echo "Why the hell does the pipe break"
    break
  fi
  if [ $(expr $(date +%s) - $start_time) -gt 600 ]
  then
    break
  fi
  echo "REQUEST #:$req"
  sleep 1
done

echo "$(bash curl-test.sh get-release | md5sum | cut -d ' ' -f 1)"
if [ $(bash curl-test.sh get-release | md5sum | cut -d ' ' -f 1) == $FF28_FF29_PARTIAL_MD5 ]
then
  echo "TEST PASSED, W00t"
  cleanup
  exit 0 # imply success
else
  echo "Test failed :("
  cleanup
  killeverything
  exit 1
fi
