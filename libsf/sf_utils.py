#!/usr/bin/env python

# libsf utils

import re
import sys

# Returns a list of all the keys from a string.Template.
# TODO(chema): there should be a better way to do this
def get_template_keys(template):
	# http://stackoverflow.com/questions/13037401/get-keys-from-template
	keys = re.findall(r'\$%s' % template.idpattern, template.template)
	# remove the leading '$'
	return [k[1:] for k in keys]


# gets the current position
def get_current_position(client):
	position_money = 0
	position_stock = 0
	live_orders = {}
	# get the list of orders
	ret = client.account_stock_status()
	if ret[0] != 0:
		print 'error: %s' % ret[1]
		sys.exit(-1)
	orders = ret[1]
	for order in orders['orders']:
		# account for filled orders
		for fill in order['fills']:
			if order['direction'] == 'buy':
				position_money -= (fill['price'] * fill['qty'])
				position_stock += fill['qty']
			else:
				position_money += (fill['price'] * fill['qty'])
				position_stock -= fill['qty']
		if not order['open']:
			continue
		order_left = order['originalQty'] - order['totalFilled']
		if order_left == 0:
			continue
		# non-empty order
		order_id = order['id']
		order['orderLeft'] = order_left
		live_orders[order_id] = order
	return position_money, position_stock, live_orders
