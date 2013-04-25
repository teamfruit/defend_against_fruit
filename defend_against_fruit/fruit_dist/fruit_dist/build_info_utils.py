from collections import namedtuple
from functools import partial
from fruit_dist.artifactory import artifactory_rest, repo_detail
from fruit_dist.build.agent import Agent
from fruit_dist.build.build_info import BuildInfo
from fruit_dist.build.build_retention import BuildRetention
from fruit_dist.build.module import Module
from fruit_dist.iso_time import ISOTime
import json
import os


EnvInfo = namedtuple(
    'EnvInfo', [
        'build_name',
        'build_number',
        'build_agent_name',
        'build_agent_version',
        'build_version'])


def collect_env_info():
    env_errors = []
    check_environ = partial(_get_environ, error_fn=env_errors.append)

    major_version = check_environ('MAJOR_VERSION')
    minor_version = check_environ('MINOR_VERSION')
    build_number = check_environ('BUILD_NUMBER')
    build_name = check_environ(('BUILD_NAME', 'TEAMCITY_BUILDCONF_NAME'))

    if env_errors:
        msg = os.linesep.join(
            ['The following environment variables should be set but are not:'] +
            map(lambda vars_tried: ('    => ' + ' or '.join(map(repr, vars_tried))), env_errors))
        raise RuntimeError(msg)

    build_number = int(build_number)
    build_agent_name = _get_environ('BUILD_AGENT_NAME', default='TeamCity')
    build_agent_version = _get_environ(('BUILD_AGENT_VERSION', 'TEAMCITY_VERSION'))
    build_version = '{}.{}.{}'.format(major_version, minor_version, build_number)

    return EnvInfo(
        build_name=build_name,
        build_number=build_number,
        build_agent_name=build_agent_name,
        build_agent_version=build_agent_version,
        build_version=build_version)


def merge_module_info_files(build_info_files, env_info):
    if env_info.build_agent_name and env_info.build_agent_version:
        build_agent = Agent(name=env_info.build_agent_name, version=env_info.build_agent_version)
    else:
        build_agent = None

    bi_builder = BuildInfo.Builder(
        version=env_info.build_version,
        name=env_info.build_name,
        number=env_info.build_number,
        type='GENERIC',
        started=ISOTime.now().as_str,
        build_agent=build_agent,
        artifactory_principal="admin",
        agent=Agent(name="defend_against_fruit", version="5.2"),
        build_retention=BuildRetention(
            count=-1,
            delete_build_artifacts=False))

    if build_info_files:
        for build_info_file in build_info_files:
            with open(build_info_file, 'r') as f:
                bi_builder.add_module(Module.from_json_data(json.loads(f.read())))

    return bi_builder.build()


def get_deploy_artifact_function(repo_details, env_info=None, verify_cert=True):
    # Create a short-hand version of the deploy function with the just the repo details filled out.
    if env_info is None:
        attributes = None
    else:
        attributes = {
            'build.name': env_info.build_name,
            'build.number': env_info.build_number}

    return partial(
        artifactory_rest.deploy_globbed_files,
        repo_base_url=repo_details.repo_base_url,
        repo_push_id=repo_details.repo_push_id,
        username=repo_details.username,
        password=repo_details.password,
        attributes=attributes,
        verify_cert=verify_cert)


def get_deploy_build_info_function(repo_details, verify_cert=True):
    return partial(
        artifactory_rest.publish_build_info,
        repo_base_url=repo_details.repo_base_url,
        username=repo_details.username,
        password=repo_details.password,
        verify_cert=verify_cert)


def get_deploy_functions(env_info=None, verify_cert=True):
    repo_details = repo_detail.read_options()
    return (
        get_deploy_artifact_function(repo_details, env_info=env_info, verify_cert=verify_cert),
        get_deploy_build_info_function(repo_details, verify_cert=verify_cert))


def build_info_to_text(build_info):
    return json.dumps(build_info.as_json_data, sort_keys=True, indent=4)


def _get_environ(order, default=None, error_fn=None):
    if isinstance(order, basestring):
        order = (order,)
    for o in order:
        try:
            return os.environ[o]
        except KeyError:
            pass
    if error_fn:
        error_fn(order)
    return default
