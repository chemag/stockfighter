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


class SFClient(object):
	"""Access to the stockfighters API."""

	def __init__(self, local=True, server_url=None, **kwargs):
		self.local_ = local
		self.ob_url_ = sf_api.LOCAL_URL if local else sf_api.URL
		self.ob_url_ += '/' + sf_api.URL_PREFIX
		self.gm_url_ = sf_api.LOCAL_URL if local else sf_api.URL
		self.gm_url_ += '/' + sf_api.GM_URL_PREFIX
		# support explicit server URLs
		if server_url is not None:
			self.ob_url_ = server_url + '/' + sf_api.URL_PREFIX
			self.gm_url_ = server_url + '/' + sf_api.GM_URL_PREFIX
		self.debug_ = kwargs.get('debug', 0)

	def run_http(self, url, http_type, data=None):
		# TODO(chema): not for gm
		http_headers = sf_api.HTTP_HEADERS
		if self.debug_ > 0:
			print '...tx-headers(%s): %r' % (url, http_headers)
			if data is not None:
				print '...tx-post_data(%s): %r' % (url, data)
		if http_type == sf_api.GET:
			ret = requests.get(url, headers=http_headers)
		elif http_type == sf_api.POST:
			ret = requests.post(url, headers=http_headers, data=data)
		elif http_type == sf_api.DELETE:
			ret = requests.delete(url, headers=http_headers)
		if self.debug_ > 1:
			print '...rx-headers(%s): %r' % (url, ret.headers)
		# parse return
		if not ret.ok:
			return -1, 'unsuccessful %s command: "%r"' % (
					sf_api.get_http_type_str(http_type), ret)
		try:
			out = ret.json()
			if self.debug_ > 0:
				print '...rx-data: %s' % out
			return 0, out
		except ValueError:
			pass
		return -1, 'invalid value received: "%s"' % ret.text

	def run(self, cmd, **kwargs):
		# check the command
		if cmd in sf_api.URL_TEMPLATES:
			return self.ob_run(cmd, **kwargs)
		elif cmd in sf_api.GM_URL_TEMPLATES:
			return self.gm_run(cmd, **kwargs)
		else:
			return -1, 'invalid command: "%s"' % cmd

	def ob_run(self, cmd, **kwargs):
		# check required input parameters
		http_type = sf_api.URL_TEMPLATES[cmd][0]
		template = sf_api.URL_TEMPLATES[cmd][1]
		for key in sf_utils.get_template_keys(template):
			if kwargs.get(key, None) is None:
				return -1, 'error: "%s" command (%s) requires %s' % (cmd,
						sf_api.get_http_type_str(http_type), key)
		# POST data build
		data = None
		if http_type == sf_api.POST:
			if kwargs.get('data', None) is not None:
				data = kwargs.get('data', None)
			else:
				if cmd == 'order_add':
					if type(kwargs.get('order', None)) is not sf_order.SFOrder:
						return -1, 'error: "%s" command (%s) requires valid order' % (cmd,
								sf_api.get_http_type_str(http_type))
					data = json.dumps(kwargs['order'].todict_short())
		# build the url
		url = (self.ob_url_ + '/' + template.substitute(**kwargs))
		return self.run_http(url, http_type, data)

	def gm_run(self, cmd, **kwargs):
		# check required input parameters
		http_type = sf_api.GM_URL_TEMPLATES[cmd][0]
		template = sf_api.GM_URL_TEMPLATES[cmd][1]
		for key in sf_utils.get_template_keys(template):
			if kwargs.get(key, None) is None:
				return -1, 'error: "%s" command (%s) requires %s' % (cmd,
						sf_api.get_http_type_str(http_type), key)
		# POST data build
		data = None
		if http_type == sf_api.POST:
			data = '\r\n'.join(sf_api.GM_POST_PARAMETERS)
		# build the url
		url = (self.gm_url_ + '/' + template.substitute(**kwargs))
		return self.run_http(url, http_type, data)

	def first_steps(self):
		return self.gm_run('first_steps')

	def restart(self, instance):
		return self.gm_run('restart', instance)

	def stop(self, instance):
		return self.gm_run('stop', instance)

	def resume(self, instance):
		return self.gm_run('resume', instance)

	def status(self, instance):
		return self.gm_run('status', instance)

	def levels(self):
		return self.gm_run('first_steps')
