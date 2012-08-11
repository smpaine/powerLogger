#!/usr/bin/env python
import signal, sys, serial, time, datetime, sys, curses
from xbee import xbee
from backend_storage import open_log, write_changes, flush_log, close_log

DEBUG = False

if (sys.argv and len(sys.argv) > 1):
	if sys.argv[1] == "-d":
		DEBUG = True

SERIALPORT = "/dev/ttyU0"	# the com/serial port the XBee is connected to
BAUDRATE = 9600				# the baud rate we talk to the xbee
CURRENTSENSE = 4			# which XBee ADC has current draw data
VOLTSENSE = 0				# which XBee ADC has mains voltage data
MAINSVPP = 180 * 2			# +-170V is what 120 Vrms ends up being (= (120*2)/sqrt(2))
# Except, it's wrong; so used ~127 Vrms to get voltage reading parity between kill a watt and sensor readings.
vrefcalibration = [492,	# Calibration for sensor #0
		498,		# Calibration for sensor #1
		489,		# Calibration for sensor #2
		492,		# Calibration for sensor #3
		501,		# Calibration for sensor #4
		493]		# etc... approx ((2.4v * (10Ko/14.7Ko)) / 3
CURRENTNORM = 15.5	# conversion to amperes from ADC
cycleLength = 18
maxVolts = 0.0
minVolts = 150.0
maxAmps = 0.0
minAmps = 15.5
maxWatts = 0.0
minWatts = 2015.0
longAvgVolts = 0.0
longAvgAmps = 0.0
longAvgWatts = 0.0
longMaxVolts = 0.0
longMinVolts = 150.0
longMaxAmps = 0.0
longMinAmps = 15.5
counter = 0
xb = set()

if not DEBUG:
	# Setup curses for output to screen
	scr = curses.initscr()
	curses.cbreak()
	curses.noecho()
	scr.keypad(1)
	height,width=scr.getmaxyx()
	height-=0
	width-=1

# open up the FTDI serial port to get data transmitted to xbee
ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.open()

# open our datalogging file
# open database/log file
backends=open_log()
logfile='yes'

def write_to_log():
	#global backends, maxVolts, minVolts, maxAmps, minAmps, maxWatts, minWatts, DEBUG, height, width, counter, longAvgVolts, longAvgAmps, longAvgWatts, longMaxVolts, longMinVolts, longMaxAmps, longMinAmps, xb
	global backends, DEBUG, counter, longAvgVolts, longAvgAmps, longAvgWatts, longMaxVolts, longMinVolts, longMaxAmps, longMinAmps, xb
	temp=write_changes(backends, counter, longAvgVolts, longAvgAmps, longAvgWatts, longMaxVolts, longMinVolts, longMaxAmps, longMinAmps, xb)
	
	counter=0
	longAvgVolts = 0.0
	longAvgAmps = 0.0
	longAvgWatts = 0.0
	longMaxVolts = 0.0
	longMinVolts = 150.0
	longMaxAmps = 0.0
	longMinAmps = 15.5
	
	if DEBUG:
		print temp
		print "\tLog file flushed."
	else:
		scr.addstr(1,42,"Log file flushed.")

