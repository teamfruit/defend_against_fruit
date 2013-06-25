import glob
import os
import shutil
from build.constants import PYTHON_GROUP_ID


MODULE_INFO_DIR = 'module-info'


class DirectoryContextManager(object):
    def __init__(self, new_cwd):
        self.__new_cwd = new_cwd

    def __enter__(self):
        self.__old_cwd = os.getcwd()
        os.chdir(self.__new_cwd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.__old_cwd)


def ensure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def split_ext(filename):
    """
    Example usage:
    > _split_ext('script.py')
    ('script', 'py')
    """
    split = filename.split('.')
    return '.'.join(split[:-1]), split[-1]


def rm(*glob_patterns):
    for pattern in glob_patterns:
        for path in glob.glob(pattern):
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)


def compute_module_info_filename(artifact_id, module_version):
    output_filename = '{}-{}-module-info.json'.format(
        artifact_id,
        module_version)
    return output_filename


def compute_module_info_filename_full_path(
        artifact_id,
        version,
        module_info_dir=MODULE_INFO_DIR):
    filename = compute_module_info_filename(artifact_id, version)
    relative_path = os.path.join(module_info_dir, filename)
    return os.path.abspath(relative_path)


def compute_requirements_filename(artifact_id, module_version):
    output_filename = '{}-{}-requirements.txt'.format(
        artifact_id,
        module_version)
    return output_filename


def compute_requirements_filename_full_path(
        artifact_id,
        version,
        dist_dir='dist'):
    filename = compute_requirements_filename(artifact_id, version)
    relative_path = os.path.join(dist_dir, filename)
    return os.path.abspath(relative_path)


def compute_repo_path_from_module_name(module):
    return '{}/{}'.format(PYTHON_GROUP_ID, module)


def get_submodule_info(module_dir, module_info_dir=MODULE_INFO_DIR):
    """Find json module info file for the specified module directory.

    :param module_dir: directory of module or submodule being searched
    :param module_info_dir: sub-directory within module directory in
        which to search
    """

    def _one_json_file(files):
        """
        There should not be more than one JSON file per module. If there
        is, this method raises an error.
        """
        assert len(files) <= 1, \
            'Submodules should have a maximum of one module-info JSON ' \
            'file each.'

        return files[0] if files else None

    def _glob_submodule_info(module_dir, module_info_dir):
        json_pattern = os.path.join(
            module_dir,
            module_info_dir,
            '*-module-info.json')
        return glob.glob(json_pattern)

    return _one_json_file(_glob_submodule_info(
        module_dir=module_dir,
        module_info_dir=module_info_dir))


def get_file_digests(filename, digests, block_size=2 ** 20):
    """
    Calculate hashes of the given file. 'digests' should be an iterable
    container of hashlib-compatible objects.

    Example usage:
    > md5, sha1 = get_file_digests(
        'archive.tar.gz',
        digests=(hashlib.md5(), hashlib.sha1()))
    > md5.hexdigest()
    'b488a911018964989d158a34c47709d4'
    > sha1.hexdigest()
    'e4ba5c0279368c131799e01c774b49ded12fc331'
    """
    with open(filename, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            for d in digests:
                d.update(data)
    return digests


def write_to_file(file_path, to_write, write_mode='w'):
    """
    Write the given data into the file at the given path. If the path
    does not exist, it is created.
    """
    dirname = os.path.dirname(os.path.abspath(file_path))

    if dirname:
        ensure_path_exists(dirname)

    with open(file_path, write_mode) as f:
        f.write(to_write)
