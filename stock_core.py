# -*- coding:utf-8 -*-
import logging
from stock_file_util import *
from stock_analyze import *
from stock_crawler import *

# 1.获取一只股票的所有信息：
# stocks=readStockDataFromFile('data_id/000001.txt')
# for stock in stocks:
# 	print stock

# 2.获取某一天股票的所有信息：
# stocks = readStockDataFromFile('data_date/2016-07-21.txt')
# for stock in stocks:
# 	print stock

# 4.获得所有id或date的信息：
# stockDic=readStockDataFromDirs('data_date')
# for key,stocks in stockDic.items():
# 	print key +"::"+ str(len(stockDic[key]))

# 5.具体的函数实现可以看stock包里相关的工具包

# 6.data_id和data_date是数据文件，已经经过清洗和去重，配合工具函数可以直接读取信息，信息的具体构成请看Stock类。请
# 尽量不要破坏本工程的目录结构，否则可能出现数据文件无法读取的问题

# stockDic = readStockDataFromDirs('data_id')
# stockIdLength = len(stockDic.keys())
# totalStockAmount = sum([len(x) for x in stockDic.values()])
# average = totalStockAmount / stockIdLength
# for stockid, stocks in stockDic.items():
# 	if len(stocks) < average: continue
# 	writeStocksToFile('data_id_clean/' + stockid + '.txt', stocks)

logging.basicConfig(level=logging.NOTSET,
					format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
					datefmt='%a, %d %b %Y %H:%M:%S'
					)


def corrTest(stockIdList):
	corrList = []
	for stockid, stocks in stockIdList.items():
		price = [stock.stockprice for stock in stocks]
		deltaPrice = [stock.stockprice - stocks[stocks.index(stock) - 1].stockprice for stock in stocks[1:]]
		# deltaDate=[(datetime.datetime.today()-stock.stockdate).days for stock in stocks[0:-1]]
		oriScore = [stock.stockscore for stock in stocks[0:-1]]
		dates = [stock.stockdate for stock in stocks[0:-1]]
		score = standardrizedScore(oriScore)
		deltaPrice.reverse()
		score.reverse()
		# deltaDate.reverse()
		dates.reverse()
		weighedCorr = []
		groupNumber = len(stocks) / 10
		groupPrice = []
		groupScore = []
		dayDateDiff = []
		groupDateDiff = []
		groupCount = 1
		# oriCorr=[]
		maxDays = (datetime.datetime.today() - stocks[0].stockdate).days
		for i in range(1, len(deltaPrice) + 1):
			groupPrice.append(deltaPrice[i - 1])
			groupScore.append(score[i - 1])
			diff = (datetime.datetime.today() - dates[i - 1]).days
			dayDateDiff.append(diff)
			if i % 10 == 0:
				s = sim(groupPrice, groupScore)
				# groupDateDiff.append(average(dayDateDiff))
				days = average(dayDateDiff)
				if isnan(s):
					s = 0
				# oriCorr.append(s)
				w = getWeight(groupCount, groupNumber, days)
				weighedCorr.append(w * s)
				groupPrice = []
				groupScore = []
				dayDateDiff = []
				groupCount += 1
		# t1=[]
		# print oriCorr
		# print groupDateDiff
		# for d in groupDateDiff:
		# 	t1.append(groupDateDiff[-1]-d+1)
		# print t1
		# sT1=sum(t1)
		# for i in range(len(oriCorr)):
		# 	w=t1[i]*oriCorr[i]/sT1
		# 	weighedCorr.append(w)
		# print weighedCorr
		ws = sum(weighedCorr)
		corrList.append((stockid, ws))

	corrList.sort(key=lambda x: x[1], reverse=True)

	return corrList


