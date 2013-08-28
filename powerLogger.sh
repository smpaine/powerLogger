#!/bin/sh

script_dir=$(dirname "$0")

cd ${script_dir}
#./wattcher.py -d 2>&1 > /dev/null &
./wattcher.py -d 1>/dev/null 2>wattcher_error_log.txt &
#./external_vfd.sh &

