#!/usr/bin/env python

import string
import sys

# https://www.stockfighter.io/ui/api_keys
api_key_header = "X-Starfighter-Authorization"

URL = 'https://api.stockfighter.io'
LOCAL_URL = 'http://localhost:8080'
WEBSOCKET_URL = 'wss://api.stockfighter.io/ob/api/ws'

URL_PREFIX = 'ob/api'
GM_URL_PREFIX = 'gm'

# http types
[GET, POST, DELETE, HTTP_TYPE_TOTAL] = range(4)
def get_http_type_str(http_type):
	if http_type == GET:
		return 'GET'
	elif http_type == POST:
		return 'POST'
	elif http_type == DELETE:
		return 'DELETE'
	return 'UNKNOWN'

def get_http_type(http_type):
	if http_type in range(HTTP_TYPE_TOTAL):
		return http_type
	# check whether there is a valid text value
	for i in range(HTTP_TYPE_TOTAL):
		if get_http_type_str(i) == http_type:
			return i
	raise ValueError('invalid http_type value: "%s"' % http_type)

# directions
[DIRECTION_BUY, DIRECTION_SELL, DIRECTION_TOTAL] = range(3)
def get_direction_str(direction):
	if direction == DIRECTION_BUY:
		return 'buy'
	elif direction == DIRECTION_SELL:
		return 'sell'
	return 'UNKNOWN'

def get_direction(direction):
	if direction in range(DIRECTION_TOTAL):
		return direction
	# check whether there is a valid text value
	for i in range(DIRECTION_TOTAL):
		if get_direction_str(i) == direction:
			return i
	raise ValueError('invalid direction value: "%s"' % direction)

# order types
[LIMIT, IOC, FOK, MARKET, ORDER_TYPE_TOTAL] = range(5)
def get_order_type_str(orderType):
	if orderType == LIMIT:
		return 'limit'
	elif orderType == IOC:
		return 'ioc'
	elif orderType == FOK:
		return 'fok'
	elif orderType == MARKET:
		return 'market'
	return 'UNKNOWN'

def get_order_type(orderType):
	if orderType in range(ORDER_TYPE_TOTAL):
		return orderType
	# check whether there is a valid text value
	for i in range(ORDER_TYPE_TOTAL):
		if get_order_type_str(i) == orderType:
			return i
	raise ValueError('invalid orderType value: "%s"' % orderType)


URL_TEMPLATES = {
	# http_type, url template, [required POST fields], [optional POST fields]
	'heartbeat': [GET, string.Template('heartbeat')],
	'venue_list': [GET, string.Template('venues')],
	'venue_heartbeat': [GET, string.Template('venues/$venue/heartbeat')],
	'venue_list_stocks': [GET, string.Template('venues/$venue/stocks')],
	'order_list': [GET,
			string.Template('venues/$venue/stocks/$stock')],
	'order_add': [POST,
			string.Template('venues/$venue/stocks/$stock/orders'),
			['venue', 'stock', 'direction', 'qty', 'orderType', 'account'],
			['price']],
	'order_status': [GET,
			string.Template('venues/$venue/stocks/$stock/orders/$order')],
	'order_cancel': [DELETE,
			string.Template('venues/$venue/stocks/$stock/orders/$order')],
	'stock_get_quote': [GET,
			string.Template('venues/$venue/stocks/$stock/quote')],
	'account_stock_status': [GET,
			string.Template('venues/$venue/accounts/$account/stocks/$stock/orders')],
	'account_status': [GET,
			string.Template('venues/$venue/accounts/$account/orders')],
}

GM_URL_TEMPLATES = {
	# http_type, url template
	'first_steps': [POST, string.Template('levels/first_steps')],
	'restart': [POST, string.Template('instances/$instance/restart')],
	'stop': [POST, string.Template('instances/$instance/stop')],
	'resume': [POST, string.Template('instances/$instance/resume')],
	'status': [GET, string.Template('instances/$instance')],
	'levels': [GET, string.Template('levels')],
}

WEBSOCKET_URL_TEMPLATES = {
	'tickertape': string.Template('$account/venues/$venue/tickertape'),
	'stock_tickertape': string.Template('$account/venues/$venue/tickertape/stocks/$stock'),
	'executions': string.Template('$account/venues/$venue/executions'),
	'stock_executions': string.Template('$account/venues/$venue/executions/stock/$stock'),
}

HTTP_HEADERS = {
	'Accept': '*/*',
	'accept-encoding': 'gzip',
}
WEBSOCKET_HEADERS = {
}

try:
	import api_key
except ImportError:
	print 'libsf requires an api_key.py file that defines a key variable'
	sys.exit(-1)

HTTP_HEADERS[api_key_header] = api_key.key
WEBSOCKET_HEADERS[api_key_header] = api_key.key
GM_POST_PARAMETERS = [
		'Cookie:api_key=' + api_key.key,
]

NOK = {
	'ok': False,
	'reason': ''
}

OK = {
	'ok': True,
}
