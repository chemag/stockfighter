#!/usr/bin/env python

# libsf plotting device

import dateutil
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import time


import inspect
LOGFILE = '/tmp/logfile.py'
import os
try:
	os.remove(LOGFILE)
except OSError:
	pass
def MYLOG(funname, **kwargs):
	with open(LOGFILE, 'a+') as f:
		f.write('self.%s(%s)\n' % (funname,
				', '.join(['%s=%s' % (key, ('"%s"' % val)
				if type(val) in (unicode, str) else val)
				for key, val in kwargs.iteritems()])))
		print('self.%s(%s)\n' % (funname,
				', '.join(['%s=%s' % (key, ('"%s"' % val)
				if type(val) in (unicode, str) else val)
				for key, val in kwargs.iteritems()])))

class SFPlot(object):
	"""Simple matplotlib-based plotter."""

	MAX_LEN = 100
	def __init__(self, local_ts=True):
		self.redraw_last_ = 0
		self.redraw_period_ = 0.5
		self.local_ts_ = local_ts
		self.tsi_ = 0
		# ticker data
		self.ticker_ask_ = []
		self.ticker_ask_ts_ = []
		self.ticker_bid_ = []
		self.ticker_bid_ts_ = []
		# outstanding order data
		self.wanted_ts_ = []
		self.wanted_ask_ = []
		self.wanted_bid_ = []
		# execution data
		self.exec_buy_ = []
		self.exec_buy_ts_ = []
		self.exec_sell_ = []
		self.exec_sell_ts_ = []
		# position data
		self.pos_ts_ = []
		self.pos_stock_ = []
		self.pos_money_ = []
		self.pos_total_ = []
		# create the figure and the axes
		self.fig_ = plt.figure()
		self.gs_ = gridspec.GridSpec(2, 1, height_ratios=[3, 2])
		# axes
		self.ticker_ax_ = plt.subplot(self.gs_[0])
		self.pos_stock_ax_ = plt.subplot(self.gs_[1])
		self.pos_money_ax_ = self.pos_stock_ax_.twinx()
		# ticker plots
		self.ticker_plot_ask_, = self.ticker_ax_.step([], [], 'g')
		self.ticker_plot_bid_, = self.ticker_ax_.step([], [], 'r')
		self.wanted_plot_ask_, = self.ticker_ax_.step([], [], 'r.')
		self.wanted_plot_bid_, = self.ticker_ax_.step([], [], 'g.')
		# position plots
		self.pos_plot_total_, = self.pos_money_ax_.step([], [], 'g')
		self.pos_plot_money_, = self.pos_money_ax_.step([], [], 'r')
		self.pos_plot_stock_, = self.pos_stock_ax_.step([], [], 'b')
		# draw and show them
		self.fig_.canvas.draw()
		plt.show(block=False)

	def inc_ts(self):
		self.tsi_ += 1
		self.redraw()

	def get_ts(self, tss):
		if self.local_ts_:
			return self.tsi_
		else:
			ts = float(dateutil.parser.parse(tss).strftime("%s.%f"))
			return ts

	# quote =
	# {
	# u'lastTrade': u'2015-12-27T23:53:53.313535042Z',
	# u'last': 9703,
	# u'askSize': 42,
	# u'symbol': u'ADSL',
	# u'venue': u'DKNEX',
	# u'lastSize': 117,
	# u'bidDepth': 0,
	# u'ask': 9958,
	# u'bidSize': 0,
	# u'askDepth': 126,
	# u'quoteTime': u'2015-12-27T23:53:53.348559452Z'
	# }
	def add_tickertape(self, quote):
		MYLOG(inspect.stack()[0][3], quote=quote)
		ts = self.get_ts(quote['quoteTime'])
		if quote.get('ask', 0) != 0:
			self.ticker_ask_.append(quote['ask'])
			self.ticker_ask_ts_.append(ts)
		if quote.get('bid', 0) != 0:
			self.ticker_bid_.append(quote['bid'])
			self.ticker_bid_ts_.append(ts)
		self.redraw()

	# order = {
	#  u'direction': u'buy',
	#  u'ok': True,
	#  u'ts': u'2015-12-27T23:57:28.808262222Z',
	#  u'fills': [{u'price': 8415, u'ts': u'2015-12-27T23:57:28.808264977Z',
	#              u'qty': 100}],
	#  u'originalQty': 100,
	#  u'orderType': u'market',
	#  u'symbol': u'MWC',
	#  u'venue': u'CVCEX',
	#  u'account': u'SE55020649',
	#  u'qty': 0,
	#  u'id': 529,
	#  u'totalFilled': 100,
	#  u'open': False,
	#  u'price': 0
	# }
	def add_execution(self, order):
		MYLOG(inspect.stack()[0][3], order=order)
		# get the latest fill
		fill = order['fills'][-1]
		ts = self.get_ts(fill['ts'])
		if order['direction'] == 'buy':
			self.exec_buy_.append(fill['price'])
			self.exec_buy_ts_.append(ts)
		elif order['direction'] == 'sell':
			self.exec_sell_.append(fill['price'])
			self.exec_sell_ts_.append(ts)
		self.redraw()

	def add_outstanding(self, ts, ask_size, ask_price, bid_size, bid_price):
		MYLOG(inspect.stack()[0][3], ask_size=ask_size, ask_price=ask_price,
				bid_size=bid_size, bid_price=bid_price)
		ts = self.get_ts(ts)
		self.wanted_ts_.append(ts)
		self.wanted_ask_.append(ask_price)
		self.wanted_bid_.append(bid_price)
		self.redraw()

	def add_position(self, ts, nav_stock, nav_money, est_money):
		MYLOG(inspect.stack()[0][3], ts=ts, nav_stock=nav_stock,
				nav_money=nav_money, est_money=est_money)
		ts = self.get_ts(ts)
		self.pos_ts_.append(ts)
		self.pos_stock_.append(nav_stock)
		self.pos_money_.append(nav_money / 100)  # convert to dollars
		self.pos_total_.append(est_money / 100)  # convert to dollars
		self.redraw()

	def redraw(self):
		ts = time.time()
		if (ts - self.redraw_last_) < self.redraw_period_:
			return
		self.redraw_last_ = ts
		# clean up axes
		self.ticker_ax_.clear()
		self.pos_money_ax_.clear()
		self.pos_stock_ax_.clear()
		# get the (common) x axis
		# TODO(chema): subset x axis
		x_all = (self.ticker_ask_ts_ + self.ticker_bid_ts_ + self.wanted_ts_ +
				self.exec_buy_ts_ + self.exec_sell_ts_ + self.pos_ts_)
		if not x_all:
			return
		self.MIN_X_LENGTH = 100
		xmin = int(math.floor(min(x_all)))
		xmax = max(xmin + self.MIN_X_LENGTH, int(math.ceil(max(x_all))))
		self.XTICKS = 100
		x = range(xmin, xmax, max(1, int((xmax - xmin) / self.XTICKS)))
		# print price graph
		self.ticker_ax_.set_xlabel('time')
		self.ticker_ax_.set_ylabel('price (cents)')
		self.ticker_ax_.set_xbound(xmin, xmax)
		# set the new price data
		self.ticker_plot_ask_, = self.ticker_ax_.step(
				self.ticker_ask_ts_, self.ticker_ask_,
				where='post',
				mfc='none',
				color='darkgreen', linestyle='-', marker='o')
		self.ticker_plot_bid_, = self.ticker_ax_.step(
				self.ticker_bid_ts_, self.ticker_bid_,
				where='post',
				mfc='none',
				color='darkred', linestyle='-', marker='o')
		self.wanted_plot_ask_, = self.ticker_ax_.step(
				self.wanted_ts_, self.wanted_ask_,
				where='post',
				color='lawngreen', linestyle='-', marker='x')
		self.wanted_plot_bid_, = self.ticker_ax_.step(
				self.wanted_ts_, self.wanted_bid_,
				where='post',
				color='red', linestyle='-', marker='x')
		# print position graph
		self.pos_money_ax_.set_xlabel('time')
		self.pos_money_ax_.set_ylabel('money ($)')
		self.pos_stock_ax_.set_ylabel('stock (shares)')
		self.pos_money_ax_.set_xbound(xmin, xmax)
		self.pos_stock_ax_.set_xbound(xmin, xmax)
		# set the new position data
		self.pos_plot_total_, = self.pos_money_ax_.step(
				self.pos_ts_, self.pos_total_,
				where='post',
				color='green', linewidth=3.0)
		self.pos_plot_money_, = self.pos_money_ax_.step(
				self.pos_ts_, self.pos_money_,
				where='post',
				color='green')
		self.pos_plot_stock_, = self.pos_stock_ax_.step(
				self.pos_ts_, self.pos_stock_,
				where='post',
				color='blue')

		# redraw canvas
		self.fig_.canvas.draw()

