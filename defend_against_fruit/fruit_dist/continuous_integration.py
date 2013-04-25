import os


def integrate():
    # Test this package, then install the development version of it.
    from fruit_dist.ci_single_module_utils import standard_develop_run

    standard_develop_run()

    # Also build an sdist to be uploaded later.
    from fruit_dist.exec_utils import build_sdist

    build_sdist()


if __name__ == '__main__':
    # Change active directories to the one containing this file.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    integrate()