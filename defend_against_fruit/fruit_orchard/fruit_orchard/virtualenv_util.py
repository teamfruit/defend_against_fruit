import argparse
import glob
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from textwrap import dedent

VIRTUALENV_PACKAGE_NAME = 'virtualenv'
VIRTUALENV_BOOTSTRAP_NAME = 'virtualenv-bootstrap'
VIRTUALENV_UTIL_PACKAGE_NAME = 'fruit_orchard'

if sys.version_info >= (3, 0):
    # noinspection PyUnresolvedReferences
    import configparser
    # noinspection PyUnresolvedReferences
    import urllib.request as urllib
    # noinspection PyUnresolvedReferences   
    import urllib.parse as urlparse
else:
    # noinspection PyUnresolvedReferences
    import ConfigParser as configparser
    # noinspection PyUnresolvedReferences
    import urllib2 as urllib
    # noinspection PyUnresolvedReferences   
    import urlparse


def version():
    return open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'version.txt'), 'r').read()


def get_python_version_string():
    return '{:d}.{:d}.{:d}'.format(sys.version_info[0], sys.version_info[1], sys.version_info[2])


def get_options_from_config_file_and_args(config_file_path=None,options_overrides={}):

    if config_file_path is None and options_overrides.get('cfg_file', None):
        config_file_path = options_overrides['cfg_file'] 

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
    parser.add_argument('--noupdate', '--venoupdate', '-`', action='store_true')
    parser.add_argument('--requirements_file', '-r', default=None)
    parser.add_argument('--requirement_specifiers', default=None)
    parser.add_argument('--installed_list_file', default=None)
    parser.add_argument('--environment_variables', default={})
    parser.add_argument('--pypi_pull_server', default='http://pypi.python.org/simple')
    parser.add_argument('--pypi_pull_repo_id', default=None)
    parser.add_argument('--pypi_push_server', default=None)
    parser.add_argument('--pypi_push_username', default=None)
    parser.add_argument('--pypi_push_password', default=None)
    parser.add_argument('--pypi_push_repo_id', default=None)
    parser.add_argument('--pypi_push_no_cert_verify', default=False)
    parser.add_argument('--pypi_server_base', default=None)
    parser.add_argument('--virtualenv_path', default='./_python_virtualenv')
    parser.add_argument('--virtualenv_version', default=None)
    parser.add_argument('--python_version', default=get_python_version_string())
    parser.add_argument('--pip_install_args', default='--upgrade')
    parser.add_argument('--download_dir', default=None)
    parser.add_argument('--download_cache_dir', default=None)
    # Force type=bool since the config file will be a string
    parser.add_argument('--sitepkg_install', type=int, default=0)
    parser.add_argument('--helper_scripts', action='store_true', default=False)
    
    parser.set_defaults(**config_file_global_settings)
    
    if options_overrides.get('dont_parse_argv', False):
        # Don't actually parse anything from the command line if this
        # option override is set.
        options = parser.parse_args([])
    else:
        options = parser.parse_args()
    
    options.cfg_file = config_file_path

    if options.requirements_file is None:
        options.requirements_file = config_file_global_settings.get('', None)

    for key in options_overrides:
        setattr(options, key, options_overrides[key]) 

    update_path_options(options)

    return options


def update_path_options(options):
    path_options = ['virtualenv_path', 'requirements_file', 'installed_list_file']

    # If a config file is specified, paths should be relative to that. Otherwise, paths should be relative to this file.
    root_path = os.path.dirname(os.path.abspath(options.cfg_file)) if options.cfg_file else os.path.dirname(os.path.abspath(__file__))

    for path_option in path_options:
        if getattr(options, path_option, None) is not None:
            value = getattr(options, path_option)

            if value.startswith('.'):
                # relative path
                setattr(options, path_option, os.path.abspath(os.path.join(root_path, value)))
            else:
                # absolute path
                setattr(options, path_option, os.path.abspath(value))

# TODO: Is this function ever called?
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

