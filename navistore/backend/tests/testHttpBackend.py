#!/usr/bin/env python
import common
import unittest
import time
import os
import testNavistoreBackend
from navistore.backend.nhttp import HttpStorageBackend
from navistore.backend.restkit.errors import ResourceNotFound

"""
This module is used to contain all the HttpStorageBackend tests.

To implement a new backend, just subclass StorageBackendTestCase
in a new test module file ,add your setup and teardown logic and 
iterate through implementation and testing until the test 
completes with SUCCESS.

If your backend requires special considerations for things like
in memory processing and syncing, override the test method from
the base StorageBackendTestCase , add your special care, and
then execute the parent's method for the actual logic test.

"""

SERVER_HOST ="http://" + common.HOST + ":" + common.PORT

class HttpStorageBackendTestCase(testNavistoreBackend.StorageBackendTestCase):
	"""
	HTTP storage backend client test case.

	This tests the HttpStorageBackend class, according to the
	interface conformance we defined in StorageBackendTestCase.

	This test also makes the http server we work against,
	conforms to the navistore backend interface specification
	and actually serves to test the http server as well.

	Since replication support is outside of the defined interface,
	and is part of the http server implementation we use a different
	test to test it, testServerReplication.py
	"""
	store = None
	def setUp(self):
		"""
		create a backend object that allows us
		to interact with the key value storage
		"""
		self.store = HttpStorageBackend(SERVER_HOST)
	def tearDown(self):
		self.store.reset() # cleaning up the store for the nex test
	def test_delete(self):
		self.store.save("sample_key2","sample_value2")
		self.assertTrue(self.store.haskey("sample_key2"))
		self.store.delete("sample_key2")
		self.assertRaises(ResourceNotFound, self.store.get, ("sample_key2"))
	def test_reset(self):
		self.store.save("mkey","value")
		self.assertTrue(self.store.haskey("mkey"))
		self.store.reset()
		self.assertRaises(ResourceNotFound, self.store.get, ("mkey"))
	def test_loadstore(self):
		# not relevant here since we cannot
		# stop and start the service from here
		pass


if __name__ == '__main__':
	unittest.main()

	