def deltaPriceRatioTest(stockIdList):
	averageRatio = []
	dTimeRatio = []
	dPriceRatio = []
	for stockid, stocks in stockIdList.items():
		price = [stock.stockprice for stock in stocks]
		deltaPrice = [stock.stockprice - stocks[stocks.index(stock) - 1].stockprice for stock in stocks[1:]]
		dr = 0
		da = 0
		dd = 0
		for d in deltaPrice:
			if d > 0:
				dr += 1
				da += d
			else:
				dd += d
		aTimeRatio = float(dr) / float(len(deltaPrice))
		dTimeRatio.append((stockid, aTimeRatio))
		if (float(abs(dd)) + float(da)) == 0:
			aPriceRatio = 0
		else:
			aPriceRatio = float(da) / (float(abs(dd)) + float(da))
		dPriceRatio.append((stockid, aPriceRatio))
		aRatio = (aTimeRatio * 0.2 + aPriceRatio * 0.8)
		averageRatio.append((stockid, aRatio))
	# dTimeRatio.sort(key=lambda x: x[1], reverse=True)
	# dPriceRatio.sort(key=lambda x: x[1], reverse=True)
	averageRatio.sort(key=lambda x: x[1], reverse=True)
	return averageRatio


def comprehensiveTest(stockIdList=readStockDataFromDirs('data_clean')):
	logging.info('start reading data')
	logging.info('read %d stocks data' % len(stockIdList))
	compList = []
	logging.info('start calculating corr')
	corr = corrTest(stockIdList)
	print 'corr: ', corr
	logging.info('calculating corr finished')
	logging.info('start calculating delta price rate')
	dr = deltaPriceRatioTest(stockIdList)
	print 'delta price: ', dr
	logging.info('calculating delta price finished')
	logging.info('start calculating comprehensive score')
	for c in corr:
		for d in dr:
			if c[0] == d[0]:
				totalValue = 0.4 * ((c[1] * 0.7 + d[1] * 0.3) * 2 + 6) + stockIdList[c[0]][-1].stockscore * 0.6
				compList.append((c[0], totalValue, datetime.datetime.today()))
	logging.info('sorting score')
	compList.sort(key=lambda x: x[1], reverse=True)
	logging.info('done.')
	print 'compList: ', compList
	return compList


def getAllStockID():
	sid = crawlStockID()
	fsid = readIdFile('id/id.txt')
	newid = []
	for s in sid:
		if s not in fsid:
			newid.append(s)
	if len(newid) > 0:
		writeIdFile(newid, 'id/id.txt')
	sid.extend(fsid)
	tmp = set(sid)
	id = list(tmp)
	id.sort()
	logging.info('crawl ' + str(len(id)) + ' stockid')
	return id


def statisticBestStock():
	result = readResultFromDir('result')
	stockCount = {}
	for date, stocks in result.items():
		for stock in stocks[0:10]:
			if stock[0] not in stockCount.keys():
				stockCount.setdefault(stock[0], 1)
			else:
				stockCount[stock[0]] += 1
	r = []
	for k, v in stockCount.items():
		r.append((k, v))
	r.sort(key=lambda x: x[1], reverse=True)
	return r


def getOneStockRank(stockid, result):
	stockrank = []
	for d in result:
		if d.has_key(stockid):
			stockrank.append(d[stockid])
	return stockrank


def getBestStockByAverageCompScore():
	averageRank = []
	sids = getAllStockID()
	result = readStockRankFromDir('result')
	for sid in sids:
		rk = getOneStockRank(sid, result)
		if len(rk) < len(result) * 0.6: continue
		aValue = average([float(record[1]) for record in rk])
		averageRank.append((sid, aValue))
	averageRank.sort(key=lambda x: x[1], reverse=True)
	print averageRank
	return averageRank


def crawlTodayStock(date=datetime.datetime.today().strftime('%Y-%m-%d')):
	stocks = fetchOneDayDataFromMyServer(date=date)
	writeStocksToFile('data_date/' + date + '.txt', stocks)
	appendData(stocks, 'data_clean')


def recalc():
	data = readStockDataFromDirs('data_clean')
	dates = []
	for id, stocks in data.items():
		for stock in stocks:
			if stock.stockdate not in dates:
				dates.append(stock.stockdate)
	dates.sort()
	print len(dates)
	for i in range(20, len(dates)):
		calcStocksDic = {}
		for id, stocks in data.items():
			calcStocks = []
			for stock in stocks:
				if stock.stockdate in dates[0:i]:
					calcStocks.append(stock)
			if len(calcStocks) < 20:
				continue
			calcStocks.sort(key=lambda x: x.stockdate)
			calcStocksDic[id] = calcStocks
		if len(calcStocksDic) < 100:
			continue
		print dates[i].strftime('%Y-%m-%d')
		print len(calcStocksDic)
		result = comprehensiveTest(calcStocksDic)
		writeResultToFile(result, 'spec_result/' + dates[i].strftime('%Y-%m-%d') + '.txt')