def _install_req(tarball):
    '''Used to install distribute or pip to site-packages from the given 
    source dist tarball.
    '''
    cwd = os.getcwd()
    # Copy to a temp directory 
    d = tempfile.mkdtemp()
    t = None
    try:
        # Unpack to the temp dir
        t = tarfile.open(tarball,'r:gz')
        t.extractall(d)
        # Change to extracted directory, and install (expect only 1 directory)
        extract_dir = os.listdir(d)[0]
        unpack_dir = os.path.join(d,extract_dir)
        os.chdir(unpack_dir)
        # Make sure setup.py exists
        if not os.path.isfile('setup.py'):
            raise RuntimeError('Could not find setup.py for {}'.format(tarball))
        # Finally, run the installer
        print 'Running setup.py for {}'.format(tarball)
        with open(os.devnull, 'w') as tempf:
            subprocess.check_call([sys.executable,'setup.py','install'],
                stdout=tempf)
    finally:
        if t: 
            t.close()
        os.chdir(cwd)
        shutil.rmtree(d)

def do_sitepkg_install(options):
    '''Install user specifications to local site-packages.
    '''
    # Set this to None in case it fails to get set in the try block
    temp_dir = None
    try:
        # Get the virtualenv package which has distribute and pip that we 
        # will install to site-packages
        temp_dir = _stage_virtualenv(options, install_virtualenv=False)
        
        # Use the bootstrap virtualenv to install distribute and pip to 
        # site-packages. We expect those packages to be in virtualenv_support.
        tool_path = os.path.join(temp_dir, 'virtualenv_support')
        distribute_src = glob.glob(os.path.join(
            temp_dir,'virtualenv-*/virtualenv_support/distribute-*.tar.gz'))
        pip_src = glob.glob(os.path.join(
            temp_dir,'virtualenv-*/virtualenv_support/pip-*.tar.gz'))
        # Expect only one to be there
        if len(distribute_src) != 1 or len(pip_src) != 1:
            raise RuntimeError('Expect exactly one version of distribute and '
                'pip in virtualenv_support. Found {}, {}'.format(
                    distribute_src, pip_src))
        # Install them both to site-packages
        _install_req(distribute_src[0])
        _install_req(pip_src[0])
    finally:
        if temp_dir:
            # Clean up the temp. virtual environment. 
            pass #_cleanup_virtualenv(temp_dir)
    

def do_virtualenv_install(options):
    print('Creating new virtual environment at {}...'.format(options.virtualenv_path))
    
    # Remove any old virtualenv that may be sitting in the target virtualenv 
    # directory.
    if os.path.isdir(options.virtualenv_path):
        shutil.rmtree(options.virtualenv_path, ignore_errors=False, onerror=handle_remove_readonly)
    
    # Set this to None in case it fails to get set in the try block
    temp_dir = None
    try:
        # Stage a virtual environment that will perform the real install
        temp_dir = _stage_virtualenv(options)
        bootstrap_vm_dir = os.path.join(temp_dir, VIRTUALENV_BOOTSTRAP_NAME)
        
        # Use the bootstrap virtualenv to create the "real" virtualenv in the
        # view at the right location. 
        # We have to be careful to get the python version correct this time.  
        try:
            subprocess.check_call([
            os.path.join(bootstrap_vm_dir, 'Scripts', 'virtualenv'),
            '--distribute', options.virtualenv_path], shell=True)
        except subprocess.CalledProcessError, e:
            print 'Real VM create return code', e.returncode
            #print e.output                   
            raise  
        #print output           
        #subprocess.check_call([
        #    os.path.join(bootstrap_vm_dir, 'Scripts', 'virtualenv'),
        #    '--distribute', options.virtualenv_path])
    finally:
        if temp_dir:
            # Clean up the temp. virtual environment. 
            _cleanup_virtualenv(temp_dir)
            
