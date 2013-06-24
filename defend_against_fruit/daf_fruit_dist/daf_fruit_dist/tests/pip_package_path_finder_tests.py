import re
from nose.plugins.attrib import attr
from nose.tools import raises, eq_
from pip.exceptions import DistributionNotFound
import pkg_resources
from daf_fruit_dist.build.constants import PYTHON_GROUP_ID
from daf_fruit_dist.pip_package_path_finder import PipPackagePathFinder, _requirement_finder


@attr("integration")
def test_available_package_and_version():
    ################
    #Assemble test fixtures
    finder = PipPackagePathFinder()

    ############
    #Execute unit under test
    observed_file_path = finder.determine_file_path(pkg_name="nose", pkg_version="1.2.1")

    ###########
    #Assert results
    match_regex = r"{}/nose/nose.*1\.2\.1.*".format(PYTHON_GROUP_ID)
    path_as_expected = re.match(match_regex, observed_file_path)
    assert path_as_expected, "match_regex: {} should match observed_file_path: {}".format(
        match_regex, observed_file_path)


@attr("integration")
@raises(DistributionNotFound)
def test_unavailable_version():
    finder = PipPackagePathFinder()
    finder.determine_file_path(pkg_name="nose", pkg_version="999.999.999")


@attr("integration")
@raises(DistributionNotFound)
def test_unavailable_package():
    finder = PipPackagePathFinder()
    finder.determine_file_path(pkg_name="non-existent-pkg-1234", pkg_version="1.2.1")


class FinderStub(object):
    def __init__(self, expected_reqs_and_rv_pairs):
        self.expected = FinderStub._parse_expected_reqs(expected_reqs_and_rv_pairs)
        self.times_called = 0

    @staticmethod
    def _parse_expected_reqs(expected_reqs_and_rv_pairs):
        expected_list = []

        for desired_req_str, return_value in expected_reqs_and_rv_pairs:
            expected_list.append((pkg_resources.Requirement.parse(desired_req_str), return_value))

        return tuple(expected_list)

    def find_requirement(self, req, upgrade):
        desired_req, return_value = self.expected[self.times_called]
        eq_(req.req, desired_req)

        self.times_called += 1

        if return_value is None:
            raise DistributionNotFound()
        else:
            return return_value


@raises(DistributionNotFound)
def test_nothing_matches():
    finder = FinderStub(expected_reqs_and_rv_pairs=(
        ('some-package_name==1.2.0', None),
        ('some-package-name==1.2.0', None),
        ('some_package_name==1.2.0', None),
    ))

    _requirement_finder(finder=finder, req_str='some-package_name==1.2.0')


def test_first_try_matches():
    dummy_link = 'dummy link'
    real_package_string = 'some-package_name==1.2.0'

    finder = FinderStub(expected_reqs_and_rv_pairs=(
        (real_package_string, dummy_link),
    ))

    actual_result = _requirement_finder(finder=finder, req_str=real_package_string)

    eq_(actual_result, dummy_link)


def test_second_try_matches():
    dummy_link = 'dummy link'
    real_package_string = 'some-package_name==1.2.0'

    finder = FinderStub(expected_reqs_and_rv_pairs=(
        (real_package_string, None),
        ('some-package-name==1.2.0', dummy_link),
    ))

    actual_result = _requirement_finder(finder=finder, req_str=real_package_string)

    eq_(actual_result, dummy_link)


def test_third_try_matches():
    dummy_link = 'dummy link'
    real_package_string = 'some-package_name==1.2.0'

    finder = FinderStub(expected_reqs_and_rv_pairs=(
        (real_package_string, None),
        ('some-package-name==1.2.0', None),
        ('some_package_name==1.2.0', dummy_link),
    ))

    actual_result = _requirement_finder(finder=finder, req_str=real_package_string)

    eq_(actual_result, dummy_link)
