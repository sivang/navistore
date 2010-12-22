#!/usr/bin/env python

import common
import unittest
import time
import os

class StorageBackendTestCase(unittest.TestCase):
	"""
	Canonical storage backend test.

	This test case also serves to secure the API, or
	rather the minimal API a backend should support
	to be used as a Navistore backend.
	"""
	store = None
	def setUp(self):
		"""
		create a backend object that allows us
		to interact with the key value storage
		- Specific to the backend being tested.
		"""
	def tearDown(self):
		"""
		Clear test residual
		- This is specific to the backend tested.
		"""
	def test_save_and_get(self):
		"""
		Test saving a value by a key to the database
		and fetching it back.
		"""
		self.store.save("1", "testcase inserted value")
		fvalue = self.store.get("1")
		self.assertTrue(fvalue=='testcase inserted value')
	def test_modify(self):
		"""
		Make sure that values can be modified, e.g.
		saving a new value under the same key replaces
		the previous value stored.
		"""
		self.store.save("thekey","first saved value")
		self.assertTrue(self.store.get("thekey") == "first saved value")
		self.store.save("thekey","second saved value")
		self.assertTrue(self.store.get("thekey") == "second saved value")
	def test_listkeys(self):
		keys = ["1","2","3"]
		for k in keys:
			self.store.save(k, ("%s" % k))
		mykeys = self.store.listkeys()
		for k in mykeys:
			self.assertTrue(k in keys)
	def test_haskey(self):
		self.store.save("sample_key","sample_value")
		self.assertTrue(self.store.haskey("sample_key"))
	def test_delete(self):
		self.store.save("sample_key2", "sample_value2")
		self.store.delete("sample_key2")
		self.assertRaises(KeyError, self.store.get, ("sample_key2"))
	def test_loadstore(self):
		"""
		Make sure that we are truly persistent.
		E.g. when re-instantiated we just give access
		the whatever values are already stored in the store
		and not fail due to backend implementatino detail.
		Like,for example in sqlite when a table already exists.
		"""
		self.store.save("pkey","persistent value")
		self.setUp()
		self.assertTrue(self.store.get("pkey") == "persistent value")
	def test_reset(self):
		"""
		This should wipe all data from the
		store as if we reset it up.
		"""
		self.store.save("mkey","value")
		self.assertTrue(self.store.haskey("mkey"))
		self.store.reset()
		self.assertRaises(KeyError, self.store.get, ("mkey"))


	
