#!/bin/sh
script_location="/Users/spaine/powerLogger"
#script_location="/usr/home/spaine/powerLogger"
#page_location="/usr/home/spaine/public_html/voltageLog"
page_location="/Users/spaine/public_html/voltageLog"
page_name="home_voltage.html"
prevMonths="/Users/spaine/public_html/voltageLog/previousMonths"

date=`date`

#sqlite="/usr/local/bin/sqlite3 -init /usr/home/spaine/.sqliterc"
sqlite="/Users/spaine/bin/sqlite3 -init /Users/spaine/.sqliterc"

gnuplot="/usr/local/bin/gnuplot"

cd ${script_location}

# Make voltage graph
${gnuplot} graph_voltage.p 2>/dev/null
# Set it up for web access
chmod 755 home_voltage.png
#chown spaine:www home_voltage.png
# Move it to web folder
mv home_voltage.png ${page_location}/home_voltage.png

# Make average voltage graph
${gnuplot} graph_average_voltage.p 2>/dev/null
# Set it up for web access
chmod 755 home_voltage_average.png
#chown spaine:www home_voltage_average.png
# Move it to web folder
mv home_voltage_average.png ${page_location}/home_voltage_average.png

# Find maximum voltage from file
#MaxVoltage=`cut -f 1,6 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n -r +2 | head -n 1`
MaxVoltage=`${sqlite} datalog.db 'SELECT timestamp, max(maxVoltage) FROM voltageLog WHERE strftime("%Y-%m", timestamp) = strftime("%Y-%m", "now", "localtime")' 2>/dev/null | tail -n 1 | tr '|' ' '`
# Find minimum voltage from file
#MinVoltage=`cut -f 1,7 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n +2 | head -n 1`
MinVoltage=`${sqlite} datalog.db 'SELECT timestamp, min(minVoltage) FROM voltageLog WHERE strftime("%Y-%m", timestamp) = strftime("%Y-%m", "now", "localtime")' 2>/dev/null | tail -n 1 | tr '|' ' '`
# Find Maximum amperage from file
#MaxAmperage=`cut -f 1,8 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n -r +2 | head -n 1`
MaxAmperage=`${sqlite} datalog.db 'SELECT timestamp, max(maxAmperage) FROM voltageLog WHERE strftime("%Y-%m", timestamp) = strftime("%Y-%m", "now", "localtime")' 2>/dev/null | tail -n 1 | tr '|' ' '`
# Find Minimum amperage from file
#MinAmperage=`cut -f 1,9 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n +2 | head -n 1`
MinAmperage=`${sqlite} datalog.db 'SELECT timestamp, min(minAmperage) FROM voltageLog WHERE strftime("%Y-%m", timestamp) = strftime("%Y-%m", "now", "localtime")' 2>/dev/null | tail -n 1 | tr '|' ' '`

echo "MaxVoltage=${MaxVoltage}"
echo "MinVoltage=${MinVoltage}"
echo "MaxAmperage=${MaxAmperage}"
echo "MinAmperage=${MinAmperage}"

cat > ${page_location}/${page_name} <<EOF
<html>
	<head><title>Home Voltage Statistics</title></head>
	<body>
		<div align="center">
			<h2>Home Voltage Statistical Information</h2>
			<h4>Generated on ${date}</h4>
			<img src="home_voltage.png" alt="home voltage graph"></img>
			<img src="home_voltage_average.png" alt="average home voltage graph"></img>
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
			</table>
			<br>
			<p>
				<strong>Previous Month's Graphs</strong><br>
EOF

cd ${prevMonths}
for file in `ls -rt *.html`; do
	linkName=${file/home_voltage_/}
	linkName=${linkName/.html/}
	echo "<a href=\"previousMonths/${file}\">${linkName}</a><br>\n" >> ${page_location}/${page_name}
done

cat >> ${page_location}/${page_name} <<EOF
			</p>
		</div>
	</body>
</html>
EOF