def simulateTransaction():
	money = 10000
	all_results = readSimpleResult()
	all_results = all_results[80:]
	bestResults = []
	for result in all_results:
		bestResults.append(result[0])
	date_data = readDataFromDateDir('data_date_new')
	dayIndex = 0
	inHand = 0
	yesterdayStock = None
	inStock = 0
	for r in bestResults:
		id = r[0]
		date = r[2]
		print '+++++++++++++++++++++++++++++++++++++++++++'
		print '0-today is: ' + date
		print 'day index: %d' % dayIndex
		todayToBuy = id
		if dayIndex == 0:
			print '2.5-first day'
			if id not in date_data[date]:
				print '0.5-stock' + id + ' stopped or no data,pass today transaction'
				dayIndex += 1
				continue
			p = date_data[date][id].stockprice * 100
			yesterdayStock = date_data[date][id]
			inHand = int(money / p)
			print '1-ready to buy: ' + todayToBuy
			print '2-buy price is: %.2f' % p
			print '3-buy in: %d' % inHand
			inStock = inHand * p
			print '4-money in stock: %.2f' % inStock
			money -= inHand * p
			print '5-money in hand: %.2f' % money
		else:
			if yesterdayStock != None:
				todayToSell = yesterdayStock.stockid
			else:
				todayToSell = ''
			print '3-ready to sell: ' + todayToSell
			print todayToBuy
			if todayToSell == todayToBuy:
				print '3.2-same stock as yesterday ' + todayToSell + ' no need to transaction'
				dayIndex += 1
				continue
			else:
				if todayToSell != '':
					if todayToSell not in date_data[date]:
						print '3.5-stock: ' + todayToSell + ' stopped or no data, pass today transaction'
						dayIndex += 1
						continue
					sell = date_data[date][todayToSell]
					print '4-sell price: %.2f' % (sell.stockprice * 100)
					money += inHand * sell.stockprice * 100
					print '4.5-sell: %d' % inHand
					print '5-money in hand: %.2f' % money
					yesterdayStock = None
					inHand = 0
				if id not in date_data[date]:
					print '0.5-stock to buy: ' + id + ' stopped or no data,pass today transaction'
					dayIndex += 1
					continue
				p = date_data[date][id].stockprice * 100
				buy = date_data[date][id]
				yesterdayStock = buy
				inHand = int(money / p)
				print '1-ready to buy: ' + todayToBuy
				print '2-buy price is: %.2f' % p
				print '6-buy in: %d' % inHand
				inStock = inHand * p
				print '7-money in stock: %.2f' % inStock
				money -= inHand * p
				print '8-money in hand: %.2f' % money
		dayIndex += 1


