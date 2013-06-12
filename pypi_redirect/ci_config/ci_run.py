import logging
import os
import subprocess
from fruit_dist.ci_utils import standard_sdist_run
from fruit_dist.exec_utils import install_dev


def run_integration_tests():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.abspath(os.path.join(
        this_dir, '..', 'pypi_redirect_integration', 'tests'))
    os.chdir(test_dir)
    subprocess.check_call(['nosetests'])


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')

    standard_sdist_run()
    install_dev()
    run_integration_tests()