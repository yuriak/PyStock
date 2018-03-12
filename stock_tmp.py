# -*- coding:utf-8 -*-
# from stock_core import *
# if __name__ == '__main__':
#     crawlTodayStock('2016-08-29')
# import MySQLdb
# import pandas as pd
# from datetime import datetime
# from dateutil.parser import parse
# import numpy as np
# data = []
# db = MySQLdb.connect("localhost", "root", "", "stockdb")
# cursor = db.cursor()
# # cursor.execute("select DISTINCT stockdate from stocktable order by stockdate")
# cursor.execute("select DISTINCT stockid from stocktable group by stockid")
# rows = cursor.fetchall()
# for row in rows:
# 	cursor.execute("select * from stocktable where stockid='" + row[0] + "' group by stockdate order by stockdate")
# 	srows = cursor.fetchall()
# 	for srow in srows:
# 		data.append({'id': srow[0], 'stockid': srow[1], 'stockname': srow[2], 'stockprice': srow[3], 'stockscore': srow[4], 'stockadvice': srow[5], 'stockdate': srow[6]})
# df = pd.DataFrame(data)
# print df.shape
import urllib
import urllib2
import json

def post(url, data):
	req = urllib2.Request(url,data)
	# data = urllib.urlencode(data)
	# print data

	# enable cookie
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	# req.add_header('Origin','http://m.ctrip.com')
	# req.add_header('User-Agent','Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36')
	# req.add_header('Cookie','_abtest_userid=43f76300-afa1-404d-807e-9ee0a31add3f; adscityen=Huhehaote; FD_SearchHistorty={"type":"S","data":"S%24%u5317%u4EAC%28BJS%29%24BJS%242017-02-15%24%u957F%u6C99%28CSX%29%24CSX%24%24%24"}; traceExt=campaign=CHNbaidu81&adid=index; appFloatCnt=7; FlightIntl=Search=%5B%22Beijing%7C%E5%8C%97%E4%BA%AC(BJS)%7C1%7CBJS%7C480%22%2C%22Melbourne%7C%E5%A2%A8%E5%B0%94%E6%9C%AC(%E6%BE%B3%E5%A4%A7%E5%88%A9%E4%BA%9A)(MEL)%7C358%7CMEL%7C660%22%2C%222017-02-14%22%5D; __zpspc=9.7.1480422083.1480422295.3%231%7Cbaidu%7Ccpc%7Cbaidu81%7C%25E6%2590%25BA%25E7%25A8%258B%7C%23; Union=SID=155952&AllianceID=4897&OUID=baidu81|index|||; Session=SmartLinkCode=U155952&SmartLinkKeyWord=&SmartLinkQuary=&SmartLinkHost=&SmartLinkLanguage=zh; _gat=1; _fpacid=09031111310411842509; GUID=09031111310411842509; NSC_WT_Hbufxbz_8443=ffffffff0907d30645525d5f4f58455e445a4a423660; _ga=GA1.2.1098760174.1476448667; _bfa=1.1476448664551.25p5l4.1.1480420743494.1480424761691.6.41; _bfs=1.7; MKT_Pagesource=H5; _bfi=p1%3D600003404%26p2%3D600003404%26v1%3D41%26v2%3D40; _jzqco=%7C%7C%7C%7C1480340695131%7C1.1513396824.1476448667112.1480424801229.1480424838867.1480424801229.1480424838867.undefined.0.0.36.36')
	req.add_header('Content-Type', 'application/json')
	response = opener.open(req, data)
	# response=urllib2.urlopen(req)
	return response.read()


def main():
	posturl = "https://sec-m.ctrip.com/restapi/soa2/11782/Flight/International/FlightListV2/Query?_fxpcqlniredt=09031111310411842509"
	# data = {'email': 'myemail', 'password': 'mypass', 'autologin': '1', 'submit': '登 录', 'type': ''}
	datastr='{"grade":0,"osource":2,"params":[{"typ":1,"val":7},{"typ":3,"val":1},{"typ":4,"val":"dep=,ari=MEL"}],"psglst":[{"psgtype":1,"psgcnt":"1"}],"prdid":"","segno":1,"segs":[{"dcity":"BJS","acity":"MEL","ddate":"2017-02-15","segno":1}],"sortinfo":{"idx":1,"size":100,"ordby":105,"meyordby":2,"dir":2,"token":""},"triptype":1,"ver":0,"head":{"cid":"09031111310411842509","ctok":"","cver":"1.0","lang":"01","sid":"8888","syscode":"09","auth":null,"extension":[{"name":"protocal","value":"http"}]},"contentType":"json"}'
	# data=json.loads(datastr)
	result=post(posturl, datastr)
	result=json.loads(result)
	for f in result['segs']:
		for info in f['flgs']:
			if info['basinfo']['flgno']=='HU483'or info['basinfo']['flgno'] == 'QF108':
				print  info['basinfo']['flgno']+':'+str(f['policys'][0]['prices'][0]['price'])
	# print len(result['segs'])

def postTest():
	url="http://www.cninfo.com.cn/cninfo-new/announcement/query"


if __name__ == '__main__':
	# main()
	import re
	ptn=re.compile(u'.*(\d{4})年(\d{2})月(\d{2})日.*')
	print ptn.search(u'[诊断日期:2016年05月12日 17:25]').groups()