def _get_newest_package_version_and_url(pypi_server, package_name, package_extension = '.tar.gz'):    
    '''Utility function that searches the pypi_server specified for
    the latest version of the package with the name specified.
    Will return the version of the newest package found and the
    url to the package file on the server.
    '''

    # If we are getting our packages from the local filesystem, we
    # need to get the directory listing specially.
    if urlparse.urlparse(pypi_server).scheme == 'file':
        filenames = os.listdir(urlparse.urlparse(pypi_server).path.lstrip('/'))
        url_dir = pypi_server
    else:
        url_dir = pypi_server + '/' + package_name
        
        try:
            f_remote = urllib.urlopen(url_dir)
            index = f_remote.read()

        # If we get a URL error, try the special case of a "flat" directory structure.
        except urllib.URLError:    
            url_dir = pypi_server

            f_remote = urllib.urlopen(url_dir)
            index = f_remote.read()

        # Very simple regex parser that finds all hyperlinks in the index
        # HTML... this may break in some cases, but we want to keep it super 
        # simple in the bootstrap.               
        filenames = re.findall('href="(.*?)"', str(index.lower()))    

    # Get all hyperlinks that start with the virtualenv package name
    # and end with the package extension.
    versions = []
    for filename in filenames:
        if filename.startswith(package_name+'-') and filename.endswith(package_extension):
            version = filename.split('-')[-1].replace(package_extension, '')
            versions.append(version)

    # Sort the versions from lowest to highest.
    # NOTE: This simple sort will work for most versions we expect to
    # use in the virtualenv_util package.  This could be enhanced.  
    versions.sort()

    # Select the highest version.        
    # Select the highest version.  
    try:      
        highest_version = versions[-1]
    except IndexError:
        raise RuntimeError('Unable to find any version of package {} at URL {}'.format(package_name, pypi_server))    
        
    return highest_version, '/'.join([url_dir,
                                      '{}-{}{}'.format(package_name, highest_version, package_extension)])    

def _stage_virtualenv(options, install_virtualenv=True):
    '''Creates staging virtual environment in order to help with the "real"
    installation. Returns path to staged virtual env. If install_virtualenv is
    False, then unpack the virtual env. package, but don't actually create 
    a virtual environment.
    '''
    # Create a temporary directory to put the virtual env. in.
    temp_dir = tempfile.mkdtemp()
    try:
        # Was a fixed virtualenv version specified?  If not, we need to check
        # the PyPI server for the latest version.    
        if options.virtualenv_version is None:
            options.virtualenv_version, virtualenv_url = _get_newest_package_version_and_url(options.pypi_pull_server,
                                                                                             options.virtualenv_package_name)
        else:
            virtualenv_url = '/'.join([options.pypi_pull_server, 
                                       options.virtualenv_package_name, 
                                       '{}-{}.tar.gz'.format(options.virtualenv_package_name, options.virtualenv_version)])                                                                                  

        virtualenv_tar_filename = os.path.basename(urlparse.urlparse(virtualenv_url).path)

        f_remote = urllib.urlopen(virtualenv_url)
        f_local = open(os.path.join(temp_dir, virtualenv_tar_filename), 'wb')
        f_local.write(f_remote.read())
        f_local.close()
        
        # If a download dir or download cache directory was specified, 
        # copy the virtualenv package file to that directory if it is not
        # already there. 
        for dir in [options.download_dir, options.download_cache_dir]:
            if dir and not os.path.isfile(os.path.join(dir, virtualenv_tar_filename)):
                shutil.copy2(os.path.join(temp_dir, virtualenv_tar_filename), dir)
        
        # Unpack the tarball to the temporary directory.
        tarf = tarfile.open(os.path.join(temp_dir, virtualenv_tar_filename), 'r:gz')
        tarf.extractall(temp_dir)
        tarf.close()
        unpacked_tar_directory = os.path.join(temp_dir, virtualenv_tar_filename.replace('.tar.gz', ''))
        bootstrap_vm_directory = os.path.join(temp_dir, VIRTUALENV_BOOTSTRAP_NAME)
        # Create the bootstrap virtualenv in the temporary directory using the 
        # current python executable we are using plus the virtualenv stuff we 
        # unpacked.
        if install_virtualenv:
            try:
                subprocess.check_call([
                    sys.executable, 
                    os.path.join(unpacked_tar_directory, 'virtualenv.py'), 
                    '--distribute', 
                    bootstrap_vm_directory], shell=True)
            except subprocess.CalledProcessError, e:
                print 'Bootstrap VM create return code', e.returncode
                #print e.output                   
                raise 
                
            #print output    
                
            # Get the right options to pass to pip to install virtualenv
            # to the bootstrap environment.  Again, this is necessary because
            # pip does not support file:// index urls.
            if urlparse.urlparse(options.pypi_pull_server).scheme == 'file':
                install_options = ['--no-index','--find-links', options.pypi_pull_server]
            else:
                install_options = ['-i', options.pypi_pull_server]                    

            # Install virtualenv into this bootstrap environment using pip, pointing
            # at the right server.
            subprocess.check_call([
                os.path.join(bootstrap_vm_directory, 'Scripts', 'pip'),
                'install'] 
                + install_options +
                ['{}=={}'.format(options.virtualenv_package_name, 
                                options.virtualenv_version)] )
        
    except Exception:
        # Even though the calling code is normally responsible for cleaning
        # up the temp dir, if an exception occurs, we do it here because we 
        # won't be able to return the temp_dir to the caller
        _cleanup_virtualenv(temp_dir)
        raise
    
    # Return the bootstrap vm dir that was created
    return temp_dir


