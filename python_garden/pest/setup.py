from setuptools import setup, find_packages

# import sys
# sys.path.append(r'C:\path\to\pydev\egg')
# import pydevd
# pydevd.settrace('localhost', port=5555, stdoutToServer=True, stderrToServer=True)

# Work-around for a bug: http://bugs.python.org/msg170215
try:
    import multiprocessing
except ImportError:
    pass

setup(
    #name attribute is now being used by setuptools_webdav
    name='pest',
    version=open('version.txt').read().strip(),
    url='https://github.com/teamfruit/fruit_dist',
    author='Team Fruit',
    author_email='defend.against.fruit@gmail.com',
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    license="Apache License 2.0",
    long_description=open('README.txt').read(),
    test_suite='nose.collector',
    setup_requires=['nose>=1.2.1'],
)
