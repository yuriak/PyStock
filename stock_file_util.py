# -*- coding:utf-8 -*-
import codecs
import datetime
import json

from stock import Stock
import os

# 这是股票数据的文件操作工具包，你可以在下面自己添加自己的文件读写方法
RESULT_PATH = 'result'
ID_DATA_PATH = 'data_clean'
ID_PATH = 'id'
DATE_DATA_PATH = 'data_date'


def readStockDataFromFile(path):
	stocks = []
	if not os.path.exists(path):
		return stocks
	f = open(path, 'r')
	lines = f.readlines()
	for line in lines:
		stocks.append(Stock.parse(line))
	return stocks


def writeStocksToFile(path, stocks):
	if not os.path.exists(path.split('/')[0]):
		os.mkdir(os.getcwd() + "\\" + path.split('/')[0])
	f = file(path, mode='w+')
	for stock in stocks:
		f.write(stock.toStr() + "\n")


def readStockDataFromDirs(path):
	stockDic = {}
	if not os.path.exists(path):
		return None
	fnames = os.listdir(path)
	for fname in fnames:
		f = open(path + '/' + fname)
		lines = f.readlines()
		if len(lines) < 10:
			continue
		stockid = fname.split('.')[0]
		stockDic.setdefault(stockid, [])
		for line in lines:
			stockDic[stockid].append(Stock.parse(line))
	return stockDic


def readDateStockDataFromDirs(path):
	stockDic = {}
	if not os.path.exists(path):
		return None
	fnames = os.listdir(path)
	for fname in fnames:
		stockDate = fname.split('.')[0]
		stockDic.setdefault(stockDate, [])
		f = open(path + '/' + fname)
		lines = f.readlines()
		for line in lines:
			stockDic[stockDate].append(Stock.parse(line))
	idDic = {}
	for d, s in stockDic.items():
		for stock in s:
			if stock.stockid not in idDic:
				idDic.setdefault(stock.stockid, [])
			idDic[stock.stockid].append(stock)

	for id, stocks in idDic.items():
		stocks.sort(key=lambda stock: stock.stockdate)
	return idDic


def cleanData(stockDic, newPath):
	for id, stocks in stockDic.items():
		currenti = 0
		while len(stocks) > 0:
			if stocks[currenti].stockprice == 0:
				del stocks[currenti]
				currenti = 0
				continue
			if currenti == len(stocks) - 1: break
			currenti += 1
		if len(stocks) < 50:
			del stockDic[id]
			continue
		deltaPrice = [stock.stockprice - stocks[stocks.index(stock) - 1].stockprice for stock in stocks[1:]]
		zeroCount = 0
		zeroSi = 0
		zeroEi = 0
		currenti = 0
		firstZero = False
		while len(deltaPrice) > 0:
			if deltaPrice[currenti] == 0:
				if firstZero == True:
					zeroSi = currenti
					firstZero = False
				if zeroCount >= 2:
					zeroEi = currenti
					deltaPrice = deltaPrice[0:zeroSi] + deltaPrice[zeroEi:]
					stocks = stocks[0:zeroSi] + stocks[zeroEi:]
					currenti = 0
					zeroCount = 0
					continue
				zeroCount += 1
			else:
				zeroCount = 0
				firstZero = True
			currenti += 1
			if currenti == len(deltaPrice) - 1:
				break
		if len(stocks) < 20:
			del stockDic[id]
			continue
		writeStocksToFile(newPath + id + '.txt', stocks)
	# zeroCount=sum([1 if d==0 else 0 for d in deltaPrice])
	# ratio=zeroCount/len(deltaPrice)
	# if ratio >0.4:


def appendData(stocks, datadir):
	fnames = os.listdir(datadir)
	idlist = [name.split('.')[0] for name in fnames]
	for stock in stocks:
		if stock.stockid in idlist:
			f = open(datadir + '/' + stock.stockid + '.txt', 'a')
			f.write(stock.toStr() + '\n')
		else:
			f = open(datadir + '/' + stock.stockid + '.txt', 'w')
			f.write(stock.toStr() + '\n')
		f.close()


