import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from textwrap import dedent

if sys.version_info >= (3, 0):
    # noinspection PyUnresolvedReferences
    import configparser
    # noinspection PyUnresolvedReferences
    import urllib.request as urllib
else:
    # noinspection PyUnresolvedReferences
    import ConfigParser as configparser
    # noinspection PyUnresolvedReferences
    import urllib2 as urllib


def version():
    return '9.9.9'


def get_python_version_string():
    return '{:d}.{:d}.{:d}'.format(sys.version_info[0], sys.version_info[1], sys.version_info[2])


def get_options_from_config_file_and_args(config_file_path=None):
    if config_file_path is not None:
        config = configparser.SafeConfigParser()
        config.read([config_file_path])
        config_file_global_settings = dict(config.items("global"))
    else:
        config_file_global_settings = {}

    parser = argparse.ArgumentParser(description='Setup and update a Python virtualenv for a firmware view')
    parser.add_argument('--clean', '--veclean', action='store_true')
    parser.add_argument('--run', default=None)
    parser.add_argument('--script', default=None)
    parser.add_argument('--requirements_file', '-r', default=None)
    parser.add_argument('--installed_list_file', default=None)
    parser.add_argument('--environment_variables', default={})
    parser.add_argument('--pypi_server', default='http://pypi.python.org/simple')
    parser.add_argument('--pypi_push_server', default=None)
    parser.add_argument('--pypi_push_credentials', default=None)
    parser.add_argument('--virtualenv_path', default='./_python_virtualenv')
    parser.add_argument('--virtualenv_version', default=None)
    parser.add_argument('--python_version', default=get_python_version_string())

    parser.set_defaults(**config_file_global_settings)
    options = parser.parse_args()
    options.cfg_file = config_file_path

    if options.requirements_file is None:
        options.requirements_file = config_file_global_settings.get('', None)

    update_path_options(options)

    return options


def update_path_options(options):
    path_options = ['virtualenv_path', 'requirements_file', 'installed_list_file']

    # If a config file is specified, paths should be relative to that. Otherwise, paths should be relative to this file.
    root_path = os.path.dirname(os.path.abspath(options.cfg_file) if options.cfg_file else os.path.abspath(__file__))

    for path_option in path_options:
        if getattr(options, path_option, None) is not None:
            value = getattr(options, path_option)

            if value.startswith('.'):
                # relative path
                setattr(options, path_option, os.path.abspath(os.path.join(root_path, value)))
            else:
                # absolute path
                setattr(options, path_option, os.path.abspath(value))


def parse_requirements_file(requirements_file_path, options):
    if not os.path.isfile(requirements_file_path):
        raise RuntimeError('Requirements file {} is missing!'.format(requirements_file_path))

    python_version = None
    virtualenv_package_name = None
    virtualenv_version = None

    for line in file(requirements_file_path).readlines():
        if line.startswith('#python'):
            python_version = line.split('==')[1].strip()
        elif line.startswith('virtualenv'):
            virtualenv_package_name, virtualenv_version = line.split('==')
            virtualenv_package_name = virtualenv_package_name.strip()
            virtualenv_version = virtualenv_version.strip()

    if python_version is None:
        raise RuntimeError(
            'Requirements file {} does not list required python version!'.format(requirements_file_path))

    if virtualenv_package_name is None or virtualenv_version is None:
        raise RuntimeError(
            'Requirements file {} does not list required virtualenv package!'.format(requirements_file_path))

    return python_version, virtualenv_package_name, virtualenv_version


