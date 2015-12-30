#!/usr/bin/env python

# a simple requests-based rest client to interact with the stockfighters API

# http://isbullsh.it/2012/06/Rest-api-in-python/

import json
import requests
import string
import sys

import sf_api
import sf_order
import sf_utils


def run_http(url, http_type, data=None, http_headers=None, debug=0):
	if debug > 0:
		print '...tx-headers(%s): %r' % (url, http_headers)
		if data is not None:
			print '...tx-post_data(%s): %r' % (url, data)
	if http_type == sf_api.GET:
		ret = requests.get(url, headers=http_headers)
	elif http_type == sf_api.POST:
		ret = requests.post(url, headers=http_headers, data=data)
	elif http_type == sf_api.DELETE:
		ret = requests.delete(url, headers=http_headers)
	if debug > 1:
		print '...rx-headers(%s): %r' % (url, ret.headers)
	# parse return
	out = ret.json()
	if not ret.ok:
		return -1, 'unsuccessful %s command: "%r"' % (
				sf_api.get_http_type_str(http_type), out['error'])
	try:
		if debug > 0:
			print '...rx-data: %s' % out
		return 0, out
	except ValueError:
		pass
	return -1, 'invalid value received: "%s"' % ret.text


class SFClient(object):
	"""Access to the stockfighters API."""

	def __init__(self, local=True, server_url=None, **kwargs):
		self.local_ = local
		self.url_ = sf_api.LOCAL_URL if local else sf_api.URL
		self.url_ += '/' + sf_api.URL_PREFIX
		# support explicit server URLs
		if server_url is not None:
			self.url_ = server_url + '/' + sf_api.URL_PREFIX
		self.debug_ = kwargs.get('debug', 0)
		self.account_ = kwargs.get('account', None)
		self.venue_ = kwargs.get('venue', None)
		self.stock_ = kwargs.get('stock', None)

	def run(self, cmd, **kwargs):
		# check the command
		if cmd not in sf_api.URL_TEMPLATES:
			return -1, 'invalid command: "%s"' % cmd
		# check required input parameters
		http_type = sf_api.URL_TEMPLATES[cmd][0]
		template = sf_api.URL_TEMPLATES[cmd][1]
		for key in sf_utils.get_template_keys(template):
			if kwargs.get(key, None) is None:
				return -1, 'error: "%s" command (%s) requires %s' % (cmd,
						sf_api.get_http_type_str(http_type), key)
		# POST data build
		data = kwargs.get('data', None) if http_type == sf_api.POST else None
		# build the url
		url = (self.url_ + '/' + template.substitute(**kwargs))
		http_headers = sf_api.HTTP_HEADERS
		return run_http(url, http_type, data, http_headers, self.debug_)

	def get_args(self, **kwargs):
		account = kwargs.get('account', self.account_)
		assert account is not None
		venue = kwargs.get('venue', self.venue_)
		assert venue is not None
		stock = kwargs.get('stock', self.stock_)
		assert stock is not None
		return account, venue, stock

	def heartbeat(self):
		return self.run('heartbeat')

	def venue_list(self):
		return self.run('venue_list')

	def venue_heartbeat(self, **kwargs):
		account, venue, stock = self.get_args(**kwargs)
		return self.run('venue_heartbeat', venue=venue)

	def venue_list_stocks(self, **kwargs):
		account, venue, stock = self.get_args(**kwargs)
		return self.run('venue_list_stocks', venue=venue)

	def order_list(self, **kwargs):
		account, venue, stock = self.get_args(**kwargs)
		return self.run('order_list', venue=venue, stock=stock)

	def order_add(self, direction, orderType, price, qty, **kwargs):
		account, venue, stock = self.get_args(**kwargs)
		# create the order
		order_d = {}
		order_d['account'] = account
		order_d['venue'] = venue
		order_d['stock'] = stock
		order_d['direction'] = direction
		order_d['qty'] = qty
		order_d['price'] = price
		order_d['orderType'] = orderType
		order = sf_order.create_order(**order_d)
		# run the command
		data = json.dumps(order.todict_short())
		return self.run('order_add', venue=venue, stock=stock, data=data)

	def order_status(self, order_id, **kwargs):
		account, venue, stock = self.get_args(**kwargs)
		return self.run('order_status', venue=venue, stock=stock, order=order_id)

	def order_cancel(self, order_id, **kwargs):
		account, venue, stock = self.get_args(**kwargs)
		return self.run('order_cancel', venue=venue, stock=stock, order=order_id)

	def stock_get_quote(self, **kwargs):
		account, venue, stock = self.get_args(**kwargs)
		return self.run('stock_get_quote', venue=venue, stock=stock)

	def account_stock_status(self, **kwargs):
		account, venue, stock = self.get_args(**kwargs)
		return self.run('account_stock_status', venue=venue, account=account,
				stock=stock)

	def account_status(self, **kwargs):
		account, venue, stock = self.get_args(**kwargs)
		return self.run('account_status', venue=venue, account=account)

	# short-cut commands
	def order_add_bid(self, **kwargs):
		return self.order_add(direction=sf_api.DIRECTION_BUY, **kwargs)

	def order_add_ask(self, **kwargs):
		return self.order_add(direction=sf_api.DIRECTION_SELL, **kwargs)

