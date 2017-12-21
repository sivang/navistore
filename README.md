naviStore
=========

Pure Python implementation of a key value store using the twisted.web framework
Navistore Copyright (C) 2011 Sivan Greenberg <sivan@omniqueue.com>


Following Python Zen (https://www.python.org/dev/peps/pep-0020/):

	- A reference key value store engine written in Python, using twisted.web.
	- Very simply coded, easy to study.
	- Uses proven components for critical path; hence
	- Not just an example, can be used in production (used to distribute config data).
	- Supports replication.
	- Has the author's name in its own name, reversed.
	- Open source, released under the GNU v2/v3 General Public License
  
Navistore is an example implementation of a key/value HTTP rest api
storage engine. It is loosely coupled, and revolves mainly around
a reference interface specification that defines the API a storage
backend needs to support, if to be used by Navistore. Since using
twisted.web for network support, it deals mainly with the logic
one can put into a server implementation, examplified with replication
support that Navistore has.
Navistore was designed with testability in mind, and hence already
contains a test suite that backend implementors can 'plugin' to
in order to make sure their backend is compliant with the interface.
Navistore was developed through a Test Driven Development process; this
greatly enabled good design and easier process in development iterations,
but took more time at start of development for design of APIs 
and interface as a result of tests design.
Design followed the following delimitations:
	- Navistore is used inside a LAN, so no need to deal with authentication.
	- The LAN usecase allowed for a rather naive replication implementation,
  	  that might not hold in deployment across WANs due to latency.
	- Replication strategy assumes no issue with bandwidth; e.g. LAN usecase.
	- Access to specific value is mostly done by the same specific client over time, 
	  this is mainly due to the sqlite3 backend, but can be easily improved
	  with adding support for highly concurrent MVCC stores like CouchDB. 
	  The current implementation does not try to answer MVCC problem domain,
	  as this is a subject for great research and years of development and is
	  already addressed by available market solutions.
	- twisted is performant enough and robust to handle load given a backend
	  does not block or is latent in handling reads/writes.
There is currently only one backend provided, that uses sqlite3 for
the actual data storage. However, given the defined interface and
the reference backend as a base point, it shouldn't be hard to add
more backends. sqlite3 was chosen as it is concurrent and performant 
given transactions are kept short and small, which Navistore follows 
as well. Sqlite is also a good reference point since using the 
DBI 2.0 specification one can upgrade to an enterprise grade database 
server with a change of a mere connection string!
The Navistore package contains:
	- nhttpserver: A twisted.web based server script that implements the rest api
	  and does the actual serving of values by keys through HTTP. To learn about
	  the definition of the rest API, look at the respective test, testHttpBackend.
	- backend: This subpackage holds all backend code that nhttpserver uses, 
	  including tests.
