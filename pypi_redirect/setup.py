from setuptools import setup, find_packages

# Work-around for a bug: http://bugs.python.org/msg170215
try:
    import multiprocessing
except ImportError:
    pass

setup(
    name='pypi_redirect',
    version=open('version.txt').read().strip(),
    url='https://github.com/teamfruit/fruit_dist',
    author='Team Fruit',
    author_email='defend.against.fruit@gmail.com',
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    license="Apache License 2.0",
    long_description=open('README.txt').read(),
    test_suite='nose.collector',
    install_requires=['lxml', 'requests', 'cherrypy>=3.1'],
    tests_require=['lxml', 'nose>=1.2.1'],
)