def _cleanup_virtualenv(temp_dir):
    '''Cleans up the temp virtual folder and environment created by 
    _stage_virtualenv().
    '''
    print('Cleaning up bootstrap environment')
    #print '****', temp_dir
    shutil.rmtree(temp_dir, ignore_errors=False, onerror=handle_remove_readonly)
        

def _write_pip_config(home_dir, options):
    virtualenv_util = os.path.basename(__file__)
    additional_global_options = ''
    
    # Pip is not happy with an index-url that is on the local filesystem
    # (i.e. file://).  It would be cool if pip would be enhanced to handle
    # this someday, but for now, we need to pass these things to pip via
    # the find-links option.     
    if urlparse.urlparse(options.pypi_pull_server).scheme == 'file':
        additional_global_options = 'no_index=true\nfind_links={}'.format(options.pypi_pull_server)

    ################################
    #Create pip.ini
    pip_ini = dedent('''
        # This file was auto-generated by "{virtualenv_util}" from "{virtualenv_util_cfg}".

        [global]
        index-url={index_url}
        {additional_global_options}

        [install]
        use-wheel=true
        ''').strip()

    pip_ini_contents = pip_ini.format(
        virtualenv_util=virtualenv_util,
        virtualenv_util_cfg=options.cfg_file,
        index_url=options.pypi_pull_server,
        additional_global_options=additional_global_options)

    _write_config_file(home_dir=home_dir, home_file_name='pip\pip.ini', contents=pip_ini_contents)


