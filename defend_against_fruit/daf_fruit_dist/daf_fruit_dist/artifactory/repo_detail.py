from collections import namedtuple
from distutils.errors import DistutilsOptionError
from distutils.dist import Distribution

RepoDetail = namedtuple(
    'RepoDetail', [
        'repo_base_url',
        'repo_push_id',
        'repo_pull_id',
        'username',
        'password'])


def read_options(
        repo_base_url=None,
        repo_push_id=None,
        repo_pull_id=None,
        username=None,
        password=None):

    if repo_base_url and repo_push_id and username and password:
        return RepoDetail(
            repo_base_url=repo_base_url,
            repo_push_id=repo_push_id,
            repo_pull_id=repo_pull_id,
            username=username,
            password=password)

    artifactory_opts = _read_artifactory_config_section()

    return RepoDetail(
        repo_base_url=_read_value_from_opts(artifactory_opts, 'repo_base_url'),
        repo_push_id=_read_value_from_opts(artifactory_opts, 'repo_push_id'),
        repo_pull_id=_read_value_from_opts(artifactory_opts, 'repo_pull_id'),
        username=_read_value_from_opts(artifactory_opts, 'username'),
        password=_read_value_from_opts(artifactory_opts, 'password'))


def _read_value_from_opts(artifactory_opts, key):
    try:
        config_file_name, config_value = artifactory_opts.get(key)
        return config_value
    except KeyError:
        return None


def _read_artifactory_config_section():
    dist = Distribution()
    file_names = dist.find_config_files()
    dist.parse_config_files(filenames=file_names)
    artifactory_config_key = "artifactory"
    artifactory_opts = dist.get_option_dict(artifactory_config_key)

    if not artifactory_opts:
        raise DistutilsOptionError(
            'Could not find a {} section in {}'.format(
                artifactory_config_key,
                file_names))

    return artifactory_opts
