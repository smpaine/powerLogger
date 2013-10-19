#!/bin/sh

for pid in `ps ax | fgrep "wattcher.py" | cut -d' ' -f1`; do
	echo "Killing PID ${pid}";
	kill ${pid};
done;

