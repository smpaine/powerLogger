#!/usr/bin/env python
import signal, sys, serial, time, datetime, sys, curses
from xbee import xbee

DEBUG = True

SERIALPORT = "/dev/ttyU0"	# the com/serial port the XBee is connected to
BAUDRATE = 9600				# the baud rate we talk to the xbee
CURRENTSENSE = 4			# which XBee ADC has current draw data
VOLTSENSE = 0				# which XBee ADC has mains voltage data
MAINSVPP = 183 * 2			# +-170V is what 120 Vrms ends up being (= (120*2)/sqrt(2))
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
counter = 0

# open up the FTDI serial port to get data transmitted to xbee
ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.open()

# the 'main loop' runs once a second or so
def update_log():
	global maxVolts, minVolts, maxAmps, minAmps, maxWatts, minWatts, DEBUG, height, width, counter

	# grab one packet from the xbee, or timeout
	packet = xbee.find_packet(ser)
	if not packet:
		return        # we timedout

	xb = xbee(packet)             # parse the packet
	#print xb.address_16
	#if DEBUG:       # for debugging sometimes we only want one
		#print xb

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

	#if DEBUG:
		#print "ampdata: "+str(ampdata)
	print "voltdata: "+str(voltagedata)
	# get max and min voltage and normalize the curve to '0'
	# to make the graph 'AC coupled' / signed
	max_v=max(voltagedata)
	min_v=min(voltagedata)

	# figure out the 'average' of the max and min readings
	avgv = (max_v + min_v) / 2
	# also calculate the peak to peak measurements
	vpp =  max_v-min_v

	for i in range(len(voltagedata)):
		#remove 'dc bias', which we call the average read
		voltagedata[i] -= avgv
		# We know that the mains voltage is 120Vrms = +-170Vpp
		voltagedata[i] = (voltagedata[i] * MAINSVPP) / vpp

	if DEBUG:
		print "min_v="+str(min_v)
		print "max_v="+str(max_v)
		print "avgv="+str(avgv)
		print "vpp="+str(vpp)
		print "voltdata: "+str(voltagedata)

	# normalize current readings to amperes
	for i in range(len(ampdata)):
		# VREF is the hardcoded 'DC bias' value, its
		# about 492 but would be nice if we could somehow
		# get this data once in a while maybe using xbeeAPI
		#if vrefcalibration[xb.address_16]:
		#	ampdata[i] -= vrefcalibration[xb.address_16]
		#else:
		#	ampdata[i] -= vrefcalibration[0]
		ampdata[i] -= avgv
		# the CURRENTNORM is our normalizing constant
		# that converts the ADC reading to Amperes
		ampdata[i] /= CURRENTNORM

	# calculate instant. watts, by multiplying V*I for each sample point
	wattdata = [0] * len(voltagedata)
	for i in range(len(wattdata)):
		wattdata[i] = voltagedata[i] * ampdata[i]

	avgvolts = 0
	#for i in range(len(voltagedata)):
	for i in range(cycleLength):
		avgvolts += abs(voltagedata[i])
	#avgvolts /= float(len(voltagedata))
	avgvolts /= float(cycleLength)

	avgamps = 0
	#for i in range(len(ampdata)):
	for i in range(cycleLength):
		avgamps += abs(ampdata[i])
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
	counter+=1

def on_exit():
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

