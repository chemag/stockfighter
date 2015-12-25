#!/usr/bin/env python

# a simple rest server using web.py

# http://www.dreamsyssoft.com/python-scripting-tutorial/create-simple-rest-web-service-with-python.php

import argparse
import json
import socket
import sys
import web

import sf_api
import sf_order
import sf_storage

VENUE_LIST = ["FOOEX"]
STOCK_LIST = ["BAR"]

# TODO(chema): how do you pass variables to the application classes?
DEBUG = 2

urls = (
	'/heartbeat', 'Heartbeat',
	'/venues', 'VenueList',
	'/venues/([^/]*)/stocks/([^/]*)/orders', 'VenueHandler',
	#'/venues/([^/]*)/stocks/([^/]*)/fill', 'VenueHandler',
	'/debug/([^/]*)/([^/]*)', 'DebugHandler',
)

storage = sf_storage.SFStorage(use_database=False)


class Heartbeat:
	def GET(self):
		output = json.dumps(sf_api.OK)
		if DEBUG > 1:
			print '...tx: %s' % output
		return output

class VenueList:
	def GET(self):
		output = VENUE_LIST
		output = json.dumps(output)
		if DEBUG > 1:
			print '...tx: %s' % output
		return output


class VenueHandler:
	#def GET(self, user):
	#	for child in root:
	#		if child.attrib['id'] == user:
	#			output = json.dumps(child.attrib)
	#			print '...tx: %r' % output
	#			return output

	EXAMPLE_OUTPUT = {
			'ok': True,
			'stock': 'BAR',
			'venue': 'FOOEX',
			'direction': 'buy',
			'originalQty': 100,
			'qty': 20,   # this is the quantity *left outstanding*
			'price':  5100, # the price on the order - may not match that of fills!
			'type': 'limit',
			'id': 12345, # guaranteed unique *on this venue*
			'account' : 'OGB12345',
			'ts': '2015-07-05T22:16:18+00:00', # ISO-8601 timestamp for rx time
			'fills':
			[
				# may have zero or multiple fills.
				{
					'price': 5050,
					'qty': 50,
					'ts': '2015-07-05T22:16:18+00:00',
				},
				# Note this order presumably has a total of 80 shares worth
			],
			'totalFilled': 80,
			'open': True,
	}

	def POST(self, venue, stock):
		data = web.data()
		try:
			order_d = json.loads(data)
		except ValueError:
			# invalid json data
			output = sf_api.NOK
			output['reason'] = 'invalid json data: "%s"' % data
			print output['reason']
			return output
		if DEBUG > 1:
			print '...rx.headers: %r' % web.ctx.env
			print '...rx.data: %r' % order_d
		# parse order
		try:
			order = sf_order.SFOrder.fromdict(order_d)
		except ValueError:
			output = sf_api.NOK
			output['reason'] = 'invalid order dict: "%r"' % order_d
			print output
			return output
		# start order
		order.start()
		# add order
		id = storage.add_order(order)
		if id < 0:
			output = sf_api.NOK
			output['reason'] = 'cannot add order: %r' % order
			print output['reason']
			return output
		output = sf_api.OK
		output.update(order.todict())
		output = json.dumps(output)
		return output


class DebugHandler:
	def POST(self, table, command):
		# check input parameters
		if table not in storage.VALID_TABLES:
			output = sf_api.NOK
			output['reason'] = 'invalid table: "%s"' % table
			print output['reason']
			return output
		if command not in storage.VALID_COMMANDS[table]:
			output = sf_api.NOK
			output['reason'] = 'invalid command: "%s"' % command
			print output['reason']
			return output
		# check input
		data = web.data()
		try:
			data_d = json.loads(data)
		except ValueError:
			# invalid json data
			output = sf_api.NOK
			output['reason'] = 'invalid json data: "%s"' % data
			print output['reason']
			return output
		if DEBUG > 1:
			print '...%s.%s.rx: %r' % (table, command, data_d)
		# parse request
		#try:
		#	out = database.db_vft[table][command](**data_d)
		#except ValueError:
		#	output = sf_api.NOK
		#	output['reason'] = 'invalid data dict: "%r"' % data_d
		#	print output['reason']
		#	return output

def get_opts(argv):
	# init parser
	parser = argparse.ArgumentParser(description='An argparser demo.')
	parser.add_argument('-d', '--debug', dest="debug", default=0,
			action="count",
			help="Increase verbosity (specify multiple times for more)")
	parser.add_argument('--quiet', action='store_const',
			dest='debug', const=-1,
			help='Zero verbosity',)
	# do the parsing
	parser.add_argument('remaining', nargs=argparse.REMAINDER)
	return parser.parse_args(argv[1:])


def main(argv):
	vals = get_opts(argv)
	# print arguments
	print "vals: %r" % vals
	print "remaining: %r" % vals.remaining
	if vals.debug > 1:
		for k, v in vars(vals).iteritems():
			print 'vals.%s = %s' % (k, v)
		print 'remaining args is %s' % vals.remaining

	global DEBUG
	DEBUG = vals.debug

	# web.py doesn't like to see our arguments
	sys.argv = [argv[0]]
	# run the server
	app = web.application(urls, globals())
	try:
		app.run()
	except socket.error as (msg):
		print 'error: %s' % msg


if __name__ == '__main__':
	main(sys.argv)