def handle_remove_readonly(func, path, exc):
    if func in (os.rmdir, os.remove):
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def create_virtualenv(
        virtualenv_path=None,
        virtualenv_version=None,
        pypi_server=None,
        virtualenv_package_name='virtualenv'):
    print('Creating new virtual environment at {}...'.format(virtualenv_path))

    # Remove any old virtualenv that may be sitting in the target virtualenv 
    # directory.
    if os.path.isdir(virtualenv_path):
        shutil.rmtree(virtualenv_path, ignore_errors=False, onerror=handle_remove_readonly)

    # Create a temporary directory.
    temp_dir = tempfile.mkdtemp()

    try:
        # Was a fixed virtualenv_util version specified?  If not, we need to check
        # the PyPI server for the latest version.    
        if virtualenv_version is None:
            virtualenv_url_dir = pypi_server + '/' + virtualenv_package_name

            f_remote = urllib.urlopen(virtualenv_url_dir)
            index = f_remote.read()

            # Very simple regex parser that finds all hyperlinks in the index
            # HTML... this may break in some cases, but we want to keep it super 
            # simple in the bootstrap.               
            hyperlinks = re.findall('href="(.*?)"', str(index.lower()))

            # Get all hyperlinks that start with the virtualenv package name
            # and end with the package extension.
            versions = []
            for hyperlink in hyperlinks:
                if hyperlink.startswith(virtualenv_package_name + '-') and hyperlink.endswith('.tar.gz'):
                    version = hyperlink.split('-')[-1].replace('.tar.gz', '')
                    versions.append(version)

                    # Sort the versions from lowest to highest.
                    # NOTE: This simple sort will work for most versions we expect to
                    # encounter.  This could be enhanced.
            versions.sort()

            # Select the highest version.        
            virtualenv_version = versions[-1]

            # Attempt to locate and download a virtualenv package of the version
            # specified on the artifact server.
        virtualenv_tar_filename = '{}-{}.tar.gz'.format(virtualenv_package_name, virtualenv_version)
        virtualenv_url = '/'.join([pypi_server, virtualenv_package_name, virtualenv_tar_filename])

        f_remote = urllib.urlopen(virtualenv_url)
        f_local = open(os.path.join(temp_dir, virtualenv_tar_filename), 'wb')
        f_local.write(f_remote.read())
        f_local.close()

        # Unpack the tarball to the temporary directory.
        tarf = tarfile.open(os.path.join(temp_dir, virtualenv_tar_filename), 'r:gz')
        tarf.extractall(temp_dir)
        tarf.close()
        unpacked_tar_directory = os.path.join(temp_dir, virtualenv_tar_filename.replace('.tar.gz', ''))

        # Create the bootstrap virtualenv in the temporary directory using the 
        # current python executable we are using plus the virtualenv stuff we 
        # unpacked.
        bootstrap_vm_directory = os.path.join(temp_dir, 'virtualenv-bootstrap')
        os.system(
            '"{}" {} --distribute {}'.format(
                sys.executable, os.path.join(unpacked_tar_directory, 'virtualenv.py'), bootstrap_vm_directory))

        # Install virtualenv into this bootstrap environment using pip, pointing
        # at the right server.
        os.system('"{}" install {}=={} -i {}'.format(
            os.path.join(bootstrap_vm_directory, 'Scripts', 'pip'),
            virtualenv_package_name,
            virtualenv_version,
            pypi_server))

        # Use the bootstrap virtualenv to create the "real" virtualenv in the
        # view at the right location. 
        # We have to be careful to get the python version correct this time.    
        os.system('"{}" --distribute {}'.format(
            os.path.join(bootstrap_vm_directory, 'Scripts', 'virtualenv'),
            virtualenv_path))
    finally:
        # Always clean up our temporary directory litter.
        shutil.rmtree(temp_dir, ignore_errors=False, onerror=handle_remove_readonly)

    # Return the virtualenv path and virtualenv version used.
    return (virtualenv_path, virtualenv_version)


def _write_config_files(home_dir, options, virtualenv_util_cfg):
    """Write config files used by PIP and distutils"""

    virtualenv_util = os.path.basename(__file__)

    ################################
    #Create pip.ini
    pip_ini = dedent('''
        # This file was auto-generated by "{virtualenv_util}" from "{virtualenv_util_cfg}".

        [global]
        index-url={index_url}

        [install]
        use-wheel=true
        ''').strip()

    pip_ini_contents = pip_ini.format(
        virtualenv_util=virtualenv_util,
        virtualenv_util_cfg=virtualenv_util_cfg,
        index_url=options.pypi_pull_server)

    _write_config_file(home_dir=home_dir, home_file_name='pip\pip.ini', contents=pip_ini_contents)

    ################################
    #Create pydistutils.cfg
    pydistutils_cfg = dedent('''
        # This file was auto-generated by "{virtualenv_util}" from "{virtualenv_util_cfg}".

        [easy_install]
        index_url={index_url}

        [artifactory]
        # Used for Artifactory API calls.
        repo_base_url={repo_base_url}
        repo_push_id={repo_push_id}
        repo_pull_id={repo_pull_id}
        username={username}
        password={password}
        ''').strip()

    pydistutils_cfg_contents = pydistutils_cfg.format(
        virtualenv_util=virtualenv_util,
        virtualenv_util_cfg=virtualenv_util_cfg,
        index_url=options.pypi_pull_server,
        repo_base_url=options.pypi_server_base,
        repo_push_id=options.pypi_push_repo_id,
        repo_pull_id=options.pypi_pull_repo_id,
        username=options.pypi_push_username,
        password=options.pypi_push_password)

    _write_config_file(home_dir=home_dir, home_file_name='pydistutils.cfg', contents=pydistutils_cfg_contents)


def _write_version_file(home_dir, virtual_env_version):
    """Write out some package version information to a text file in the home directory."""

    home_versions_file_path = os.path.join(home_dir, 'virtualenv_versions.txt')
    with open(home_versions_file_path, 'w') as f:
        f.write('# __python=={}\n'.format(get_python_version_string()))
        f.write('# __virtualenv=={}\n'.format(virtual_env_version))
        f.write('# __virtualenv_util=={}\n'.format(version()))


