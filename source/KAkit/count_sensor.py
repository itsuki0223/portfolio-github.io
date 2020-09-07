#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time, csv, json, subprocess, kvs, sys, os, logging
import importlib
import db

reload(sys)
sys.setdefaultencoding('utf-8')
LOG_FILENAME = './iot_kit.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

def outLog(e):
	logging.debug(str(type(e)) + ":" + e.message)

def tmp_csv():
	f = open("/home/pi/tmp_data/sensor/status"+setting[1]+".csv","r")
	reader = csv.reader(f)
	for row in reader:
		data = row
	f.close()
	data[0] = "on"

	f = open("/home/pi/tmp_data/sensor/status"+setting[1]+".csv","w")
	writer = csv.writer(f)
	writer.writerow(data)
	f.flush()
	os.fdatasync(f.fileno())
	f.close()

def csv_write(rec):
        global raspi_sid, setting, config
        dict = ['raspi_sid','mode','status','timestamp','suborder','person','sensor_id','count','starttime','process_id']
        keys = rec.keys()
        data = []
        for i in dict:
                if i in keys:
                        data.append(rec[i])
                else:
                        data.append(None)
        DIR = '/home/pi/data/'
        file_name = raspi_sid+'_'+time.strftime("%Y%m%d")+'.csv'
	file = open(DIR + file_name, 'a')
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(data)
	file.flush()
	os.fdatasync(file.fileno())
	file.close()

def value_csv(value,data):
        global config, raspi_sid, setting, sensor_no

        mode = str(config['mode'])

        f = '/home/pi/CountValue/'+sensor_no+'_'+raspi_sid+'_'+time.strftime('%Y%m%d')+'_'+str(setting[2])+'_countvalue.csv'
	file = open(f, 'a')
        csvlist = time.strftime("%Y-%m-%d %H:%M:%S"),value,data
        writer = csv.writer(file,lineterminator='\n')
        writer.writerow(csvlist)
	file.close()

def alerm_status(sensor_id, status):
	alarm_status = {}
        f = open('/home/pi/tmp_data/alarm/alarm_status.csv', 'r')
        reader = csv.reader(f)
        for line in reader:
		try:
        		alarm_status[line[0]] = line[1]
		except:
			pass
        f.close()

        alarm_status[sensor_id] = status
        write_status = []
        for key,value in alarm_status.items():
        	data = [key,value]
                write_status.append(data)

        f = open('/home/pi/tmp_data/alarm/alarm_status.csv', 'w')
        writer = csv.writer(f)
        writer.writerows(write_status)
        f.flush()
        os.fdatasync(f.fileno())
        f.close()

class countOn:
	def main(self,file_config, count_setting, raspiId, sensorId, main_sensor):
		global raspi_sid, config, setting, sensor_no
		config = file_config
		setting = count_setting
		raspi_sid = raspiId
		sensor_no = sensorId

		datasetid = config['kvs_datasetid']
       		kvs.kvs_server = config['kvs_server']
		kvs.init(config['kvs_id'], config['kvs_password'])

		count_file = "/home/pi/tmp_data/Counter/count"+str(setting[1])+".csv"
#		if config['sound']=='ON':
#			cmd = "sudo python /home/pi/sound/soundinput.py"
#			subprocess.Popen( cmd .strip().split(" ") )

		base_value = float(setting[18])
		sma_cycle = int(setting[19])
		sma_array = []
		COUNT = False
		wait = False
		try:
			f = open("/home/pi/tmp_data/sensor/status"+setting[1]+".csv","r")
			line = csv.reader(f)
			for row in line:
				data = row
			if data[0] == "on":
				starttime = data[1]
				updated = False
			else:
				updated = True
			f.close()
		except:
			updated = True
		rec = {}

		module = "sensor" + sensor_no
		module = importlib.import_module(module)
		module.sensor_setup(int(setting[15]))
		time.sleep(0.01)

		self.demon = True
		while self.demon == True:
			try:
				val = module.get(int(setting[15]))
				csv_val = val
				if sma_cycle > 1 :
					sma_array.append(val)
					if len(sma_array)>sma_cycle: sma_array.pop(0)
					val = float(sum(sma_array))/len(sma_array)
#				print(val)

				if setting[16][0:1] == "T":
					if val > base_value and wait == False:
						wait = True
						COUNT = True
					elif val < base_value:
						wait = False
				elif setting[16][0:1] == "F":
					if val < base_value and wait == False:
						wait = True
						COUNT = True
					if val > base_value:		
						wait = False

				if setting[20]=="ON":
					value_csv(csv_val,val)
				if COUNT==True:
					if updated == True:
						starttime = time.strftime("%Y/%m/%d %H:%M:%S")
						rec['timestamp'] = starttime
						rec['status'] = 'on'
						rec['raspi_sid'] = raspi_sid
                				rec['mode'] = 3
                				rec['sensor_id'] = main_sensor + sensor_no
						rec['process_id'] = setting[2]
                				data = {'record': rec}
						if config['csv'] == 'ON':
        	        				csv_write(rec)
                				if config['kvs']=='ON':
                					response = kvs.request(u'/r/'+datasetid+u'/センサーデーター/', 'POST', data)
						print(rec)
						tmp_csv()
						updated = False

						time.sleep(0.5)
						if setting[4] == 'ON':
							alerm_status(setting[1], rec['status'])

					try:
						file = open(count_file,"r")
						count_data = csv.reader(file)
						for row in count_data:
							count = int(row[0])
					except:
						file = open(count_file,"w")
						w = csv.writer(file)
						w.writerow([0,""])
						count = 0
					file.close()
					f = open(count_file,"w")
					writer = csv.writer(f)
					count = count + 1
					print("count: ",count)
					writer.writerow([count,starttime])
					f.flush()
					os.fdatasync(f.fileno())
					f.close()
					COUNT = False

			except Exception as e:
				print(e)
				outLog(e)

			time.sleep(float(setting[17]))

	def delete(self):
		self.demon = False

