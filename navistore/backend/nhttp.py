#!/usr/bin/env python

"""
Navistore HTTP backend client module. 

Allows to instnatiate a resource that enables
talking to the HTTP storage, save and get values
and some utility methods for resetting the store.

This requires the restkit module. All methods are subject
to the standard HTTP error raised through restkit exceptions.

Consult the restkit documentation for the possible errors that
need to be caught when working with module:
- http://benoitc.github.com/restkit/api/toc-restkit.errors-module.html

To read about restkit:
- http://benoitc.github.com/restkit/index.html
"""

from navistore.backend import iface
import simplejson as json

# to workaround the fact that restkit is not included in lenny
# we deliver it part of our navistore package.
# TODO: Contribute a backported package to lenny-backports.
from navistore.backend.restkit import Resource
from navistore.backend.restkit.errors import ResourceNotFound

class HttpStorageBackend(iface.StorageBackend):
	res = None
	def __init__(self, uri):
		self.res = Resource(uri)
	def listkeys(self):
		return json.loads(self.res.get("/listkeys").body_string())
	def haskey(self, key):
		try:
			self.res.get("/%s" % key)
			return True
		except ResourceNotFound:
			return False
	def save(self, key, value):
		return self.res.put('/%s' % key, value).body_string()
	def get(self, key):
		return self.res.get('/%s' % key).body_string()
	def delete(self, key):
		return self.res.delete('/%s' % key).body_string()
	def reset(self):
		return self.res.get('/reset').body_string()
	
		


