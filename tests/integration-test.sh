#!/bin/bash
# Author: Anhad Jai Singh

set -e
set -x

script_dir=$(dirname $0)
EXPECTED_MD5='83bb6318c4e12b842ceeb2eee4e247f1'
tmp_file=$(mktemp)

function cleanup {
    rm -f $tmp_file
}

trap cleanup EXIT

echo "Starting tests"
$script_dir/curl-test.sh trigger-release
start_time=$(date +%s)
req=0
while true
do
  # TODO: check what does HEAD actually do in Flask
  # TODO: use python to test things, no curl!
  POLL=$($script_dir/curl-test.sh get-release -I | awk '{print $2}' | head -1 )
  req=$(($req + 1))
  if [ "$POLL" = "200" ]; then
    break
  fi
  # Timeout within 600 seconds
  if [ $(expr $(date +%s) - $start_time) -gt 600 ]; then
    break
  fi
  echo "REQUEST #:$req"
  sleep 30
done

$script_dir/curl-test.sh get-release -o $tmp_file
GENERATED_MD5=$(md5sum $tmp_file | cut -d ' ' -f 1)
echo "Gen Hash: $GENERATED_MD5"
if [ "$GENERATED_MD5" = "$EXPECTED_MD5" ]; then
  echo "TEST PASSED, W00t"
else
  echo "Test failed :("
  echo "Expected hash: $EXPECTED_MD5, got $GENERATED_MD5"
  exit 1
fi
