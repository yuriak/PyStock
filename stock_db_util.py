# -*- coding:utf-8 -*-
from time import clock

import MySQLdb
import datetime
import sys

from stock import Stock
from stock_file_util import *


# 这是股票的数据库操作工具，不过你没有数据库，如果需要的话可以管我要，然后你可以自己扩展这个工具包


def getAllStockInfoFromDB():
	stockIdList = {}
	conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='stockdb', port=3306, charset='utf8')
	cur = conn.cursor()
	cur.execute("select DISTINCT stockid from stocktable ORDER BY stockid")
	result = cur.fetchall()
	for row in result:
		stockIdList.setdefault(row[0], [])

	for stockid in stockIdList:
		cur.execute("select * from stocktable WHERE stockid=" + stockid + " order by stockdate")
		result = cur.fetchall()
		for row in result:
			stockIdList[stockid].append(
				Stock(stockid=row[1], stockname=row[2], stockprice=row[3], stockscore=row[4],
					  stockadvice=row[5],
					  stockdate=row[6]))
		print stockid + ":" + stockIdList[stockid][0].stockname + ":" + str(len(stockIdList[stockid]))
	cur.close()
	conn.close()
	return stockIdList


def getStockIDList():
	stockIdList = []
	conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='stockdb', port=3306, charset='utf8')
	cur = conn.cursor()
	cur.execute("select DISTINCT stockid from stocktable ORDER BY stockid")
	result = cur.fetchall()
	for row in result:
		stockIdList.append(row[0])
	return stockIdList


def getStockDateList():
	stockDateList = []
	conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='stockdb', port=3306, charset='utf8')
	cur = conn.cursor()
	cur.execute("select DISTINCT stockdate from stocktable ORDER BY stockdate")
	result = cur.fetchall()
	for row in result:
		stockDateList.append(row[0].strftime('%Y-%m-%d'))
	return stockDateList


def getStockByStockID(stockid):
	stocks = []
	conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='stockdb', port=3306, charset='utf8')
	cur = conn.cursor()
	cur.execute("select * from stocktable WHERE stockid='" + stockid + "' group by stockdate order by stockdate")
	result = cur.fetchall()
	for row in result:
		stocks.append(Stock(stockid=row[1], stockname=row[2], stockprice=row[3], stockscore=row[4],
							stockadvice=row[5],
							stockdate=row[6]))
	return stocks


def getStockByDate(date, host='localhost', user='root', passwd='', db='stockdb', port=3306):
	stocks = []
	conn = MySQLdb.connect(host, user, passwd, db, port, charset='utf8')
	cur = conn.cursor()
	cur.execute("SELECT * FROM stocktable WHERE stockdate='" + date + "' group by stockid order by stockid")
	result = cur.fetchall()
	for row in result:
		stocks.append(Stock(stockid=row[1], stockname=row[2], stockprice=row[3], stockscore=row[4],
							stockadvice=row[5],
							stockdate=row[6]))
	return stocks


# if __name__ == '__main__':
# 	reload(sys)
	exec "sys.setdefaultencoding('utf-8')"
	# stocks = getStockByDate('2016-07-29', host='115.29.143.181', user='root', passwd='wmh67392982', db='stockdb',
	# 						port=3306)
	# writeStocksToFile('data_date/2016-07-29.txt',stocks)
