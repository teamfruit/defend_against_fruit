from nose.tools import eq_, raises
from nose.plugins.attrib import attr
from requests import HTTPError

from fruit_dist.artifactory.artifactory_rest import determine_checksums
from fruit_dist.artifactory.repo_detail import read_options
from fruit_dist.build.constants import PYTHON_GROUP_ID


nose_file_path = "{}/nose/nose-1.2.1.tar.gz".format(PYTHON_GROUP_ID)


@attr("integration")
def test_typical_usage():
    repo_details = read_options()
    found_checksums = determine_checksums(username=repo_details.username,
                                          password=repo_details.password,
                                          repo_base_url=repo_details.repo_base_url,
                                          repo_pull_id=repo_details.repo_pull_id,
                                          file_path=nose_file_path,
                                          verify_cert=False)

    eq_(found_checksums.sha1, "02cc3ffdd7a1ce92cbee388c4a9e939a79f66ba5")
    eq_(found_checksums.md5, "735e3f1ce8b07e70ee1b742a8a53585a")


@attr("integration")
@raises(HTTPError)
def test_invalid_username():
    repo_details = read_options()
    determine_checksums(username="badusername123",
                        password=repo_details.password,
                        repo_base_url=repo_details.repo_base_url,
                        repo_pull_id=repo_details.repo_pull_id,
                        file_path=nose_file_path,
                        verify_cert=False)


@attr("integration")
@raises(HTTPError)
def test_invalid_password():
    repo_details = read_options()
    determine_checksums(username=repo_details.username,
                        password="ThisBadPasswordCantBeRight",
                        repo_base_url=repo_details.repo_base_url,
                        repo_pull_id=repo_details.repo_pull_id,
                        file_path=nose_file_path,
                        verify_cert=False)


@attr("integration")
@raises(HTTPError)
def test_bad_file_path():
    repo_details = read_options()
    determine_checksums(username=repo_details.username,
                        password=repo_details.password,
                        repo_base_url=repo_details.repo_base_url,
                        repo_pull_id=repo_details.repo_pull_id,
                        file_path="badorg/badmodule/bebad-1.2.3.tar.gz",
                        verify_cert=False)


@attr("integration")
@raises(HTTPError)
def test_invalid_repo_pull_id():
    repo_details = read_options()
    determine_checksums(username=repo_details.username,
                        password=repo_details.password,
                        repo_base_url=repo_details.repo_base_url,
                        repo_pull_id="bad-repo-pull-id",
                        file_path=nose_file_path,
                        verify_cert=False)