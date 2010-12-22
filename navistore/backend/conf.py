"""
Configuration module: holds configuration constants used
by Navistore.
"""
import logging


# specify logleve here, according
# to the 'logging' module docs
LOGLEVEL = logging.DEBUG

# this is used for marking which paths 
# are actuall API calls rather than key
# storage operations.
# use can use this list to protect certain
# api calls from ever being called.
ALLOWED_VERBS = ['listkeys', 
			'reset',
			'dummy',]


# this defines special keys that act as 
# internal configurations of Navistore rather 
# than user stored values. This is used to
# exclude them from replication, for example
RESERVED_KEYS = ['_replication_slaves', ]

# Used by the replication support; this configures
# a list of hosts to disribute value modification 
# calls to.
# When this list is non empty, the navistore instance
# will communicate changes to those hosts as well, 
# such that they could be used for value retrival if
# the original instance fails or becomes overloaded.
# NOTE: This can also be set through the reference http
# server itself, and it *should* be implemeted in
# any reimplementations to allow to change this without
# restarts in real time. The values here are ofcourse
# overriden when this is set through the server.
# The reserved key by which to save the values is:
# '_replication_slaves', and the value should be a strin
# of the form:
# "http://hostname:port,....,"
# Where multiple hosts are delimited by a comma.
# NOTE: Not used currently as this can be dynamically
# set from the REST api.
SLAVES = ["127.0.0.1:8887", "127.0.0.1:8885"]
