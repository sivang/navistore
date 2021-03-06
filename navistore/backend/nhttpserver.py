#!/usr/bin/env python
"""
Navistore rest server module.
"""

import sys
from twisted.web.server import Site
from twisted.web.client import getPage
from twisted.internet import reactor
from twisted.web.resource import Resource
from optparse import OptionParser


# backend imports:
# to change the backend storage, just replace nsqlite with your
# newly created backend class. It has to conform to the interface
# defined in iface.py ofcourse, and pass all the storage backend
# tests.
from navistore.backend.nsqlite import SqliteStorageBackend as StorageBackend
from navistore.backend.demonize import demonize
from navistore.backend.errorpage import NoResource
from navistore.backend import conf

import simplejson as json
import time
import os
import logging

class NavistoreValuePage(Resource):
	isLeaf = True
	def __init__(self, name, backend, logger):
		Resource.__init__(self)
		self.backend = backend
		self.name = name
		self.logger = logger
	def render_GET(self, request):
		if self.name in conf.ALLOWED_VERBS:
			# If the path represents an API call then 
			# dynamically try call it from the storage 
			# backend rather than treating it as a key.
			if self.logger:
				self.logger.info("%s API request, not a key." % self.name)
			return "%s" % json.dumps((getattr(self.backend, self.name)()))
		else:
			key = self.name
			value = None
			try:
				value =  self.backend.get(key)
				if self.logger:
					self.logger.info('%s found in database.' % key)
					self.logger.info("'%s' => '%s'" % (key, value))
			except:
				if self.logger:
					self.logger.info("%s not found in db." % key)
				return NoResource().render(request)
			return "%s" % str(value) # workaround bug with unicode strings in twisted 
						 # When returning a unicode string, twisted treats
						 # it as if the request did not return any string
						 # and raises an exception refusing to render.
						 # TODO: Open a bug report to JP Calderon
	def render_PUT(self, request):
		# content is an file like object that 
		# can be read for the content of the request payload,
		# so if you do something like: 
		# $ curl -X PUT http://localhost:8888/mykey -d "this is the value"
		# .getvalue() will return "this is the value"
		if self.logger:
			self.logger.info("saving %s under %s key." % (request.content.getvalue(), self.name))
		self.backend.save(self.name, request.content.getvalue())
		if self.name in conf.RESERVED_KEYS:
			# don't replicate RESERVED_KEYS's values.
			return "OK"
		try:
			slaves_str = self.backend.get("_replication_slaves")
			slaves = slaves_str.split(",")
			for s in slaves:
				uri = str(s + "/" + self.name)
				if self.logger:
					self.logger.info("replicating to: %s" % uri)
				getPage(uri, method='PUT',
					postdata=request.content.getvalue())
		except Exception, e:
			if self.logger:
				self.logger.error("not replicating: %s" % e)
		return "OK"
	def render_DELETE(self, request):
		self.backend.delete(self.name)
		if self.name in conf.RESERVED_KEYS:
			# don't replicate deletion of RESERVED_KEYS
			return "OK"
		try:
			slaves_str = self.backend.get("_replication_slaves")
			slaves = slaves_str.split(",")
			for s in slaves:
				uri = str(s + "/" + self.name)
				if self.logger:
					self.logger.info("replicating delete to: %s" % uri)
				getPage(uri, method='DELETE')
		except Exception, e:
			if self.logger:
				self.logger.error("not replicating: %s" % e)
		return "OK"


class NavistoreRoot(Resource):
	def __init__(self, backend, store_path="./navistore.db", logger=None):
		Resource.__init__(self)
		self.backend = backend(store_path) 
		self.logger = logger
	def getChild(self, name, request):
		return NavistoreValuePage(name, self.backend, self.logger)


def get_logger(filepath):
	"""
	Create a logger instance, that will
	log to the specified 'filepath'.
	Uses the Python stdlib logging facility.
	"""
	if filepath:
		logging.basicConfig(filename=filepath,
					system_name='nhttpserver',
					level=conf.LOGLEVEL,
					format='%(asctime)s %(message)s')
	else:
		logging.basicConfig(system_name='nhttpserver',
					level=conf.LOGLEVEL)
	return logging.getLogger('nhttpserver')


