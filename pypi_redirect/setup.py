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
    install_requires=['lxml', 'requests', 'CherryPy>=3.1'],
    tests_require=['lxml', 'nose>=1.2.1'],
    data_files=[
        ('pypi_redirect/config',
         ['server_config/pypi_redirect.conf.template'])],
    entry_points={
        'console_scripts': [
            'pypi_redirect_service '
            '= pypi_redirect.daemon.pypi_windows_service:main']}
)