def simulateTransactWithOriScore():
	date_data = readDataFromDateDir('data_date_new')
	dates = date_data.keys()
	dates.sort()
	bestStock = []
	money = 10000
	for date in dates[80:]:
		stocks = date_data[date]
		stockList = [v for k, v in stocks.items()]
		stockList.sort(key=lambda x: x.stockscore, reverse=True)
		bestStock.append(stockList[3])
	hand = 0
	yesterdayStock = None
	inStock = 0
	dayIndex = 0
	stock2Buy = None
	stock2Sell = None
	record = []
	for r in bestStock:
		id = r.stockid
		date = r.stockdate.strftime('%Y-%m-%d')
		print '+++++++++++++++++++++++++++++++++++++++++++'
		print '0-today is: ' + date
		print 'day index: %d' % dayIndex
		todayToBuy = id
		todayBest = id
		if dayIndex == 0:
			print '2.5-first day'
			if id not in date_data[date]:
				print '0.5-stock' + id + ' stopped or no data,pass today transaction'
				dayIndex += 1
				continue
			p = date_data[date][id].stockprice * 100
			yesterdayStock = date_data[date][id]
			hand = int(money / p)
			print '1-ready to buy: ' + todayToBuy
			print '2-buy price is: %.2f' % p
			print '3-buy in: %d' % hand
			inStock = hand * p
			print '4-money in stock: %.2f' % inStock
			money -= hand * p
			print '5-money in hand: %.2f' % money
			record.append((money, inStock, money + inStock, r.stockdate))
			print 'rate %.2f' % (((money + inStock) - 10000) / 10000)
		else:
			if yesterdayStock != None:
				todayToSell = yesterdayStock.stockid
				print '3-ready to sell: ' + todayToSell
			else:
				todayToSell = ''
			if todayToSell == todayToBuy:
				print '3.2-same stock as yesterday ' + todayToSell + ' no need to transaction'
				dayIndex += 1
				continue
			else:
				if todayToSell != '':
					if todayToSell not in date_data[date]:
						print '3.5-stock: ' + todayToSell + ' stopped or no data, pass today transaction'
						dayIndex += 1
						continue
					sell = date_data[date][todayToSell]
					print '4-sell price: %.2f' % (sell.stockprice * 100)
					money += hand * sell.stockprice * 100
					print '4.5-sell: %d' % hand
					print '5-money in hand: %.2f' % money
					yesterdayStock = None
					hand = 0
					inStock = 0
					print 'rate %.2f' % (((money + inStock) - 10000) / 10000)
				if id not in date_data[date]:
					print '0.5-stock to buy: ' + id + ' stopped or no data,pass today transaction'
					dayIndex += 1
					if todayToSell != '':
						record.append((money, inStock, money + inStock, r.stockdate))
					continue
				p = date_data[date][id].stockprice * 100
				buy = date_data[date][id]
				yesterdayStock = buy
				hand = int(money / p)
				print '1-ready to buy: ' + todayToBuy
				print '2-buy price is: %.2f' % p
				print '6-buy in: %d' % hand
				inStock = hand * p
				print '7-money in stock: %.2f' % inStock
				money -= hand * p
				print '8-money in hand: %.2f' % money
				record.append((money, inStock, money + inStock, r.stockdate))
				print 'rate %.2f' % (((money + inStock) - 10000) / 10000)
		dayIndex += 1

	return record


