# -*- coding:utf-8 -*-
from stock_core import *
from stock_file_util import *
from stock_server import *
import sys
import re
import platform
from snownlp import *

if len(sys.argv) >= 2:
	args = sys.argv[1:]
	if args[0] == 'crawler':
		if args[1] == 'today':
			crawlTodayStock()
		else:
			p = re.compile('\d{4}-\d{2}-\d{2}')
			if p.match(args[1]) != None:
				crawlTodayStock(date=p.match(args[1]).group())
			else:
				print 'invalid date'
	elif args[0] == 'analyzer':
		if args[1] == 'today':
			result = comprehensiveTest()
			writeResultToFile(result, 'result/' + datetime.datetime.today().strftime('%Y-%m-%d')+'.txt')
		else:
			p = re.compile('\d{4}-\d{2}-\d{2}')
			if p.match(args[1]) != None:
				result = comprehensiveTest()
				writeResultToFile(result, 'result/' + args[1]+'.txt')
			else:
				print 'invalid date'
	elif args[0] == 'server':
		pf = platform.platform()
		if args[1] == '-start':
			if len(args) >= 3 and args[2] != None and args[2] == '-port':
				start_server(int(args[3]))
			else:
				start_server()
		elif args[1] == '-stop':
			if 'Windows' in pf:
				print 'stop it on your own!'
			elif 'Linux' in pf:
				pid = os.popen("ps aux| grep stock_launcher.py| awk '{print $2}'").readlines()[0]
				if pid != None and re.match('\d{2,8}', pid) != None:
					os.popen("kill -9 " + pid)
			else:
				print 'sorry, you have to stop it on your own'
		else:
			print 'invalid command for server'
	else:
		print 'invalid module'
else:
	print 'invalid arguments'
