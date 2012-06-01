#!/bin/sh

cd /usr/home/spaine/powerLogger
/usr/local/bin/gnuplot graph_voltage.p # 2>/dev/null
/bin/chmod 755 home_voltage.png
/usr/sbin/chown spaine:www home_voltage.png
/bin/mv home_voltage.png /usr/home/spaine/public_html/home_voltage.png