def simulateTransactWithOriScoreCorrected():
	date_data = readDataFromDateDir('data_date')
	dates = date_data.keys()
	dates.sort()
	bestStock = []
	money = 10000
	for date in dates:
		stocks = date_data[date]
		stockList = [v for k, v in stocks.items()]
		stockList.sort(key=lambda x: x.stockscore, reverse=True)
		bestStock.append(stockList[1])
	hand = 0
	yesterdayStock = None
	inStock = 0
	dayIndex = 0
	tomorrow2Buy = None
	tomorrow2Sell = None
	acceptableRaiseRate = 0.015
	acceptableStopRate=0.05
	buyPrice = 0.0
	sellPrice = 0.0
	record = []
	for r in bestStock[100:]:
		id = r.stockid
		date = r.stockdate.strftime('%Y-%m-%d')
		print '+++++++++++++++++++++++++++++++++++++++++++'
		print '0-today is: ' + date
		print 'day index: %d' % dayIndex
		if dayIndex == 0:
			print '2.5-first day'
			tomorrow2Buy = id
			tomorrow2Sell = None
		else:
			todayToBuy = tomorrow2Buy
			tomorrow2Buy = id
			todayToSell = tomorrow2Sell
			tomorrow2Sell = todayToBuy
			if todayToSell != None:
				if todayToSell == todayToBuy:
					print '3.2-same stock as yesterday ' + todayToSell + ' no need to transaction'
					dayIndex += 1
					continue
				if todayToSell not in date_data[date]:
					print '3.5-stock: ' + todayToSell + ' stopped or no data, pass today transaction'
					todayToBuy = None
					tomorrow2Sell = todayToSell
					todayToSell = None
					dayIndex += 1
					continue
				sell = date_data[date][todayToSell]
				print '4-sell price: %.2f' % (sell.stockprice * 100)
				raisePrice=(sell.stockprice - buyPrice)
				income=(sell.stockprice - buyPrice)*hand*100
				raiseRate=raisePrice / buyPrice
				fee=(hand * sell.stockprice * 100 * (5.0 / 10000))
				print '4.05-stock: ' + todayToSell + ' fee is %.2f' % fee
				print '4.05-stock: ' + todayToSell + ' raise amount is %.2f' % income
				print '4.1-stock: ' + todayToSell + ' raise rate is %.2f' % raiseRate
				if raiseRate >-acceptableStopRate and raiseRate<acceptableRaiseRate :
					print '4.2-stock: ' + todayToSell + ' not reach %.2f' % acceptableRaiseRate
					dayIndex += 1
					tomorrow2Sell = todayToSell
					todayToSell = None
					todayToBuy = None
					continue
				money += (hand * sell.stockprice * 100 - (hand * sell.stockprice * 100 * (5.0 / 10000)))
				print '4.5-sell: %d' % hand
				print '5-money in hand: %.2f' % money
				hand = 0
				inStock = 0
				print 'rate %.2f' % (((money + inStock) - 10000) / 10000)
				todayToSell = None
			if todayToBuy not in date_data[date]:
				print '0.5-stock to buy: ' + id + ' stopped or no data,pass today transaction'
				dayIndex += 1
				todayToBuy = None
				tomorrow2Sell = None
				if todayToSell != None:
					record.append((money, inStock, money + inStock, r.stockdate))
				continue
			buyPrice=date_data[date][todayToBuy].stockprice
			p = date_data[date][todayToBuy].stockprice * 100
			hand = int(money / p)
			print '1-ready to buy: ' + todayToBuy
			print '2-buy price is: %.2f' % p
			print '6-buy in: %d' % hand
			inStock = hand * p
			print '7-money in stock: %.2f' % inStock
			money -= (hand * p + (hand * p * (5.0 / 10000)))
			print '8-money in hand: %.2f' % money
			record.append((money, inStock, money + inStock, r.stockdate))
			print 'rate %.2f' % (((money + inStock) - 10000) / 10000)
		dayIndex += 1
		print '7-money in stock: %.2f' % inStock
		print '8-money in hand: %.2f' % money
		print 'total money: %.2f'%(money+inStock)
		print 'rate %.2f' % (((money + inStock) - 10000) / 10000)
	return record


