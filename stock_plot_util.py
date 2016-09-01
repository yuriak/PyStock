# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
from stock_core import *
from stock_file_util import readStockDataFromFile

plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题


#
# if __name__ == '__main__':
# 	scores = [stock.stockscore for stock in readStockDataFromFile('data_id/000001.txt')]
# 	prices = [stock.stockprice for stock in readStockDataFromFile('data_id/000001.txt')]
# 	plt.plot(scores)
# 	plt.plot(prices)
# 	plt.ylabel('numbers')
# 	plt.show()


def plotAStock(stocks):
	scores = []
	prices = []
	dates = []
	advices = []
	for stock in stocks:
		scores.append(stock.stockscore)
		prices.append(stock.stockprice)
		dates.append(stock.stockdate)
		advices.append(stock.stockadvice)
	# plt.plot(scores)
	# plt.plot(prices)
	# plt.plot(advices)
	plt.title(stocks[0].stockname.decode('utf-8'))
	plt.plot_date(dates, scores, linestyle='-')
	plt.plot_date(dates, prices, linestyle='-')
	plt.plot_date(dates, advices, linestyle='-')
	# ax=plt.subplot(1,1,1)
	# ax.scatter(prices,dates,c='red')
	# ax.scatter(scores,dates,c='green')
	# ax.scatter(advices,dates,c='blue')
	# ax.legend(handles[::-1], labels[::-1])
	plt.show()


def plotIncome():
	record = simulateTransactWithOriScoreCorrected()
	# record=simulateTransactionCorrected()
	money = []
	inStock = []
	total = []
	dates = []
	rate = []
	for r in record:
		money.append(r[0])
		inStock.append(r[1])
		total.append(r[2])
		dates.append(r[3])
	plt.plot_date(dates, money, linestyle='-')
	plt.plot_date(dates, inStock, linestyle='-')
	plt.plot_date(dates, total, linestyle='-')
	plt.show()


if __name__ == '__main__':
	plotIncome()
