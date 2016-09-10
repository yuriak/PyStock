# -*- coding:utf-8 -*-
import json
import urllib2

import datetime
from bs4 import BeautifulSoup

from stock import Stock


def crawlStockID():
	sid = []
	response = None
	try:
		response = urllib2.urlopen('http://quote.eastmoney.com/stocklist.html')
		html = response.read()
		soup = BeautifulSoup(html, "html5lib")
		result = soup.select('#quotesearch')[0]
		lis = result.find_all('li')
		for l in lis:
			sid.append(l.get_text().split('(')[1].split(')')[0])
	except urllib2.URLError as e:
		if hasattr(e, 'code'):
			print 'Error code:', e.code
		elif hasattr(e, 'reason'):
			print 'Reason:', e.reason
	finally:
		if response:
			response.close()
	return sid

def crawlStockIDAndName():
	sid = {}
	response = None
	try:
		response = urllib2.urlopen('http://quote.eastmoney.com/stocklist.html')
		html = response.read()
		soup = BeautifulSoup(html, "html5lib")
		result = soup.select('#quotesearch')[0]
		lis = result.find_all('li')
		for l in lis:
			sid[l.get_text().split('(')[1].split(')')[0].strip()]=l.get_text().encode('utf-8').split('(')[0].strip()
	except urllib2.URLError as e:
		if hasattr(e, 'code'):
			print 'Error code:', e.code
		elif hasattr(e, 'reason'):
			print 'Reason:', e.reason
	finally:
		if response:
			response.close()
	return sid

def crawlStockInfo(sid):
	stocks = []
	response = None
	count=0
	for s in sid:
		try:
			# headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
			# req=urllib2.Request(url='http://doctor.10jqka.com.cn/' + s,headers=headers)
			response = urllib2.urlopen('http://doctor.10jqka.com.cn/' + s)
			html = response.read()
			response.close()
			soup = BeautifulSoup(html, 'lxml')
			nameAndId = soup.select('.stockname')[0].get_text().strip().encode('utf-8')
			title = soup.select('.title')[0].get_text().strip().encode('utf-8')
			if '停牌' in title:
				continue
			score = float(soup.select('.bignum')[0].get_text().strip().encode('utf-8') + soup.select('.smallnum')[
				0].get_text().strip().encode('utf-8'))
			ad = soup.select('.cur')[0].get_text().encode('utf-8')
			name = nameAndId.split('（')[0]
			id = nameAndId.split('（')[1].split('）')[0]
			advice = convertAdviceWord2Number(ad)
			price = float(soup.select('.cnt')[0].select('strong')[0].get_text().strip().encode('utf-8').split('元')[0])
			d = soup.select('.date')[0].get_text().strip().encode('utf-8')
			if len(d) > 0:
				d = d.split(':')[1].split(' ')[0]
				stockdate = datetime.datetime.strptime(d, '%Y年%m月%d日')
			else:
				stockdate = datetime.date.today()
			stocks.append(Stock(stockid=id, stockname=name, stockprice=price, stockscore=score, stockadvice=advice,
								stockdate=stockdate))
			print name, ':', id
			count+=1
			if count>10:
				break
		except urllib2.URLError as e:
			if hasattr(e, 'code'):
				print 'Error code:', e.code
			elif hasattr(e, 'reason'):
				print 'Reason:', e.reason
		finally:
			if response:
				response.close()
	return stocks


def crawlStockPrice(stockid):
	headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
	req = urllib2.Request(url='http://stockpage.10jqka.com.cn/spService/' + stockid + '/Header/realHeader',
						  headers=headers)
	response = urllib2.urlopen(req)
	print response
	html = response.read()
	response.close()
	data = json.loads(html)
	price = data['zs']
	return price





def convertAdviceWord2Number(advice):
	ad = {'卖出': 0, '减持': 1, '中性': 2, '增持': 3, '买入': 4}
	if ad[advice] == None:
		return -1
	else:
		return ad[advice]

def fetchOneDayDataFromMyServer(url='http://115.29.143.181:8080/stock',key='8e88c0bdba3ea10c5cec4112fc7a1494',date=datetime.date.today().strftime('%Y-%m-%d')):
	realUrl=url+'?key='+key+'&date='+date
	stocks=[]
	try:
		response=urllib2.urlopen(realUrl)
		data=response.read()
		jData=json.loads(data)
		for j in jData:
			stock=Stock.parseDic(j)
			if stock.stockprice!=0.0:
				stocks.append(stock)
	except urllib2.URLError as e:
		if hasattr(e, 'code'):
			print 'Error code:', e.code
		elif hasattr(e, 'reason'):
			print 'Reason:', e.reason
	print len(stocks)
	return stocks






