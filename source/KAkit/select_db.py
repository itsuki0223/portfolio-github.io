#cording:utf-8
import sys, os
import db

ip_dir = ['iot.config','command','receive_data']
dl_list = ['iot.config','iot_kit','ShareMaster','command']
up_list = {'sensor_data':'data','receive_data':'senddata','Raspberrypi_list':'RaspberryPi_list'}

dir = sys.argv
cont_dir = len(dir) - 1
for i in range(cont_dir):
	if dir[i + 1] in dl_list:
		if dir[i + 1] in ip_dir:
			db.get_file(dir[i + 1])	
		else:
			db.get_file(dir[i + 1], ip="")	
	elif dir[i + 1] in up_list:
		file_list = os.listdir("/home/pi/"+up_list[dir[i + 1]])
		for file in file_list:
			if dir[i + 1] in ip_dir:
                        	db.send_file("/home/pi/"+up_list[dir[i + 1]]+"/"+file,dir[i + 1])
                	else:
                        	db.send_file("/home/pi/"+up_list[dir[i + 1]]+"/"+file,dir[i + 1],ip="")

