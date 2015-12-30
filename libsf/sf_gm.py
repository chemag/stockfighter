#!/usr/bin/env python

# a simple requests-based rest client to interact with the stockfighters GM API

# https://discuss.starfighters.io/t/the-gm-api-how-to-start-stop-restart-resume-trading-levels-automagically/143

import autopep8
import os.path
import sys

from libsf import sf_api
from libsf import sf_client
from libsf import sf_utils


LIBSFPATH = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))

INSTRUCTIONS_FILENAME = 'instructions.txt'
KEYS_FILENAME = 'level_keys.py'
PYTHON_HEADER = '#!/usr/bin/env python\n\n'


class SFGMClient(object):
	"""Access to the stockfighters GM API."""

	def __init__(self, local=True, server_url=None, **kwargs):
		self.local_ = local
		self.url_ = sf_api.LOCAL_URL if local else sf_api.URL
		self.url_ += '/' + sf_api.GM_URL_PREFIX
		# support explicit server URLs
		if server_url is not None:
			self.url_ = server_url + '/' + sf_api.GM_URL_PREFIX
		self.debug_ = kwargs.get('debug', 0)

	def run(self, cmd, **kwargs):
		# check the command
		if cmd not in sf_api.GM_URL_TEMPLATES:
			return -1, 'invalid command: "%s"' % cmd
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
		# implement pseudo-levels
		if cmd == 'level':
			return self.level(int(kwargs['level']))
		# build the url
		url = (self.url_ + '/' + template.substitute(**kwargs))
		# TODO(chema): not for gm
		http_headers = sf_api.HTTP_HEADERS
		return sf_client.run_http(url, http_type, data, http_headers, self.debug_)

	def level(self, level):
		# check this is a valid level
		assert level in sf_api.GM_LEVELNAMES
		ret = self.run(cmd=sf_api.GM_LEVELNAMES[level])
		if ret[0] != 0:
			return -1, ret[1]
		# get the level path
		level_path = os.path.join(LIBSFPATH, 'level%i' % level)
		# store the instructions
		if 'instructions' in ret[1]:
			instructions_filename = os.path.join(level_path, INSTRUCTIONS_FILENAME)
			with open(instructions_filename, 'w') as f:
				for k, v in ret[1]['instructions'].iteritems():
					f.write('\n== %s\n\n%s\n' % (k, v))
			del ret[1]['instructions']
		# store the rest
		if not ret[1]['ok']:
			return -1, 'error: checking client: %r' % ret[1]
		del ret[1]['ok']
		keys_filename = os.path.join(level_path, KEYS_FILENAME)
		with open(keys_filename, 'w') as f:
			f.write(PYTHON_HEADER)
			f.write(autopep8.fix_code('kwargs = %s' % ret[1],
					options={'aggressive': 1}))
		print 'keys filename: %s' % keys_filename
		return 0, ''

	def restart(self, instance):
		return self.run('restart', instance=instance)

	def stop(self, instance):
		return self.run('stop', instance=instance)

	def resume(self, instance):
		return self.run('resume', instance=instance)

	def status(self, instance):
		return self.run('status', instance=instance)

	def levels(self):
		return self.run('first_steps')

