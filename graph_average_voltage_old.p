# Gnuplot script file to plot 2012_july.dat
set title "Average Home Voltage over Time (July 2012)"
#set timefmt "%Y/%m/%d %H:%M:%S"
set timefmt "%Y/%m/%d"
set xdata time
set xlabel "Date" offset character 0,-3
set ylabel "Voltage (Volts AC)"
set autoscale
set xtics in nomirror offset character 0,-5 rotate by 90
#set xtics border out offset character 0,-10 rotate by 90 format "%Y/%m/%d %H:%M:%S"
#set xtic auto
#set ytic auto
#set yr [0:160]
#set format x "%Y/%m/%d %H:%M:%S"
set format x "%Y/%m/%d"
set terminal png
set output "home_voltage_average_july_2012.png"
#unset key
#set key on outside bottom center title "Key"
#show key
#plot "2012_july.dat" using 1:4
#plot "2012_july.dat" using 1:4:xticlabels(1) title column(3)
unset key
set key on outside bottom center title "Key"
show key
#plot "2012_july.dat" using 1:4:xticlabels(1) title column(3)
set datafile separator "|"
plot "< /usr/local/bin/sqlite3 -init /usr/home/spaine/.sqliterc datalog.db \"SELECT strftime('%m/%d/%Y',timestamp) AS 'Date', avgVoltage AS 'Average Voltage' FROM voltageLog WHERE timestamp >='2012-07-01 00:00:00' AND timestamp < '2012-08-01 00:00:00'\" 2>/dev/null | sed '/^$/d' | tail -n+2" using 1:2:xticlabels(1) title column(2)
