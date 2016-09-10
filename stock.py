# -*- coding:utf-8 -*-
import datetime

# 这是股票的数据结构，其中包含了__str__和parse方法，输出的时候可以直接打印，输入的时候直接Stock.parse就可以获得股票对象
import json


class Stock:
	stockid = ''
	stockname = ''
	stockprice = 0.0
	stockscore = 0.0
	stockadvice = -1
	stockdate = datetime.date.today()

	def __init__(self, stockid, stockname, stockprice, stockscore, stockadvice, stockdate):
		self.stockid = stockid
		self.stockname = stockname
		self.stockprice = stockprice
		self.stockscore = stockscore
		self.stockadvice = stockadvice
		self.stockdate = stockdate

	def __str__(self):
		return ("%s,%s,%3.2f,%2.1f,%d,%s" % (
			self.stockid, self.stockname, self.stockprice, self.stockscore, self.stockadvice,
			self.stockdate.strftime('%Y-%m-%d')))

	def toStr(self):
		return ("%s,%s,%3.2f,%2.1f,%d,%s" % (
			self.stockid, self.stockname, self.stockprice, self.stockscore, self.stockadvice,
			self.stockdate.strftime('%Y-%m-%d'))).encode('utf-8')

	@classmethod
	def parse(cls, source):
		values = source.strip().split(',')
		s = Stock(stockid=values[0], stockname=values[1], stockprice=float(values[2]),
				  stockscore=float(values[3]), stockadvice=int(values[4]),
				  stockdate=datetime.datetime.strptime(values[5], '%Y-%m-%d'))
		return s

	@classmethod
	def parseDic(cls, dic):
		stockid = dic['stockid']
		stockname = dic['stockname']
		stockscore = float(dic['stockscore'])
		stockprice = float(dic['stockprice'])
		stockadvice = int(dic['stockadvice'])
		stockdate = datetime.datetime.strptime(dic['stockdate'], '%Y-%m-%d')
		return Stock(stockid=stockid, stockname=stockname, stockprice=stockprice, stockscore=stockscore,
					 stockadvice=stockadvice, stockdate=stockdate)

	@classmethod
	def parseAdvice(cls, ad):
		stockAdvices = {0: '卖出', 1: '坚持', 2: '中性', 3: '增持', 4: '买入'}
		if stockAdvices.has_key(ad):
			return stockAdvices[ad]
		return '无效'


class CJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%d')
		else:
			return json.JSONEncoder.default(self, obj)
