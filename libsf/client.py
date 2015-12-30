#!/usr/bin/env python

# a simple requests-based rest client

# http://isbullsh.it/2012/06/Rest-api-in-python/

import argparse
import requests
import json
import re
import sys

import sf_api
import sf_client
import sf_order
import sf_utils


def get_opts(argv):
	# init parser
	parser = argparse.ArgumentParser(description='A generic SF client.')
	# common flags
	parser.add_argument('-d', '--debug', dest="debug", default=0,
			action="count",
			help="Increase verbosity (specify multiple times for more)")
	parser.add_argument('--quiet', action='store_const',
			dest='debug', const=-1,
			help='Zero verbosity',)
	parser.add_argument('-v', '--version', action="version",
			version='%(prog)s 1.0')
	parser.add_argument('--local', action='store_const',
			dest='server_url', const='local', default='local',
			help='Run the command using the local server',)
	parser.add_argument('--sf', action='store_const',
			dest='server_url', const='stockfighter',
			help='Run the command using the stockfighter server',)
	parser.add_argument('--server', dest='server_url',
			help='Run the command using a specified server',)
	# add sub-parsers
	subparsers = parser.add_subparsers()
	# independent subcommands
	parser_cmd = {}
	for cmd in sf_api.URL_TEMPLATES.keys():
		http_type = sf_api.URL_TEMPLATES[cmd][0]
		template = sf_api.URL_TEMPLATES[cmd][1]
		parser_cmd[cmd] = subparsers.add_parser(cmd, help='run %s' % cmd)
		parser_cmd[cmd].set_defaults(cmd=cmd)
		# add per-command flags
		for key in sf_utils.get_template_keys(template):
			parser_cmd[cmd].add_argument('--%s' % key)
		# add POST parameters
		if http_type == sf_api.POST:
			key_l = sf_api.URL_TEMPLATES[cmd][2] + sf_api.URL_TEMPLATES[cmd][3]
			for key in key_l:
				if key not in sf_utils.get_template_keys(template):
					parser_cmd[cmd].add_argument('--%s' % key)
	for cmd in sf_api.GM_URL_TEMPLATES.keys():
		http_type = sf_api.GM_URL_TEMPLATES[cmd][0]
		template = sf_api.GM_URL_TEMPLATES[cmd][1]
		parser_cmd[cmd] = subparsers.add_parser(cmd, help='run gm %s' % cmd)
		parser_cmd[cmd].set_defaults(cmd=cmd)
		# add per-command flags
		for key in sf_utils.get_template_keys(template):
			parser_cmd[cmd].add_argument('--%s' % key)
	parser.add_argument('remaining', nargs=argparse.REMAINDER)
	# do the parsing
	return parser.parse_args(argv[1:])


def main(argv):
	vals = get_opts(argv)
	# print arguments
	if vals.debug > 1:
		print "vals: %r" % vals
		print "remaining: %r" % vals.remaining
		for k, v in vars(vals).iteritems():
			print 'vals.%s = %s' % (k, v)
		print 'remaining args is %s' % vals.remaining

	kwargs = vars(vals)

	# parse vals parameters
	local = False
	server_url = None
	if vals.server_url == 'local':
		local = True
		del kwargs['server_url']
	elif vals.server_url == 'stockfighter':
		local = False
		del kwargs['server_url']
	else:
		server_url = vals.server_url
		del kwargs['local']

	ret = run_command(local, server_url, **kwargs)
	print 'result: %r' % ret


def run_command(local, server_url, **kwargs):
	# create a client
	client = sf_client.SFClient(local, server_url, **kwargs)
	# run the command
	if kwargs['cmd'] == 'order_add':
		kwargs['order'] = sf_order.create_order(**kwargs)
	cmd = kwargs['cmd']
	del kwargs['cmd']
	ret = client.run(cmd, **kwargs)
	if ret[0] == -1:
		print ret[1]
		sys.exit(-1)
	return ret[1]


if __name__ == '__main__':
	main(sys.argv)