def _write_pydistutils_cfg(home_dir, options):
    virtualenv_util = os.path.basename(__file__)
    
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
        no_cert_verify={no_cert_verify}
        
        [module_generator]
        no-cert-verify={no_cert_verify}        
        ''').strip()

    pydistutils_cfg_contents = pydistutils_cfg.format(
        virtualenv_util=virtualenv_util,
        virtualenv_util_cfg=options.cfg_file,
        index_url=options.pypi_pull_server,
        repo_base_url=options.pypi_server_base,
        repo_push_id=options.pypi_push_repo_id,
        repo_pull_id=options.pypi_pull_repo_id,
        username=options.pypi_push_username,
        password=options.pypi_push_password,
        no_cert_verify='1' if options.pypi_push_no_cert_verify else '0')

    _write_config_file(home_dir=home_dir, home_file_name='pydistutils.cfg', contents=pydistutils_cfg_contents)
    

def _get_implicit_versions_string(options):
    s = '# __python=={}\n'.format(get_python_version_string())
    s += '# __{}=={}\n'.format(options.virtualenv_package_name, options.virtualenv_version)
    s += '# __{}=={}\n'.format(VIRTUALENV_UTIL_PACKAGE_NAME, version())

    return s

def _write_version_file(home_dir, options):
    """Write out some package version information to a text file in the home directory."""

    home_versions_file_path = os.path.join(home_dir, 'virtualenv_versions.txt')
    f = open(home_versions_file_path, 'w')
    f.write(_get_implicit_versions_string(options))
    f.close()

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


def _populate_home_dir(options):
    if options.sitepkg_install:
        # For a sitepkg install, we need to write the config files in the 
        # the correct system locations.
        # TODO: We could write to the user's %HOME% env variable, but it's a pain 
        # to get it to persist. We've done this in ratools using the _winreg and
        # win32gui libraries, but win32gui is a third party module that I'm not
        # sure we want to try and install
        _write_pip_config(os.path.expanduser('~'), options)
        _write_pydistutils_cfg(os.path.join(sys.prefix,
            'Lib/distutils/pydistutils.cfg'), options)
    else:
        # For a virtual env. install, we can neatly create a home directory and
        # put the config files there.
        home_dir = os.path.join(options.virtualenv_path, 'home')
        options.environment_variables['HOME'] = home_dir
        if not os.path.isdir(home_dir):
            os.mkdir(home_dir)
        _write_pip_config(home_dir,options)
        _write_pydistutils_cfg(home_dir,options)
        _create_env_file(home_dir=home_dir, environment_variables=options.environment_variables)
        _write_version_file(home_dir=home_dir, options=options)


def _write_config_file(home_dir, home_file_name, contents):
    home_file_path = os.path.join(home_dir, home_file_name)

    if not os.path.isdir(os.path.dirname(home_file_path)):
        os.makedirs(os.path.dirname(home_file_path))

    # TODO: Don't we want to overwrite this file? For now, I changed it do 
    # overwrite. Not sure if/how we want to persist user changes, unless we 
    # just write parts of the file we're concerned about.
    #if not os.path.isfile(home_file_path):
    with open(home_file_path, 'w') as f:
        f.write(contents)
        
def _get_pip_install_args(options):
    args = options.pip_install_args        

    if options.download_cache_dir:
        args += ' --download-cache="{}"'.format(options.download_cache_dir)

    if options.download_dir:
        args += ' --download="{}"'.format(options.download_dir)
    
    return args
    
def _fix_download_cache_dir_filenames(options):
    for item in os.listdir(options.download_cache_dir):
        #print item
        if os.path.isfile(os.path.join(options.download_cache_dir, item)) and '%2F' in item:
            shutil.move(os.path.join(options.download_cache_dir, item),
                        os.path.join(options.download_cache_dir, item.split('%2F')[-1]))                                    


def _create_ve_helper_scripts(options):
    '''This function drops some files that are useful for dealing with
    the virtual environment that was created in the root directory of
    the ve.  The files are platform specific since they need to make
    changes to the environment, among other things.
        
    Think of this as a lite version of virtualenvwrapper, without having
    to have a special package installed in your global site-packages,
    and without the restrictions on where / how your virtualenvs can be
    stored.'''

    # If we installed to the global site-packages (i.e. we didn't make a
    # virtualenv) then there is nothing to do.
    if options.sitepkg_install:
        return
    
    if os.name == 'nt':
        # Batch file to activate the virtualenv.  This does a little extra
        # magic, like restoring our environment variables 
        f = open(os.path.join(options.virtualenv_path, 'activate.bat'), 'w')        
        f.write(dedent(r'''
                @echo off
                %~dp0\Scripts\virtualenv_util_make_platform_helpers
                call %~dp0\home\virtualenv_util_activate.bat
                %~dp0\Scripts\activate.bat
                '''))                
        f.close()                

        # Batch file to deactivate the virtualenv.
        f = open(os.path.join(options.virtualenv_path, 'deactivate.bat'), 'w')        
        f.write(dedent(r'''
                @echo off
                call %~dp0\home\virtualenv_util_deactivate.bat
                %~dp0\Scripts\deactivate.bat
                '''))                
        f.close()    

        # Batch file to open a command shell / prompt to the root of the
        # virtualenv, then activate it.  Good for messing around at the 
        # command line.
        f = open(os.path.join(options.virtualenv_path, 'shell.bat'), 'w')        
        f.write(dedent(r'''
                @echo off
                start cmd.exe /k "%~dp0\activate.bat"
                '''))                
        f.close()                
    else:
        print('Creating virtualenv helper scripts not supported for OS {}, skipping'.format(os.name))    

def read_and_update_environment_variables(options = None, home_dir = None):
    if home_dir is None and options:
        home_dir = os.path.join(options.virtualenv_path, 'home')
    
    home_env_file_path = os.path.join(home_dir, '.env')

    original_environment_variables = {}

    if not os.path.isfile(home_env_file_path):
        environment_variables = {}
    else:
        config = configparser.SafeConfigParser()
        config.read([home_env_file_path])
        environment_variables = dict(config.items("environment_variables"))

    for name in environment_variables.keys():
        if os.environ.has_key(name.upper()):
            original_environment_variables[name] = os.environ[name.upper()]
        else:
            original_environment_variables[name] = None            
        
        os.environ[name.upper()] = environment_variables[name]
        
    return environment_variables, original_environment_variables         

def make_platform_helpers():
    # Make sure we are running in a virtualenv...
    if not hasattr(sys, 'real_prefix'):
        return

    home_dir = os.path.join(sys.prefix, 'home')
    
    if not os.path.isdir(home_dir):
        return
    
    # Read the environment variables from the .env configuration file.
    new_env_vars, original_env_vars = read_and_update_environment_variables(home_dir=home_dir)        

    if os.name == 'nt':
        f = open(os.path.join(home_dir, 'virtualenv_util_activate.bat'), 'w')
        for new_env_var in new_env_vars.keys():
            f.write('set {}={}\n'.format(new_env_var.upper(), new_env_vars[new_env_var]))
        f.close()    
                
        f = open(os.path.join(home_dir, 'virtualenv_util_deactivate.bat'), 'w')
        for original_env_var in original_env_vars.keys():
            if original_env_vars[original_env_var] is None:
                f.write('set {}=\n'.format(original_env_var.upper()))            
            else:
                f.write('set {}={}\n'.format(original_env_var.upper(), original_env_vars[original_env_var]))
        f.close() 
        
def _handle_run_script_nested_arguments(options):           
    # Special case of "nested" arguments when doing a run or script.

    # Can pass in some arguments as an argument inside of --run or --script
    # and they will have the same effect as passing them directly to this
    # script.
    look_for_args = {'--veclean': 'clean', '--venoupdate': 'noupdate', '-`': 'noupdate'}    
    
    run_script_args = options.run if options.run is not None else options.script
    
    # No --run or --script was specified.
    if run_script_args is None:
        return

    for look_for_arg in look_for_args.keys():
        if look_for_arg in run_script_args.split():
            setattr(options, look_for_args[look_for_arg], True)        

        if options.run:
            options.run = options.run.replace(look_for_arg, '')

        if options.script:
            options.script = options.script.replace(look_for_arg, '')


def main(config_file_path=None, options_overrides={}):
    options = get_options_from_config_file_and_args(config_file_path, options_overrides)

    # Special case of "nested" arguments when doing a run or script.
    _handle_run_script_nested_arguments(options)

    # Set virtualenv package name to a default. Don't currently see a need
    # for this to be configurable
    options.virtualenv_package_name = VIRTUALENV_PACKAGE_NAME
    
    # If we are running from INSIDE a virtualenv already, assume that the 
    # virtualenv already exists and we only need to update it.
    if hasattr(sys, 'real_prefix'):
        if options.sitepkg_install:
            raise RuntimeError(
                'Cannot install to site-packages from a virtual environment')
        # Otherwise, check that the version of Python in the virtualenv being 
        # used is correct.  We cannot update this, so error if it is incorrect.
    else:
        # If the user wants a sitepkg install...
        if options.sitepkg_install:
            do_sitepkg_install(options)
        # Otherwise, we're giving them a virtualenv. 
        # Does the virtualenv already exist?  If so, we just check to make 
        # sure it is up to date.
        elif os.path.isfile(os.path.join(options.virtualenv_path, 'Scripts', 'python.exe')) and not options.clean:
            # Check the version of Python in the virtualenv.  We cannot
            # update it after the virtualenv is created (we have to destroy and
            # recreate this virtualenv), so just show an error.
            pass
        else:
            do_virtualenv_install(options)
        
        # Write config files
        _populate_home_dir(options)

        if not options.sitepkg_install:
            read_and_update_environment_variables(options)

        # Choose the pip tool location based on if this is a virtualenv install
        # or a site-packages install            
        if options.sitepkg_install:
            piptool = os.path.join(sys.prefix, 'Scripts', 'pip')            
        else:
            piptool = os.path.join(options.virtualenv_path, 'Scripts', 'pip')
            
        # Always install a copy of ourselves, even if no one asked for us.
        if not options.noupdate:
            returncode = subprocess.call(
                '"{}" install {} {}=={}'.format(piptool,
                                                _get_pip_install_args(options),
                                                VIRTUALENV_UTIL_PACKAGE_NAME,
                                                version()),
                shell = True)                                                       
        
            if returncode != 0:
                raise RuntimeError('Failed to install package {} via pip, check pip output for more information'.format(VIRTUALENV_UTIL_PACKAGE_NAME)) 
             

        # If requirements were specified as a list of requirements
        # specifiers separated by commas, install each package individually.
        if options.requirement_specifiers and not options.noupdate:
            for requirement in options.requirement_specifiers.split(','):
                returncode = subprocess.call(
                    '"{}" install {} {}'.format(piptool,
                                                _get_pip_install_args(options),
                                                requirement),
                    shell = True)                                                       
                
                if returncode != 0:
                    raise RuntimeError('Failed to install required package(s) via pip, check pip output for more information (requirement {})'.format(requirement)) 
            
        # Run pip to install / update the required
        # tool packages listed in the requirements.txt file.
        if options.requirements_file and not options.noupdate:
            returncode = subprocess.call(
                '"{}" install {} -r {}'.format(piptool,
                                               _get_pip_install_args(options),
                                               options.requirements_file),
                shell = True)

            if returncode != 0:
                raise RuntimeError('Failed to install required package(s) via pip, check pip output for more information (requirements file {})'.format(options.requirements_file))                               

        if options.installed_list_file:
        
            # Output the list of installed tools to a text file. 
            output = subprocess.check_output([piptool, 'freeze'])
            f = open(options.installed_list_file, 'w')
            f.write(_get_implicit_versions_string(options))
            f.write(output)
            f.close()
            
        if options.download_cache_dir:
            _fix_download_cache_dir_filenames(options)
            
        if options.helper_scripts:
            _create_ve_helper_scripts(options)        

    if options.sitepkg_install:
        scripts_dir = os.path.join(sys.prefix, 'Scripts') 
    else:
        scripts_dir = os.path.join(options.virtualenv_path, 'Scripts')
        
    if options.run is not None or options.script is not None:
    
        # Add Scripts directory to the path so those executables are
        # available to the item being executed.
        os.environ["PATH"] = scripts_dir + os.pathsep + os.environ["PATH"]
        
    if options.run is not None:
        if options.sitepkg_install:
            python_executable = sys.executable 
        else:
            python_executable = os.path.join(scripts_dir, 'python.exe')
    
        # Run the file using the Python executable in the virtualenv.
        p = subprocess.Popen(python_executable + ' ' + options.run, shell=True)
        sys.exit(p.wait())
    elif options.script is not None:
   
        # Run a script, assumed to be located in the Scripts directory.                   
        # Note that the script name cannot have any spaces using the logic 
        # below.             
        if len(options.script.split()) > 1:
            p = subprocess.Popen(os.path.join(scripts_dir, options.script.split()[0]) + ' ' + ' '.join(options.script.split()[1:]))
        else:            
            p = subprocess.Popen(os.path.join(scripts_dir, options.script))
        sys.exit(p.wait())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create / update a Python virtualenv')
    parser.add_argument('--cfg_file')
    parsed, remaining_args = parser.parse_known_args(sys.argv[1:])
    sys.argv = [sys.argv[0]] + remaining_args

    main(parsed.cfg_file)
