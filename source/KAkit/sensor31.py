#coding:utf-8
import csv, time, subprocess


def sensor_setup(dummy):
	pass

def clean():
	pass

def get(port):
	f = open("/home/pi/tmp_data/PAL/Temperature_"+str(port)+".csv", "r")
	reader = csv.reader(f)
	for line in reader:
		data = float(line[0])
	f.close()
	return data
