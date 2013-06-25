import glob
import os
import subprocess
import sys


def build_sdist():
    subprocess.check_call([
        sys.executable,
        'setup.py',
        'sdist',
        '--formats=gztar',
        'freeze',
        'module_generator'])


def build_and_deploy_sdist():
    subprocess.check_call([
        sys.executable,
        'setup.py',
        'sdist',
        '--formats=gztar',
        'freeze',
        'module_generator',
        'artifactory_upload'])


def install_dev():
    subprocess.check_call([
        sys.executable, 'setup.py', 'sdist', '--formats=gztar'])
    sdist = glob.glob(os.path.join('dist', '*.tar.gz'))[0]
    subprocess.check_call(['pip', 'install', sdist])


def run_nosetests():
    subprocess.check_call([sys.executable, 'setup.py', 'nosetests'])


def run_ci_script():
    subprocess.check_call([sys.executable, 'continuous_integration.py'])