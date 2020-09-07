#coding:utf-8
'''
  IoT Kit Program 
'''
import sys, struct, commands, logging, time, os, socket
import binascii, urllib2
import kvs, json, screan, datetime
import csv, subprocess, threading
#
import db
from main_sensor import Sensor

reload(sys)
sys.setdefaultencoding('utf-8')
LOG_FILENAME = './iot_kit.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

def outLog(e):
	logging.debug(str(type(e)) + ":" + e.message)

## Raspberry Pi IPアドレス ##
def sendIp():
	global config, raspi_sid, datasetid
	# KVSログイン
	kvs.init(config['kvs_id'], config['kvs_password'])

	today = datetime.datetime.today()
	ip = commands.getoutput('hostname -I')
	value = {'record':{'SerialId': raspi_sid, 'IPアドレス': ip, 'タイムスタンプ': today.strftime("%Y-%m-%d %H:%M:%S")}}
	path = u'/r/'+datasetid+u'/RaspberryPiリスト'
	response = kvs.request(path, 'POST', value)

def getSerial():
	# Extract serial from cpuinfo file
	cpuserial = "0000000000000000"
	try:
		f = open('/proc/cpuinfo','r')
		for line in f:
			if line[0:6]=='Serial':
				cpuserial = line[10:26]
		f.close()
	except:
		cpuserial = "ERROR"

	return cpuserial

def create_sensor():
	global config, raspi_sid, datasetid

	if config['alarm'] == 'ON':
		subprocess.Popen(['sudo','python','/home/pi/iot_kit/alarm.py'])

	threads = []
	f = open('/home/pi/iot.config/sensor_def.csv', 'r')
	read_lines = csv.reader(f)
	for read_line in read_lines:
		try:
			if read_line[3] == "ON":
				sensor = Sensor(config, read_line)
				thread = threading.Thread(target=sensor.SensorLoop, args=(config, raspi_sid))
				threads.append(thread)
		except Exception as e:
			outLog(e)
			continue

	for target in threads:
		target.start()

	f.close()

## スタートルーチン ##
def main():
	global datasetid, config ,raspi_sid
	f = open('/home/pi/iot.config/raspberry_pi_def.csv', 'r')
	reader = csv.DictReader(f)
	for line in reader:
		config = line
	time.sleep(float(config['init_time']))
	logging.debug("IoT kit Start")

	mode = int(config['mode'])
	if mode==0:
		logging.debug("`mode` in iot.config is OFF")
		return

	datasetid = config['kvs_datasetid']
	kvs.kvs_server = config['kvs_server']
	raspi_sid = getSerial()

	if config['kvs'] == 'ON':
		Conect = False
		while Conect == False:
			try:
        			sendIp()
				Conect = True
        		except urllib2.URLError as e:
	        		time.sleep(1)
                		outLog(e)
            		except Exception as e:
                		outLog(e)
	if config['csv'] == 'ON':
		file_name = '/home/pi/RaspberryPi_list/'+raspi_sid+'_RaspberryPi_list.csv'
		file = open(file_name, 'a')
		ip = commands.getoutput('hostname -I')
		data = ip,time.strftime("%Y/%m/%d %H:%M:%S"),raspi_sid
        	writer = csv.writer(file,lineterminator='\n')
        	writer.writerow(data)
		file.flush()
		os.fdatasync(file.fileno())
		file.close()

		if config['dropbox'] == 'ON':
			db.send_file(file_name, "Raspberrypi_list",ip="")

	subprocess.Popen(["sudo","python","/home/pi/iot_kit/command.py"])

	try:
		if config["twelite"] == "ON":
			subprocess.Popen(["sudo","python","/home/pi/iot_kit/twelite.py"])
	except:
		pass

	if config['dropbox'] == 'ON':
		try:
			subprocess.call(["sudo","rm","./DB.log"])
		except:
			pass
		subprocess.Popen(["sudo","python","/home/pi/iot_kit/db_download.py",raspi_sid])

	if mode==1:
		logging.debug("Dual Mode")
		if config['screanID'][0:1] == "A":
			thread_1 = threading.Thread(target=screan.GUI,args=(raspi_sid,))
		elif config['screanID'][0:1] == "B":
			thread_1 = threading.Thread(target=screan.MultiGUI_order,args=(raspi_sid,))
		else:
			thread_1 = threading.Thread(target=screan.MultiGUI_ope,args=(raspi_sid,))
    		thread_2 = threading.Thread(target=create_sensor)
    		thread_1.start()
    		thread_2.start()
	elif mode==2:
		logging.debug("GUI Mode")
		if config['screanID'][0:1] == "A":
			screan.GUI(raspi_sid)
		elif config['screanID'][0:1] == "B":
			screan.MultiGUI_order(raspi_sid)
		else:
			screan.MultiGUI_ope(raspi_sid)
	elif mode==3:
		logging.debug("Sensor Mode")
		create_sensor()

if __name__ == "__main__":
	main()
