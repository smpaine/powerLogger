powerLogger
====

powerLogger
----
powerLogger is a (heavily) modified version of the Tweet-a-Watt
(adafruit.com) python software.

Major differences:
----
-Twitter part removed
-Added curses console output, which creates a nice, useful,
 readible terminal output of incoming and averaged data
(Voltage, Amperage, and Wattage).
-Added ability to log to either/both flatfile and sqlite db.
-Created gnuplot graph generation scripts.
-Created bash script to generate a stats page (put in cron job).

