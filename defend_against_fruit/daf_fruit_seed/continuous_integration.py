import os
import sys


def integrate():
    # From the newly-included 'daf_fruit_dist' module, import the standard CI run for a raw Python script.
    from daf_fruit_dist.ci_single_module_utils import standard_py_run

    # Execute the CI run against the bootstrap script.
    standard_py_run('virtualenv_util_bootstrap.py')


if __name__ == '__main__':
    # Change active directories to the one containing this file.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Include the co-bundled 'daf_fruit_dist' module in the search path.
    sys.path.insert(0, os.path.abspath(os.path.join('..', 'daf_fruit_dist')))

    integrate()