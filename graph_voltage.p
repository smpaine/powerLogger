# Gnuplot script file to plot datalog.dat
set title "Home Voltage over Time"
#set timefmt "%Y/%m/%d %H:%M:%S"
set timefmt "%m/%d/%Y"
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
set output "home_voltage.png"
unset key
set key on outside bottom center title "Key"
show key
set datafile separator "|"
plot "< /Users/spaine/bin/sqlite3 -init /Users/spaine/.sqliterc datalog.db \"SELECT strftime('%m/%d/%Y',timestamp) AS 'Date', maxVoltage AS 'Maximum Voltage' FROM voltageLog\ WHERE strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now', 'localtime')\" 2>/dev/null | sed '/^$/d' | tail -n+2" using 1:2:xticlabels(1) title column(2) , "< /Users/spaine/bin/sqlite3 -init /Users/spaine/.sqliterc datalog.db \"SELECT strftime('%m/%d/%Y',timestamp) AS 'Date', minVoltage AS 'Minimum Voltage' FROM voltageLog WHERE strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now', 'localtime')\" 2>/dev/null | sed '/^$/d' | tail -n+2" using 1:2:xticlabels(1) title column(2)
