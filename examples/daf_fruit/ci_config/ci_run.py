import logging
from daf_fruit_dist.ci_utils import standard_sdist_run

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')

    standard_sdist_run(submodule_order=('daf_apple', 'daf_citrus'))