def _create_env_file(home_dir, environment_variables):
    """Create a file containing all the environment variable settings that
    should be made each time the virtual environment is used"""

    environment_variables['HOME'] = home_dir

    home_env_file_path = os.path.join(home_dir, '.env')
    if not os.path.isfile(home_env_file_path):
        with open(home_env_file_path, 'w') as f:
            f.write('[environment_variables]\n')
            for name in environment_variables.keys():
                f.write('{}={}\n'.format(name, environment_variables[name]))


def _populate_home_dir(virtualenv_path, options, config_file_path):
    home_dir = os.path.join(virtualenv_path, 'home')
    options.environment_variables['HOME'] = home_dir

    if not os.path.isdir(home_dir):
        os.mkdir(home_dir)

    _write_config_files(home_dir, options, config_file_path)

    _create_env_file(home_dir=home_dir, environment_variables=options.environment_variables)

    _write_version_file(home_dir=home_dir, virtual_env_version=options.virtualenv_version)


def _write_config_file(home_dir, home_file_name, contents):
    home_file_path = os.path.join(home_dir, home_file_name)

    if not os.path.isdir(os.path.dirname(home_file_path)):
        os.makedirs(os.path.dirname(home_file_path))

    if not os.path.isfile(home_file_path):
        with open(home_file_path, 'w') as f:
            f.write(contents)


def read_and_update_environment_variables(virtualenv_path):
    home_dir = os.path.join(virtualenv_path, 'home')
    home_env_file_path = os.path.join(home_dir, '.env')

    if not os.path.isfile(home_env_file_path):
        environment_variables = {}
    else:
        config = configparser.SafeConfigParser()
        config.read([home_env_file_path])
        environment_variables = dict(config.items("environment_variables"))

    for name in environment_variables.keys():
        os.environ[name.upper()] = environment_variables[name]


def main(config_file_path=None):
    options = get_options_from_config_file_and_args(config_file_path)

    # Special case of "nested" arguments when doing a run or script.
    # Can pass in '--veclean' as an argument inside of --run or --script,
    # which will cause the virtual environment to be cleaned (the same as
    # when passing --clean directly into the script).
    if options.run is not None and '--veclean' in options.run.split():
        options.clean = True
        options.run = options.run.replace('--veclean', '')

    # If we are running from INSIDE a virtualenv already, assume that the 
    # virtualenv already exists and we only need to update it.
    if hasattr(sys, 'real_prefix'):
        # Check that the version of Python in the virtualenv being used is
        # correct.  We cannot update this, so error if it is incorrect.
        pass
    else:
        # Does the virtualenv already exist?  If so, we just check to make 
        # sure it is up to date.
        if os.path.isfile(os.path.join(options.virtualenv_path, 'Scripts', 'python.exe')) and not options.clean:
        # Check the version of Python in the virtualenv.  We cannot
            # update it after the virtualenv is created (we have to destroy and
            # recreate this virtualenv), so just show an error.
            pass
        else:
            options.virtualenv_path, options.virtualenv_version = create_virtualenv(
                options.virtualenv_path,
                options.virtualenv_version,
                options.pypi_pull_server)

            _populate_home_dir(options.virtualenv_path, options, config_file_path)

        read_and_update_environment_variables(options.virtualenv_path)

        # Run PIP in the virtual environment to install / update the required
        # tool packages listed in the requirements.txt file.
        if options.requirements_file:
            p = subprocess.Popen(
                '"{}" install -r {} --upgrade'.format(os.path.join(options.virtualenv_path, 'Scripts', 'pip'),
                                                      options.requirements_file))
            p.wait()

            # Append the Python version used to the list of installed tools.
        if options.installed_list_file:
            home_dir = os.path.join(options.virtualenv_path, 'home')
            home_versions_file_path = os.path.join(home_dir, 'virtualenv_versions.txt')

            f = open(options.installed_list_file, 'w')

            if os.path.isfile(home_versions_file_path):
                f.write(open(home_versions_file_path, 'r').read())
            else:
                f.write('# __python=={}\n'.format(get_python_version_string()))

            f.close()

            # Output the list of installed tools to a text file. 
            os.system(
                '{} freeze >> {}'.format(os.path.join(options.virtualenv_path, 'Scripts', 'pip'),
                                         options.installed_list_file))

    if options.run is not None:
        # Run the file using the Python executable in the virtualenv.
        p = subprocess.Popen(os.path.join(options.virtualenv_path, 'Scripts', 'python.exe') + ' ' + options.run)
        sys.exit(p.wait())
    elif options.script is not None:
        # Run a script, assumed to be located in the Scripts directory.                   
        # of the virtualenv.  Note that the script name cannot have any spaces
        # using the logic below.             
        p = subprocess.Popen(os.path.join(options.virtualenv_path, 'Scripts', options.script.split()[0]))
        sys.exit(p.wait())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup and update a Python virtualenv for a firmware view')
    parser.add_argument('--cfg_file')
    parsed, remaining_args = parser.parse_known_args(sys.argv[1:])
    sys.argv = [sys.argv[0]] + remaining_args

    main(parsed.cfg_file)