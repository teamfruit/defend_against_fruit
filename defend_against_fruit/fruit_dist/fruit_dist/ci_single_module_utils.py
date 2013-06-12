import logging
import os
import shutil
from file_management import ensure_path_exists, split_ext, rm
from file_management import get_submodule_info
from file_management import compute_repo_path_from_module_name
from file_management import MODULE_INFO_DIR
from exec_utils import run_nosetests, install_dev, build_sdist
from build_info_utils import merge_module_info_files, build_info_to_text
from build_info_utils import get_deploy_functions
from version_utils import VersionUtils


def standard_py_run(script):
    _execute_py_run(script)


def standard_develop_run():
    _execute_develop_run()


def execute_sdist_run(integration_tests_fn=None):
    # Clean!
    _standard_clean()

    # Create the version.txt file.
    VersionUtils().write_version()

    # Run unit tests.
    run_nosetests()

    # Create sdist .tar.gz archive.
    build_sdist()

    # Run integration tests if any are specified.
    if integration_tests_fn:
        integration_tests_fn()


def _extract_single_module_from_build_info(build_info):
    if len(build_info.modules) != 1:
        raise RuntimeError(
            "One and only one module is expected in the build info of a "
            "single module build.")

    return build_info.modules[0]


def deploy_module(env_info, verify_cert=True):
    module_info_file = get_submodule_info(module_dir=".")

    build_info = merge_module_info_files(
        build_info_files=(module_info_file,),
        env_info=env_info)

    logging.debug(os.linesep.join(
        ('Build info:', build_info_to_text(build_info))))

    deploy_artifact, deploy_build_info = get_deploy_functions(
        env_info=env_info,
        verify_cert=verify_cert)

    module_info = _extract_single_module_from_build_info(build_info)
    path = compute_repo_path_from_module_name(module_info.id.artifact_id)

    deployed_files = [
        deploy_artifact(path=path, glob_patterns=[os.path.join('dist', '*')])]

    deploy_build_info(build_info=build_info)

    return deployed_files


def _execute_py_run(script):
    # Clean!
    _standard_clean()

    # Create the version.txt file.
    version = VersionUtils().write_version()

    # To "build" the script, simply copy it into the 'dist' directory
    # and tag it with the version.
    destination = _built_script_destination(script, version)
    ensure_path_exists(os.path.dirname(destination))
    shutil.copy2(script, destination)


def _execute_develop_run():
    # Clean!
    _standard_clean()

    # Create the version.txt file.
    VersionUtils().write_version()

    # Run unit tests.
    run_nosetests()

    # Install a link from site-packages back to this package.
    install_dev()


def _standard_clean():
    rm(MODULE_INFO_DIR, 'dist', '*.egg-info', '*.egg', 'version.txt')


def _built_script_destination(script, version):
    base, ext = split_ext(script)
    build_filename = '{base}-{version}.{ext}'.format(
        base=base,
        version=version,
        ext=ext)
    return os.path.join('dist', build_filename)
