#!/usr/bin/env python
# backend_storage.py
#
# Backend storage abstraction layer
# Either store to a flat file or database
#
# Run this file directly to create/initialize database
#
# Written by Stephen Paine (smpaine@gmail.com) 7/10/2012
# Last update: 10/19/2013
# Modified by Dick C. Reichenbach (dick.reichenbach@gmail.com) 9/2/2013
# 	Added MySQL capability

#import MySQLdb, sqlite3, sys, getopt, time, datetime, ConfigParser
import sys, getopt, time, datetime, ConfigParser

# Variables defining data layout
#array[columns]
#array[datatypes]
# column
# datatype
columns = [
		"timestamp",
		"sensor",
		"avgVoltage",
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

# Get configuration options from file config.ini
config = ConfigParser.ConfigParser()
#print("Preparing to read configuration file, config.ini")
config.readfp(open('config.ini'))

flatFileOn = 0
sqliteOn = 0
mysqlOn = 0

if (config.get('flatfile', 'enable') == 'true'):
	#print("enabling flat file")
	flatFileOn = 1
	flatFileName = config.get('flatfile', 'flatFileName')
	#print("flat file name = " + flatFileName)

if (config.get('sqlite', 'enable') == 'true'):
	import sqlite3
	#print("enabling sqlite")
	sqliteOn = 1
	sqliteFileName = config.get('sqlite', 'sqliteFileName')
	#print("sqlite file name = " + sqliteFileName)

if (config.get('mysql', 'enable') == 'true'):
	#print("enabling mysql")
	import MySQLdb
	mysqlOn = 1
	mysqldbname = config.get('mysql', 'mysqldbname')
	#print("mysqldbname = " + mysqldbname)
	mysqlhost = config.get('mysql', 'mysqlhost')
	#print("mysqlhost = " + mysqlhost)
	mysqluser = config.get('mysql', 'mysqluser')
	#print("mysqluser = " + mysqluser)
	mysqlpass = config.get('mysql', 'mysqlpass')
	#print("mysqlpass = " + mysqlpass)

# New array backendType OFF=0 ON=not zero
# Array positions for both backendType and backends
logfile = 0
sqlite = 1
mysql = 2
backendType=(flatFileOn, sqliteOn, mysqlOn)
#print("flatFileOn = " + str(flatFileOn))
#print("sqliteOn = " + str(sqliteOn))
#print("mysqlOn = " + str(mysqlOn))

def sqlite_connect():
	return sqlite3.connect(sqliteFileName)

def sqlite_disconnect(con):
	con.close()

def mysql_connect():
	return MySQLdb.connect(host=mysqlhost, user=mysqluser, passwd=mysqlpass, db=mysqldbname )

def write_changes(backends, counter, longAvgVolts, longAvgAmps, longAvgWatts, longMaxVolts, longMinVolts, longMaxAmps, longMinAmps, xb):
	global backendType

	if (counter < 1):
		return

	# Don't want to do any divides by zero!
	if (longAvgVolts > 0.0):
		longAvgVolts /= counter
	if (longAvgAmps > 0.0):
		longAvgAmps /= counter
	if (longAvgWatts > 0.0):
		longAvgWatts /= counter

	if (longMaxVolts>150.0):
		print "longMaxVolts > 150, using longAvgVolts (and longAvgAmps) instead."
		longMaxVolts=longAvgVolts
		longMaxAmps=longAvgAmps
	
	if (backendType[0]!=0):
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

	if (backendType[1]!=0 or backendType[2]!=0):
		print "Updating log using SQL:"
	#	print "queryString="+queryString
		results=[ (time.strftime("%Y-%m-%d %H:%M:%S"), xb.address_16, longAvgVolts, longAvgAmps, longAvgWatts, longMaxVolts, longMinVolts, longMaxAmps, longMinAmps) ]
		if (backendType[1]!=0):
			print "Updating SQLite log:"
			queryString="INSERT INTO voltageLog (timestamp, sensor, avgVoltage, avgAmperage, avgWattage, maxVoltage, minVoltage, maxAmperage, minAmperage) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
			cur1 = backends[sqlite].cursor()
			cur1.executemany(queryString, results)
		if (backendType[2]!=0):
			print "Updating MySQL log:"
			queryString="INSERT INTO voltageLog (timestamp, sensor, avgVoltage, avgAmperage, avgWattage, maxVoltage, minVoltage, maxAmperage, minAmperage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
			cur2 = backends[mysql].cursor()
			cur2.executemany(queryString, results)
			
	flush_log(backends)
	temp="Wrote "+time.strftime("%Y/%m/%d %H:%M:%S")+"\t"+str(xb.address_16)+"\t"+str(longAvgVolts)+"\t"+str(longAvgAmps)+"\t"+str(longAvgWatts)+"\t"+str(longMaxVolts)+"\t"+str(longMinVolts)+"\t"+str(longMaxAmps)+"\t"+str(longMinAmps)+" to the log."
	return temp

def flush_log(backends):
	if (backendType[0]!=0):
		backends[logfile].flush()
	if (backendType[1]!=0):
		backends[sqlite].commit()
	if (backendType[2]!=0):
		backends[mysql].commit()

def open_log():
	global backendType
	backends=[None, None, None]
	if (backendType[0]!=0):
		try:
			myLog = open(flatFileName, 'r+')
			myLog.seek(0, 2) # 2 == SEEK_END. ie, go to the end of the file
		except IOError:
			print "Creating new flatfile."
			myLog = open(flatFileName, 'w+')
			myLog.write("Timestamp\tSensor\tVoltage\tAmperage\tWattage\tMaxVolts\tMinVolts\tMaxAmps\tMinAmps\n");
			flush_log(myLog)
			myLog.seek(0, 2) # 2 == SEEK_END. ie, go to the end of the file
		backends[logfile] = myLog
	if (backendType[1]!=0):
		backends[sqlite] = sqlite_connect()
	if (backendType[2]!=0):
		backends[mysql] = mysql_connect()
	return backends

def close_log(backends):
	global backendType
	flush_log(backends)
#
# I don't understand the purpose of this section because all three types use the .close, so why split it out?
#
	if (backendType[0]!=0):
		backends[logfile].close()
	if (backendType[1]!=0):
		sqlite_disconnect(backends[sqlite])
	if (backendType[2]!=0):
		sqlite_disconnect(backends[mysql])

def create_sqlite_file():
	try:
		logfile = open(sqliteFileName, 'r+')
		print "Sqlite database file already exists, quitting now."
	except IOError:
		print "Creating new sqlite database."
# This is in the original, but it doesn't work.  I'm not sure why it's in here so I'm not removing it yet.
#		sqlite_backend()
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

def create_mysql_dbase():
#	try:
#		mysql_connect()
#		print "MySQL database file already exists, quitting now."
#	except IOError:
		print "Creating new mysql database."
# This is in the original, but it doesn't work.  I'm not sure why it's in here so I'm not removing it yet.
#		sqlite_backend()
		con=MySQLdb.connect(host=mysqlhost, user=mysqluser, passwd=mysqlpass)
		c = con.cursor()
		c.execute("CREATE DATABASE "+mysqldbname)
		c.execute("USE "+mysqldbname)
		columnString="id INTEGER PRIMARY KEY AUTO_INCREMENT"
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
	print "\t-m,--mysql\tcreate new, empty mysql database"
	print "\t-h,--help\tshow this help\n"

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "fsmh", ["flatfile", "sqlite", "mysql", "help"])
	except getopt.GetoptError:
		print str("Option not recognized.")
		usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-f", "--flatfile"):
			create_flatfile()
		elif o in ("-s", "--sqlite"):
			create_sqlite_file()
		elif o in ("-m", "--mysql"):
			create_mysql_dbase()
		elif o in ("-h", "--help"):
			print "Here is the help:"
			usage()
		else:
			assert False, "unhandled option"

if __name__ == "__main__":
	main()