def simulateTransactionCorrected():
	money = 10000
	all_results = readSimpleResult()
	bestResults = []
	for i in range(0, len(all_results)):
		bestResults.append(all_results[i][1])
	date_data = readDataFromDateDir('data_date')
	hand = 0
	inStock = 0
	dayIndex = 0
	tomorrow2Buy = None
	tomorrow2Sell = None
	record = []
	todayToBuy = None
	acceptableRate = 0.02
	buyPrice = 0.0
	sellPrice = 0.0
	for r in bestResults[50:]:
		id = r[0]
		date = r[2]
		print '+++++++++++++++++++++++++++++++++++++++++++'
		print '0-today is: ' + date
		print 'day index: %d' % dayIndex
		todayToBuy = id
		if dayIndex == 0:
			print '2.5-first day'
			print '2.5-first day'
			tomorrow2Buy = id
			tomorrow2Sell = None
		else:
			todayToBuy = tomorrow2Buy
			tomorrow2Buy = id
			todayToSell = tomorrow2Sell
			tomorrow2Sell = todayToBuy
			if todayToSell != None:
				if todayToSell == todayToBuy:
					print '3.2-same stock as yesterday ' + todayToSell + ' no need to transaction'
					dayIndex += 1
					continue
				if todayToSell not in date_data[date]:
					print '3.5-stock: ' + todayToSell + ' stopped or no data, pass today transaction'
					todayToBuy = None
					tomorrow2Sell = todayToSell
					todayToSell = None
					dayIndex += 1
					continue
				sell = date_data[date][todayToSell]
				print '4-sell price: %.2f' % (sell.stockprice * 100)
				raisePrice=(sell.stockprice - buyPrice)
				income=(sell.stockprice - buyPrice)*hand*100
				raiseRate=raisePrice / buyPrice
				fee=(hand * sell.stockprice * 100 * (5.0 / 10000))
				print '4.05-stock: ' + todayToSell + ' fee is %.2f' % fee
				print '4.05-stock: ' + todayToSell + ' raise amount is %.2f' % income
				print '4.1-stock: ' + todayToSell + ' raise rate is %.2f' % raiseRate
				if raiseRate >-0.05 and raiseRate<0.015 :
					print '4.2-stock: ' + todayToSell + ' not reach %.2f' % acceptableRate
					dayIndex += 1
					tomorrow2Sell = todayToSell
					todayToSell = None
					todayToBuy = None
					continue
				money += (hand * sell.stockprice * 100 - (hand * sell.stockprice * 100 * (5.0 / 10000)))
				print '4.5-sell: %d' % hand
				print '5-money in hand: %.2f' % money
				hand = 0
				inStock = 0
				print 'rate %.2f' % (((money + inStock) - 10000) / 10000)
				todayToSell = None
			if todayToBuy not in date_data[date]:
				print '0.5-stock to buy: ' + id + ' stopped or no data,pass today transaction'
				dayIndex += 1
				todayToBuy = None
				tomorrow2Sell = None
				if todayToSell != None:
					record.append((money, inStock, money + inStock, datetime.datetime.strptime(date, '%Y-%m-%d')))
				continue
			buyPrice=date_data[date][todayToBuy].stockprice
			p = date_data[date][todayToBuy].stockprice * 100
			hand = int(money / p)
			print '1-ready to buy: ' + todayToBuy
			print '2-buy price is: %.2f' % p
			print '6-buy in: %d' % hand
			inStock = hand * p
			print '7-money in stock: %.2f' % inStock
			money -= (hand * p + (hand * p * (5.0 / 10000)))
			print '8-money in hand: %.2f' % money
			print 'rate %.2f' % (((money + inStock) - 10000) / 10000)
		record.append((money, inStock, money + inStock, datetime.datetime.strptime(date, '%Y-%m-%d')))
		dayIndex += 1
	print '7-money in stock: %.2f' % inStock
	print '8-money in hand: %.2f' % money
	print 'total money: %.2f'%(money+inStock)
	print 'rate %.2f' % (((money + inStock) - 10000) / 10000)
	return record


if __name__ == '__main__':
	# stocks=fetchOneDayDataFromMyServer(date='2016-08-09')
	# writeStocksToFile('data_date_new/2016-08-09.txt',stocks)
	# simulateTransaction()
	# record = simulateTransactWithOriScore()
	# data=readStockDataFromDirs('data_clean')
	# test=data['000916']
	# for i in range(20,len(test)):
	# 	r=corrTest({'000916':test[0:i]})
	# 	print str(r)+test[i].stockdate.strftime('%Y-%m-%d')
	# recalc()
	# getBestStockByAverageCompScore()
	# getAllStockID()
	# crawlTodayStock('2016-09-06')
	# stockDic=readStockDataFromDirs('data_clean')
	# deleteOneDayStockData(['2015-08-25'])
	# corrTest(stockDic)
	# result = comprehensiveTest()
	# writeResultToFile(result, 'result/2016-08-29.txt')
	# deltaPriceTest()
	# 	plotAStock(readStockDataFromFile('data_clean/000863.txt'))
	# 	plotAStock(readStockDataFromFile('data_clean/000501.txt'002120),'2')
	# print statisticBestStock()
	# getOneStockRank('000001')
	# 	sn=crawlStockIDAndName()
	# 	writeIDAndNameFile(sn,'id/id.txt')
	# 	print (datetime.datetime.today()-datetime.datetime.strptime('2016-08-16','%Y-%m-%d')).days
	# 	print corrTest(stockIdList = readStockDataFromDirs('data_clean'))
	pass
# stockDic = readDateStockDataFromDirs('data_date')
# cleanData(stockDic, 'data_clean/')
# for stock in stocks:
# 	print stock

# print sim(price,score)
