#coding:utf-8
import kvs
import time, datetime, importlib, os
import logging, sys, csv, subprocess, threading
import RPi.GPIO as GPIO
import db
from count_sensor import countOn

reload(sys)
sys.setdefaultencoding('utf-8')
LOG_FILENAME = './iot_kit.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

class Sensor:
	def __init__(self, config, setting):
		self.setting = setting
		if config['kvs'] == "ON":
			kvs.init(config['kvs_id'], config['kvs_password'])

		self.sensor_no = "00" + str(self.setting[6])
		self.sensor_no = self.sensor_no[-2:]
                self.module = "sensor" + self.sensor_no
       	        self.module = importlib.import_module(self.module)
             	self.module.sensor_setup(int(self.setting[7]))

	def SensorLoop(self, config, raspi_sid):
		self.raspi_sid = raspi_sid
		sleep_internal = float(self.setting[9])
		base_value = float(self.setting[10])
		sma_cycle = int(self.setting[11])
		if self.setting[21] == "ON":
			GPIO.setwarnings(False)
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(26,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

		if self.setting[8][0:1] == "T":
			value_last = 0
		else:
			value_last = base_value + 0.01
		sma_array = []

		count_sensor_no = "00" + str(self.setting[14])
		count_sensor_no = count_sensor_no[-2:]

		if "status"+self.setting[1]+".csv" in os.listdir("/home/pi/tmp_data/sensor"):
			On = True
		else:
			On = False
		Off = False
		count = 0
		powercheck = True
		while 1:
			try:
				time.sleep(sleep_internal)
				value =  self.module.get(int(self.setting[7]))
				csv_value = value
				today = datetime.datetime.today()
				rec = {}
				updated = False
				# 移動平均
				if self.setting[21] == "ON":
					if GPIO.input(26) == 1:
						powercheck = True
					else:
						powercheck = False

				if sma_cycle > 1 :
					sma_array.append(value)
					if len(sma_array)>sma_cycle: sma_array.pop(0)
					value = float(sum(sma_array))/len(sma_array)
				print(value)
				if value_last < base_value and base_value < value :
					if self.setting[8][0:1] == "T" and powercheck == True:
						On = True
					elif self.setting[8][0:1] == "F":
						Off = True
				elif value_last > base_value and value < base_value :
					if self.setting[8][0:1] == "T":
						Off = True
					elif self.setting[8][0:1] == "F" and powercheck == True:
						On = True

				if base_value != -1 :
					# 基準値
					if On == True :
						if count_sensor_no!='00':
							rec['status'] = 'pon'
							count_work = countOn()
							count_thread = threading.Thread(target=count_work.main,args=(config,self.setting,self.raspi_sid,count_sensor_no,self.sensor_no))
							count_thread.start()
						else:
							rec['status'] = 'on'
						On = False
						updated = True
						if "status"+self.setting[1]+".csv" in os.listdir("/home/pi/tmp_data/sensor"):
							updated = False
							f = open("/home/pi/tmp_data/sensor/status"+self.setting[1]+".csv","r")
							data = csv.reader(f)
							for row in data:
								value_last = float(row[2])
							f.close()
						else:
							self.tmp_csv(rec["status"], value)
					if Off == True :
						if count_sensor_no!='00':
							count_work.delete()
							del count_work
							file = open("/home/pi/tmp_data/Counter/count"+str(self.setting[1])+".csv","r")
							count_data = csv.reader(file)
							for row in count_data:
								count = int(row[0])
								starttime = str(row[1])
							file.close()
							rec['count'] = count
							count = 0
							f = open("/home/pi/tmp_data/Counter/count"+str(self.setting[1])+".csv","w")
							writer = csv.writer(f)
							writer.writerow([count,None])
							f.flush()
							os.fdatasync(f.fileno())
							f.close()
						else:
							f = open("/home/pi/tmp_data/sensor/status"+self.setting[1]+".csv","r")
							data = csv.reader(f)
							for row in data:
								starttime = row[1]
							f.close()
#						if config['sound']=='ON':
#							proc.terminate()
						rec['status'] = 'off'
						rec['starttime'] = starttime
						Off = False
						updated = True
						os.remove("/home/pi/tmp_data/sensor/status"+self.setting[1]+".csv")
				if self.setting[12]=="ON":
					self.value_csv(csv_value,value)

				if updated:
   					rec['timestamp'] = today.strftime("%Y/%m/%d %H:%M:%S")
					rec['raspi_sid'] = self.raspi_sid
					rec['mode'] = 3
					rec['sensor_id'] = self.sensor_no + count_sensor_no
					rec['process_id'] = self.setting[2]
					data = {'record': rec}
					value_last = value
					print(rec)
					if config['csv'] == 'ON':
						self.csv_write(rec)
					if config['kvs']=='ON':
						response = kvs.request(u'/r/'+config['kvs_datasetid']+u'/センサーデーター/', 'POST', data)
					if self.setting[4] == 'ON':
						self.alerm_status(self.setting[1], rec['status'])

			except Exception as e:
				print(e)
				self.outLog(e)
		self.module.clean()

	def value_csv(self,value,data):
		today = datetime.datetime.today()

		f = '/home/pi/SensorValue/'+self.sensor_no+'_'+self.raspi_sid+'_'+today.strftime('%Y%m%d')+'_'+str(self.setting[2])+'_value.csv'
		file = open(f, 'a')
		csvlist = today.strftime("%Y-%m-%d %H:%M:%S"),value,data
		writer = csv.writer(file, lineterminator='\n')
		writer.writerow(csvlist)
		file.close()

	def csv_write(self,rec):
		dict = ['raspi_sid','mode','status','timestamp','suborder','person','sensor_id','count','starttime','process_id']
		keys = rec.keys()
		data = []
		for i in dict:
			if i in keys:
				data.append(rec[i])
			else:
				data.append(None)
		DIR = '/home/pi/data/'
		file_name = self.raspi_sid+'_'+time.strftime("%Y%m%d")+'.csv'
		file = open(DIR + file_name, 'a')
        	writer = csv.writer(file, lineterminator='\n')
        	writer.writerow(data)
		file.flush()
		os.fdatasync(file.fileno())
		file.close()

	def alerm_status(self, sensor_id, status):
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

	def tmp_csv(self, status, value):
		data = []
		data.append(status)
		data.append(time.strftime("%Y/%m/%d %H:%M:%S"))
		data.append(value)
		f = open("/home/pi/tmp_data/sensor/status"+self.setting[1]+".csv","w")
		writer = csv.writer(f)
		writer.writerow(data)
		f.flush()
		os.fdatasync(f.fileno())
		f.close()

	def outLog(self, e):
        	logging.debug(str(type(e)) + ":" + e.message)
