#!/bin/sh
script_location="/Users/spaine/powerLogger"
#script_location="/usr/home/spaine/powerLogger"
#page_location="/usr/home/spaine/public_html/voltageLog"
page_location="/Users/spaine/public_html/voltageLog/previousMonths/"

if [ "$#" =  2 ]; then
	year=${1}
	month=${2}
	date="${1}-${2}"
else
	#echo "Usage: ./generate_stats_page_previous_month.sh YYYY MM"
	#exit 1
	year=`date -v-1m "+%Y"`
	month=`date -v-1m "+%m"`
	date="${year}-${month}"
	echo "Using date ${date}"
fi

case ${month} in
	01 )
		month_name="January"
		;;
	02 )
		month_name="February"
		;;
	03 )
		month_name="March"
		;;
	04 )
		month_name="April"
		;;
	05 )
		month_name="May"
		;;
	06 )
		month_name="June"
		;;
	07 )
		month_name="July"
		;;
	08 )
		month_name="August"
		;;
	09 )
		month_name="September"
		;;
	10 )
		month_name="October"
		;;
	11 )
		month_name="November"
		;;
	12 )
		month_name="December"
		;;
	* )
		echo "Unknown month #, ${month}."
		exit 2
		;;
esac

month_name_lower=`echo $month_name | tr '[A-Z]' '[a-z]'`
page_name="home_voltage_${month_name_lower}_${year}.html"

graph1="home_voltage_${month_name_lower}_${year}.png"
graph2="home_voltage_average_${month_name_lower}_${year}.png"

echo "Making previous month stats page for ${month_name}, ${year}."

#sqlite="/usr/local/bin/sqlite3 -init /usr/home/spaine/.sqliterc"
sqlite="/Users/spaine/bin/sqlite3 -init /Users/spaine/.sqliterc"

gnuplot="/usr/local/bin/gnuplot"

cd ${script_location}

# Make voltage graph
${gnuplot} << EOF
set title "Home Voltage over Time (${month_name} ${year})"
set timefmt "%Y/%m/%d"
set xdata time
set xlabel "Date" offset character 0,-3
set ylabel "Voltage (Volts AC)"
set autoscale
set xtics in nomirror offset character 0,-5 rotate by 90
set format x "%Y/%m/%d"
set terminal png
set output "${graph1}"
unset key
set key on outside bottom center title "Key"
show key
set datafile separator "|"
plot "< /Users/spaine/bin/sqlite3 -init /Users/spaine/.sqliterc datalog.db \"SELECT strftime('%m/%d/%Y',timestamp) AS 'Date', maxVoltage AS 'Maximum Voltage' FROM voltageLog WHERE timestamp >= '${year}-${month}-01 00:00:00' AND timestamp < date('${year}-${month}-01 00:00:00','+1 MONTH')\" 2>/dev/null | sed '/^$/d' | tail -n+2" using 1:2:xticlabels(1) title column(2) , "< /Users/spaine/bin/sqlite3 -init /Users/spaine/.sqliterc datalog.db \"SELECT strftime('%m/%d/%Y',timestamp) AS 'Date', minVoltage AS 'Minimum Voltage' FROM voltageLog WHERE timestamp >= '${year}-${month}-01 00:00:00' AND timestamp < date('${year}-${month}-01 00:00:00','+1 MONTH')\" 2>/dev/null | sed '/^$/d' | tail -n+2" using 1:2:xticlabels(1) title column(2)
EOF
# Set it up for web access
chmod 755 ${graph1}
#chown spaine:www ${graph1}
# Move it to web folder
mv ${graph1} ${page_location}/

# Make average voltage graph
${gnuplot} << EOF
set title "Average Home Voltage over Time (${month_name} ${year})"
set timefmt "%Y/%m/%d"
set xdata time
set xlabel "Date" offset character 0,-3
set ylabel "Voltage (Volts AC)"
set autoscale
set xtics in nomirror offset character 0,-5 rotate by 90
set format x "%Y/%m/%d"
set terminal png
set output "${graph2}"
unset key
set key on outside bottom center title "Key"
show key
set datafile separator "|"
plot "< /Users/spaine/bin/sqlite3 -init /Users/spaine/.sqliterc datalog.db \"SELECT strftime('%m/%d/%Y',timestamp) AS 'Date', avgVoltage AS 'Average Voltage' FROM voltageLog WHERE timestamp >= '${year}-${month}-01 00:00:00' AND timestamp < date('${year}-${month}-01 00:00:00','+1 MONTH')\" 2>/dev/null | sed '/^$/d' | tail -n+2" using 1:2:xticlabels(1) title column(2)
EOF
# Set it up for web access
chmod 755 ${graph2}
#chown spaine:www ${graph2}
# Move it to web folder
mv ${graph2} ${page_location}/

# Find maximum voltage from file
#MaxVoltage=`cut -f 1,6 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n -r +2 | head -n 1`
MaxVoltage=`${sqlite} datalog.db 'SELECT timestamp, max(maxVoltage) FROM voltageLog WHERE strftime("%Y-%m", timestamp) = "'${date}'"' 2>/dev/null | tail -n 1 | tr '|' ' '`
# Find minimum voltage from file
#MinVoltage=`cut -f 1,7 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n +2 | head -n 1`
MinVoltage=`${sqlite} datalog.db 'SELECT timestamp, min(minVoltage) FROM voltageLog WHERE strftime("%Y-%m", timestamp) = "'${date}'"' 2>/dev/null | tail -n 1 | tr '|' ' '`
# Find Maximum amperage from file
#MaxAmperage=`cut -f 1,8 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n -r +2 | head -n 1`
MaxAmperage=`${sqlite} datalog.db 'SELECT timestamp, max(maxAmperage) FROM voltageLog WHERE strftime("%Y-%m", timestamp) = "'${date}'"' 2>/dev/null | tail -n 1 | tr '|' ' '`
# Find Minimum amperage from file
#MinAmperage=`cut -f 1,9 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n +2 | head -n 1`
MinAmperage=`${sqlite} datalog.db 'SELECT timestamp, min(minAmperage) FROM voltageLog WHERE strftime("%Y-%m", timestamp) = "'${date}'"' 2>/dev/null | tail -n 1 | tr '|' ' '`

echo "MaxVoltage=${MaxVoltage}"
echo "MinVoltage=${MinVoltage}"
echo "MaxAmperage=${MaxAmperage}"
echo "MinAmperage=${MinAmperage}"
echo "page_location=${page_location}"
echo "page_name=${page_name}"

cat > ${page_location}/${page_name} <<EOF
<html>
	<head><title>Home Voltage Statistics</title></head>
	<body>
		<div align="center">
			<h2>Home Voltage Statistical Information</h2>
			<h4>For ${month_name} ${year}</h4>
			<img src="${graph1}" alt="home voltage graph"></img>
			<img src="${graph2}" alt="average home voltage graph"></img>
			<br><br>
			<table width="500" border="1" cellpadding="10">
				<tr>
					<td align="right">Maximum Voltage</td>
					<td align="left">${MaxVoltage}</td>
				</tr>
				<tr>
					<td align="right">Minimum Voltage</td>
					<td align="left">${MinVoltage}</td>
				</tr>
				<tr>
					<td align="right">Maximum Amperage</td>
					<td align="left">${MaxAmperage}</td>
				</tr>
				<tr>
					<td align="right">Minimum Amperage</td>
					<td align="left">${MinAmperage}</td>
				</tr>
				<br><br>
				<a href="../home_voltage.html">Back</a>
			</table>
		</div>
	</body>
</html>
EOF

