#!/usr/bin/env bash

# Takes in a CSV file of the format:
# src_url, dst_url, src_hash, dst_hash, channel_id, product_version

trigger() {
  line=$1
  IFS=',' read -a params <<< "$line"
  cmd="../../Docker/docker-curl-test.sh trigger-release ${params[@]}"
  echo -e "Executing:\n$cmd"
  $cmd
  #../curl-test.sh trigger-release ${params[@]}
}

if [ $# -gt 0 ]; then
  while read l
  do
    trigger $l
  done < $1
else
  while read l
  do
    trigger $l
  done
fi


