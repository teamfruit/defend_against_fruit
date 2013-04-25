import os

_DEFAULT_MAJOR_REVISION = 1
_DEFAULT_MINOR_REVISION = 1
_DEFAULT_BUILD_NUMBER = 0


class VersionUtils(object):
    def __init__(self, basedir=None):
        super(VersionUtils, self).__init__()
        self.basedir = basedir or os.getcwd()
        self.version_file = os.path.join(os.path.abspath(basedir), 'version.txt')

    def write_version(self, major_version=None, minor_version=None, build_number=None):
        if major_version is None:
            major_version = os.environ.get('MAJOR_VERSION', _DEFAULT_MAJOR_REVISION)
        if minor_version is None:
            minor_version = os.environ.get('MINOR_VERSION', _DEFAULT_MINOR_REVISION)
        if build_number is None:
            build_number = os.environ.get('BUILD_NUMBER', _DEFAULT_BUILD_NUMBER)

        version = '{}.{}.{}'.format(major_version, minor_version, build_number)

        with open(self.version_file, "w") as f:
            f.write(version)

        return version

    def read_version(self):
        return self._read_text(self.version_file)

    def _read_text(self, filename):
        return unicode(open(filename).read()) if os.path.exists(filename) else None