def writeResultToFile(compList, filename):
	f = open(filename, 'w+')
	for result in compList:
		f.write(str(result[0]) + ',' + str(result[1]) + '\n')
	f.close()


def readIdFile(filepath):
	sid = []
	if not os.path.exists(filepath):
		f = open(filepath, 'w')
		f.close()
		return sid
	f = open(filepath, 'r')
	lines = f.readlines()
	for l in lines:
		sid.append(l.strip())
	f.close()
	return sid


def readIDAndNameFile(filepath):
	sid = {}
	if not os.path.exists(filepath):
		f = open(filepath, 'w')
		f.close()
		return sid
	f = open(filepath, 'r')
	lines = f.readlines()
	for l in lines:
		id = l.split(',')[0].strip()
		name = l.split(',')[1].strip()
		sid[id] = name
	f.close()
	return sid


def writeIdFile(sid, filepath):
	f = open(filepath, 'a')
	for s in sid:
		f.write(s + '\n')
	f.close()


def writeIDAndNameFile(sn, filePath):
	f = open(filePath, 'a')
	for id, name in sn.items():
		f.write(id.encode('utf-8') + ',' + str(name) + '\n')
	f.close()


def readResultFromFile(filepath):
	f = open(filepath, 'r')
	stockReulst = []
	for line in f.readlines():
		stockid = line.split(',')[0]
		score = line.split(',')[1]
		stockReulst.append((stockid, score))
	return stockReulst


def readResultFromDir(filepath):
	stockDic = {}
	if not os.path.exists(filepath):
		return None
	fnames = os.listdir(filepath)
	for fname in fnames:
		stockDate = fname.split('.')[0]
		stockDic.setdefault(stockDate, [])
		f = open(filepath + '/' + fname)
		lines = f.readlines()
		stockDic.setdefault(stockDate, [])
		for line in lines:
			stockid, score = line.split(',')
			stockDic[stockDate].append((stockid, score))

	return stockDic


def readStockRankFromDir(filepath):
	if not os.path.exists(filepath):
		return None
	fnames = os.listdir(filepath)
	stockrank = [i for i in range(len(fnames))]
	dateIndex = 0
	fnames.sort()
	for fname in fnames:
		resultDate = fname.split('.')[0]
		f = open(filepath + '/' + fname)
		lines = f.readlines()
		stockrank[dateIndex] = {}
		rank = 1
		for line in lines:
			sid = line.split(',')[0].strip()
			score = line.split(',')[1].strip()
			stockrank[dateIndex][sid] = (sid, score, resultDate, rank)
			rank += 1
		dateIndex += 1
	return stockrank


def readStockRankFromDateDataDir(filepath):
	if not os.path.exists(filepath):
		return None
	fnames = os.listdir(filepath)
	stockrank = [i for i in range(len(fnames))]
	dateIndex = 0
	fnames.sort()
	for fname in fnames:
		resultDate = fname.split('.')[0]
		f = open(filepath + '/' + fname)
		lines = f.readlines()
		stockrank[dateIndex] = {}
		stockList = []
		for line in lines:
			stockList.append(Stock.parse(line.strip()))
		stockList.sort(key=lambda x: x.stockscore, reverse=True)
		rank = 1
		for stock in stockList:
			stockrank[dateIndex][stock.stockid] = (stock.stockid, stock.stockscore, resultDate, rank)
			rank += 1
		dateIndex += 1
	return stockrank


def readSimpleResult(filepath=RESULT_PATH):
	result = []
	if not os.path.exists(filepath):
		return result
	fnames = os.listdir(filepath)
	fnames.sort()
	for fname in fnames:
		resultDate = fname.split('.')[0]
		oneDayResult = []
		rank = 1
		f = open(filepath + '/' + fname)
		lines = f.readlines()
		for line in lines:
			id = line.split(',')[0]
			score = line.split(',')[1].strip()
			oneDayResult.append((id, score, resultDate, rank))
			rank += 1
		result.append(oneDayResult)
	return result


