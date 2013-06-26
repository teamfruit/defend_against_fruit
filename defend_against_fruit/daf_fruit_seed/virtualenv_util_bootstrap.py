import imp
import os
import sys
if sys.version_info >= (3, 0):
    import configparser
    import urllib.request as urllib
else:
    import ConfigParser as configparser
    import urllib2 as urllib
import argparse
import tarfile
import re


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(ROOT_PATH, 'virtualenv_util.cfg')
VIRTUALENV_UTIL_PACKAGE_NAME = 'daf_fruit_orchard'
VIRTUALENV_UTIL_PACKAGE_FILE_EXTENSION = '.tar.gz'

parser = argparse.ArgumentParser(
    description='Bootstrap script for the virtualenv_util module (will '
                'attempt to download and execute the virtualenv_util main '
                'routine')
parser.add_argument('--cfg_file', default=CONFIG_FILE_PATH)
options, unknown_args = parser.parse_known_args()

# Parse the virtualenv_util config file, if present.
# NOTE: At the moment this will likely fail unless
# virtualenv_util_path OR pypi_server is set in the config file or
# passed in as arguments.
config_file_global_settings = {}
if os.path.isfile(options.cfg_file):
    config = configparser.SafeConfigParser()
    ROOT_PATH = os.path.abspath(os.path.dirname(options.cfg_file))
    try:
        config.read([options.cfg_file])
        config_file_global_settings = dict(config.items("global"))
    except:
        pass

pypi_server = config_file_global_settings.get(
    'pypi_pull_server', None)
virtualenv_util_version = config_file_global_settings.get(
    'virtualenv_util_version', None)
virtualenv_util_path = config_file_global_settings.get(
    'virtualenv_util_path', None)
virtualenv_util_local = False

# Is the user requesting that a local virtualenv_util package be used?
if virtualenv_util_path is not None:
    print('Using local {} package at {}...'.format(
        VIRTUALENV_UTIL_PACKAGE_NAME, virtualenv_util_path))

    path_exists = os.path.isfile(
        os.path.join(virtualenv_util_path, 'virtualenv_util.py'))

    if not path_exists:
        print(
            'Could not find local {} package, attempting to '
            'download...'.format(VIRTUALENV_UTIL_PACKAGE_NAME))
        virtualenv_util_path = None
    else:
        virtualenv_util_path = os.path.normpath(
            os.path.join(ROOT_PATH, virtualenv_util_path))
        virtualenv_util_local = True

else:
    # Look for something that appears like a virtualenv_util package
    # already in the root directory. We do not attempt to re-bootstrap
    # (redownload the virtualenv_util package) if one of the correct
    # version already exists.
    for item in os.listdir(ROOT_PATH):
        possible_dir = os.path.join(
            ROOT_PATH, item, VIRTUALENV_UTIL_PACKAGE_NAME)

        looks_like_virtualenv_util = item.startswith(
            VIRTUALENV_UTIL_PACKAGE_NAME)

        if looks_like_virtualenv_util and os.path.isdir(possible_dir):
            # Special case... if specific version was specified, make sure
            # it is the right version.
            if (virtualenv_util_version is None or (
                    virtualenv_util_version is not None and
                    item.split('-')[-1] == virtualenv_util_version)):
                virtualenv_util_path = possible_dir
                virtualenv_util_version = item.split('-')[-1]


# See if the virtualenv_util of the correct version has already been
# downloaded and unpacked.  If not, look at the config file to get
# the location where we should be getting the virtualenv_util package
# from.
if virtualenv_util_path is None:

    print('Checking for {} package on server {}...'.format(
        VIRTUALENV_UTIL_PACKAGE_NAME, pypi_server))

    # Was a fixed virtualenv_util version specified?  If not, we need to check
    # the PyPI server for the latest version.
    if virtualenv_util_version is None:
        virtualenv_util_url_dir = (
            pypi_server + '/' + VIRTUALENV_UTIL_PACKAGE_NAME)
        print('Looking in: {}'.format(virtualenv_util_url_dir))

        f_remote = urllib.urlopen(virtualenv_util_url_dir)
        index = f_remote.read()

        # Very simple regex parser that finds all hyperlinks in the index
        # HTML... this may break in some cases, but we want to keep it super
        # simple in the bootstrap.
        hyperlinks = re.findall('href="(.*?)"', str(index.lower()))

        # Get all hyperlinks that start with the virtualenv package name
        # and end with the package extension.
        versions = []
        for hyperlink in hyperlinks:
            if (
                    hyperlink.startswith(VIRTUALENV_UTIL_PACKAGE_NAME+'-') and
                    hyperlink.endswith(VIRTUALENV_UTIL_PACKAGE_FILE_EXTENSION)
            ):
                version = hyperlink.split('-')[-1].replace(
                    VIRTUALENV_UTIL_PACKAGE_FILE_EXTENSION, '')
                versions.append(version)

        print('Found versions: {}'.format(versions))

        # Sort the versions from lowest to highest.
        # NOTE: This simple sort will work for most versions we expect to
        # use in the virtualenv_util package.  This could be enhanced.
        versions.sort()

        # Select the highest version.
        virtualenv_util_version = versions[-1]

    print('Downloading {} package version {}...'.format(
          VIRTUALENV_UTIL_PACKAGE_NAME, virtualenv_util_version))

    # Download the package source tar from the server.
    virtualenv_util_tar_filename = '{}-{}{}'.format(
        VIRTUALENV_UTIL_PACKAGE_NAME,
        virtualenv_util_version,
        VIRTUALENV_UTIL_PACKAGE_FILE_EXTENSION)

    virtualenv_util_url = '/'.join([
        pypi_server,
        VIRTUALENV_UTIL_PACKAGE_NAME,
        virtualenv_util_tar_filename])

    f_remote = urllib.urlopen(virtualenv_util_url)
    f_local = open(os.path.join(ROOT_PATH, virtualenv_util_tar_filename), 'wb')
    f_local.write(f_remote.read())
    f_local.close()
    f_remote.close()

    # Unpack the tarball to the current directory.
    tarf = tarfile.open(
        os.path.join(ROOT_PATH, virtualenv_util_tar_filename),
        'r:gz')

    tarf.extractall(ROOT_PATH)
    tarf.close()

    # Remove the tarball from the current directory.
    try:
        os.unlink(os.path.join(ROOT_PATH, virtualenv_util_tar_filename))
    except:
        pass

    virtualenv_util_path = os.path.join(
        ROOT_PATH,
        '{}-{}'.format(
            VIRTUALENV_UTIL_PACKAGE_NAME,
            virtualenv_util_version),
        VIRTUALENV_UTIL_PACKAGE_NAME)

else:
    if not virtualenv_util_local:
        print(
            'Using previously downloaded {} package version {}...'.format(
                VIRTUALENV_UTIL_PACKAGE_NAME,
                virtualenv_util_version))

orchard_script = os.path.join(virtualenv_util_path, 'virtualenv_util.py')

print('Importing script: {}'.format(orchard_script))

virtualenv_util = imp.load_source(VIRTUALENV_UTIL_PACKAGE_NAME, orchard_script)
virtualenv_util.main(options.cfg_file)
