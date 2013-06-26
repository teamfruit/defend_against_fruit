#!/usr/bin/env python
import os
import sys

if sys.version_info[0] == 3:
    import configparser
    from urllib.request import urlretrieve
else:
    import ConfigParser as configparser
    from urllib import urlretrieve

config = configparser.SafeConfigParser()
config.read('ci_config/virtualenv_util.cfg')
bootstrap_url = config.get('global', 'bootstrap_url')
destination = os.path.basename(bootstrap_url)

if not os.path.exists(destination):
    urlretrieve(bootstrap_url, destination)

execfile(destination)

