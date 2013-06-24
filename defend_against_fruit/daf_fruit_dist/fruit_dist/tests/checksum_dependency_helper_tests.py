from collections import namedtuple
from nose.tools import eq_, raises
from pip.exceptions import DistributionNotFound
from requests import RequestException
from fruit_dist.checksum_dependency_helper import ChecksumDependencyHelper


def found_files_and_checksums_test():
    """Verify that finding a package and its associated checksums results in those checksums being returned."""
    TestContext(
        determine_file_path_succeeds=True,
        determine_checksums_succeeds=True,
        expected_checksums=checksums_found).run()


def failed_to_find_file_test():
    """Verify that failing to find a package results in None being returned for each checksum."""
    TestContext(
        determine_file_path_succeeds=False,
        determine_checksums_succeeds=False,
        expected_checksums=checksums_not_found).run()


@raises(RequestException)
def found_file_but_not_checksums_test():
    """Verify that successfully finding a package but not its associated checksums results in an exception."""
    TestContext(
        determine_file_path_succeeds=True,
        determine_checksums_succeeds=False,
        checksum_lookup_exception=RequestException).run()


########################################################################################################################
################################################################################################## Test Data and Helpers

Checksums = namedtuple('Hashes', ('md5', 'sha1'))

checksums_found = Checksums(md5='MD5', sha1='SHA1')
checksums_not_found = Checksums(md5=None, sha1=None)


class TestContext(object):
    def __init__(
            self,
            determine_file_path_succeeds,
            determine_checksums_succeeds,
            expected_checksums=None,
            checksum_lookup_exception=Exception):

        self.__checksums = expected_checksums
        self.__checksum_lookup_exception = checksum_lookup_exception

        if determine_file_path_succeeds:
            self.__determine_file_path_fn = lambda pkg_name, pkg_version: None
        else:
            def fn(pkg_name, pkg_version):
                raise DistributionNotFound()
            self.__determine_file_path_fn = fn

        if determine_checksums_succeeds:
            self.__determine_checksums_fn = lambda dependency_path: self.__checksums
        else:
            def fn(dependency_path):
                raise self.__checksum_lookup_exception()
            self.__determine_checksums_fn = fn

    def __verify_checksums(self, actual_md5, actual_sha1):
        eq_(actual_md5, self.__checksums.md5)
        eq_(actual_sha1, self.__checksums.sha1)

    def run(self):
        checksum_dependency_helper = ChecksumDependencyHelper(
            determine_file_path_fn=self.__determine_file_path_fn,
            determine_checksums_from_file_path_fn=self.__determine_checksums_fn)

        actual_md5, actual_sha1 = checksum_dependency_helper(artifact_id=None, version=None)

        self.__verify_checksums(actual_md5, actual_sha1)
