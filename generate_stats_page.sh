#!/bin/sh

page_location="/usr/home/spaine/public_html/voltageLog"
page_name="home_voltage.html"

date=`date`

sqlite="/usr/local/bin/sqlite3 -init /usr/home/spaine/.sqliterc"

cd /usr/home/spaine/powerLogger

# Make voltage graph
/usr/local/bin/gnuplot graph_voltage.p 2>/dev/null
# Set it up for web access
/bin/chmod 755 home_voltage.png
/usr/sbin/chown spaine:www home_voltage.png
# Move it to web folder
/bin/mv home_voltage.png ${page_location}/home_voltage.png

# Make average voltage graph
/usr/local/bin/gnuplot graph_average_voltage.p 2>/dev/null
# Set it up for web access
/bin/chmod 755 home_voltage_average.png
/usr/sbin/chown spaine:www home_voltage_average.png
# Move it to web folder
/bin/mv home_voltage_average.png ${page_location}/home_voltage_average.png

# Find maximum voltage from file
#MaxVoltage=`cut -f 1,6 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n -r +2 | head -n 1`
MaxVoltage=`${sqlite} datalog.db 'SELECT timestamp, max(maxVoltage) FROM voltageLog' 2>/dev/null | tail -n 1 | tr '|' ' '`
# Find minimum voltage from file
#MinVoltage=`cut -f 1,7 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n +2 | head -n 1`
MinVoltage=`${sqlite} datalog.db 'SELECT timestamp, min(minVoltage) FROM voltageLog' 2>/dev/null | tail -n 1 | tr '|' ' '`
# Find Maximum amperage from file
#MaxAmperage=`cut -f 1,8 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n -r +2 | head -n 1`
MaxAmperage=`${sqlite} datalog.db 'SELECT timestamp, max(maxAmperage) FROM voltageLog' 2>/dev/null | tail -n 1 | tr '|' ' '`
# Find Minimum amperage from file
#MinAmperage=`cut -f 1,9 datalog.dat | awk '{ if (($3!="")) {print($1" "$2"    "$3)} }' | sort -t' ' -n +2 | head -n 1`
MinAmperage=`${sqlite} datalog.db 'SELECT timestamp, min(minAmperage) FROM voltageLog' 2>/dev/null | tail -n 1 | tr '|' ' '`

#echo "MaxVoltage=${MaxVoltage}"
#echo "MinVoltage=${MinVoltage}"
#echo "MaxAmperage=${MaxAmperage}"
#echo "MinAmperage=${MinAmperage}"

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
				<img src="home_voltage_april_2012.png"></img><br>
				<img src="home_voltage_may_2012.png"></img><br>
				<img src="home_voltage_june_2012.png"></img><br>
				<img src="home_voltage_average_june_2012.png"></img><br>
			</p>
		</div>
	</body>
</html>
EOF

