from functools import partial
from pip.baseparser import ConfigOptionParser
from pip.exceptions import DistributionNotFound
from pip.index import PackageFinder
from pip.req import InstallRequirement
from daf_fruit_dist.build.constants import PYTHON_GROUP_ID
from daf_fruit_dist.url_utils import subtract_index_url


class PipPackagePathFinder(object):
    """Performs the PIP related aspects of determining a module path within Artifactory"""

    def __init__(self):
        self.pip_index_url = PipPackagePathFinder._get_pip_index_url()

        package_finder = PackageFinder(
            find_links=[],
            index_urls=[self.pip_index_url],
            use_mirrors=False,
            mirrors=[])

        self.finder = partial(_requirement_finder, finder=package_finder)

    @staticmethod
    def _get_pip_index_url():
        pip_config_parser = ConfigOptionParser(name='daf_fruit_dist')
        try:
            return dict(pip_config_parser.get_config_section('global'))['index-url']
        except KeyError:
            raise KeyError(
                'The "index-url" option was not specified under the [global] section within any of the following '
                'files: {}'.format(pip_config_parser.get_config_files()))

    def _determine_pip_tail(self, pkg_name, pkg_version):
        """This stuff is only coming from pip.ini."""
        req_str = '{}=={}'.format(pkg_name, pkg_version)
        link = self.finder(req_str=req_str)

        pip_tail = subtract_index_url(
            index_url=self.pip_index_url,
            pkg_url=link.url_without_fragment)

        return pip_tail

    def determine_file_path(self, pkg_name, pkg_version):
        """Determines path portion of python module URL used by PIP to download module earlier.

        This method uses the PIP tooling to determine the download URL which corresponds to a given python
        package name and version.
        """
        pip_tail = self._determine_pip_tail(pkg_name, pkg_version)

        file_path = '{python_group_id}/{artifact_path}'.format(
            python_group_id=PYTHON_GROUP_ID,
            artifact_path=pip_tail)

        return file_path


def _get_package_name_alternatives(req_str):
    yield req_str
    yield req_str.replace('-', '_')
    yield req_str.replace('_', '-')


def _requirement_finder(finder, req_str):
    """
    First try to find the given requirement. If that fails, try several alternatives. If they all fail, raise
    the first exception caught.
    """
    err = None

    for req_name in _get_package_name_alternatives(req_str):
        req = InstallRequirement(req=req_name, comes_from=None)
        try:
            return finder.find_requirement(req=req, upgrade=True)
        except DistributionNotFound as e:
            if err is None:
                err = e
    raise err
