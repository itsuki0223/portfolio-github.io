#coding:utf-8
import spidev,time

def sensor_setup(dummy):
        global spi
        spi = spidev.SpiDev()
        spi.open(0,1)
	spi.max_speed_hz = 1000000

def clean():
	spi.close()

def get(port):
	start = 0b00000001
	if port == 7:
        	ch = 0b11111111
	elif port == 6:
        	ch = 0b11101111
        trans = ch
        dummy = 0b11111111
        ad = spi.xfer2([start,trans,dummy])
        voltage = ((((ad[1] & 0b00000011) << 8) + ad[2] ) * 3.3 ) / 1023
        current = voltage*30
        return current