def readOneDayResult(date):
	result = []
	filepath = RESULT_PATH
	if not os.path.exists(filepath):
		return result
	dates = [name.split('.')[0] for name in os.listdir(filepath)]
	rank = 1
	if date in dates:
		f = open(RESULT_PATH + '/' + date + '.txt')
		sn = readIDAndNameFile('id/id.txt')
		lines = f.readlines()
		for line in lines:
			id = line.split(',')[0]
			score = ('%.4f' % float(line.split(',')[1]))
			name = 'NULL'
			if id in sn:
				name = sn[id]
			result.append((rank, id, name, score))
			rank += 1
	return result


def deleteOneDayStockData(date):
	filepath = ID_DATA_PATH
	if not os.path.exists(filepath):
		return
	fnames = os.listdir(filepath)
	for name in fnames:
		remainLines = []
		f = open(ID_DATA_PATH + '/' + name)
		lines = f.readlines()
		for l in lines:
			if l.split(',')[-1].strip() not in date:
				remainLines.append(l)
		f.close()
		fn = open(ID_DATA_PATH + '/' + name + '.tmp', 'w+')
		fn.writelines(remainLines)
		fn.close()
		os.remove(ID_DATA_PATH + '/' + name)
		os.rename(ID_DATA_PATH + '/' + name + '.tmp', ID_DATA_PATH + '/' + name)

	# fn=open(ID_DATA_PATH+'/'+name+'.bak')
	# fn.writelines(lines[0:-1])


def rewriteDataDate():
	data = readStockDataFromDirs(ID_DATA_PATH)
	dates = []
	for id, stocks in data.items():
		for stock in stocks:
			if stock.stockdate not in dates:
				dates.append(stock.stockdate)
	dates.sort()
	for d in dates:
		f = open('data_date_new/' + d.strftime('%Y-%m-%d') + '.txt', 'w+')
		for id, stocks in data.items():
			for stock in stocks:
				if stock.stockdate == d:
					f.write(str(stock) + '\n')
		f.close()


def readDataFromDateDir(filepath=DATE_DATA_PATH):
	if not os.path.exists(filepath):
		return
	fnames = os.listdir(filepath)
	data = {}
	for fname in fnames:
		date = fname.split('.')[0].strip()
		f = open(filepath + '/' + fname)
		lines = f.readlines()
		oneDayData = {}
		for line in lines:
			stock = Stock.parse(line.strip())
			oneDayData[stock.stockid] = stock
		data[date] = oneDayData
	return data


def readWechatConfig(filepath='config/config.json'):
	if not os.path.exists(filepath):
		return
	f = open(filepath)
	str = f.read()
	return json.loads(str)


def readOneStockData(stock, date):
	ids = readIDAndNameFile(ID_PATH + '/id.txt')
	queryID = None
	queryName=None
	arank = 0
	ascore = 0
	nrank = 0
	nscore = 0
	price = 0
	advice = 0
	currdt = date
	if stock in ids.keys():
		queryID = stock
		queryName=ids[stock]
	elif stock in ids.values():
		for k, v in ids.items():
			if v == stock:
				queryID = k
				queryName=v
	else:
		return None
	if queryID == None:
		return None
	else:
		if not os.path.exists(RESULT_PATH + '/' + date + '.txt'):
			currdt = sorted(os.listdir(RESULT_PATH))[-1].split('.')[0]
		f = open(RESULT_PATH + '/' + currdt + '.txt')
		aList = []
		nList = []
		for line in f.readlines():
			id = line.split(',')[0]
			if line.split(',')[1] == 'nan': continue
			ascore = float(line.split(',')[1])
			aList.append((id, ascore))
		aList.sort(key=lambda x: x[1], reverse=True)
		result = [(aList.index(x), x[1]) for x in aList if x[0] == queryID]
		if len(result) != 0:
			arank = result[0][0] * 100.0 / len(aList)
			ascore = result[0][1]
		f.close()
		currdt = date
		if not os.path.exists(DATE_DATA_PATH + '/' + date + '.txt'):
			currdt = sorted(os.listdir(DATE_DATA_PATH))[-1].split('.')[0]
		f = open(DATE_DATA_PATH + '/' + currdt + '.txt')
		for line in f.readlines():
			nList.append(Stock.parse(line))
		nList.sort(key=lambda x: x.stockscore, reverse=True)
		result = [(nList.index(stock), stock) for stock in nList if stock.stockid == queryID]
		if len(result) != 0:
			nrank = result[0][0] * 100.0 / len(nList)
			nscore = result[0][1].stockscore
			advice = Stock.parseAdvice(int(result[0][1].stockadvice))
			price = result[0][1].stockprice
		return (queryID,queryName,arank, ascore, nrank, nscore, advice, price, currdt)


