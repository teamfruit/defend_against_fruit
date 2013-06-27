import os
from nose.tools import raises, eq_
from daf_fruit_dist.build_info_utils import collect_env_info, EnvInfo


###############################################################################
######################################################################### Tests

def test_all_required_set():
    """
    Test that all required environment variables being set results in no
    error.
    """
    with only_these_environment_variables_set(ALL_REQ_ENV_VARS):
        env_info = collect_env_info()

    validate_env_info_against_ideal(
        actual=env_info,
        expected=expected_using_build_name)


@raises(RuntimeError)
def test_no_required_set():
    """
    Test that no required environment variables being set results in an
    error.
    """
    with no_environment_variables_set():
        collect_env_info()


@raises(RuntimeError)
def test_all_required_set_except_major_version():
    """
    Test that all required environment variables being set except
    MAJOR_VERSION generates an error.
    """
    all_except_major_version = dict_subtract(ALL_REQ_ENV_VARS, 'MAJOR_VERSION')

    with only_these_environment_variables_set(all_except_major_version):
        collect_env_info()


@raises(RuntimeError)
def test_all_required_set_except_minor_version():
    """
    Test that all required environment variables being set except
    MINOR_VERSION generates an error.
    """
    all_except_minor_version = dict_subtract(ALL_REQ_ENV_VARS, 'MINOR_VERSION')

    with only_these_environment_variables_set(all_except_minor_version):
        collect_env_info()


@raises(RuntimeError)
def test_all_required_set_except_build_number():
    """
    Test that all required environment variables being set except
    BUILD_NUMBER generates an error.
    """
    all_except_build_number = dict_subtract(ALL_REQ_ENV_VARS, 'BUILD_NUMBER')

    with only_these_environment_variables_set(all_except_build_number):
        collect_env_info()


@raises(RuntimeError)
def test_all_required_set_except_build_name_and_teamcity_buildconf_name():
    """
    Test that all required environment variables being set except
    BUILD_NAME *and* TEAMCITY_BUILDCONF_NAME generates an error.
    """
    all_except_any_build_name = dict_subtract(
        ALL_REQ_ENV_VARS, ('BUILD_NAME', 'TEAMCITY_BUILDCONF_NAME'))

    with only_these_environment_variables_set(all_except_any_build_name):
        collect_env_info()


def test_all_required_set_except_build_name():
    """
    Test that all required environment variables being set except
    BUILD_NAME is happy.
    """
    all_except_build_name = dict_subtract(ALL_REQ_ENV_VARS, 'BUILD_NAME')

    with only_these_environment_variables_set(all_except_build_name):
        env_info = collect_env_info()

    validate_env_info_against_ideal(
        actual=env_info,
        expected=expected_using_teamcity_buildconf_name)


def test_all_required_set_except_teamcity_buildconf_name():
    """
    Test that all required environment variables being set except
    TEAMCITY_BUILDCONF_NAME is happy.
    """
    all_but_teamcity_buildconf_name = dict_subtract(
        ALL_REQ_ENV_VARS, 'TEAMCITY_BUILDCONF_NAME')

    with only_these_environment_variables_set(all_but_teamcity_buildconf_name):
        env_info = collect_env_info()

    validate_env_info_against_ideal(
        actual=env_info,
        expected=expected_using_build_name)


@raises(ValueError)
def test_non_integer_build_number():
    """
    Test that all required environment variables being set except
    BUILD_NUMBER generates an error.
    """
    all_set_with_non_int_build_num = dict(ALL_REQ_ENV_VARS)
    all_set_with_non_int_build_num['BUILD_NUMBER'] = 'foo'

    with only_these_environment_variables_set(all_set_with_non_int_build_num):
        collect_env_info()


def test_custom_build_agent_name():
    """
    Test that setting a custom BUILD_AGENT_NAME works.
    """
    custom_build_agent_name = 'Agent Smith'

    env = dict(
        ALL_REQ_ENV_VARS.items() + [
            ('BUILD_AGENT_NAME', custom_build_agent_name)])

    with only_these_environment_variables_set(env):
        env_info = collect_env_info()

    eq_(env_info.build_agent_name, custom_build_agent_name)


###############################################################################
######################################################### Test Helper Utilities

def no_environment_variables_set():
    return StashEnviron()


def only_these_environment_variables_set(variables):
    return StashEnviron(variables)


class StashEnviron(object):
    def __init__(self, temp_vars=None):
        self.__temp_vars = temp_vars or {}

    def __enter__(self):
        self.__environ = os.environ
        os.environ = self.__temp_vars

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.environ = self.__environ


def dict_subtract(dictionary, keys_to_subtract):
    d = dict(dictionary)
    if isinstance(keys_to_subtract, basestring):
        keys_to_subtract = (keys_to_subtract,)
    for k in keys_to_subtract:
        del d[k]
    return d


ALL_REQ_ENV_VARS = {
    'MAJOR_VERSION': '5',
    'MINOR_VERSION': '5',
    'BUILD_NUMBER': '5',
    'BUILD_NAME': 'Foo',
    'TEAMCITY_BUILDCONF_NAME': 'Bar'}

ideal = ALL_REQ_ENV_VARS
ideal_build_version = '{}.{}.{}'.format(
    ideal['MAJOR_VERSION'], ideal['MINOR_VERSION'], ideal['BUILD_NUMBER'])
ideal_build_number = int(ideal['BUILD_NUMBER'])
ideal_build_agent_name = 'TeamCity'
ideal_build_agent_version = None

expected_using_build_name = EnvInfo(
    build_version=ideal_build_version,
    build_number=ideal_build_number,
    build_agent_name=ideal_build_agent_name,
    build_agent_version=ideal_build_agent_version,
    build_name=ideal['BUILD_NAME'])

expected_using_teamcity_buildconf_name = EnvInfo(
    build_version=ideal_build_version,
    build_number=ideal_build_number,
    build_agent_name=ideal_build_agent_name,
    build_agent_version=ideal_build_agent_version,
    build_name=ideal['TEAMCITY_BUILDCONF_NAME'])


def validate_env_info_against_ideal(actual, expected):
    eq_(actual.build_version, expected.build_version)
    eq_(actual.build_number, expected.build_number)
    eq_(actual.build_agent_name, expected.build_agent_name)
    eq_(actual.build_agent_version, expected.build_agent_version)
    eq_(actual.build_name, expected.build_name)
