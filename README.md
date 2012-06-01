--powerLogger
Modified version of Tweet-a-Watt (adafruit.com) python software.

Removed twitter part (not needed), and added curses console output,
which creates a nice, useful, readible terminal output of incoming
and averaged data (Voltage, Amperage, and Wattage).

Also contains sh scripts to run gnuplot to make nice png graphs, and
to create a basic HTML page of the graphs and current statistics (add
to cron job to re-create as often as wanted).

