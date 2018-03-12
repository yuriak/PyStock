# -*- coding:utf-8 -*-
import datetime
import hashlib
import re
import urllib
import urllib2
from xml import etree

from flask import *
from wechat_sdk import *
from wechat_sdk.core.conf import WechatConf
from wechat_sdk.exceptions import *
from wechat_sdk.messages import *

import stock
from stock import *
from stock_file_util import *
import sys

reload(sys)
sys.setdefaultencoding('utf8')
app = Flask(__name__)

CONFIG = {}


@app.route('/')
def index():
	return redirect(url_for('rank'))

@app.route('/rank', methods=['GET', 'POST'])
def rank():
	if request.method == 'GET':
		date = request.args.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))
		result = readOneDayResult(date)
		return render_template('rank.html', date=date, result=result)
	else:
		return redirect(url_for('index'))


@app.route('/nrank', methods=['GET', 'POST'])
def ori_rank():
	if request.method == 'GET':
		date = request.args.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))
		result = readStockDataFromFile(DATE_DATA_PATH + '/' + date + '.txt')
		result.sort(key=lambda x: x.stockscore, reverse=True)
		return render_template('n_rank.html', date=date, result=result)
	else:
		return redirect(url_for('index'))


@app.route('/detail/<id>', methods=['GET', 'POST'])
def detail(id):
	if request.method == 'GET':
		sn = readIDAndNameFile('id/id.txt')
		name = sn[id]
		if name == None:
			return redirect(url_for('rank'))
		return render_template('detail.html', id=id, name=name)
	else:
		return redirect(url_for('index'))


@app.route('/getStockData/<id>')
def getStockData(id):
	stocks = readStockDataFromFile(ID_DATA_PATH + '/' + id + '.txt')
	return json.dumps(stocks, ensure_ascii=False, default=json_default)


@app.route('/getResultData/<id>')
def getResultData(id):
	result = []
	results = readStockRankFromDir(RESULT_PATH)
	index = 0
	for r in results:
		if id in r:
			result.append([float(r[id][1]), r[id][2], int(r[id][3]), index])
			index += 1
	return json.dumps(result, ensure_ascii=False)


@app.route('/getNResultData/<id>')
def getNResultData(id):
	result = []
	results = readStockRankFromDateDataDir(DATE_DATA_PATH)
	index = 0
	for r in results:
		if id in r:
			result.append([float(r[id][1]), r[id][2], int(r[id][3]), index])
			index += 1
	return json.dumps(result, ensure_ascii=False)


@app.route('/logout')
def logout():
	session.pop('username')
	return redirect(url_for('index'))


def json_default(value):
	if isinstance(value, datetime.date):
		return value.strftime('%Y-%m-%d')
	else:
		return value.__dict__


def dict2object(d):
	# convert dict to object
	if '__class__' in d:
		class_name = d.pop('__class__')
		module_name = d.pop('__module__')
		module = __import__(module_name)
		class_ = getattr(module, class_name)
		args = dict((key.encode('ascii'), value) for key, value in d.items())  # get args
		inst = class_(**args)  # create new instance
	else:
		inst = d
	return inst


@app.route('/wechat', methods=['GET', 'POST'])
def wechat_auth():
	CONFIG = readWechatConfig()
	conf = WechatConf(token=CONFIG['token'],
					  appid=CONFIG['appid'],
					  appsecret=CONFIG['appsecret'],
					  encrypt_mode=CONFIG['encrypt_mode'],
					  encoding_aes_key=CONFIG['encoding_aes_key'])
	wechat = WechatBasic(conf=conf)
	if request.method == 'GET':
		token = 'kernelbooster'  # your token
		query = request.args  # GET 方法附上的参数
		signature = query.get('signature', '')
		timestamp = query.get('timestamp', '')
		nonce = query.get('nonce', '')
		echostr = query.get('echostr', '')
		s = [timestamp, nonce, token]
		s.sort()
		s = ''.join(s)
		if wechat.check_signature(signature, timestamp, nonce):
			return make_response(echostr)
		else:
			return make_response('error auth')
	else:
		body = request.data
		try:
			wechat.parse_data(body)
			id = wechat.message.id  # 对应于 XML 中的 MsgId
			target = wechat.message.target  # 对应于 XML 中的 ToUserName
			source = wechat.message.source  # 对应于 XML 中的 FromUserName
			time = wechat.message.time  # 对应于 XML 中的 CreateTime
			type = wechat.message.type  # 对应于 XML 中的 MsgType
			xml = None
			if isinstance(wechat.message, TextMessage):
				str = wechat.message.content
				ret = assambleWechatXML(str)
				xml = wechat.response_text(ret, escape=False)
			elif isinstance(wechat.message, EventMessage):
				xml=wechat.response_none()
				if wechat.message.type == 'subscribe':  # 关注事件(包括普通关注事件和扫描二维码造成的关注事件)
					key = wechat.message.key  # 对应于 XML 中的 EventKey (普通关注事件时此值为 None)
					ticket = wechat.message.ticket  # 对应于 XML 中的 Ticket (普通关注事件时此值为 None)
					xml= wechat.response_text('感谢关注KernelBooster!,该账公众号处于实验阶段,目前只开放股票推荐功能,如有问题,请联系开发者:yuriak\n输入l [yyyy-mm-dd]获得今天/[yyyy-mm-dd]天的股票推荐列表\n输入s <sid|sname> 获得最新<sid|sname>股票排名信息')
				elif wechat.message.type == 'unsubscribe':  # 取消关注事件（无可用私有信息）
					pass
				elif wechat.message.type == 'scan':  # 用户已关注时的二维码扫描事件
					key = wechat.message.key  # 对应于 XML 中的 EventKey
					ticket = wechat.message.ticket  # 对应于 XML 中的 Ticket
				elif wechat.message.type == 'location':  # 上报地理位置事件
					latitude = wechat.message.latitude  # 对应于 XML 中的 Latitude
					longitude = wechat.message.longitude  # 对应于 XML 中的 Longitude
					precision = wechat.message.precision  # 对应于 XML 中的 Precision
				elif wechat.message.type == 'click':  # 自定义菜单点击事件
					key = wechat.message.key  # 对应于 XML 中的 EventKey
				elif wechat.message.type == 'view':  # 自定义菜单跳转链接事件
					key = wechat.message.key  # 对应于 XML 中的 EventKey
				elif wechat.message.type == 'templatesendjobfinish':  # 模板消息事件
					status = wechat.message.status  # 对应于 XML 中的 Status
				elif wechat.message.type in ['scancode_push', 'scancode_waitmsg', 'pic_sysphoto', 'pic_photo_or_album', 'pic_weixin', 'location_select']:  # 其他事件
					key = wechat.message.key  # 对应于 XML 中的 EventKey
			elif isinstance(wechat.message,ImageMessage):
				url=wechat.message.picurl
				filename= url.split('/')[-2][-1:]+'_'+url.split('/')[-1]
				urllib.urlretrieve(url,'pic/'+filename+'.jpg')
				xml=wechat.response_none()
			else:
				xml = wechat.response_text(content='暂时不接受其他类型的消息')
			response = make_response(xml)
			response.content_type = 'application/xml'
			return response
		except ParseError:
			return make_response('error body text')


