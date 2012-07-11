# Gnuplot script file to plot 2012_june.dat
set title "Average Home Voltage over Time (June 2012)"
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
set output "home_voltage_average_june_2012.png"
#unset key
#set key on outside bottom center title "Key"
#show key
#plot "2012_june.dat" using 1:4
#plot "2012_june.dat" using 1:4:xticlabels(1) title column(3)
unset key
set key on outside bottom center title "Key"
show key
plot "2012_june.dat" using 1:4:xticlabels(1) title column(3)
