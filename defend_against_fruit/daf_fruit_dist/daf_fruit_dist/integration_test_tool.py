import argparse
from collections import namedtuple
import json
import logging
import os
import sys
import textwrap
from daf_fruit_dist.artifactory.artifactory_rest import publish_build_info, build_promote
from daf_fruit_dist.build.agent import Agent
from daf_fruit_dist.build.build_info import BuildInfo
from daf_fruit_dist.build.build_retention import BuildRetention
from daf_fruit_dist.build.constants import PYTHON_SDIST, PYTHON_FREEZE
from daf_fruit_dist.build.id import Id
from daf_fruit_dist.build.module import Module
from daf_fruit_dist.build.promotion_request import PromotionRequest
from daf_fruit_dist.build_info_utils import build_info_to_text


_OPTION_NAMES = {
    'base_url': 'PYPI_SERVER_BASE',
    'username': 'PYPI_PUSH_USERNAME',
    'password': 'PYPI_PUSH_PASSWORD'}


def execute():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    args = _parse_args()
    sub_command_function = args.func
    sub_command_function(args)


EnvTemplateValues = namedtuple('EnvTemplateValues', _OPTION_NAMES.keys())


def _read_environment_for_defaults():
    env_values = {}

    for opt, env in _OPTION_NAMES.iteritems():
        env_values[opt] = os.environ.get(env, None)

    return EnvTemplateValues(**env_values)


def _parse_and_validate(parser, command_line_args):
    env_template_values = _read_environment_for_defaults()

    parsed_args = parser.parse_args(command_line_args)

    def handle_arg(key_name):
        opt_value = getattr(parsed_args, key_name, None)
        if not opt_value:
            opt_value = getattr(env_template_values, key_name, None)

        if not opt_value:
            msg = (
                "Error: {key_name} value must be provided.\n\n"
                "This can be done using the relevant command line argument\n"
                "or the corresponding environment variable: {env_name}\n\n{usage}".format(
                    key_name=key_name,
                    env_name=_OPTION_NAMES[key_name],
                    usage=parser.format_usage()))
            print msg
            sys.exit(1)

        setattr(parsed_args, key_name, opt_value)

    for key_name in _OPTION_NAMES:
        handle_arg(key_name=key_name)

    return parsed_args


def _parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Integration test utility for testing Artifactory Rest API calls.',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.epilog = textwrap.dedent('''
            To see options for a subcommand:
                > python {} <subcommand> --help'''.format(parser.prog))

    parser.add_argument('--username', help='Artifactory username')
    parser.add_argument('--password', help='Artifactory password')
    parser.add_argument('--base-url', help='Artifactory base URL')
    parser.add_argument('--ignore-cert-errors', action='store_true', default=False, help='Verify certificate')

    subparsers = parser.add_subparsers(title="subcommands", description="Various subcommands for testing")

    parser_build_info = subparsers.add_parser('build-info')
    parser_build_info.add_argument('--name', action='store', required=True, help="name to use in build-info")
    parser_build_info.add_argument('--number', action='store', required=True, help="build number to use in build-info")
    parser_build_info.set_defaults(func=_build_info)

    #build_name, build_number
    parser_build_info = subparsers.add_parser('build-promote')
    parser_build_info.add_argument('--name', action='store', required=True, help="build name to promote")
    parser_build_info.add_argument('--number', action='store', required=True, help="build number to promote")
    parser_build_info.set_defaults(func=_build_promote)

    return _parse_and_validate(parser=parser, command_line_args=args)


def _build_promote(args):
    my_build_number = args.number
    my_build_name = args.name
    promotion_request = PromotionRequest(
        status="monkey",
        comment="promoted using integration test tool",
        ci_user="builder",
        timestamp="2013-03-21T11:30:06.143-0500",
        dry_run=False,
        target_repo="pypi-teamfruit-2-local",
        properties={
            "components": ["c1", "c3", "c14"],
            "release-name": ["fb3-ga"]}
    )
    promotion_request_as_text = json.dumps(promotion_request.as_json_data, sort_keys=True, indent=4)
    logging.debug(promotion_request_as_text)

    promotion_response_json = build_promote(
        username=args.username,
        password=args.password,
        repo_base_url=args.base_url,
        build_name=my_build_name,
        build_number=my_build_number,
        promotion_request=promotion_request,
        verify_cert=not args.ignore_cert_errors
    )

    print "Promotion Response {}".format(promotion_response_json)


def _build_info(args):
    my_build_number = args.number
    my_build_name = args.name

    bi_builder = BuildInfo.Builder(
        version="2.2.2",
        name=my_build_name,
        number=my_build_number,
        type='GENERIC',  # Looks like valid values are "GENERIC", "MAVEN", "ANT", "IVY" and "GRADLE"
        started="2013-03-21T10:49:01.143-0500",  # Looks like time format is very specific
        duration_millis=10000,
        artifactory_principal="dude",
        agent=Agent(name="defend_against_fruit", version="5.2"),
        build_agent=Agent(name="TeamCity", version="1.3"),
        build_retention=BuildRetention(
            count=-1,
            delete_build_artifacts=False,
            build_numbers_not_to_be_discarded=[111, 999])  # Is this for TeamCity "pinned" builds?
    )
    module_builder = Module.Builder(id=Id(group_id="python", artifact_id="daf_fruit_dist", version="1.2.15"))
    module_builder.add_artifact(
        type=PYTHON_SDIST,
        name="daf_fruit_dist-1.2.15.tar.gz",
        sha1="0a66f5619bcce7a441740e154cd97bad04189d86",
        md5="2a17acbb714e7b696c58b4ca6e07c611")
    module_builder.add_artifact(
        type=PYTHON_FREEZE,
        name="daf_fruit_dist-1.2.15-requirements.txt",
        sha1="06e5f0080b6b15704be9d78e801813d802a90625",
        md5="254c0e43bbf5979f8b34ff0428ed6931"
    )
    module_builder.add_dependency(
        type=PYTHON_SDIST,
        id=Id(group_id="python", artifact_id="nose", version="1.2.1"),
        sha1="02cc3ffdd7a1ce92cbee388c4a9e939a79f66ba5",
        md5="735e3f1ce8b07e70ee1b742a8a53585a")

    bi_builder.add_module(module_builder.build())

    build_info = bi_builder.build()

    logging.debug(build_info_to_text(build_info))

    publish_build_info(
        username=args.username,
        password=args.password,
        repo_base_url=args.base_url,
        build_info=build_info,
        verify_cert=not args.ignore_cert_errors
    )


if __name__ == "__main__":
    execute()