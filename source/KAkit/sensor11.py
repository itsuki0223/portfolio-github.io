#coding:utf-8
import RPi.GPIO as GPIO

def sensor_setup(CH):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(CH,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def clean():
        GPIO.cleanup()

def get(CH):
	value = GPIO.input(CH)
	return value
