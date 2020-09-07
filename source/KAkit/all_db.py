#cording:utf-8
import csv, os
import db

f = open('/home/pi/iot.config/raspberry_pi_def.csv', 'r')
reader = csv.DictReader(f)
for line in reader:
        config = line

if config['dropbox'] == 'ON':
	ip_list = ['iot.config','command','receive_data']
	dl_list = ['iot.config','ShareMaster','iot_kit']
	up_list = {'sensor_data':'data','receive_data':'senddata'}
	try:
		for dl in dl_list:
			if dl in ip_list:
				db.get_file(dl)
			else:
				db.get_file(dl, ip="")

		for dir in up_list:
			file_list = os.listdir("/home/pi/"+up_list[dir])
			for file in file_list:
				if dir in ip_list:
					db.send_file("/home/pi/"+up_list[dir]+"/"+file, dir)
				else:
					db.send_file("/home/pi/"+up_list[dir]+"/"+file, dir, ip="")
	except:
		print("error")