def start_server(*args):
	logpath = None
	portnum = int(args[0])
	storage_path = args[1]
	if len(args) == 3:
		# a logging filename and path
		# has been specified.
		logpath = args[2]
	lgr = get_logger(logpath)
	root = NavistoreRoot(StorageBackend, storage_path, lgr)
	factory = Site(root)
	reactor.listenTCP(portnum, factory)
	reactor.addSystemEventTrigger('before',
					'shutdown',
					root.backend.close)
	reactor.run()

def runtime_opts():
	"""
	Use optparse to parse command line arguments
	passed to the server upon invocation.
	"""
	parser = OptionParser()
	parser.add_option("-P", "--port", 
				dest="portnumber", default=8888,
				help="Use PORT as the listening port for the daemon",
				metavar="PORT")
	parser.add_option("-p", "--pidfile",
				dest="pidfile",
				help="Use PIDFILE as the path where to store the file with pid of started"
					" daemon. This is to support various stopping and starting of "
					"damoens machinery, e.g. Debian's start-stop-daemon and is only"
					" needed in case nhttpserver is run as a service in the background.",
				metavar="PIDFILE")
	parser.add_option("-b", "--background",
				dest="background", default=False,
				action="store_true",
				help="Run the server as a background process rather than in "
					"the foreground. Running in the foreground is useful"
					" for local development and testing.")
	parser.add_option("-s", "--storage-path",
				dest="storage_path",
				help="Storage backend files will be saved to STORAGE_PATH. "
					"If not specified, defaults to current directory. "
					"This should include the file name as well.")
	parser.add_option("-l", "--log-path",
				dest="logpath",
				help="Specify where to store operation log file if executed "
					"as a background service. When running in the foreground "
					"logging output goes to stdout.")
	(options, args) = parser.parse_args()
	return options

def main():
	"""
	Navistore reference HTTP REST server, supporting the
	Navistore storage backend API. 
	
	Serves values through keys, using the currently set storage
	backend.

	To replace the currently used backend find the line with:

	C{from navistore.backend.nsqlite import SqliteStorageBackend as StorageBackend}

	And replace 'SqliteStorageBackend' and 'nsqlite' with the module and class
	name where your backend is.

	This reference http rest server supports replication by repeating
	the data modification operations across the navistore instances
	listed by the /_replicated_slaves key's value.

	This approach for replication was taken after assuming the following:
	   - The classic operation model for Navistore is inside a LAN, where 
  	     bandwidth is not an issue.
	   - Twisted is performant enough to stand high growth in request
	     and its deferreds mechanism will be able to properly handle remote
	     data modification through its asynchronous PUT and DELETE calls.
	   - High load on storage backend will not delay replication operations.


	Uses demonize.py for proper service creation. This includes
	exist status propogated through the child process hirarchy.

	To run the server on the foreground, suitable for testing
	and experimenting with the server in a non system-wide fashion.
	To do that simply issue C{ $ nhttpserver } in a terminal.

	To use it as a daemon, please consult the command line arguments
	by issuing:
	C{ $ nhttpserver --help }

	If in foreground mode, once started log messages are sent 
	to stdout and you can use curl (install it through your 
	system's package manager) to use the server:

	To save a key:
	C{ $ curl -X PUT http://localhost:8888/name -d "sivan"}

	Retrieve the value:
	C{ $ curl -X GET http://localhost:8888/name }

	To list all keys in the instance:
	C{ $ curl -X GET http://localhost:8888/listkeys }

	To delete a key (and the value):
	C{ $ curl -X DELETE http://localhost:8888/name }

	To clear the instance and start fresh:
	C{ $ curl -X GET http://localhost:8888/reset }

	Enable replication; this will replicate any value from 
	now on to the peers defined in:
	C{ $ curl -X PUT http://localhost:8888/_replication_slaves -d "http://192.168.1.1:8880,http://192.168.1.2:8880 }

	To disable replication just delete the key:
	C{ $ curl -X DELETE http://localhost:8888/_replication_slaves }
"""
	opts = runtime_opts()
	if opts.background:
		demonize(otps.pidfile,
				start_server,
				opts.portnumber,
				opts.storage_path,
				opts.logpath)
	else:
		start_server(opts.portnumber, opts.storage_path)


if __name__ == "__main__":
	main()


