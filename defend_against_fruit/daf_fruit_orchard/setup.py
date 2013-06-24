from setuptools import setup, find_packages

# Work-around for a bug: http://bugs.python.org/msg170215
try:
    import multiprocessing
except ImportError:
    pass

setup(
    #name attribute is now being used by setuptools_webdav
    name='daf_fruit_orchard',
    version=open('version.txt').read(),
    url='http://teamfruit.github.io/defend_against_fruit/',
    author='Team Fruit',
    author_email='defend.against.fruit@gmail.com',
    packages=find_packages(exclude=['*.tests', '*.tests.*']),
    license='Apache License 2.0',
    description='virtualenv bootstrap utility for Defend Against Fruit',
    long_description=open(name='README.txt').read(),
    test_suite='nose.collector',
    keywords="pypi artifactory bootstrap continuous integration deployment "
             "ci cd",
    setup_requires=['nose>=1.2.1'],
)
