# -*- coding:utf-8 -*-
import MySQLdb
import pandas as pd
from datetime import datetime
from datetime import date
from dateutil.parser import parse
import numpy as np
import json


def updateOneDayScore(result):
	db = MySQLdb.connect("localhost", "root", "", "stockdb_clean")
	cursor = db.cursor()
	for index, value in result.iterrows():
		cursor.execute("update stocktable set myscore=%f where id=%d " % (value['myscore'], value['id']))
	db.commit()
	db.close()


def getDataFromDatabase(datebetween=['2015-11-02', datetime.strftime(datetime.today(), '%Y-%m-%d')]):
	db = MySQLdb.connect("localhost", "root", "", "stockdb_clean")
	df = pd.read_sql("select id,stockid,stockprice,stockscore,stockdate from stocktable where stockdate between '" + datebetween[0] + "' and '" + datebetween[1] + "' and stockprice>0", db)
	return df


def pre_process_data(data):
	max_score = df.stockscore.max()
	min_score = df.stockscore.min()
	mean_score = df.stockscore.mean()
	scorelist = data.stockscore.as_matrix()
	standarized_sc = standardrizScore(max_score, min_score, mean_score, scorelist)
	data['standarized_score'] = standarized_sc
	delta_price = np.zeros(data.shape[0])
	delta_price[1:] = data.stockprice[1:].as_matrix() - data.stockprice[0:-1].as_matrix()
	delta_score = np.zeros(data.shape[0])
	delta_score[1:] = data.stockscore[1:].as_matrix() - data.stockscore[0:-1].as_matrix()
	data['delta_price'] = delta_price
	data['delta_score'] = delta_score
	return data

def standardrizScore(max, min, mean, scorelist):
	paramList = np.array([max, min, mean])
	result = np.zeros(scorelist.shape[0])
	if max - min == 0:
		return result
	else:
		result = (scorelist - mean) / (max - min)
	return result


def corr_analysis(data, group_size=10):
	corrs = np.zeros(data.shape[0] / group_size)
	group_index = np.arange(data.shape[0] / group_size)
	max_index = data.shape[0]
	min_index = 1
	delta_days = np.arange(group_index.shape[0], dtype='float32')
	for i in group_index:
		a = 0
		mean_days = 0
		if i == group_index[0]:
			a = data[min_index:group_size].corr(method='pearson').as_matrix()[3][2]
			mean_days = (date.today() - data[min_index:group_size].stockdate).mean().days
		elif i == group_index[-1]:
			a = data[i * group_size:max_index].corr(method='pearson').as_matrix()[3][2]
			mean_days = (date.today() - data[i * group_size:max_index].stockdate).mean().days
		else:
			a = data[i * group_size:i * group_size + group_size].corr(method='pearson').as_matrix()[3][2]
			mean_days = (date.today() - data[i * group_size:i * group_size + group_size].stockdate).mean().days
		if np.isnan(a):
			corrs[i] = 0
		else:
			corrs[i] = a
		delta_days[i] = mean_days
	dweights = 1 / (1 + (delta_days / group_index.shape[0]) ** 2) * (2 / np.pi)
	gweights = (2 * (np.arange(0, group_index.shape[0], dtype='float64') + 1) / group_index.shape[0] ** 2)
	wcorr = ((dweights + gweights) / 2).dot(corrs)
	scorr = corrs.sum() / corrs.shape[0]
	return corrs, wcorr, scorr, gweights, dweights


def price_analysis(data):
	values = data.delta_price.as_matrix()
	growthValue = values[np.where(values > 0)]
	decentValue = values[np.where(values <= 0)]
	growthCount = growthValue.shape[0]
	decentCount = decentValue.shape[0]
	fluctuation = 0.0
	growthAmount = growthValue.sum()
	decentAmount = decentValue.sum()
	fluctuatility = float(growthCount - decentCount) / values.shape[0]
	if (abs(decentAmount) + growthAmount) == 0.0:
		fluctuation = 0.0
	else:
		fluctuation = values.sum() / (abs(decentAmount) + growthAmount)
	ratio = (fluctuatility * 0.2 + fluctuation * 0.8)
	return fluctuatility, fluctuation, ratio


def analysisOneDay(day):
	result_frame = df[datetime.strftime(day, '%Y-%m-%d')].copy()
	result_frame['myscore'] = 0.0
	result_frame.index = result_frame.stockid
	if result_frame.shape[0] == 0:
		return None
	ddata = df[:day]
	for key in result_frame.index:
		kdata = ddata[ddata.stockid == key].copy()
		if kdata.shape[0] < 20:
			oriscore = result_frame.loc[key].stockscore
			result_frame.loc[key, 'myscore'] = oriscore
			continue
		data = pre_process_data(kdata)
		corr = corr_analysis(data)[1]
		aratio = price_analysis(data)[2]
		comp = data.stockscore[-1] + (corr * 0.5 + aratio * 0.5)
		result_frame.loc[key, 'myscore'] = comp
	return result_frame


if __name__ == '__main__':
	df = getDataFromDatabase()
	df.index = pd.DatetimeIndex(df.stockdate)
	all_stock_id = df.groupby('stockid').groups.keys()
	all_stock_id.sort()
	all_stock_date = df.groupby('stockdate').groups.keys()
	all_stock_date.sort()
	for day in all_stock_date[21:]:
		result = analysisOneDay(day)
		updateOneDayScore(result)
		print day