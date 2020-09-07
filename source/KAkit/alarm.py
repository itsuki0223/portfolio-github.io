#coding:utf-8
import time, csv, threading
import RPi.GPIO as GPIO
import logging

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

pin = {'red':27, 'green':22, 'yellow':17}
for ch in pin.values():
	GPIO.setup(ch, GPIO.OUT)

LOG_FILENAME = './iot_kit.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

def outLog(e):
        logging.debug(str(e) + ":" + time.strftime("%Y/%m/%d %H:%M:%S"))

class ptThread:
	def __init__(self):
		self.demon = False
 
	def ptLite(self, sensor_id, status):
		for ch in pin.values():
			GPIO.output(ch, GPIO.HIGH)

		file = open('/home/pi/iot.config/alarm_def.csv', 'r')
		reader = csv.reader(file)

		for row in reader:
			if sensor_id == row[1] and status == row[2]:
				data = row
				break
		file.close()
#		print(data)

		count = 0
		color_pattern = {}

		while self.demon == False:
			try:
				for index,value in enumerate(data):
					if value == str(count) and index > 2 and data[index + 1] != "0" and data[index + 1] != "":
						color_pattern[data[index + 1]] = [data[index + 2], False]
						break

				for color, pattern in color_pattern.items():
					if pattern[1] == True:
						GPIO.output(pin[color], GPIO.LOW)
						if pattern[0] == 'dot' or pattern[0] == 'off':
							pattern[1] = False

					else:
						GPIO.output(pin[color], GPIO.HIGH)
						if pattern[0] == 'dot' or pattern[0] == 'flashing':
							pattern[1] = True

				print(sensor_id,color_pattern)
				count += 1
				time.sleep(1)
			except:
				count += 1
				time.sleep(1)
	def delete(self):
		self.demon = True

def main():
	thread = []
	while True:
		time.sleep(3)
		f = open('/home/pi/tmp_data/alarm/alarm_status.csv', 'r')
		reader = csv.reader(f)
		for read in reader:
			csv_data = read
			try:
				for line in thread:
					tmp_data = line
					if tmp_data[0] == csv_data[0] and tmp_data[1] != csv_data[1]:
						print("change status")
						tmp_data[2].delete()
						time.sleep(1)
						del tmp_data[2]
						tmp_data[1] = csv_data[1]
						thread_tmp = ptThread()
						tmp_data.append(thread_tmp)
						thread_tmp = threading.Thread(target=thread_tmp.ptLite, args=(csv_data[0], csv_data[1]))
						thread_tmp.start()
						print(thread)
						outLog(thread)
						break
					elif tmp_data[0] == csv_data[0] and tmp_data[1] == csv_data[1]:
						break
				else:
					tmp_data = []
					tmp_data.append(csv_data[0])
					tmp_data.append(csv_data[1])
					thread_tmp = ptThread()
					tmp_data.append(thread_tmp)
					thread_tmp = threading.Thread(target=thread_tmp.ptLite, args=(csv_data[0], csv_data[1]))
					thread_tmp.start()
					thread.append(tmp_data)
					print(thread)
					outLog(thread)
			except:
				pass
		f.close()

if __name__ == "__main__":
        main()

GPIO.cleanup()
