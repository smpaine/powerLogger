#!/usr/bin/env python
# backend_storage.py
#
# Backend storage abstraction layer
# Either store to a flat file or database
#
# Run this file directly to create/initialize database
#
# Written by Stephen Paine (smpaine@gmail.com) 7/10/2012
# Last update: 7/10/2012

import sqlite3, sys, getopt, time, datetime

# Variables defining data layout
#array[columns]
#array[datatypes]
# column
# datatype
columns = [
		"timestamp",
		"sensor",
		"avgAoltage",
		"avgAmperage",
		"avgWattage",
		"maxVoltage",
		"minVoltage",
		"maxAmperage",
		"minAmperage"
		]

columnTypes = [
		"TIMESTAMP",
		"INTEGER",
		"REAL",
		"REAL",
		"REAL",
		"REAL",
		"REAL",
		"REAL",
		"REAL"
		]
		
flatFileName="datalog.dat"
sqliteFileName="datalog.db"

# Default to flatfile unless initialized as one or the other
#backendType="flat"
backendType="sqlite"
#backendType="both"

logfile=0
if (backendType=="sqlite"): 
	sqlite=0
else:
	sqlite=1

def sqlite_connect():
	return sqlite3.connect(sqliteFileName)

def sqlite_disconnect(con):
	con.close()

def write_changes(backends, maxVolts, minVolts, maxAmps, minAmps, maxWatts, minWatts, counter, longAvgVolts, longAvgAmps, longAvgWatts, longMaxVolts, longMinVolts, longMaxAmps, longMinAmps, xb):
	global backendType
	longAvgVolts /= counter
	longAvgAmps /= counter
	longAvgWatts /= counter
	if (backendType=="flat" or backendType=="both"):
		print "Updating flatfile log:"
		backends[logfile].write(time.strftime("%Y/%m/%d %H:%M:%S")+"\t"+
				str(xb.address_16)+"\t"+
				str(longAvgVolts)+"\t"+
				str(longAvgAmps)+"\t"+
				str(longAvgWatts)+"\t"+
				str(longMaxVolts)+"\t"+
				str(longMinVolts)+"\t"+
				str(longMaxAmps)+"\t"+
				str(longMinAmps)+"\n")
	if (backendType=="sqlite" or backendType=="both"):
		print "Updating sqlite log:"
		c = backends[sqlite].cursor()
		queryString="INSERT INTO voltageLog (timestamp, sensor, avgVoltage, avgAmperage, avgWattage, maxVoltage, minVoltage, maxAmperage, minAmperage) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
	#	print "queryString="+queryString
		results=[ (time.strftime("%Y-%m-%d %H:%M:%S"), xb.address_16, longAvgVolts, longAvgAmps, longAvgWatts, longMaxVolts, longMinVolts, longMaxAmps, longMinAmps) ]
		c.executemany(queryString, results)

	flush_log(backends)
	temp="Wrote "+time.strftime("%Y/%m/%d %H:%M:%S")+"\t"+str(xb.address_16)+"\t"+str(longAvgVolts)+"\t"+str(longAvgAmps)+"\t"+str(longAvgWatts)+"\t"+str(longMaxVolts)+"\t"+str(longMinVolts)+"\t"+str(longMaxAmps)+"\t"+str(longMinAmps)+" to the log."
	return temp

def flush_log(backends):
	if (backendType=="flat" or backendType=="both"):
		backends[logfile].flush()
	if (backendType=="sqlite" or backendType=="both"):
		backends[sqlite].commit()

def open_log():
	global backendType
	backends=[]
	if (backendType=="flat" or backendType=="both"):
		try:
			myLog = open(flatFileName, 'r+')
			myLog.seek(0, 2) # 2 == SEEK_END. ie, go to the end of the file
		except IOError:
			print "Creating new flatfile."
			myLog = open(flatFileName, 'w+')
			myLog.write("Timestamp\tSensor\tVoltage\tAmperage\tWattage\tMaxVolts\tMinVolts\tMaxAmps\tMinAmps\n");
			flush_log(myLog)
			myLog.seek(0, 2) # 2 == SEEK_END. ie, go to the end of the file
		backends.append(myLog)
	if (backendType=="sqlite" or backendType=="both"):
		backends.append(sqlite_connect())
	return backends

def close_log(backends):
	global backendType
	flush_log(backends)
	if (backendType=="flat" or backendType=="both"):
		backends[logfile].close()
	if (backendType=="sqlite" or backendType=="both"):
		sqlite_disconnect(backends[sqlite])

def create_sqlite_file():
	try:
		logfile = open(sqliteFileName, 'r+')
		print "Sqlite database file already exists, quitting now."
	except IOError:
		print "Creating new sqlite database."
		sqlite_backend()
		con=sqlite_connect()
		c = con.cursor()
		columnString="id INTEGER PRIMARY KEY"
		for i in range(len(columns)):
			columnString=columnString+", "+columns[i]+" "+columnTypes[i]
		
		queryString = "CREATE TABLE voltageLog ("+columnString+")"
		print "queryString="+queryString
		c.execute(queryString)
		print "Table (possibly) created. Go check it out."
		sqlite_disconnect(con)

def create_flatfile():
	try:
		logfile = open(flatFileName, 'r+')
		print "Logfile already exists, quitting now."
	except IOError:
		print "Creating new flatfile."
		logfile = open(flatFileName, 'w+')
		logfile.write("Timestamp\tSensor\tVoltage\tAmperage\tWattage\tMaxVolts\tMinVolts\tMaxAmps\tMinAmps\n");
		logfile.flush()
		logfile.close()

def usage():
	print "Usage: ./backend_storage.py -f -s -h --flatfile --sqlite --help"
	print "\t-f,--flatfile\tcreate new, empty flatfile with header row"
	print "\t-s,--sqlite\tcreate new, empty sqlite database"
	print "\t-h,--help\tshow this help\n"

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "fsh", ["flatfile", "sqlite", "help"])
	except getopt.GetoptError:
		print str("Option not recognized.")
		usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-f", "--flatfile"):
			create_flatfile()
		elif o in ("-s", "--sqlite"):
			create_sqlite_file()
		elif o in ("-h", "--help"):
			print "Here is the help:"
			usage()
		else:
			assert False, "unhandled option"

if __name__ == "__main__":
	main()
