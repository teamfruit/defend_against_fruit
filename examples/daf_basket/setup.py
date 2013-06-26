from setuptools import setup, find_packages

# Work-around for a bug: http://bugs.python.org/msg170215
try:
    import multiprocessing  # flake8: noqa
except ImportError:
    pass

setup(
    #name attribute is now being used by setuptools_webdav
    name='daf_basket',
    version=open('version.txt').read().strip(),
    url='http://teamfruit.github.io/defend_against_fruit/',
    author='Team Fruit',
    author_email='defend.against.fruit@gmail.com',
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    license="Apache License 2.0",
    description='Single-module continuous deployment example using '
                'Defend Against Fruit',
    long_description=open('README.txt').read(),
    test_suite='nose.collector',
    keywords="pypi artifactory continuous integration deployment ci cd",
    install_requires=['daf_apple>=1.1.20', 'daf_citrus>=1.1.20'],
    setup_requires=['nose>=1.2.1'],
)
