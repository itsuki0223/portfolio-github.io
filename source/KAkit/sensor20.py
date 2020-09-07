#coding:utf-8
import RPi.GPIO as GPIO
import time

TRIG = 17
ECHO = 27

def sensor_setup(dummy):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TRIG,GPIO.OUT)
        GPIO.setup(ECHO,GPIO.IN)

def clean():
        GPIO.cleanup()

def get(dummy):
        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(0.3)

        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
        	signaloff = time.time()
        while GPIO.input(ECHO) == 1:
        	signalon = time.time()

        timepassed = signalon - signaloff
        distance = timepassed * 17000
        if distance > 450:
        	distance = 450
        return distance


