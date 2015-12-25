#!/usr/bin/env python

# from http://webpy.org/src/blog/0.3

import datetime
import web

DATABASE='sqlite'

db = web.database(dbn=DATABASE, db='database.sqlite')

def get_orders(id=None):
	if id:
		return db.select('orders', where='id=$id', order='id DESC')
	else:
		return db.select('orders', order='id DESC')

def add_order(ok, stock, venue, direction, originalQty, qty, price, orderType,
		account, ts, totalFilled, open, id=None, fills=None):
	return db.insert(
			'orders', ok=ok, stock=stock, venue=venue, direction=direction,
			originalQty=originalQty, qty=qty, price=price, orderType=orderType,
			account=account, ts=ts, totalFilled=totalFilled, open=open)

def del_order(id):
	return db.delete('orders', where="id=$id", vars=locals())

def update_order(id, ok, stock, venue, direction, originalQty, qty, price,
		orderType, account, ts, totalFilled, open):
	return db.update(
			'orders', where="id=$id", vars=locals(),
			ok=ok, stock=stock, venue=venue, direction=direction,
			originalQty=originalQty, qty=qty, price=price, orderType=orderType,
			account=account, ts=ts, totalFilled=totalFilled, open=open)

def get_fills(id=None, order_id=None):
	try:
		if id:
			return db.select('fills', where='id=$id', vars=locals())[0]
		elif order_id:
			return db.select('fills', where='order_id=$order_id', vars=locals())[0]
		else:
			return db.select('fills', vars=locals())[0]
	except IndexError:
		return None

def add_fill(price, qty, ts, order_id, id=None):
	return db.insert('fills', price=price, qty=qty, ts=ts, order_id=order_id)

def del_fill(id):
	return db.delete('fills', where="id=$id", vars=locals())

def update_fill(id, price, qty, ts, order_id):
	return db.update('fills', where="id=$id", vars=locals(),
			price=price, qty=qty, ts=ts, order_id=order_id)

db_vft = {
	'orders': {
		'get': get_orders,
		'add': add_order,
		'del': del_order,
		'update': update_order,
	},
	'fills': {
		'get': get_fills,
		'add': add_fill,
		'del': del_fill,
		'update': update_fill,
	},
}

