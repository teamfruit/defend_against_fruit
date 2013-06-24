from setuptools import setup, find_packages

# Work-around for a bug: http://bugs.python.org/msg170215
try:
    import multiprocessing
except ImportError:
    pass

setup(
    #name attribute is now being used by setuptools_webdav
    name='daf_fruit_dist',
    version=open('version.txt').read().strip(),
    url='http://teamfruit.github.io/defend_against_fruit/',
    author='Team Fruit',
    author_email='defend.against.fruit@gmail.com',
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    license='Apache License 2.0',
    description='Provides various utilities for setup utils and continuous '
                'integration',
    long_description=open('README.rst').read(),
    test_suite='nose.collector',
    keywords="pypi artifactory continuous integration deployment ci cd",
    entry_points={
        "distutils.commands": [
            "artifactory_upload = daf_fruit_dist.commands.artifactory_upload:"
            "artifactory_upload",
            "freeze = daf_fruit_dist.commands.freeze:freeze",
            "module_generator = daf_fruit_dist.commands.module_generator_command:"
            "ModuleGeneratorCommand",
            ]},
    setup_requires=['nose>=1.2.1'],
    install_requires=['requests>=1.1.0', 'pkginfo>=1.0b2'],
    tests_require=['mock>=1.0.1'],
)