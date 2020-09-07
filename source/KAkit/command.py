#coding:utf-8
import time, os, sys, csv
import db

f = open('/home/pi/iot.config/raspberry_pi_def.csv', 'r')
reader = csv.DictReader(f)
for line in reader:
	config = line

count = int(config['db_interval'])
DB = False

while True:
	time.sleep(5)
	try:
		if config['dropbox'] == 'ON':
			count += 5
			if count >= int(config['db_interval']):
				count = 0
				db.get_file("command")
				DB = True

		file = open("/home/pi/command/command.txt","r")
		command_list = file.readlines()
		file.close()

		if "DONE" in command_list[-1]:
			continue

		f = open("/home/pi/command/command.txt","a")
		f.write("\nDONE "+time.strftime("%Y/%m/%d %H:%M:%S"))
		f.close()

		if DB == True:
			db.send_file("/home/pi/command/command.txt","command")
			DB = False

		for command in command_list:
			os.system(command)

	except:
		pass
