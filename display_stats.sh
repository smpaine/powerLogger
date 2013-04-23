#!/bin/sh
INTERVAL=1
INTERVAL1=1
INTERVAL2=0
INTERVAL3=20
INTERVAL4=40
counter=0
# Octal characters!
# Brightness 0=100%, 1=75%, 2=50%, 3=25%
# 033=27
setBright100='\033\004\n'
setBright75='\033\001\n'
setBright50='\033\002\n'
setBright25='\033\003\n'
# 034=28
clear='\034\n'
# 035=29
# 036=30*10 = 300 ms scrolling speed
# 022=18
#speed='\035\022\n'
speed='\035\017\n'
# 036=30
top='\036\n'
# 037=31
bot='\037\n'

#sqlite="/usr/local/bin/sqlite3 -init /usr/home/spaine/.sqliterc"
sqlite="/usr/bin/sqlite3 -init /Users/spaine/.sqliterc"

sleep ${INTERVAL}
printf ${speed}
printf ${setBright100}
sleep ${INTERVAL}
printf ${setBright75}
sleep ${INTERVAL}
printf ${setBright50}
sleep ${INTERVAL}
printf ${setBright25}
printf ${clear}
while [ true ]
do
	printf ${top}
	date "+%m/%d/%Y %H:%M:%S"

	if [ ${counter} = ${INTERVAL2} ];
	then
		printf ${clear}
		#printf ${setBright25}
		printf ${top}
		date "+%m/%d/%Y %H:%M:%S"
		printf ${bot}
		#echo "   "
		# FreeeBSD
		#uptime | cut -d ' ' -f 4-9-
		# Mac OS
		#uptime | cut -d ' ' -f 3-
		uptime | cut -d ' ' -f 4-7 | cut -d ',' -f 1-2
	elif [ ${counter} = ${INTERVAL3} ];
	then
		printf ${clear}
		#printf ${setBright25}
		printf ${bot}
		#echo -n "  "
		#/usr/games/fortune -s fortunes murphy startrek zippy
		echo "Voltage at "
		${sqlite} datalog.db "SELECT max(id), strftime('%m/%d/%Y %H:%M:%S', timestamp), avgVoltage FROM voltageLog" 2>/dev/null | tail -n 1 | cut -d '|' -f 2- | tr '|' ' '
		printf ${top}
		date "+%m/%d/%Y %H:%M:%S"
	fi

	if [ ${counter} = ${INTERVAL4} ];
	then
		counter=0
	else
		counter=`expr $counter + 1`
	fi
	sleep ${INTERVAL1}
done
printf ${clear}
