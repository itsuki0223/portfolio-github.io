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

class Operator_list:
	def __init__(self, Frame, sort_num, expr, id, response, person_time, raspi_sid, func, getInfo):
		self.Frame = Frame
		self.raspi_sid = raspi_sid
		self.expr = expr
		self.id = id
		self.sensor_id = config['sensor2']+config['screanID']
		self.starttime = person_time
		self.func = func
		self.getInfo = getInfo

		self.operator = response[u'氏名']
		op_text = " "+self.operator+" "
		try:
			file = open('/home/pi/tmp_data/modeD/'+str(self.id)+'.csv', 'r')
			data = csv.reader(file)
			for line in data:
				tmp_data = line
                	self.order = tmp_data[0]
                        self.Order = tmp_data[1]
                        self.order_name = tmp_data[2]
                        self.client = tmp_data[3]
			self.start_time = tmp_data[4]

		except:
			self.order = ""
			self.Order = ""
			self.order_name = ""
			self.client = ""
			self.start_time = ""
			if config['kvs'] == "ON":
				self.Kvs_res(0, self.starttime)
			if config['csv'] == "ON":
				self.csv_write(0, self.starttime)

		self.tmp_csv()

	def button_line(self, index):
		try:
			self.button.destroy()
		except:
			pass
		finally:
			if index != None:
				op_text = " "+self.operator+" "
				if self.order == "":
					self.button = Button(self.Frame, text=op_text[0:7], font=("",25), bg='gray84',bd=5,relief=RAISED)
				else:
					self.button = Button(self.Frame, text=op_text[0:7], font=("",25),fg='white', bg='red',bd=5,relief=RAISED)
                		self.button.bind("<Button-1>",self.buttonOperator)
                		self.button.grid(row=index//3, column=index%3, padx=30, pady=10)

	def Kvs_res(self, id, TIME):
		rec = {}
		rec['raspi_sid'] = self.raspi_sid
		rec['mode'] = 2
		rec['sensor_id'] = self.sensor_id
		rec['timestamp'] = TIME
		rec['person'] = self.expr
		rec['suborder'] = self.Order
		rec['process_id'] = config['process_machine_id']
		if id == 0:
			rec['status'] = 'touched'
		elif id == 1:
			rec['status'] = 'start'
		elif id == 2:
			rec['status'] = 'end'
			rec['starttime'] = self.start_time
		else:
			rec['status'] = 'released'
			rec['starttime'] = self.starttime

		value = {'record': rec}
		response = kvs.request(u'/r/'+datasetid+u'/センサーデーター/', 'POST', value)

        def csv_write(self, id, TIME):
                rec = {}
                rec['raspi_sid'] = self.raspi_sid
                rec['mode'] = 2
                rec['sensor_id'] = self.sensor_id
                rec['timestamp'] = TIME
		rec['person'] = self.expr
		rec['suborder'] = self.Order
		rec['process_id'] = config['process_machine_id']
                if id == 0:
                        rec['status'] = 'touched'
                elif id == 1:
                        rec['status'] = 'start'
                elif id == 2:
                        rec['status'] = 'end'
                        rec['starttime'] = self.start_time
                else:
                        rec['status'] = 'released'
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

	def buttonOperator(self, event):
		self.root = Tk()
		self.root.attributes("-fullscreen",True)
        	self.root.title(u'バーコード読取画面')

        	frame = Frame(self.root, bg='LightSkyBlue')
        	frame.place(relheight=0.1, relwidth=1)
        	label = Label(frame,text='作業内容画面',bg='LightSkyBlue',fg="white",font=("",30))
        	label.pack()

		operator_label = Label(self.root,text='作業者: '+self.operator[0:6],font=("",30),anchor='w')
		operator_label.place(rely=0.3,relx=0.05, relheight=0.17, relwidth=0.45)

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

		#作業ラベル
		self.order_text = "作業: "+self.order_name
		self.order_label = Label(self.root, text=self.order_text+"　"+str(self.client), font=("",30), anchor='w')
		self.order_label.place(relx=0.05, relwidth=0.9, rely=0.55, relheight=0.17)

		if self.order == "":
			self.alarm = Label(self.root,text='作業なし',font=("",35))
		else:
			self.alarm = Label(self.root,text='作業中',font=("",35),fg='red')
		self.alarm.place(relx=0.13, rely=0.8, relheight=0.2, relwidth=0.45)

		# ホーム画面
		button2 = Button(self.root,text='戻る',font=("",25),bg='gray84',bd=5,relief=RAISED)
		button2.bind("<Button-1>",self.del_scr)
		button2.place(relx=0, rely=0.8, relheight=0.2, relwidth=0.13)

		# 終了ボタン
		button3 = Button(self.root,text='終了',font=("",25),bg='gray84',bd=5,relief=RAISED)
                button3.bind("<Button-1>",self.del_order)
                button3.place(relx=0.58, rely=0.8, relheight=0.2, relwidth=0.13)

		button4 = Button(self.root,text='全終了',font=("",25),fg='white',bg='red',bd=5,relief=RAISED)
                button4.bind("<Button-1>",self.all_del)
                button4.place(relx=0.87, rely=0.8, relheight=0.2, relwidth=0.13)

        	self.root.mainloop()

	def del_scr(self, event):
		self.root.destroy()

	def all_del(self, event):
		self.func(self.id, self.starttime)
		self.root.destroy()

	def del_order(self,event):
		if self.order != "":
			TIME = time.strftime("%Y/%m/%d %H:%M:%S")
			self.barcode_label.configure(text=self.Order)
			if config['kvs'] == "ON":
                		self.Kvs_res(2,TIME)
			if config['csv'] == "ON":
				self.csv_write(2,TIME)

                        self.order = ""
                        self.Order = ""
                        self.order_name = ""
			self.client = ""
                        self.order_text = "作業: "+self.order_name
                        self.order_label.configure(text=self.order_text)

			self.button.configure(bg='gray84',fg='black')
                	self.alarm.configure(text="終了")
			self.tmp_csv()

	def Barcode(self, event):
		expr2 = self.barcode_entry.get()
		TIME = time.strftime("%Y/%m/%d %H:%M:%S")
					
        	if expr2 == self.order:
			self.del_order('<Button-1>')
                else:
			if self.order != "":
				self.del_order('<Button-1>')
			try:
				if expr2[0:2] == config['jobs']:
					tmp = expr2
				else:
					response = self.getInfo(ic_path, expr2)
					tmp = response[u'ID']

				response = self.getInfo(job_path, tmp)
                                self.order_name = response[u'製品名']
				try:
					self.client = response[u'顧客名']
				except:
					pass
				self.Order = tmp
				self.order = expr2
				self.start_time = TIME
				self.barcode_label.configure(text=self.Order)
                                self.order_text = "作業: "+self.order_name
                                self.order_label.configure(text=self.order_text+"　"+str(self.client))

				if config['kvs'] == "ON":
					self.Kvs_res(1,TIME)
				if config['csv'] == "ON":
					self.csv_write(1,TIME)
				self.button.configure(fg='white',bg='red')
				self.alarm.configure(text="作業中",fg='red')
				self.tmp_csv()

			except urllib2.HTTPError:
				self.barcode_label.configure(text="通信エラー")
                        except:
                                self.barcode_label.configure(text="未登録です")

		self.barcode_entry.delete(0,END)

	def tmp_csv(self):
		f = open('/home/pi/tmp_data/modeD/'+str(self.id)+'.csv','w')
		data = [self.order, self.Order, self.order_name, self.client, self.start_time]
		print(data)
		writer = csv.writer(f)
		writer.writerow(data)
		f.flush()
		os.fdatasync(f.fileno())
		f.close()

	def delete_ins(self):
		TIME = time.strftime("%Y/%m/%d %H:%M:%S")
		if self.order != "":
			if config['kvs'] == "ON":
                        	self.Kvs_res(2,TIME)
                        if config['csv'] == "ON":
                        	self.csv_write(2,TIME)

		self.order = ""
		self.Order = ""
		if config['kvs'] == "ON":
			self.Kvs_res(3, TIME)
                if config['csv'] == "ON":
			self.csv_write(3, TIME)
	
		subprocess.call(['sudo','rm','/home/pi/tmp_data/modeD/'+str(self.id)+'.csv'])
		try:
			self.button.destroy()
		except:
			pass
