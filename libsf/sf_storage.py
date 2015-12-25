#!/usr/bin/env python

import database
import datetime
import json
import time

class SFStorage(object):

	VALID_TABLES = database.db_vft.keys()
	VALID_COMMANDS = dict((k, database.db_vft[k].keys()) for k in
			database.db_vft.keys())

	orders = {}
	fills = {}

	def __init__(self, use_database=False):
		self.use_database = use_database
		self.vft = {
			'orders': {
				'get': self.get_orders,
				'add': self.add_order,
				'del': self.del_order,
				'update': self.update_order,
			},
			'fills': {
				'get': self.get_fills,
				'add': self.add_fill,
				'del': self.del_fill,
				'update': self.update_fill,
			},
		}

	def get_orders(self, id=None):
		if id:
			return self.orders.get(id, None)
		else:
			return self.orders

	def add_order(self, order):
		id = order.id
		if id in self.orders.keys():
			# cannot add an order with a valid id
			return -1
		elif id is None:
			# create a unique id
			order.id = int(time.time())
		self.orders[order.id] = order
		return order.id

	def del_order(self, id):
		if not order.id:
			# cannot del an order without a valid id
			return -1
		del self.orders[id]

	def update_order(self, order):
		if not order.id:
			# cannot update an order without a valid id
			return -1
		self.orders[order.id] = order

	# TODO(chema): how to represent fills in SFStorage?
	# - python world: list of <fills> inside the order
	# - database world: fills in a 2nd table with order_id as foreign key
	def get_fills(self, id=None, order_id=None):
		if id:
			return self.fills.get(id, None)
		elif order_id:
			l = []
			for fill in self.fills.values():
				if fill.order_id == order_id:
					l.append(fill)
			return l
		else:
			return self.fills

	def add_fill(self, fill):
		id = fill.get('id', None)
		if id in self.fills.keys():
			# cannot add an fill with a valid id
			return -1
		elif id is None:
			# create a unique id
			fill['id'] = int(time.time())
		self.fills[fill['id']] = fill
		return fill['id']

	def del_fill(self, id):
		if not fill.get('id', None):
			# cannot del an fill without a valid id
			return -1
		del self.fills[id]

	def update_fill(self, fill):
		if not fill.get('id', None):
			# cannot update an fill without a valid id
			return -1
		self.fills[fill['id']] = fill
