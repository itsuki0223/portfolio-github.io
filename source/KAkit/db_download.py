#cording:utf-8
import time, csv, sys
import db

f = open('/home/pi/iot.config/raspberry_pi_def.csv', 'r')
reader = csv.DictReader(f)
for line in reader:
        config = line

dl = 'ShareMaster'
up = 'sensor_data'

raspi_sid = sys.argv[1]
while True:
	try:
		if config["mode"] != "3": 
			db.get_file(dl, ip="")

		file = raspi_sid+'_'+time.strftime("%Y%m%d")+'.csv'
		db.send_file("/home/pi/data/"+file, up, ip="")
	except Exception as e:
		print(e)
	
	time.sleep(int(config['db_interval']))
