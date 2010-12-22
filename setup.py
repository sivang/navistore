#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='navistore',
      version='0.0.1',
      packages=find_packages('.'),
      scripts=['nhttpserver'], 
      include_package_data = True,
      package_data = {
      	'' : ['*.js'],
	}
      )


