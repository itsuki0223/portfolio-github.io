#coding:utf-8
import csv, time, subprocess


def sensor_setup(dummy):
	pass

def clean():
	pass

def get(port):
	f = open("/home/pi/tmp_data/PAL/Acceration_"+str(port)+".csv", "r")
	reader = csv.reader(f)
	data = []
	for line in reader:
		tmp = sum([float(row) for row in line]) / len(line)
		data.append(abs(tmp))
	data = sum(data)
	f.close()
	return data
