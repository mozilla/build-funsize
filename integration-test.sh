#!/bin/bash
# Author: Anhad Jai Singh

req=0

TRAVIS=false

cleanup() {
    killall python2.7
    killall python
}

while getopts "t" opt
do
    case $opt in

        t)
            TRAVIS=true
            ;;
    esac
done

if $TRAVIS
then
    mv configs/test.ini configs/celery.ini
    mv configs/test.ini configs/default.ini
fi

cleanup

celery -A tasks worker &
celery_pid=$!
python api.py &
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
    POLL=$( bash curl-test.sh -i get-release | awk '{print $2}'| head -1 )
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

echo "JUS BEFO"
bash curl-test.sh -i get-release | md5sum
echo "JUS AFTA"

echo "WHAAAAAAAAAAAA"
#cleanup
