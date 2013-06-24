import os


def integrate():
    # From the newly-included 'daf_fruit_dist' module, import the standard CI run.
    from fruit_dist.ci_utils import standard_sdist_run

    # Test this package, then create a source distribution of it.
    standard_sdist_run()


if __name__ == '__main__':
    # Change active directories to the one containing this file.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    integrate()