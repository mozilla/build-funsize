#!/usr/bin/env bash

# Takes in a CSV file of the format:
# src_url, dst_url, src_hash, dst_hash, channel_id, product_version

while read line
do
  IFS=',' read -a params <<< "$line"
  cmd="../curl-test.sh trigger-release ${params[@]}"
  echo -e "Executing:\n$cmd"
  $cmd
  #../curl-test.sh trigger-release ${params[@]}
done < $1
