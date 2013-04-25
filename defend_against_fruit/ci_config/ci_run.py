import logging
import os
import sys


def integrate():
    standard_sdist_run(submodule_order=('fruit_dist', 'fruit_seed', 'fruit_orchard'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    sys.path.insert(0, os.path.abspath('fruit_dist'))
    from fruit_dist.ci_utils import standard_sdist_run

    integrate()
