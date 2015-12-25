#!/usr/bin/env python

import datetime
import json
import time
import sys

import sf_api

class SFOrderFill(object):
	def __init__(self, price, qty, ts):
		self.price = price
		self.qty = qty
		self.ts = ts

	def dictionary(self):
		# create a valid dictionary for this order
		d = {
			'price': self.price_,
			'qty': self.qty_,
			'ts': ts.isoformat(),
		}
		return d

	# getters/setters
	@property
	def price(self):
		return self.price_ if self.price_ is not None else None
	@price.setter
	def price(self, value):
		self.price_ = int(value)

	@property
	def qty(self):
		return self.qty_ if self.qty_ is not None else None
	@qty.setter
	def qty(self, value):
		self.qty_ = int(value)

	@property
	def ts(self):
		return self.ts_ if self.ts_ is not None else None
	@ts.setter
	def ts(self, value):
		assert isinstance(value, (datetime.datetime))
		self.ts_ = value


class SFOrder(object):
	DIRECTION_BUY, DIRECTION_SELL, DIRECTION_TOTAL = range(3)
	TYPE_LIMIT, TYPE_IOC, TYPE_FOK, TYPE_MARKET, TYPE_TOTAL = range(5)
	def __init__(self, venue, stock, direction, qty, orderType, account,
			price=None, **kwargs):
		self.venue = venue
		self.stock = stock
		self.direction = direction
		self.qty = qty
		self.price = price
		self.orderType = orderType
		self.account = account

	@classmethod
	def fromdict(cls, order_d):
		# ensure the right fields exist
		assert 'venue' in order_d
		assert 'stock' in order_d
		assert 'direction' in order_d
		assert 'qty' in order_d
		assert 'orderType' in order_d
		if order_d['orderType'] in (sf_api.LIMIT, sf_api.IOC, sf_api.FOK):
			assert 'price' in order_d
		assert 'account' in order_d
		return cls(**order_d)

	def start(self):
		self.ok_ = True
		self.id = int(time.time())
		self.originalQty = self.qty
		self.ts = datetime.datetime.now()
		self.fills = []
		self.totalFilled = 0
		self.open = True

	def add_fill(self, fill):
		self.qty -= fill.qty
		self.fills.append(fill)
		self.totalFilled += fill.qty

	def todict_short(self):
		# create a valid dictionary for this order
		d = {
			'stock': self.stock,
			'venue': self.venue,
			'direction': sf_api.get_direction_str(self.direction),
			'qty': self.qty,
			'orderType': sf_api.get_order_type_str(self.orderType),
			'account': self.account,
		}
		# add optional fields
		if self.price is not None:
			d['price'] = self.price
		return d

	def todict(self):
		# create a valid dictionary for this order
		d = {
			'ok': self.ok,
			'stock': self.stock,
			'venue': self.venue,
			'direction': sf_api.get_direction_str(self.direction),
			'originalQty': self.originalQty,
			'qty': self.qty,
			'orderType': sf_api.get_order_type_str(self.orderType),
			'id': self.id,
			'account': self.account,
			'ts': self.ts.isoformat(),
			'fills': [fill.dictionary() for fill in self.fills],
			'totalFilled': self.totalFilled,
			'open': self.open,
		}
		# add optional fields
		if self.price is not None:
			d['price'] = self.price
		return d

	# getters/setters
	@property
	def venue(self):
		return self.venue_ if self.venue_ is not None else None
	@venue.setter
	def venue(self, value):
		self.venue_ = value

	@property
	def stock(self):
		return self.stock_ if self.stock_ is not None else None
	@stock.setter
	def stock(self, value):
		self.stock_ = value

	@property
	def direction(self):
		return self.direction_ if self.direction_ is not None else None
	@direction.setter
	def direction(self, value):
		self.direction_ = sf_api.get_direction(value)

	@property
	def qty(self):
		return self.qty_ if self.qty_ is not None else None
	@qty.setter
	def qty(self, value):
		self.qty_ = int(value)

	@property
	def price(self):
		return self.price_ if self.price_ is not None else None
	@price.setter
	def price(self, value):
		self.price_ = int(value) if value is not None else None

	@property
	def orderType(self):
		return self.orderType_ if self.orderType_ is not None else None
	@orderType.setter
	def orderType(self, value):
		self.orderType_ = sf_api.get_order_type(value)

	@property
	def account(self):
		return self.account_ if self.account_ is not None else None
	@account.setter
	def account(self, value):
		self.account_ = value

	@property
	def ok(self):
		return self.ok_ if self.ok_ is not None else None
	@ok.setter
	def ok(self, value):
		self.ok_ = value

	@property
	def originalQty(self):
		return self.originalQty_ if self.originalQty_ is not None else None
	@originalQty.setter
	def originalQty(self, value):
		self.originalQty_ = int(value)

	@property
	def id(self):
		return self.id_ if self.id_ is not None else None
	@id.setter
	def id(self, value):
		self.id_ = value

	@property
	def ts(self):
		return self.ts_ if self.ts_ is not None else None
	@ts.setter
	def ts(self, value):
		assert isinstance(value, (datetime.datetime))
		self.ts_ = value

	@property
	def fills(self):
		return self.fills_ if self.fills_ is not None else None
	@fills.setter
	def fills(self, value):
		self.fills_ = value

	@property
	def totalFilled(self):
		return self.totalFilled_ if self.totalFilled_ is not None else None
	@totalFilled.setter
	def totalFilled(self, value):
		self.totalFilled_ = int(value)

	@property
	def open(self):
		return self.open_ if self.open_ is not None else None
	@open.setter
	def open(self, value):
		self.open_ = value


def create_order(**kwargs):
	# check that all the required fields exist
	field_l = sf_api.URL_TEMPLATES['order_add'][2]
	for key in field_l:
		if kwargs.get(key, None) is None:
			print 'error: order_add requires "%s" field' % key
			sys.exit(-1)
	# create an order
	order = SFOrder(**kwargs)
	#venue=venue, stock=stock, direction='buy',
	#qty=100, price=500, orderType='limit', account=account)
	return order
