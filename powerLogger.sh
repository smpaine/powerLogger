#!/bin/sh

script_dir=$(dirname "$0")

cd ${script_dir}
./wattcher.py -d 2>&1 > /dev/null &
./external_vfd.sh &

