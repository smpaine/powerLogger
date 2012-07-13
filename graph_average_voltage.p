# Gnuplot script file to plot datalog.dat
set title "Average Home Voltage over Time"
#set timefmt "%Y/%m/%d %H:%M:%S"
set timefmt "%m/%d/%Y"
set xdata time
set xlabel "Date" offset character 0,-3
set ylabel "Voltage (Volts AC)"
set autoscale
set xtics in nomirror offset character 0,-5 rotate by 90
#set xtics border out offset character 0,-10 rotate by 90 format "%m/%d/%Y %H:%M:%S"
#set xtic auto
#set ytic auto
#set yr [0:160]
#set format x "%m/%d/%Y %H:%M:%S"
set format x "%m/%d/%Y"
set terminal png
set output "home_voltage_average.png"
unset key
set key on outside bottom center title "Key"
show key
#plot "datalog.dat" using 1:4
#plot "datalog.dat" using 1:4:xticlabels(1) title column(3)
unset key
set key on outside bottom center title "Key"
show key
set datafile separator "|"
plot "< /usr/local/bin/sqlite3 datalog.db \"SELECT strftime('%m/%d/%Y',timestamp) AS 'Date', avgVoltage AS 'Average Voltage' FROM voltageLog\" | tail -n+3" using 1:2:xticlabels(1) title column(2)
