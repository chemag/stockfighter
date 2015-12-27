#!/usr/bin/env python

import sys
import time

sys.path.append("..")
sys.path.append(".")
from libsf import sf_api
from libsf import client

local=False
#local=True
server_url = None

SHARES_PER_TRADE = 100
NUMBER_OF_SHARES = 100000
NUMBER_OF_TRADES = NUMBER_OF_SHARES / SHARES_PER_TRADE

kwargs = {
	'cmd': 'order_add',
	'account': 'AS78562776',
	'venue': 'HKVEX',
	'stock': 'EYBI',
	'direction': sf_api.DIRECTION_BUY,
	'qty': SHARES_PER_TRADE,
	'orderType': sf_api.MARKET,
	'debug': 0,
}




NUMBER_OF_TRADES = 1

def main(argv):
	# get list of venues

	for i in range(NUMBER_OF_TRADES):
		ret, output = client.run_command(local, server_url, **kwargs)
		if ret == 0:
			print "%i: OK" % i
		else:
			print "%i: ERROR: %r" % (i, output)
			sys.exit(-1)
		time.sleep(5)

if __name__ == '__main__':
	main(sys.argv)

