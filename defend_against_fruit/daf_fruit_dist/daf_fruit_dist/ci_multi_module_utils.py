import logging
import os
from file_management import DirectoryContextManager
from file_management import compute_repo_path_from_module_name
from file_management import get_submodule_info
from exec_utils import run_ci_script
from daf_fruit_dist.build_info_utils import merge_module_info_files
from daf_fruit_dist.build_info_utils import build_info_to_text
from daf_fruit_dist.build_info_utils import get_deploy_functions


def execute_submodule_run(submodule_order):
    # Run the CI scripts in all sub-modules.
    for module in submodule_order:
        with DirectoryContextManager(module):
            logging.info('cwd: ' + os.getcwd())
            run_ci_script()


def _collect_build_info(submodule_order, env_info):
    module_info_files = filter(None, map(get_submodule_info, submodule_order))
    merged = merge_module_info_files(module_info_files, env_info)
    return merged


def deploy_all_modules(module_order, env_info, verify_cert=True):
    build_info = _collect_build_info(module_order, env_info)

    logging.debug(os.linesep.join((
        'Build info:',
        build_info_to_text(build_info))))

    deploy_artifact, deploy_build_info = get_deploy_functions(
        env_info=env_info,
        verify_cert=verify_cert)

    def deploy_dist(module):
        path = compute_repo_path_from_module_name(module)
        return deploy_artifact(
            path=path,
            glob_patterns=[os.path.join(module, 'dist', '*')])

    deployed_files = []

    for module in module_order:
        deployed_files.extend(deploy_dist(module))

    deploy_build_info(build_info=build_info)

    return deployed_files
