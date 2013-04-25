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
    name='fruit_dist',
    version=open('version.txt').read().strip(),
    url='https://github.com/teamfruit/fruit_dist',
    author='Team Fruit',
    author_email='defend.against.fruit@gmail.com',
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    license='Apache License 2.0',
    long_description=open('README.rst').read(),
    test_suite='nose.collector',
    entry_points={
        "distutils.commands": [
            "artifactory_upload = fruit_dist.commands.artifactory_upload:artifactory_upload",
            "freeze = fruit_dist.commands.freeze:freeze",
            "module_generator = fruit_dist.commands.module_generator_command:ModuleGeneratorCommand",
            ]},
    setup_requires=['nose>=1.2.1'],
    install_requires=['requests>=1.1.0', 'pkginfo>=1.0b2'],
    tests_require=['mock>=1.0.1'],
)