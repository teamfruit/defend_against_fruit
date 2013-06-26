import argparse
import sys
from ci_multi_module_utils import execute_submodule_run, deploy_all_modules
from daf_fruit_dist.build_info_utils import collect_env_info
from daf_fruit_dist.ci_single_module_utils import execute_sdist_run
from daf_fruit_dist.ci_single_module_utils import deploy_module


def standard_sdist_run(submodule_order=None, integration_tests_fn=None):
    args = _parse_args(sys.argv[1:])

    env_info = collect_env_info() if args.publish else None
    verify_cert = not args.no_cert_verify

    if submodule_order:
        execute_submodule_run(submodule_order)

        if not args.skip_int_tests and integration_tests_fn:
            integration_tests_fn()

        if args.publish:
            deploy_all_modules(
                module_order=submodule_order,
                env_info=env_info,
                verify_cert=verify_cert)
    else:
        execute_sdist_run()

        if not args.skip_int_tests and integration_tests_fn:
            integration_tests_fn()

        if args.publish:
            deploy_module(env_info=env_info, verify_cert=verify_cert)


def _parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Continuous integration utility responsible for invoking '
                    'the build system within a virtual environment')

    parser.add_argument(
        '--publish',
        action='store_true',
        help='Publish to build artifact repository.')

    parser.add_argument(
        '--no-cert-verify',
        action='store_false',
        help='Do not verify authenticity of host cert when using SSL.')

    parser.add_argument(
        '--skip-int-tests',
        action='store_true',
        help='Skip all integration tests.')

    return parser.parse_args(args)