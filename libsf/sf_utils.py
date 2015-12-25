#!/usr/bin/env python

# libsf utils

import re

# TODO(chema): there should be a better way to do this
def get_template_keys(template):
	# http://stackoverflow.com/questions/13037401/get-keys-from-template
	keys = re.findall(r'\$%s' % template.idpattern, template.template)
	# remove the leading '$'
	return [k[1:] for k in keys]
