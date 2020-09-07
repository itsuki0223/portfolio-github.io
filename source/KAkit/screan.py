#coding:utf-8
import sys, logging, time, urllib2
import kvs, json, csv, os
from Tkinter import *
from modeB import OrderList
from modeC import OperatorList
from modeD import Operator_list

reload(sys)
sys.setdefaultencoding('utf-8')
LOG_FILENAME = './iot_kit.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

f = open('/home/pi/iot.config/raspberry_pi_def.csv', 'r')
reader = csv.DictReader(f)
for line in reader:
        config = line

kvs.kvs_server = config['kvs_server']
datasetid = config['kvs_datasetid']
kvs.init(config['kvs_id'], config['kvs_password'])

DIR = '/home/pi/data/'
job_path = u'作業指示書'
ic_path = u'ICカード'
op_path = u'従業員'

def page_back(event):
	global active_sheet

        total = (len(OpeList_ins)-1)//12
        if active_sheet == 0:
                active_sheet = total
        else:
                active_sheet -= 1
        button_sort()

def page_move(event):
	global active_sheet

	total = (len(OpeList_ins)-1)//12
	if total == active_sheet:
		active_sheet = 0
	else:
		active_sheet += 1
	button_sort()

def button_sort():
	global active_sheet
	tar_index = active_sheet*12
	count = 0
	for index,tar_ins in enumerate(OpeList_ins):
		if index == (tar_index + count) and index < (tar_index + 12):
			tar_ins.button_line(count)
			count += 1
		else:
			tar_ins.button_line(None)
	if len(OpeList_ins) >= 1:
		LabelFrame1.configure(text="作業者 "+str(active_sheet+1)+"/"+str(((len(OpeList_ins)-1)//12)+1))

def OpeBarcode(event):
	global barcode
	expr = barcode.get()
	TIME = time.strftime("%Y/%m/%d %H:%M:%S")
	operator_manage(expr, TIME)

def operator_manage(id, TIME_DATA):
	global OpeList_num, OpeList_ins, Ope_time, barcode, barcode_label, barcode_entry, LabelFrame1, active_sheet, raspi_sid
	expr = id
	ID = ""

	if expr in OpeList_num:
		index = OpeList_num.index(expr)
		operator_name = OpeList_ins[index].operator
		OpeList_ins[index].delete_ins()
		del OpeList_num[index]
		del OpeList_ins[index]
		del Ope_time[index]
		barcode_label.configure(text=operator_name+"　　終了")

		if len(OpeList_ins) <= active_sheet*12 and active_sheet >= 1:
			active_sheet -= 1
		button_sort()

		data = [OpeList_num, Ope_time]
		if config['screanID'][0:1] == "C":
			file = open('/home/pi/tmp_data/modeC/modeC.csv', 'w')
		else:
			file = open('/home/pi/tmp_data/modeD/modeD.csv', 'w')
		writer = csv.writer(file)
		writer.writerows(data)
		file.flush()
		os.fdatasync(file.fileno())
		file.close()

	else:
		try:
			if len(OpeList_ins)//12 == active_sheet:			
				sort_num = len(OpeList_ins)
			else:
				sort_num = None

			if expr[0:1] == config['person']:
				response = getInfo(op_path, expr)
				if config['screanID'][0:1] == "C":
					ins = OperatorList(LabelFrame1, sort_num, expr, expr,response,TIME_DATA,raspi_sid, operator_manage, getInfo)
				else:
					ins = Operator_list(LabelFrame1, sort_num, expr, expr,response,TIME_DATA,raspi_sid, operator_manage, getInfo)
			else:
				dumy = getInfo(ic_path, expr)
				ID = dumy['ID']
				response = getInfo(op_path, ID)
				if config['screanID'][0:1] == "C":
					ins = OperatorList(LabelFrame1, sort_num, ID, expr,response,TIME_DATA,raspi_sid, operator_manage, getInfo)
				else:
					ins = Operator_list(LabelFrame1, sort_num, ID, expr,response,TIME_DATA,raspi_sid, operator_manage, getInfo)				

			if expr == response[u'card_id'] or ID == response[u'card_id']:
				active_sheet = len(OpeList_ins)//12
				OpeList_num.append(expr)
				OpeList_ins.append(ins)
				Ope_time.append(TIME_DATA)
			#	print(OpeList_num)
				barcode_label.configure(text=response[u'氏名']+"　　開始")
				button_sort()

				data = [OpeList_num, Ope_time]
				if config['screanID'][0:1] == "C":
					file = open('/home/pi/tmp_data/modeC/modeC.csv', 'w')
				else:
					file = open('/home/pi/tmp_data/modeD/modeD.csv', 'w')
				writer = csv.writer(file)
				writer.writerows(data)
				file.flush()
				os.fdatasync(file.fileno())
				file.close()

                except urllib2.HTTPError:
                        barcode_label.configure(text="通信エラー")
                except Exception as e:
                        barcode_label.configure(text="未登録です")
                        outLog(e)

	barcode_entry.delete(0,END)
def MultiGUI_ope(raspiId):
	global barcode, barcode_entry, barcode_label, LabelFrame1, OpeList_num, OpeList_ins, Ope_time, active_sheet, raspi_sid
	raspi_sid = raspiId

	root = Tk()
	root.attributes("-fullscreen",True)
	root.title(u'バーコード読取画面')

	frame = Frame(root, bg='LightSkyBlue')
	frame.place(relheight=0.1, relwidth=1)
	label = Label(frame,text='作業者リスト画面',bg='LightSkyBlue',fg="white",font=("",30))
	label.pack()

	LabelFrame1 = LabelFrame(root, text="作業者 1/1", font=("",25))
	LabelFrame1.place(rely=0.24,relx=0.03, relheight=0.74, relwidth=0.94)

	barcode_label = Label(root, text="読み込み準備OK!",font=("",30))
	barcode_label.place(relx=0.45, rely=0.12, relheight=0.1,relwidth=0.52)

	page_left = Button(LabelFrame1, text="◀", font=("",25), fg='white',bg='gray',bd=5,relief=RAISED)
	page_left.bind("<Button-1>",page_back)
	page_left.place(relx=0, rely=0.84, relheight=0.16, relwidth=0.1)

	page_right = Button(LabelFrame1, text="▶", font=("",25), fg='white', bg='gray',bd=5,relief=RAISED)
	page_right.bind("<Button-1>",page_move)
	page_right.place(relx=0.9, rely=0.84, relheight=0.16, relwidth=0.1)

	active_sheet = 0
	OpeList_num = []
	OpeList_ins = []
	Ope_time = []

	# barcode Entry
	barcode = StringVar()
	barcode.set=("")
	barcode_entry = Entry(root,textvariable=barcode, font=("",30))
	barcode_entry.place(relx=0.03, rely=0.12, relheight=0.1,relwidth=0.4)
	# バインディング
	barcode_entry.focus_set()
	barcode_entry.bind("<Return>",OpeBarcode)	

	tmp_data = []
	if config['screanID'][0:1] == "C":
		f = open('/home/pi/tmp_data/modeC/modeC.csv', 'r')
	else:
		f = open('/home/pi/tmp_data/modeD/modeD.csv', 'r')
	data = csv.reader(f)
	for line in data:
		tmp_data.append(line)
#	print(tmp_data)
	if tmp_data:
		dummy1 = tmp_data[0]
		dummy2 = tmp_data[1]
		for operator in dummy1:
			index = dummy1.index(operator)
			operator_manage(operator,dummy2[index])
	f.close()

	root.mainloop()

def MultiBarcode(event):
	global barcode
	expr = barcode.get()
	TIME_DATA = time.strftime("%Y/%m/%d %H:%M:%S")
	order_manage(expr, TIME_DATA)

def order_manage(id, TIME_DATA):
	global OrderList_num, OrderList_ins, barcode, barcode_label, barcode_entry, raspi_sid
	expr = id
	ID = ""

	if expr in OrderList_num:
		index = OrderList_num.index(expr)
		OrderList_ins[index].delete_ins()
		del OrderList_num[index]
		del OrderList_ins[index]
		del Order_time[index]
		print(OrderList_num)
		barcode_label.configure(text="作業が終了しました")

                data = [OrderList_num, Order_time]
                file = open('/home/pi/tmp_data/modeB/modeB.csv', 'w')
                writer = csv.writer(file)
                writer.writerows(data)
                file.flush()
                os.fdatasync(file.fileno())
                file.close()

	else:
		try:
			if expr[0:2] == config['jobs']:
				response = getInfo(job_path, expr)
				ins = OrderList(Frame1, Frame2, expr, expr, response, TIME_DATA, raspi_sid, order_manage, getInfo)
			else:
				dumy = getInfo(ic_path, expr)
				ID = dumy['ID']
				response = getInfo(job_path, ID)
				ins = OrderList(Frame1, Frame2, ID, expr, response, TIME_DATA, raspi_sid, order_manage, getInfo)
				
			if expr == response[u'識別NO'] or ID == response[u'識別NO']:
				OrderList_num.append(expr)
				OrderList_ins.append(ins)
				Order_time.append(TIME_DATA)
				print(OrderList_num)
				barcode_label.configure(text="作業リストが生成されました")

				data = [OrderList_num, Order_time]
				file = open('/home/pi/tmp_data/modeB/modeB.csv', 'w')
				writer = csv.writer(file)
				writer.writerows(data)
				file.flush()
				os.fdatasync(file.fileno())
				file.close()

                except urllib2.HTTPError:
                        barcode_label.configure(text="通信エラー")
                except Exception as e:
                        barcode_label.configure(text="未登録です")
                        outLog(e)

	barcode_entry.delete(0,END)
def MultiGUI_order(raspiId):
	global barcode, barcode_entry, barcode_label, Frame1, Frame2, OrderList_num, OrderList_ins, Order_time, raspi_sid
	raspi_sid = raspiId

	root = Tk()
	root.attributes("-fullscreen",True)
	root.title(u'バーコード読取画面')

	frame = Frame(root, bg='LightSkyBlue')
	frame.place(relheight=0.1, relwidth=1)
	label = Label(frame,text='作業リスト画面',bg='LightSkyBlue',fg="white",font=("",30))
	label.pack()

	LabelFrame1 = LabelFrame(root, text="作業", font=("",25))
	LabelFrame1.place(rely=0.24,relx=0.03, relheight=0.74, relwidth=0.94)

	Frame1 = Frame(LabelFrame1)
	Frame1.place(relwidth=0.6, relheight=1, relx=0, rely=0)

	Frame2 = Frame(LabelFrame1)
	Frame2.place(relwidth=0.4, relheight=1, relx=0.6, rely=0)

	barcode_label = Label(root, text="読み込み準備OK!",font=("",30))
	barcode_label.place(relx=0.45, rely=0.12, relheight=0.1,relwidth=0.52)

	OrderList_num = []
	OrderList_ins = []
	Order_time = []

	# barcode Entry
	barcode = StringVar()
	barcode.set=("")
	barcode_entry = Entry(root,textvariable=barcode, font=("",30))
	barcode_entry.place(relx=0.03, rely=0.12, relheight=0.1,relwidth=0.4)
	# バインディング
	barcode_entry.focus_set()
	barcode_entry.bind("<Return>",MultiBarcode)	

	tmp_data = []
	f = open('/home/pi/tmp_data/modeB/modeB.csv', 'r')
	data = csv.reader(f)
	for line in data:
		tmp_data.append(line)
	print(tmp_data)
	if tmp_data:
		dummy1 = tmp_data[0]
		dummy2 = tmp_data[1]
		for order in dummy1:
			index = dummy1.index(order)
			order_manage(order,dummy2[index])
	f.close()
			
	root.mainloop()

def calc(event):
    global barcode, fram1
    global Operator, jobs, client, num, expr, Operator2, jobnum, TIME_DATA
    global raspi_sid, job_starttime, ope_starttime
    global label11, label12, label31, label41, label51, label60
    expr = barcode.get()
    TIME_DATA = time.strftime('%Y/%m/%d %H:%M:%S')

    label11.configure(text=expr)
    label12.configure(text=TIME_DATA)

    if expr[0:1] != config['person'] and expr[0:2] != config['jobs']:
        try:
		response = getInfo(ic_path, expr)
                expr = response['ID']

        except urllib2.HTTPError:
                label31.configure(text='通信エラー')
        except:
                label31.configure(text='未登録')
                label41.configure(text='未登録')
                label51.configure(text='未登録')
                label60.configure(text='未登録')

    if expr[0:1]==config['person']:
	if expr == Operator2:
		Operator = ""
		send_status(2)
		Operator2 = ""
		ope_starttime = ""
		tmp_csv()
	else:
		if Operator2 != "":
			send_status(2)
		try:
  			response = getInfo(op_path, expr)
			Operator = response[u'氏名']
			Operator2 = expr
			ope_starttime = TIME_DATA
			send_status(0)
			tmp_csv()

		except urllib2.HTTPError:
			label31.configure(text="通信エラー")

		except:
                        Operator = '未登録'
			if config['input'] == "force":
				Operator = expr
                        Operator2 = expr
                        ope_starttime = TIME_DATA
                        send_status(0)
			tmp_csv()

    elif expr[0:2]==config['jobs']:
	if expr==jobnum:
		client = ''
		jobs = ''
		num = ''
		send_status(3)
		jobnum = ""
		job_starttime = ""
		tmp_csv()
	else:
		if jobnum != "" :
			send_status(3)
		try:
			response = getInfo(job_path, expr)
			jobs = response[u'製品名']
        		client = response[u'顧客名']
        		num = response[u'枝番']
                       	jobnum = expr
                        job_starttime = TIME_DATA
			send_status(1)
			tmp_csv()

		except urllib2.HTTPError:
			label31.configure(text="通信エラー")
                except:
                        jobs = '未登録'
                        client = '未登録'
                        num = '未登録'
			if config['input'] == "force":
				jobs = ''
                                client = expr
                                num = ''
                        jobnum = expr
                        job_starttime = TIME_DATA
			send_status(1)
			tmp_csv()

    barcode_entry.delete(0,END)

def GUI(raspiId):
	global barcode, barcode2, frame1, barcode_entry, raspi_sid
	global label11, label12, label31, label41, label51, label60
	global Operator, jobs, client, num, expr, Operator2, jobnum, ope_starttime, job_starttime
	global button_ope, button_order

	raspi_sid = raspiId

	f = open('/home/pi/tmp_data/modeA/modeA_tmp.csv', 'r')
	reader = csv.reader(f)
	for line in reader:
		data = line
	Operator = data[1]
	Operator2 = data[0]
	jobnum = data[3]
	client = data[5]
	jobs = data[4]
	num = data[6]
	expr = ""
	TIME_DATA = ""
	ope_starttime = data[2]
	job_starttime = data[7]

	root = Tk()
	root.attributes("-fullscreen",True)
	root.title(u'バーコード読取画面')

	frame = Frame(root, bg='LightSkyBlue')
	frame.place(relheight=0.1, relwidth=1)
	label = Label(frame,text='バーコード画面',bg='LightSkyBlue',fg="white",font=("",30))
	label.pack()

	frame1 = Frame(root)
	frame1.place(rely=0.1, relheight=0.9, relwidth=1)

	label11 = Label(frame1, text='barcode入力準備OK!', font=("",35))
	label11.place(relx=0.52, rely=0.01, relheight=0.13,relwidth=0.45)   
   
	label2 = Label(frame1, text=u'読み込み時間:',anchor="e", font=("",35))
	label2.place(relx=0.03, rely=0.18, relheight=0.13,relwidth=0.4)
    
	label3 = Label(frame1, text=u'操作者名:',anchor="e", font=("",35))
	label3.place(relx=0.16, rely=0.35, relheight=0.13,relwidth=0.27)
    
	label4 = Label(frame1, text=u'顧客:',anchor="e", font=("",35))
	label4.place(relx=0.16, rely=0.52, relheight=0.13,relwidth=0.27)

	label5 = Label(frame1, text=u'製品:',anchor="e", font=("",35))
	label5.place(relx=0.16, rely=0.69, relheight=0.13,relwidth=0.27)

	label6 = Label(frame1, text=u'枝番:',anchor="e", font=("",35))
        label6.place(relx=0.16, rely=0.86, relheight=0.13,relwidth=0.27)

	# 操作者名
	label31 = Label(frame1, text=Operator,anchor="w", font=("",35))
        label31.place(relx=0.52, rely=0.35, relheight=0.13,relwidth=0.45)
	# 顧客 
        label41 = Label(frame1, text=client,anchor="w", font=("",35))
        label41.place(relx=0.52, rely=0.52, relheight=0.13,relwidth=0.45)
        # 製品 
        label51 = Label(frame1, text=jobs,anchor="w", font=("",35))
        label51.place(relx=0.52, rely=0.69, relheight=0.13,relwidth=0.45)
        # 枝番
        label60 = Label(frame1, text=num,anchor="w", font=("",35))
        label60.place(relx=0.52, rely=0.86, relheight=0.13,relwidth=0.45)
	# 読み込み時間
	label12 = Label(frame1, text=TIME_DATA,anchor="w", font=("",35))
	label12.place(relx=0.52, rely=0.18, relheight=0.13,relwidth=0.45)

	# barcode Entry
	barcode = StringVar()
	barcode.set=("")
	barcode_entry = Entry(frame1,textvariable=barcode, font=("",35))
	barcode_entry.place(relx=0.03, rely=0.01, relheight=0.13,relwidth=0.4)
	# バインディング
	barcode_entry.focus_set()
	barcode_entry.bind('<Return>', calc)
	
	button_ope = Button(frame1,text='終了',font=("",25),bg='gray84',bd=5,relief=RAISED)
 	button_ope.bind("<Button-1>",ope_end)
 	button_ope.place(relx=0.03, rely=0.35, relheight=0.2, relwidth=0.13)
	if Operator2 == "":
		button_ope.configure(state=DISABLED)

	button_order = Button(frame1,text='終了',font=("",25),bg='gray84',bd=5,relief=RAISED)
	button_order.bind("<Button-1>",order_end)
	button_order.place(relx=0.03, rely=0.66, relheight=0.2, relwidth=0.13)
	if jobnum == "":
		button_order.configure(state= DISABLED)

	button_all = Button(frame1,text='全終了',font=("",25),fg='white',bg='red',bd=5,relief=RAISED)
        button_all.bind("<Button-1>",all_end)
        button_all.place(relx=0.87, rely=0.8, relheight=0.2, relwidth=0.13)

	root.mainloop()

def ope_end(event):
	if Operator2 != "":
		barcode_entry.insert(END,Operator2)
		calc('<Return>')
def order_end(event):
	if jobnum != "":
		barcode_entry.insert(END,jobnum)
		calc('<Return>')
def all_end(event):
	global Operator2, Operator, ope_starttime, jobnum, TIME_DATA
	TIME_DATA = time.strftime("%Y/%m/%d %H:%M:%S")
	if Operator2 != "":
		if jobnum == "":
			barcode_entry.insert(END,Operator2)
			calc('<Return>')
		else:
			Operator = ""
			send_status(2)
			ope_starttime = ""
			barcode_entry.insert(END,jobnum)
			calc('<Return>')
			Operator2 = ""
			tmp_csv()
	elif jobnum != "":
		barcode_entry.insert(END,jobnum)
		calc('<Return>')

def outLog(e):
	logging.debug(str(type(e)) + ":" + e.message)

def getInfo(path, expr):
	if config['kvs'] == "OFF":
		file = open('/home/pi/ShareMaster/'+path+'.csv', 'r')
		reader = csv.DictReader(file)
		for line in reader:
			if expr in line.values():
				res = {}
				for key, value in line.items():
					try:
						res[unicode(key,"shift-jis")] = unicode(value,"shift-jis")
					except UnicodeDecodeError:
						res[unicode(key,"shift-jis")] = u'文字エラー'
				break
	else:
		res = kvs.request(u'/r/'+datasetid+'/'+path+'/'+expr, 'GET', None)

#	print(res)
	return res

def send_status(type):
        global raspi_sid, TIME_DATA, jobnum, Operator2, ope_starttime, job_starttime
	global label31, label41, label51, label60, button_ope, button_order
	rec = {}
	rec['starttime'] = ""
	if type == 0:
		rec['status'] = 'touched'
		button_ope.configure(state=NORMAL)
	if type == 1:
		rec['status'] = 'start'
		button_order.configure(state=NORMAL)
	if type == 2:
		rec['status'] = 'released'
		rec['starttime'] = ope_starttime
		button_ope.configure(state=DISABLED)
	if type == 3:
		rec['status'] = 'end'
		rec['starttime'] = job_starttime
		button_order.configure(state=DISABLED)
	rec['raspi_sid'] = raspi_sid
	rec['mode'] = 2
	rec['timestamp'] = TIME_DATA
	rec['suborder'] = jobnum
	rec['process_id'] = config['process_machine_id']
	rec['person'] = Operator2
	rec['sensor_id'] = config['sensor2']+config['screanID']

	if config['kvs'] == 'ON':
		value = {'record': rec}
		try:
        		response = kvs.request(u'/r/'+datasetid+u'/センサーデーター/', 'POST', value)
		except Exception as e:
			outLog(e)

	if config['csv'] == 'ON':
        	dict = ['raspi_sid','mode','status','timestamp','suborder','person','sensor_id','count','starttime','process_id']
        	keys = rec.keys()
        	data = []
        	for i in dict:
                	if i in keys:
                        	data.append(rec[i])
                	else:
                        	data.append(None)
        	file_name = raspi_sid+'_'+time.strftime("%Y%m%d")+'.csv'
		file = open(DIR + file_name, 'a')
        	writer = csv.writer(file,lineterminator='\n')
        	writer.writerow(data)
        	file.flush()
        	os.fdatasync(file.fileno())
		file.close()
        label31.configure(text=Operator)
        label41.configure(text=client)
        label51.configure(text=jobs)
        label60.configure(text=num)

def tmp_csv():
	global Operator2, Operator, jobnum, jobs, client, num, ope_starttime, job_starttime
	f = open('/home/pi/tmp_data/modeA/modeA_tmp.csv','w')
	data = [Operator2, Operator, ope_starttime, jobnum, jobs, client, num, job_starttime]
	writer = csv.writer(f)
	writer.writerow(data)
	f.flush()
	os.fdatasync(f.fileno())
	f.close()
