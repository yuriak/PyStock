# -*- coding:utf-8 -*-
import codecs
import datetime

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
		stockList.sort(key=lambda x: x.stockscore,reverse=True)
		rank=1
		for stock in stockList:
			stockrank[dateIndex][stock.stockid]=(stock.stockid,stock.stockscore,resultDate,rank)
			rank+=1
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


if __name__ == '__main__':
	# rewriteDataDate()
	# print readStockRankFromDir('result')
	# readOneDayResult('2016-08-13')
	# 	deleteOneDayStockData(['2016-08-15'])
	# 	stocks=readDateStockDataFromDirs(ID_DATA_PATH)
	# 	cleanData(stocks,'data_clean_new/')
	pass
