import logging
import os
import subprocess
from daf_fruit_dist.ci_utils import standard_sdist_run
from daf_fruit_dist.exec_utils import install_dev


def _path_from_here(*path):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    rel_path = os.path.join(this_dir, *path)
    abs_path = os.path.abspath(rel_path)
    return abs_path


def _cwd_as(path):
    class Context(object):
        def __enter__(self):
            self.old_cwd = os.getcwd()
            os.chdir(path)

        def __exit__(self, exc_type, exc_val, exc_tb):
            os.chdir(self.old_cwd)

    return Context()


def _run_integration_tests():
    install_dev()

    test_dir = _path_from_here('..', 'pypi_redirect_integration', 'tests')

    with _cwd_as(test_dir):
        subprocess.check_call(['nosetests'])


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')

    standard_sdist_run(integration_tests_fn=_run_integration_tests)
