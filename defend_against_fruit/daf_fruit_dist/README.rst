The **daf_fruit_dist** package provides various utilities for setup utils and continuous integration.

This includes a few setup commands for interacting with an Artifactory server.

Overview
========
The fruit_dist module is part of a larger subsystem responsible for making continuous deployment
style usage of Artifactory possible. Most of the details are not yet documented outside of the
working examples.

Setuptools Command Lineage
==========================
We would like to thank Marian Neagul for his **setuptools_webdav** plugin which inspired
the setup commands here.

Setuptools Command QuickStart
==================

In order to use this plugin you need to add **daf_fruit_dist** to the **setup_requires** command in your setup.py.
This will instruct setuptools to download and use this plugin.

The **daf_fruit_dist** plugin provides the **artifactory_upload** command.

The Artifactory server that will be used for the upload, and the corresponding credentials, can be configured in your
**.pypirc** in the.


Example setup.py
----------------
 ::

	from setuptools import setup, find_packages
	setup(
	name="DummyProject",
	version="3.1.4",
	packages=find_packages(),
	setup_requires=["daf_fruit_dist"],
	)

Example .pypirc
---------------
 ::

	[webdav]
	repository = http://example.com/pypi # mandatory
	username = # Optional
	password = # Optional

Example invocation
------------------

 $ python setup.py sdist bdist artifactory_upload
