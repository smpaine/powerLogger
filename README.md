powerLogger
====

powerLogger
----
powerLogger is a (heavily) modified version of the Tweet-a-Watt
(adafruit.com) python software.

Major differences:
----
1. Twitter part removed
2.-Added curses console output, which creates a nice, useful,
 readible terminal output of incoming and averaged data
(Voltage, Amperage, and Wattage).
3. Added ability to log to either/both flatfile and sqlite db.
4. Created gnuplot graph generation scripts.
5. Created bash script to generate a stats page (put in cron job).