def assambleWechatXML(cmd):
	ret = ''
	if 's' == cmd[0]:
		args = cmd.strip().split(' ')
		if len(args) > 1:
			sid = args[1]
			result = readOneStockData(sid, datetime.datetime.today().strftime('%Y-%m-%d'))
			t= result
			ret = "代码: %s\n名称: %s\n高级排名位于前: %.2f%%\n高级分数: %.4f\n普通排名位于前: %.2f%%\n普通分数: %.2f\n建议: %s\n价格: %.2f\n日期:%s\n" % t
			ret += '<a href=\"http://www.hopinglight.com/detail/' + t[0] + '\">点击进入数据页面</a>\n'
		else:
			ret = '无效股票代码或名称'
	elif 'l' == cmd[0]:
		args = cmd.strip().split(' ')
		result = None
		if len(args) > 1:
			dt = args[1]
			if not re.match('\d{4}-\d{2}-\d{2}', dt):
				ret = '无效股票日期，请输入类似2016-09-01这样格式的日期'
			else:
				result = readTodayList(dt)
				if len(result[0]) > 0:
					ret += '高级排名:\n========\n'
					for r0 in result[0]:
						t = r0
						ret += "代码: %s\n名称: %s\n分数: %.2f\n价格: %.2f\n建议: %s\n日期: %s\n" % t
						ret += '<a href=\"http://www.hopinglight.com/detail/' + t[0] + '\">点击进入数据页面</a>\n'
						ret += '--------\n'
				if len(result[1]) > 0:
					ret += '普通排名:\n========\n'
					for r1 in result[1]:
						t = r1
						ret += "代码: %s\n名称: %s\n分数: %.2f\n价格: %.2f\n建议: %s\n日期: %s\n" % t
						ret += '<a href=\"http://www.hopinglight.com/detail/' + t[0] + '\">点击进入数据页面</a>\n'
						ret += '--------\n'
		else:
			result = readTodayList(datetime.datetime.today().strftime('%Y-%m-%d'))
			if len(result[0]) > 0:
				ret += '高级排名:\n========\n'
				for r0 in result[0]:
					t= r0
					ret += "代码: %s\n名称: %s\n分数: %.2f\n价格: %.2f\n建议: %s\n日期: %s\n" % t
					ret += '<a href=\"http://www.hopinglight.com/detail/' + t[0] + '\">点击进入数据页面</a>\n'
					ret += '--------\n'
			if len(result[1]) > 0:
				ret += '普通排名:\n========\n'
				for r1 in result[1]:
					t =  r1
					ret += "代码:%s\n名称: %s\n分数: %.2f\n价格: %.2f\n建议: %s\n日期: %s\n" % t
					ret+='<a href=\"http://www.hopinglight.com/detail/'+t[0]+'\">点击进入数据页面</a>\n'
					ret += '--------\n'
	else:
		ret = '输入l [yyyy-mm-dd]获得今天/[yyyy-mm-dd]天的股票推荐列表\n输入s <sid|sname> 获得最新<sid|sname>股票排名信息'
	return ret


def start_server(port=5000):
	WECHAT_CONFIG = readWechatConfig()
	app.secret_key = '8e88c0bdba3ea10c5cec4112fc7a1494'
	app.run(host='0.0.0.0', port=port, debug=True, threaded=True)


if __name__ == '__main__':
	# CONFIG = readWechatConfig()
	# app.secret_key = '8e88c0bdba3ea10c5cec4112fc7a1494'
	# app.run(host='0.0.0.0', debug=True, threaded=True)
	# CONFIG = readWechatConfig()
	# conf = WechatConf(token=CONFIG['token'],
	# 				  appid=CONFIG['appid'],
	# 				  appsecret=CONFIG['appsecret'],
	# 				  encrypt_mode=CONFIG['encrypt_mode'],
	# 				  encoding_aes_key=CONFIG['encoding_aes_key'])
	# wechat = WechatBasic(conf=conf)
	print assambleWechatXML('l')
