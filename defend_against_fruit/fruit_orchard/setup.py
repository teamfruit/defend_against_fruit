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
    name='fruit_orchard',
    version=open('version.txt').read(),
    url='https://github.com/teamfruit/fruit_dist',
    author='Team Fruit',
    author_email='defend.against.fruit@gmail.com',
    packages=find_packages(exclude=['*.tests', '*.tests.*']),
    license='Apache License 2.0',
    long_description=open(name='README.txt').read(),
    test_suite='nose.collector',
    setup_requires=['nose>=1.2.1'],
    entry_points={
        'console_scripts': [
            'virtualenv_util_make_platform_helpers=fruit_orchard.virtualenv_util:make_platform_helpers',
        ],
    },    
)
