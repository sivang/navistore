#!/usr/bin/env python
"""
Test server replication.

Using the http backend client module, we do some
data modifications operations an make sure the resulting
values and keys are at the replication target instances.

Instead of deriving from the http storage test case, I felt 
it would be more readable to write a test from scratch, even
if that meant duplicating test code. The end result is much
more readable and understandable and can serve as usage
documentation better.
"""

import common
import unittest
import time
import os

from navistore.backend.nhttp import HttpStorageBackend
from navistore.backend.restkit.errors import ResourceNotFound

SERVER_HOST ="http://" + common.HOST + ":" + common.PORT

# the two replication slaves instances
REMOTE1 = "http://" + common.HOST + ":8889"
REMOTE2 = "http://" + common.HOST + ":8887"


class ServerReplicationTestCase(unittest.TestCase):
	def setUp(self):
		"""
		Set replication to 2 other navistore http server
		instances. For simplicity those instances are going
		to be assumed to be running on the same machine
		this test runs. 
		
		However, it should be easy to configure otherwise 
		replacing the hostnames/ports and re-running the test.

		To run the test, have 2 other instancs running at
		ports 8889 and 8887.
		"""
		self.localstore = HttpStorageBackend(SERVER_HOST)
		self.localstore.save('/_replication_slaves',
					"http://localhost:8889,http://localhost:8887")
		self.remote1 = HttpStorageBackend(REMOTE1)
		self.remote2 = HttpStorageBackend(REMOTE2)
	def test_save_and_get_replicated(self):
		"""
		Test saving a value by a key to the database, and
		then make sure the save value by the same key is also
		available in the target replication instances.
		"""
		self.localstore.save("1", "replication testcase inserted value")
		fvalue = self.localstore.get("1")
		remote1value = self.remote1.get("1")
		remote2value = self.remote2.get("1")
		self.assertTrue(fvalue == remote1value)
		self.assertTrue(fvalue == remote2value)
	def test_delete_replicated(self):
		"""
		Add a value, then delete it, and make sure
		the deletion operation was carried on
		to the replicated instances.
		"""
		self.localstore.save('/_replication_slaves',
					"http://localhost:8889,http://localhost:8887")
		self.localstore.save("sample_key2", "sample_value2")
		self.assertTrue(self.localstore.haskey("sample_key2"))
		self.assertTrue(self.remote1.haskey("sample_key2"))
		self.assertTrue(self.remote2.haskey("sample_key2"))
		self.localstore.delete("sample_key2")
		# no replication is immediate
		time.sleep(0.1)
		self.assertRaises(ResourceNotFound, 
					self.remote1.get,
					("sample_key2"))
		self.assertRaises(ResourceNotFound,
					self.remote2.get,
					("sample_key2"))
	def tearDown(self):
		self.localstore.reset()
		self.remote1.reset()
		self.remote2.reset()




if __name__ == '__main__':
	unittest.main()

	
