# -*- coding:utf-8 -*-
import datetime
from flask import *

import stock
from stock import *
from stock_file_util import *

app = Flask(__name__)


@app.route('/')
def index():
	if 'username' in session:
		return redirect(url_for('rank'))
	else:
		return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		error = request.args.get('error', -1)
		return render_template('login.html', error=error)
	else:
		if request.form['username'] == 'pystock' and request.form['password'] == 'redstone':
			print 'in'
			session['username'] = 'pystock'
			return redirect(url_for('rank'))
		else:
			return redirect(url_for('login', error=0))


@app.route('/rank', methods=['GET', 'POST'])
def rank():
	if request.method == 'GET':
		if 'username' in session:
			date = request.args.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))
			result = readOneDayResult(date)
			return render_template('rank.html', date=date, result=result)
		else:
			return redirect(url_for('index'))
	else:
		return redirect(url_for('index'))


@app.route('/nrank', methods=['GET', 'POST'])
def ori_rank():
	if request.method == 'GET':
		if 'username' in session:
			date = request.args.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))
			result = readStockDataFromFile(DATE_DATA_PATH + '/' + date + '.txt')
			result.sort(key=lambda x: x.stockscore, reverse=True)
			return render_template('n_rank.html', date=date, result=result)
		else:
			return redirect(url_for('index'))
	else:
		return redirect(url_for('index'))


@app.route('/detail/<id>', methods=['GET', 'POST'])
def detail(id):
	if request.method == 'GET':
		if 'username' in session:
			sn = readIDAndNameFile('id/id.txt')
			name = sn[id]
			# result = []
			if name == None:
				return redirect(url_for('rank'))
			# stocks = readStockDataFromFile(ID_DATA_PATH + '/' + id + '.txt')
			# results = readStockRankFromDir(RESULT_PATH)
			# for r in results:
			# 	if id in r:
			# 		result.append((r[id][1], r[id][2]))
			# if len(result)==0:
			# 	return redirect(url_for('rank'))
			return render_template('detail.html', id=id, name=name)
		else:
			return redirect(url_for('index'))
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

def start_server(port=5000):
	app.secret_key = '8e88c0bdba3ea10c5cec4112fc7a1494'
	app.run(host='0.0.0.0', debug=True, threaded=True)

if __name__ == '__main__':
	app.secret_key = '8e88c0bdba3ea10c5cec4112fc7a1494'
	app.run(host='0.0.0.0', debug=True, threaded=True)
