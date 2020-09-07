#coding:utf-8
import os, sys, time

reload(sys)
sys.setdefaultencoding('utf-8')

home_dir = "/home/pi/"
def main():
	date = sys.argv[-1]
	dirs = sys.argv[1:-1]
	print("{0}日以前>{1}".format(date,dirs))

	for dir in dirs:
		dir = home_dir + dir
		for file in os.listdir(dir):
			file = dir + "/" + file
			file_date = os.path.getmtime(file)
			file_date = time.time() - file_date
			file_date = int(round(file_date/24/60/60))

			if file_date >= int(date):
				print("{0}:{1}日前".format(file,file_date))
				os.remove(file)
if __name__ == "__main__":
	main()
