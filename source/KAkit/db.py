#coding:utf-8
import subprocess, commands, logging, csv

f = open('/home/pi/iot.config/raspberry_pi_def.csv', 'r')
reader = csv.DictReader(f)
for line in reader:
	config = line

ip = config['IP_address'] + "/"

db_app = "/home/pi/iot_kit/DB//Dropbox-Uploader/dropbox_uploader.sh"
db_dir = config['db_dir'] + "/program/data/fogfile/"
raspi_dir = "/home/pi/"

LOG_FILENAME = './DB.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

def outLog(e, file):
        logging.debug(e + ": " + file)

def get_file(dir, ip=ip):
	try:
		outLog("download", dir)
		subprocess.call([db_app, "download", db_dir + ip + dir, raspi_dir])
	except Exception as e:
		pass

def send_file(file_path, dir, ip=ip):
	try:
		file = file_path.split("/")[-1]
		outLog("upload", dir + "/" + file)
		subprocess.call([db_app, "upload", file_path, db_dir + ip + dir + "/" + file])
	except Exception as e:
		pass
