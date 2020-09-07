#!/usr/bin/env python
# coding: UTF-8

#################################################################
# Copyright (C) 2017 Mono Wireless Inc. All Rights Reserved.    #
# Released under MW-SLA-*J,*E (MONO WIRELESS SOFTWARE LICENSE   #
# AGREEMENT).                                                   #
#################################################################

# ライブラリのインポート
import sys
import os
import threading
import time, csv
import datetime
from optparse import *

# WONO WIRELESSのシリアル電文パーサなどのAPIのインポート
sys.path.append('/home/pi/iot_kit/MNLib/')
from apppal import AppPAL

# ここより下はグローバル変数の宣言
# コマンドラインオプションで使用する変数
options = None
args = None

# 各種フラグ
bEnableLog = False
bEnableErrMsg = False

# プログラムバージョン
Ver = "1.0.1"

def ParseArgs():
	global options, args

	parser = OptionParser()
	if os.name == 'nt':
		parser.add_option('-t', '--target', type='string', help='target for connection', dest='target', default='COM3')
	else:
		parser.add_option('-t', '--target', type='string', help='target for connection', dest='target', default='/dev/ttyUSB0')

	parser.add_option('-b', '--baud', dest='baud', type='int', help='baud rate for serial connection.', metavar='BAUD', default=115200)
	parser.add_option('-s', '--serialmode', dest='format', type='string', help='serial data format type. (Ascii or Binary)',  default='Ascii')
	parser.add_option('-l', '--log', dest='log', action='store_true', help='output log.', default=False)
	parser.add_option('-e', '--errormessage', dest='err', action='store_true', help='output error message.', default=False)
	(options, args) = parser.parse_args()


if __name__ == '__main__':
	print("*** MONOWIRELESS App_PAL_Viewer " + Ver + " ***")

	ParseArgs()

	bEnableLog = options.log
	bEnableErrMsg = options.err
	while True:
		try:
			PAL = AppPAL(port=options.target, baud=options.baud, tout=0.05, sformat=options.format, err=bEnableErrMsg)
			break
		except KeyboardInterrupt:
			break

	while True:
		try:
			# データがあるかどうかの確認
			if PAL.ReadSensorData():
				# あったら辞書を取得する
				Data = PAL.GetDataDict()
				print(Data)
				# なにか処理を記述する場合はこの下に書く
#				print(Data)			# 受け取った辞書をそのまま標準出力する
				if "AccelerationX" in Data.keys():
					sensor_data = [Data["AccelerationX"],Data["AccelerationY"],Data["AccelerationZ"]]
					file = open("/home/pi/tmp_data/PAL/Acceration_"+str(Data["LogicalID"])+".csv","w")
					writer = csv.writer(file, lineterminator='\n')
					writer.writerows(sensor_data)
					file.flush()
					os.fdatasync(file.fileno())
					file.close()
				if "Temperature" in Data.keys():
					sensor_data = [[Data["Temperature"]]]
					file = open("/home/pi/tmp_data/PAL/Temperature_"+str(Data["LogicalID"])+".csv","w")
					writer = csv.writer(file, lineterminator='\n')
					writer.writerows(sensor_data)
					file.flush()
					os.fdatasync(file.fileno())
					file.close()
				if "Illuminance" in Data.keys():
					sensor_data = [[Data["Illuminance"]]]
					file = open("/home/pi/tmp_data/PAL/Illuminance_"+str(Data["LogicalID"])+".csv","w")
					writer = csv.writer(file, lineterminator='\n')
					writer.writerows(sensor_data)
					file.flush()
					os.fdatasync(file.fileno())
					file.close()
				if "Humidity" in Data.keys():
					sensor_data = [[Data["Humidity"]]]
					file = open("/home/pi/tmp_data/PAL/Humidity_"+str(Data["LogicalID"])+".csv","w")

					writer = csv.writer(file, lineterminator='\n')
					writer.writerows(sensor_data)
					file.flush()
					os.fdatasync(file.fileno())
					file.close()

				# ログを出力するオプションが有効だったらログを出力する。
#				PAL.OutputCSV()	# CSVでログをとる

		# Ctrl+C でこのスクリプトを抜ける
		except KeyboardInterrupt:
			break

	del PAL

	print("*** Exit App_PAL Viewer ***")
