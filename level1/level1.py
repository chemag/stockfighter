#!/usr/bin/env python

import sys

sys.path.append("..")
sys.path.append(".")
from libsf import sf_api
from libsf import client

local=False
#local=True
server_url = None

kwargs = {
	'cmd': 'order_add',
	'account': 'CB78914943',
	'venue': 'ECAMEX',
	'stock': 'SMC',
	'direction': sf_api.DIRECTION_BUY,
	'qty': 100,
	'orderType': sf_api.MARKET,
	'debug': 2,
}

print client.run_command(local, server_url, **kwargs)
