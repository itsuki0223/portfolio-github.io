#coding:utf-8
import sys, time, json, kvs, urllib2, csv, os, subprocess
from Tkinter import *

reload(sys)
sys.setdefaultencoding('utf-8')

f = open('/home/pi/iot.config/raspberry_pi_def.csv', 'r')
reader = csv.DictReader(f)
for line in reader:
        config = line

datasetid = config['kvs_datasetid']
kvs.kvs_server = config['kvs_server']
kvs.init(config['kvs_id'], config['kvs_password'])

job_path = u'作業指示書'
ic_path = u'ICカード'
op_path = u'従業員'

class OrderList:
	def __init__(self, Frame1, Frame2, expr, id, response, order_time, raspi_sid, func, getInfo):
		self.raspi_sid = raspi_sid
		self.expr = expr
		self.id = id
		self.sensor_id = config['sensor2']+config['screanID']
		self.starttime = order_time
		self.func = func
		self.getInfo = getInfo

                self.jobs = response[u'製品名']
                self.client = response[u'顧客名']
		try:
			file = open('/home/pi/tmp_data/modeB/'+str(self.id)+'.csv', 'r')
			data = csv.reader(file)
			tmp_data = []
			for line in data:
				tmp_data.append(line)
			self.OperatorList = tmp_data[0]
			self.OperatorId = tmp_data[1]
                	self.OperatorName = tmp_data[3]
                	self.OperatorTime = tmp_data[2]
		except:
			self.OperatorList = []
			self.OperatorId = []
			self.OperatorName = []
			self.OperatorTime = []
                        if config['kvs'] == "ON":
                                self.Kvs_res(None, 0, self.starttime)
                        if config['csv'] == "ON":
                                self.csv_write(None,0,self.starttime)
			

		if len(self.OperatorList) > 0:
			self.button = Button(Frame1, text=self.jobs[0:7]+' '+self.client[0:6], font=("",30), bg='red',fg='white',bd=5,relief=RAISED)
		else:
			self.button = Button(Frame1, text=self.jobs[0:7]+' '+self.client[0:6], font=("",30), bg='gray84',bd=5,relief=RAISED)
		self.button.bind("<Button-1>",self.buttonOrder)
		self.button.pack(pady=1)

		self.tmp_csv()
		self.timeLabel = Label(Frame2, text=self.starttime, font=("",30))
		self.timeLabel.pack(pady=10)

	def Kvs_res(self, num, id, TIME):
		rec = {}
		rec['raspi_sid'] = self.raspi_sid
		rec['mode'] = 2
		rec['sensor_id'] = self.sensor_id
		rec['timestamp'] = TIME
		rec['suborder'] = self.expr
		rec['process_id'] = config['process_machine_id']
		if id == 0:
			rec['status'] = 'start'
		elif id == 1:
			rec['status'] = 'touched'
			rec['person'] = num
		elif id == 2:
			rec['status'] = 'released'
			rec['person'] = num
			rec['starttime'] = self.start_time
		else:
			rec['status'] = 'end'
			rec['starttime'] = self.starttime
		value = {'record': rec}
		response = kvs.request(u'/r/'+datasetid+u'/センサーデーター/', 'POST', value)

	def csv_write(self, num, id, TIME):
                rec = {}
                rec['raspi_sid'] = self.raspi_sid
                rec['mode'] = 2
                rec['sensor_id'] = self.sensor_id
                rec['timestamp'] = TIME
                rec['suborder'] = self.expr
		rec['process_id'] = config['process_machine_id']
                if id == 0:
                        rec['status'] = 'start'
                elif id == 1:
                        rec['status'] = 'touched'
                        rec['person'] = num
                elif id == 2:
                        rec['status'] = 'released'
                        rec['person'] = num
                        rec['starttime'] = self.start_time
                else:
                        rec['status'] = 'end'
                        rec['starttime'] = self.starttime

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


	def buttonOrder(self, event):
		self.root = Tk()
		self.root.attributes("-fullscreen",True)
        	self.root.title(u'バーコード読取画面')

        	frame = Frame(self.root, bg='LightSkyBlue')
        	frame.place(relheight=0.1, relwidth=1)
        	label = Label(frame,text='作業者リスト画面',bg='LightSkyBlue',fg="white",font=("",30))
        	label.pack()

        	self.LabelFrame2 = LabelFrame(self.root, text="作業者", font=("",25))
        	self.LabelFrame2.place(rely=0.38,relx=0.03, relheight=0.6, relwidth=0.94)

		order_txt = self.jobs[0:10]+","+self.client
		order_label = Label(self.root,text=self.expr+": "+order_txt[0:18], anchor='w',font=("",30))
		order_label.place(rely=0.25,relx=0.03, relheight=0.1, relwidth=0.94)

        	# barcode Entry
        	self.barcode = StringVar()
        	self.barcode.set=("")
        	self.barcode_entry = Entry(self.root,textvariable=self.barcode, font=("",30))
        	self.barcode_entry.place(relx=0.03, rely=0.12, relheight=0.1,relwidth=0.4)
        	# バインディング
        	self.barcode_entry.focus_set()
        	self.barcode_entry.bind("<Return>",self.Barcode)

		self.barcode_label = Label(self.root, text="読み込み準備OK!",font=("",30))
		self.barcode_label.place(relx=0.5, rely=0.12, relheight=0.1,relwidth=0.48)

		# ホーム画面
		button2 = Button(self.LabelFrame2,text='戻る',font=("",25),bg='gray84',bd=5,relief=RAISED)
		button2.bind("<Button-1>",self.del_scr)
		button2.place(relx=0.44, rely=0.8, relheight=0.2, relwidth=0.13)

		# 終了ボタン
		button3 = Button(self.LabelFrame2,text='終了',font=("",25),fg='white',bg='red',bd=5,relief=RAISED)
                button3.bind("<Button-1>",self.del_order)
                button3.place(relx=0.87, rely=0.8, relheight=0.2, relwidth=0.13)

		self.labelList = []
		self.Label_line()

        	self.root.mainloop()

	def del_scr(self, event):
		self.root.destroy()

	def del_order(self,event):
		self.root.destroy()
		self.func(self.id, self.starttime)

	def Barcode(self, event):
		Operator = self.barcode_entry.get()
		if Operator in self.OperatorList:
			index = self.OperatorList.index(Operator)
			self.start_time = self.OperatorTime[index]
			ID = self.OperatorId[index]
			self.barcode_label.configure(text=ID)
			TIME = time.strftime("%Y/%m/%d %H:%M:%S")
			if config['kvs'] == "ON":
				self.Kvs_res(ID,2,TIME)
			if config['csv'] == "ON":
				self.csv_write(ID,2,TIME)
			del self.OperatorTime[index]
			del self.OperatorId[index]
			del self.OperatorList[index]
			del self.OperatorName[index]
			self.Label_line()
			if len(self.OperatorList) == 0:
				self.button.configure(bg="gray84",fg="black")
			self.tmp_csv()
			print(self.OperatorList)
		else:
			try:
				if Operator[0:1] == config['person']:
					ID = Operator
				else:
					response = self.getInfo(ic_path, Operator)
					ID = response['ID']
				response = self.getInfo(op_path, ID)

				operator = response[u'氏名']
				TIME = time.strftime("%Y/%m/%d %H:%M:%S")
				if config['kvs'] == "ON":
					self.Kvs_res(ID,1,TIME)
				if config['csv'] == "ON":
					self.csv_write(ID,1,TIME)
				self.OperatorList.append(Operator)
				self.OperatorId.append(ID)
				self.OperatorTime.append(TIME)
				self.OperatorName.append(operator)
				print(self.OperatorList)
				if len(self.OperatorList) > 0:
					self.button.configure(fg="white",bg="red")
				self.barcode_label.configure(text=ID)
				self.Label_line()
				self.tmp_csv()

			except urllib2.HTTPError:
				self.barcode_label.configure(text="通信エラー")
			except:
				self.barcode_label.configure(text="未登録です")
		self.barcode_entry.delete(0,END)

	def Label_line(self):
		if len(self.labelList) != 0:
			for target in self.labelList:
				target.destroy()
		self.labelList = []
		for index, person in enumerate(self.OperatorName):
			label_text = " " + person
			label = Label(self.LabelFrame2, text=label_text[0:7], font=("",25))
			self.labelList.append(label)
                	if index >= 16:
                		pass
                	else:
	               		label.grid(row=index//4, column=index%4, padx=20, pady=5)
 				if index == 15:
					re_text = "(他" + str(len(self.OperatorList) - 15) + "人)"
					label.configure(text=re_text)

	def tmp_csv(self):
		f = open('/home/pi/tmp_data/modeB/'+str(self.id)+'.csv','w')
		data = [self.OperatorList, self.OperatorId, self.OperatorTime, self.OperatorName]
		print(data)
		writer = csv.writer(f)
		writer.writerows(data)
		f.flush()
		os.fdatasync(f.fileno())
		f.close()

	def delete_ins(self):
		TIME = time.strftime("%Y/%m/%d %H:%M:%S")
		for index, person in enumerate(self.OperatorList):
			try:
				self.start_time = self.OperatorTime[index]
				ID = self.OperatorId[index]
				if config['kvs'] == "ON":
					self.Kvs_res(ID, 2, TIME)
				if config['csv'] == "ON":
					self.csv_write(ID,2,TIME)
			except:
				pass
		if config['kvs'] == "ON":
			self.Kvs_res(None, 3, TIME)
		if config['csv'] == "ON":
			self.csv_write(None,3,TIME)

		subprocess.call(['sudo','rm','/home/pi/tmp_data/modeB/'+str(self.id)+'.csv'])
		self.timeLabel.destroy()
		self.button.destroy()