# the 'main loop' runs once a second or so
def update_log():
	global maxVolts, minVolts, maxAmps, minAmps, maxWatts, minWatts, DEBUG, height, width, counter, longAvgVolts, longAvgAmps, longAvgWatts, longMaxVolts, longMinVolts, longMaxAmps, longMinAmps, xb

	# grab one packet from the xbee, or timeout
	packet = xbee.find_packet(ser)
	if not packet:
		return        # we timedout

	xb = xbee(packet)             # parse the packet
	#print xb.address_16
	if DEBUG:       # for debugging sometimes we only want one
		print xb

	# we'll only store n-1 samples since the first one is usually messed up
	#voltagedata = [-1] * (len(xb.analog_samples) - 1)
	#ampdata = [-1] * (len(xb.analog_samples ) -1)
	voltagedata = [-1] * (len(xb.analog_samples))
	ampdata = [-1] * (len(xb.analog_samples ))
	# grab 1 thru n of the ADC readings, referencing the ADC constants
	# and store them in nice little arrays
	for i in range(len(voltagedata)):
		voltagedata[i] = xb.analog_samples[i][VOLTSENSE]
		ampdata[i] = xb.analog_samples[i][CURRENTSENSE]

	# get max and min voltage and normalize the curve to '0'
	# to make the graph 'AC coupled' / signed
	min_v = 1024     # XBee ADC is 10 bits, so max value is 1023
	max_v = 0
	for i in range(len(voltagedata)):
		if (min_v > voltagedata[i]):
			min_v = voltagedata[i]
		if (max_v < voltagedata[i]):
			max_v = voltagedata[i]
	# figure out the 'average' of the max and min readings
	avgv = (max_v + min_v) / 2
	# also calculate the peak to peak measurements
	vpp =  max_v-min_v

	if DEBUG:
		print "min_v="+str(min_v)
		print "max_v="+str(max_v)
		print "avgv="+str(avgv)
		print "vpp="+str(vpp)

	for i in range(len(voltagedata)):
		#remove 'dc bias', which we call the average read
		voltagedata[i] -= avgv
		# We know that the mains voltage is 120Vrms = +-170Vpp
		voltagedata[i] = (voltagedata[i] * MAINSVPP) / vpp

	# normalize current readings to amperes
	for i in range(len(ampdata)):
		# VREF is the hardcoded 'DC bias' value, its
		# about 492 but would be nice if we could somehow
		# get this data once in a while maybe using xbeeAPI
		if vrefcalibration[xb.address_16]:
			ampdata[i] -= vrefcalibration[xb.address_16]
		else:
			ampdata[i] -= vrefcalibration[0]

		# the CURRENTNORM is our normalizing constant
		# that converts the ADC reading to Amperes
		ampdata[i] /= CURRENTNORM

		ampdata[i] = abs(ampdata[i])

	# calculate instant. watts, by multiplying V*I for each sample point
	wattdata = [0] * len(voltagedata)
	for i in range(len(wattdata)):
		wattdata[i] = voltagedata[i] * ampdata[i]

	if DEBUG:
		print "voltdata: "+str(voltagedata)
		print "ampdata: "+str(ampdata)
		print "wattdata: "+str(wattdata)

	avgvolts = 0
	#for i in range(len(voltagedata)):
	for i in range(cycleLength):
		avgvolts += abs(voltagedata[i])
	#avgvolts /= float(len(voltagedata))
	avgvolts /= float(cycleLength)

	avgamps = 0
	#for i in range(len(ampdata)):
	for i in range(cycleLength):
		#avgamps += abs(ampdata[i])
		avgamps += ampdata[i]
	#avgamps /= float(len(ampdata))
	avgamps /= float(cycleLength)

	avgwatts=avgvolts*avgamps

	avgwatts2 = 0
	#for i in range(len(wattdata)):
	for i in range(cycleLength):
		avgwatts2 += abs(wattdata[i])
	#avgwatts2 /= float(len(wattdata))
	avgwatts2 /= float(cycleLength)

	if avgvolts>maxVolts:
		maxVolts=avgvolts
	if avgvolts<minVolts:
		minVolts=avgvolts
	if avgamps>maxAmps:
		maxAmps=avgamps
	if avgamps<minAmps:
		minAmps=avgamps
	if avgwatts>maxWatts:
		maxWatts=avgwatts
	if avgwatts<minWatts:
		minWatts=avgwatts

	if avgvolts>longMaxVolts:
		longMaxVolts=avgvolts
	if avgvolts<longMinVolts:
		longMinVolts=avgvolts
	if avgamps>longMaxAmps:
		longMaxAmps=avgamps
	if avgamps<longMinAmps:
		longMinAmps=avgamps
	
	longAvgVolts+=avgvolts
	longAvgAmps+=avgamps
	longAvgWatts+=avgwatts
	
	# Print out our most recent measurements
	if DEBUG:
		print str(xb.address_16)
		print "\tAverage Voltage: "+str(avgvolts)
		print "\tAverage Amperage: "+str(avgamps)
		print "\tAverage Watt draw: "+str(avgwatts)
		print "\tAverage Watt instantaneous draw: "+str(avgwatts2)
		print "\tVolts Min: "+str(minVolts)
		print "\tVolts Max: "+str(maxVolts)
		print "\tAmps Min: "+str(minAmps)
		print "\tAmps Max: "+str(maxAmps)
		print "\tWatts Min: "+str(minWatts)
		print "\tWatts Max: "+str(maxWatts)
	else:
		scr.clear()
		# Draw pretty box frame for data
		for y in range(height):
			for x in range(width):
				if (x==0 or x==width-1):
					scr.addch(y,x,curses.ACS_VLINE)
				if (x==0):
					if (y==0):
						scr.addch(y,x,curses.ACS_ULCORNER)
					elif (y==height-1):
						scr.addch(y,x,curses.ACS_LLCORNER)
				elif (x==width):
					if (y==0):
						scr.addch(y,x,curses.ACS_URCORNER)
					elif (y==height-1):
						scr.addch(y,x,curses.ACS_LRCORNER)
				elif (y==0 or y==height-1):
					scr.addch(y,x,curses.ACS_HLINE)
		#scr.addstr(height-2,5,"height="+str(height)+", width="+str(width))
		# console is 25x79
		# Show data
		scr.addstr(1,5,"Log Data for Sensor "+str(xb.address_16))
		scr.addstr(2,5,time.strftime("%m/%d/%Y %H:%M:%S"))
		scr.addstr(4,10,"Average Voltage: "+str(avgvolts))
		scr.addstr(5,10,"Average Amperage: "+str(avgamps))
		scr.addstr(6,10,"Average Wattage: "+str(avgwatts))
		scr.addstr(7,10,"Average Instantaneous Wattage: "+str(avgwatts2))
		scr.addstr(9,10,"Volts Min: "+str(minVolts))
		scr.addstr(9,40,"Volts Max: "+str(maxVolts))
		scr.addstr(10,10,"Amps Min: "+str(minAmps))
		scr.addstr(10,40,"Amps Max: "+str(maxAmps))
		scr.addstr(11,10,"Watts Min: "+str(minWatts))
		scr.addstr(11,40,"Watts Max: "+str(maxWatts))

		# voltagedata, ampdata, wattdata
		# using 10 vertical lines for sinewave
		# 19 samples horizontal for each
		
		# Draw labels
		scr.addstr(height-1,9,"Voltage Graph")
		scr.addstr(height-1,32,"Amperage Graph")
		scr.addstr(height-1,57,"Wattage Graph")

		# Draw boxes for graphs
		for x in range(11):
			if (x==0):
				linetype1=curses.ACS_ULCORNER
				linetype2=curses.ACS_LLCORNER
			elif (x==11):
				linetype1=curses.ACS_URCORNER
				linetype2=curses.ACS_LRCORNER
			else:
				linetype1=curses.ACS_VLINE
				linetype2=curses.ACS_VLINE

			scr.addch(12+x,5,linetype1)
			scr.addch(12+x,25,linetype2)
			scr.addch(12+x,29,linetype1)
			scr.addch(12+x,49,linetype2)
			scr.addch(12+x,53,linetype1)
			scr.addch(12+x,73,linetype2)

		for x in range(19):
			if (x==cycleLength-1):
				linetype=curses.ACS_VLINE
			else:
				linetype=curses.ACS_HLINE
			scr.addch(12,6+x,linetype)
			scr.addch(23,6+x,linetype)
			scr.addch(12,30+x,linetype)
			scr.addch(23,30+x,linetype)
			scr.addch(12,54+x,linetype)
			scr.addch(23,54+x,linetype)


		for x in range(len(voltagedata)):
			y=voltagedata[x]
			if (y>148):
				scr.addstr(13,x+6,'*')
			elif (y>111):
				scr.addstr(14,x+6,'*')
			elif (y>74):
				scr.addstr(15,x+6,'*')
			elif (y>37):
				scr.addstr(16,x+6,'*')
			elif (y>0):
				scr.addstr(17,x+6,'*')
			elif (y>-37):
				scr.addstr(18,x+6,'*')
			elif (y>-74):
				scr.addstr(19,x+6,'*')
			elif (y>-111):
				scr.addstr(20,x+6,'*')
			elif (y>-148):
				scr.addstr(21,x+6,'*')
			else:
				scr.addstr(22,x+6,'*')

		for x in range(len(ampdata)):
			y=ampdata[x]
			if (y>13.5):
				scr.addstr(13,x+30,'*')
			elif (y>12):
				scr.addstr(14,x+30,'*')
			elif (y>10.5):
				scr.addstr(15,x+30,'*')
			elif (y>9):
				scr.addstr(16,x+30,'*')
			elif (y>7.5):
				scr.addstr(17,x+30,'*')
			elif (y>6):
				scr.addstr(18,x+30,'*')
			elif (y>4.5):
				scr.addstr(19,x+30,'*')
			elif (y>3):
				scr.addstr(20,x+30,'*')
			elif (y>1.5):
				scr.addstr(21,x+30,'*')
			else:
				scr.addstr(22,x+30,'*')

		for x in range(len(wattdata)):
			y=abs(wattdata[x])
			if (y>1687.5):
				scr.addstr(13,x+54,'*')
			elif (y>1500):
				scr.addstr(14,x+54,'*')
			elif (y>1312.5):
				scr.addstr(15,x+54,'*')
			elif (y>1125):
				scr.addstr(16,x+54,'*')
			elif (y>937.5):
				scr.addstr(17,x+54,'*')
			elif (y>750):
				scr.addstr(18,x+54,'*')
			elif (y>562.5):
				scr.addstr(19,x+54,'*')
			elif (y>375):
				scr.addstr(20,x+54,'*')
			elif (y>187.5):
				scr.addstr(21,x+54,'*')
			else:
				scr.addstr(22,x+54,'*')

	# Lets log it! Seek to the end of our log file
	if logfile:
		# save on disk writes (for ssd)
		if (counter>=60):
			write_to_log()
			if not DEBUG:
				scr.addstr(1,42,"Log file flushed.")
		else:
			if DEBUG:
				print "\tNext log file flush in "+str((60-counter)*2)+" seconds."
			else:
				scr.addstr(1,42,"Next log file flush in "+str((60-counter)*2)+" seconds")

	if not DEBUG:
		scr.refresh()
	counter+=1

def on_exit():
	if not DEBUG:
		scr.clear()
		scr.refresh()
		curses.nocbreak()
		scr.keypad(0)
		curses.echo()
		curses.endwin()
	print "Cleaning up before exiting..."
	if logfile:
		print "Writing data to log..."
		write_to_log()
		print "Flushing log to disk..."
		flush_log(backends)
		close_log(backends)
		print "Done."
	print "Exiting now."
	if DEBUG:
		raise
	sys.exit(0)

def signal_handler_term(sig, frame=None):
	on_exit();

signal.signal(signal.SIGTERM, signal_handler_term)

while True:
	try:
		update_log()
	except:
		on_exit()

