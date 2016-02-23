#!/usr/bin/python

import sys, getopt, optparse, os, fnmatch
import MySQLdb
import re, ntpath

db_name = "showmanager"
db_user = "showmanager"
db_passwd = "4rQRhBcvy9YCt34n"

table_prefix = "sm_"


# DB names
tbl_show  = table_prefix + "show"
tbl_file  = table_prefix + "file"



def init_db ():
	global db, cursor
	print "Connecting to database"
	# Open database connection
	db = MySQLdb.connect("localhost",db_user,db_passwd,db_name)

	# prepare a cursor object using cursor() method
	cursor = db.cursor()	
	return[0]

def exit ():
	print "Disconnecting from database"
	db.close()
	quit()

	return[0]

def check_db ():
	print "checking db.."

	print " check tbl_show"
	sql = "SHOW TABLES LIKE '" + tbl_show + "'"
	cursor.execute(sql)
	results = cursor.fetchall()
	if 	len(results) == 0:
		print " FATAL: tbl_show doesnt exist"
		return False

	print " check tbl_file"
	sql = "SHOW TABLES LIKE '" + tbl_file + "'"
	cursor.execute(sql)
	results = cursor.fetchall()
	if 	len(results) == 0:
		print " FATAL: tbl_file doesnt exist"
		return False

	print "db check successful"
	return True


def reset_db(  ):
	"Inits database and wipes all data"
	print "Inits database and wipes all data"
   
	# Drop table if it already exist using execute() method.
	cursor.execute("DROP TABLE IF EXISTS " + tbl_show)
	cursor.execute("DROP TABLE IF EXISTS " + tbl_file)

	# Create table as per requirement
	sql = """CREATE TABLE {vars} (
		sid  bigint(20) UNIQUE,
		name  varchar(255) UNIQUE)""".format(vars=tbl_show)	
	cursor.execute(sql)

	sql = """CREATE TABLE {vars} (
		fid  bigint(20) UNIQUE,
		filename  varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
		showid  bigint(20),  
		season  bigint(20),
		episode  bigint(20) )""".format(vars=tbl_file)	
	cursor.execute(sql)
	return [0]

def parseonce ( source, dest ):
	parse_files(source)


	return [0]

def parse_files ( source ):
	print "Parsing files"

	# get filenames
	matches = []
	for root, dirnames, filenames in os.walk(source):
	    for filename in filenames:
	    	if filename.endswith(('.mp4', '.mkv', '.avi')):
	        	matches.append(os.path.join(root, filename))

	# convert to lowercase
	files = [x.lower() for x in matches]
	files = [x.replace(" ",".") for x in files ]

	print files

	# check if show exists and assign show ID
	run = 0
	for entry in files:
		run = run+1
		splitted = re.split("(.s\d)",entry)
		showname = ntpath.basename(splitted[0])
		sql = """SELECT * FROM {tablename} WHERE name="{show}"
			""".format(tablename=tbl_show, show=showname)	
		cursor.execute(sql)
		response = cursor.fetchall()
		if len(response)==0:
			print "There is no component named %s run=%d" %(showname,run)
		else:
			showid = response[0][0]
			print "component found: showid=%d showname=%s" %(showid,showname)


	return [0]

def main(argv):
	print "Welcome to showmanager"

	# parse input args
	p = optparse.OptionParser(usage="USAGE", version="%prog 1.0")
	p.add_option('--resetdb', action='store_true')
	p.add_option('--parseonce', '-p', action='store_true')
	p.add_option('--source-dir', '-s', dest='src_dir')
	p.add_option('--destination-dir', '-d', dest='dest_dir')
	options, arguments = p.parse_args()


	init_db()

	if check_db() == False:
		reset_db()

	if options.resetdb:
		print "resetting db..."
	if options.parseonce:
		if options.src_dir and options.dest_dir:
			if os.path.isdir(options.src_dir) and os.path.isdir(options.dest_dir):
				parseonce(options.src_dir,options.dest_dir)
				exit()
		else:
			print "Too few input arguments"


	exit()



if __name__ == "__main__":
   main(sys.argv[1:])