def readTodayList(date):
	ids = readIDAndNameFile(ID_PATH + '/id.txt')
	arank = 0
	ascore = 0
	nrank = 0
	nscore = 0
	price = 0
	advice = 0
	currdt = date
	if not os.path.exists(RESULT_PATH + '/' + date + '.txt'):
		currdt = sorted(os.listdir(RESULT_PATH))[-1].split('.')[0]
	f = open(RESULT_PATH + '/' + currdt + '.txt')
	aList = []
	nList = []
	for line in f.readlines():
		id = line.split(',')[0]
		if line.split(',')[1].strip() == 'nan': continue
		ascore = float(line.split(',')[1])
		aList.append((id, ascore))
	aList.sort(key=lambda x: x[1], reverse=True)
	f.close()
	currdt = date
	if not os.path.exists(DATE_DATA_PATH + '/' + date + '.txt'):
		currdt = sorted(os.listdir(DATE_DATA_PATH))[-1].split('.')[0]
	f = open(DATE_DATA_PATH + '/' + currdt + '.txt')
	for line in f.readlines():
		nList.append(Stock.parse(line))
	nList.sort(key=lambda x: x.stockscore, reverse=True)
	ar=[]
	for a in aList[0:5]:
		price=0.0
		advice=''
		for stock in nList:
			if stock.stockid==a[0]:
				price=stock.stockprice
				advice=Stock.parseAdvice(stock.stockadvice)
		ar.append((a[0],ids[a[0]],a[1],price,advice,currdt))

	# ar = [(a[0], ids[a[0]], a[1], [stock.stockprice for stock in nList if stock.stockid == a[0]][0], [Stock.parseAdvice(stock.stockadvice) for stock in nList if stock.stockid == a[0]][0], currdt) for a in aList[0:10]]
	nr = [(stock.stockid, stock.stockname, stock.stockscore, stock.stockprice, Stock.parseAdvice(stock.stockadvice), currdt) for stock in nList[0:5]]
	return ar, nr


if __name__ == '__main__':
	# print (datetime.date.today()+datetime.timedelta(-1)).strftime('%Y-%m-%d')
	# rewriteDataDate()
	# print readStockRankFromDir('result')
	# readOneDayResult('2016-08-13')
	# 	deleteOneDayStockData(['2016-08-15'])
	# 	stocks=readDateStockDataFromDirs(ID_DATA_PATH)
	# 	cleanData(stocks,'data_clean_new/')
	# a=[('001',22), ('002', 22), ('003', 22), ('004', 22), ('005', 22)]
	# print [a.index(x) for x in a if x[0]=='003']
	# print readOneStockData('深科技', '2016-08-29')
	# print readTodayList('2016-09-05')
	# d=sorted([1,2,3,4,5,4,3,2,1])
	# print d
	# print os.listdir(RESULT_PATH).sort(key=lambda x:datetime.datetime.strptime(x.split('.')[0],'%Y-%m-%d'))
	# pass
	# print readOneStockData('000001', '2016-09-06')
	# print readTodayList('2016-09-06')
	pass
