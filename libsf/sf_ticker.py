#!/usr/bin/env python

# a simple client to interact with the stockfighters websocket API

import json
import websocket

from libsf import sf_api
from libsf import sf_utils


class SFTicker(object):
	"""Access to the stockfighters websocket API."""

	def __init__(self, account, venue, stock=None, debug=0):
		self.kwargs_ = {
			'account': account,
			'venue': venue,
			'stock': stock,
		}
		self.debug_ = debug
		self.ws_url_ = {}
		self.ws_ = {}
		# init the ws sockets
		self.stop()

	def start(self):
		self.stop()
		for ticker, template in sf_api.WEBSOCKET_URL_TEMPLATES.iteritems():
			if ('stock' in sf_utils.get_template_keys(template) and
					self.kwargs_['stock'] is None):
				# do not open stock-based tickers if no stock was added
				continue
			self.ws_url_[ticker] = (sf_api.WEBSOCKET_URL + '/' +
					sf_api.WEBSOCKET_URL_TEMPLATES[ticker].substitute(**self.kwargs_))
			self.open(ticker)

	def open(self, ticker):
		if ticker in self.ws_:
			self.stop(ticker)
		self.ws_[ticker] = websocket.create_connection(self.ws_url_[ticker],
				header=sf_api.WEBSOCKET_HEADERS)

	def stop(self, ticker=None):
		if ticker is not None:
			# close only one ws
			if ticker not in self.ws_:
				return -1
			self.ws_[ticker].close()
			del self.ws_[ticker]
			return
		# close all ws
		self.ws_url_ = {}
		for ticker in self.ws_:
			self.ws_[ticker].close()
		self.ws_ = {}

	def get_rfds(self):
		rfds = []
		for ticker in self.ws_:
			rfds.append(self.ws_[ticker])
		return rfds

	def get_ws(self, ticker):
		if ticker not in self.ws_:
			return -1
		return self.ws_[ticker]

	def get_fileno(self, ticker):
		if ticker not in self.ws_:
			return -1
		return self.ws_[ticker].fileno()

	def recv(self, ticker):
		if ticker not in self.ws_:
			return -1, 'invalid ticker'
		try:
			result = self.ws_[ticker].recv()
		except websocket.WebSocketConnectionClosedException:
			self.open(ticker)
			return -1, 'websocket failure (%s)' % ticker
		try:
			res = json.loads(result)
		except ValueError:
			return -1, 'invalid json value ("%s")' % result
		return 0, res
