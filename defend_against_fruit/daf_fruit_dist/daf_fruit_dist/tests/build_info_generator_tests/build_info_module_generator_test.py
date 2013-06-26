from functools import wraps
import json
import os
import pprint
import tempfile

from nose.tools import eq_
from pip.exceptions import DistributionNotFound
from requests import HTTPError
from daf_fruit_dist.checksum_dependency_helper import ChecksumDependencyHelper
from daf_fruit_dist.checksums import Checksums
from daf_fruit_dist.build.artifact import Artifact
from daf_fruit_dist.build.constants import \
    PYTHON_SDIST, \
    PYTHON_BDIST, \
    PYTHON_EGG, \
    PYTHON_GROUP_ID
from daf_fruit_dist.build.dependency import Dependency
from daf_fruit_dist.build.id import Id
from daf_fruit_dist.build.module import Module
from daf_fruit_dist.build_info_module_generator import BuildInfoModuleGenerator


def set_fn_name(name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        wrapper.__name__ = name
        return wrapper
    return decorator


class BuildInfoModuleGeneratorTestHelper(object):
    def __init__(self):
        super(BuildInfoModuleGeneratorTestHelper, self).__init__()

        self.module_id = Id(
            group_id=PYTHON_GROUP_ID,
            artifact_id="pointy-stick",
            version="1.2.3")

        self.alternate_module_id = Id(
            group_id=PYTHON_GROUP_ID,
            artifact_id="very-pointy-stick",
            version="7.8.9")

        self.module_properties = {"gorilla": "loves oranges",
                                  "orangutan": "loves bananas"}

        dir_name = os.path.dirname(__file__)

        self.full_requirements_file = os.path.abspath(
            os.path.join(
                dir_name,
                "pointy-stick-1.2.3-requirements.txt"))

        self.empty_requirements_file = os.path.abspath(
            os.path.join(
                dir_name,
                "pointy-stick-1.2.3-empty-requirements.txt"))

        self.unfindable_requirements_file = os.path.abspath(
            os.path.join(
                dir_name,
                "pointy-stick-1.2.3-unfindable-requirements.txt"))

        bdist_name = 'pointy-stick-1.2.3-bdist.txt'
        self.bdist_file = os.path.abspath(os.path.join(dir_name, bdist_name))
        bdist_md5 = "4e5b207722b76b240bdab0f8170abe2e"
        bdist_sha1 = "1436227b16793cc398f2919077d700dfbba46c41"
        self.bdist_artifact = Artifact(
            type=PYTHON_BDIST,
            name=bdist_name,
            sha1=bdist_sha1,
            md5=bdist_md5)

        sdist_name = 'pointy-stick-1.2.3-sdist.txt'
        self.sdist_file = os.path.abspath(os.path.join(dir_name, sdist_name))
        sdist_md5 = "a0fd44030bb445f1b6cddb1aec5d0f5d"
        sdist_sha1 = "0a9185359e621f0916f0902b70dbe5cd3980c7bd"
        self.sdist_artifact = Artifact(
            type=PYTHON_SDIST,
            name=sdist_name,
            sha1=sdist_sha1,
            md5=sdist_md5)

        egg_name = 'pointy-stick-1.2.3-egg.txt'
        self.egg_file = os.path.abspath(os.path.join(dir_name, egg_name))
        egg_md5 = "11e074bc70ac6d067fd850a4e0fec467"
        egg_sha1 = "5308474d2eede397dde38769bb8b0c5f38376370"
        self.egg_artifact = Artifact(
            type=PYTHON_EGG,
            name=egg_name,
            sha1=egg_sha1,
            md5=egg_md5)

        # Dependency types are unknown so therefore have been
        # intentionally set to None.
        colorama_id = Id(
            group_id=PYTHON_GROUP_ID,
            artifact_id="colorama",
            version="0.2.4")

        self.colorama_dependency = Dependency(
            id=colorama_id,
            type=None,
            sha1="ColoramaSHA1SHA1SHA1",
            md5="ColoramaMD5MD5MD5")

        mock_id = Id(
            group_id=PYTHON_GROUP_ID,
            artifact_id="mock",
            version="1.0.1")

        self.mock_dependency = Dependency(
            id=mock_id,
            type=None,
            sha1="MockSHA1SHA1SHA1",
            md5="MockMD5MD5MD5")

        nose_id = Id(
            group_id=PYTHON_GROUP_ID,
            artifact_id="nose",
            version="1.2.1")

        self.nose_dependency = Dependency(
            id=nose_id,
            type=None,
            sha1="NoseSHA1SHA1SHA1",
            md5="NoseMD5MD5MD5")

        unfindable_module_id = Id(
            group_id=PYTHON_GROUP_ID,
            artifact_id="unfindablemodule",
            version="999.999.999")

        self.unfindable_dependency = Dependency(
            id=unfindable_module_id,
            type=None,
            sha1=None,
            md5=None)

        def _add_file_path_and_checksum_to_dictionary(dictionary, dependency):
            dep_file_path = BuildInfoModuleGeneratorTestHelper.\
                _compute_synthetic_path(
                    pkg_name=dependency.id.artifact_id,
                    pkg_version=dependency.id.version)

            dep_checksums = Checksums(
                sha1=dependency.sha1,
                md5=dependency.md5)
            dictionary[dep_file_path] = dep_checksums

        self.file_path_to_checksums = {}

        _add_file_path_and_checksum_to_dictionary(
            self.file_path_to_checksums, self.colorama_dependency)

        _add_file_path_and_checksum_to_dictionary(
            self.file_path_to_checksums, self.mock_dependency)

        _add_file_path_and_checksum_to_dictionary(
            self.file_path_to_checksums, self.nose_dependency)

    @staticmethod
    def _compute_synthetic_path(pkg_name, pkg_version):
        path = (
            "{python_group_id}/"
            "{pkg_name}/"
            "{pkg_name}-{pkg_version}.tar.gz".format(
                python_group_id=PYTHON_GROUP_ID,
                pkg_name=pkg_name,
                pkg_version=pkg_version))

        return path

    def determine_file_path(self, pkg_name, pkg_version):
        findable_pairs = (
            (self.colorama_dependency.id.artifact_id,
             self.colorama_dependency.id.version),

            (self.mock_dependency.id.artifact_id,
             self.mock_dependency.id.version),

            (self.nose_dependency.id.artifact_id,
             self.nose_dependency.id.version),
        )
        if (pkg_name, pkg_version) in findable_pairs:
            return self._compute_synthetic_path(pkg_name, pkg_version)
        else:
            raise DistributionNotFound()

    def determine_checksums_from_file_path(self, file_path):
        if file_path in self.file_path_to_checksums:
            return self.file_path_to_checksums[file_path]
        else:
            raise AssertionError(
                "Unexpected file_path {} within test fixture.".format(
                    file_path))

    def determine_checksums_from_file_path_throw_exception(self, file_path):
        # noinspection PyExceptionInherit
        raise HTTPError()


def _create_temp_file_name():
    temp_file = tempfile.NamedTemporaryFile(
        prefix="module_info_test_",
        suffix=".json",
        delete=True)
    temp_file_name = temp_file.name
    temp_file.close()
    return temp_file_name


def _write_module_file(module, module_file):
    json_data = module.as_json_data
    json_string = json.dumps(json_data, sort_keys=True, indent=4)

    with open(module_file, 'w') as f:
        f.write(json_string)


def _read_module_file(module_file):
    with open(module_file, 'r') as f:
        module_as_json = f.read()
        json_data = json.loads(module_as_json)
        module = Module.from_json_data(json_data)
    return module


helper = BuildInfoModuleGeneratorTestHelper()


def _execute(
        module_id,
        dist_files_tuple_array,
        freeze_file,
        module_file,
        force_dependency_rebuild,
        force_clean,
        expected_module_properties,
        expected_artifacts,
        expected_dependencies):
    #tuple pattern is: (command, python_version, dist_file)

    checksum_dependency_helper = ChecksumDependencyHelper(
        determine_file_path_fn=helper.determine_file_path,
        determine_checksums_from_file_path_fn=
        helper.determine_checksums_from_file_path)

    build_info_module_generator = BuildInfoModuleGenerator(
        determine_dependency_checksums_fn=checksum_dependency_helper)

    ########################################
    #Invoke functionality being tested
    build_info_module_generator.update(
        module_id=module_id,
        module_properties=helper.module_properties,
        freeze_file=freeze_file,
        dist_files=dist_files_tuple_array,
        module_file=module_file,
        force_dependency_rebuild=force_dependency_rebuild,
        force_clean=force_clean)

    ########################################
    #validate behavior
    module = _read_module_file(module_file)
    eq_(module.id, module_id)
    eq_(module.artifacts, expected_artifacts)
    eq_(module.dependencies, expected_dependencies)
    eq_(module.properties, expected_module_properties)


@set_fn_name(
    'test_'
    'no_module_file__'
    'no_requirements_file__'
    'no_force_dependencies_rebuild__'
    'no_force_clean')
def temp_fn_01():
    module_output_file_name = _create_temp_file_name()

    _execute(
        module_id=helper.module_id,
        dist_files_tuple_array=[
            ('sdist', None, helper.sdist_file),
            #        ('bdist', None, bdist_file),
            ('bdist_egg', None, helper.egg_file)],
        freeze_file=helper.unfindable_requirements_file,
        module_file=module_output_file_name,
        force_dependency_rebuild=False,
        force_clean=False,
        expected_module_properties=helper.module_properties,
        expected_artifacts=(helper.sdist_artifact, helper.egg_artifact),
        expected_dependencies=(
            helper.colorama_dependency,
            helper.mock_dependency,
            helper.unfindable_dependency,
            helper.nose_dependency
        )
    )
    os.unlink(module_output_file_name)


@set_fn_name(
    'test_'
    'rest_exception__'
    'no_module_file__'
    'full_req_file__'
    'no_force_dep_rebuild__'
    'no_force_clean')
def temp_fn_02():
    module_output_file_name = _create_temp_file_name()
    exception_caught = False
    try:
        checksum_dependency_helper = ChecksumDependencyHelper(
            determine_file_path_fn=helper.determine_file_path,
            determine_checksums_from_file_path_fn=
            helper.determine_checksums_from_file_path_throw_exception)

        build_info_module_generator = BuildInfoModuleGenerator(
            determine_dependency_checksums_fn=checksum_dependency_helper)

        ########################################
        #Invoke functionality being tested
        build_info_module_generator.update(
            module_id=helper.module_id,
            module_properties=helper.module_properties,
            freeze_file=helper.full_requirements_file,
            dist_files=[
                ('sdist', None, helper.sdist_file),
                #        ('bdist', None, bdist_file),
                ('bdist_egg', None, helper.egg_file)],
            module_file=module_output_file_name,
            force_dependency_rebuild=False,
            force_clean=False)
    except HTTPError:
        exception_caught = True
        #Make sure no trash module file is left behind
        assert not os.path.exists(module_output_file_name)

    assert exception_caught, "Expect HTTPError to be encountered"


@set_fn_name(
    'test_'
    'no_module_file__'
    'full_requirements_file__'
    'no_force_dependency_rebuild__'
    'no_force_clean')
def temp_fn_03():
    """No pre-existing module file and a full requirements file"""

    module_output_file_name = _create_temp_file_name()
    _execute(
        module_id=helper.module_id,
        dist_files_tuple_array=[
            ('sdist', None, helper.sdist_file),
            #        ('bdist', None, bdist_file),
            ('bdist_egg', None, helper.egg_file)],
        freeze_file=helper.full_requirements_file,
        module_file=module_output_file_name,
        force_dependency_rebuild=False,
        force_clean=False,
        expected_module_properties=helper.module_properties,
        expected_artifacts=(helper.sdist_artifact, helper.egg_artifact),
        expected_dependencies=(
            helper.colorama_dependency,
            helper.mock_dependency,
            helper.nose_dependency)
    )
    os.unlink(module_output_file_name)


@set_fn_name(
    'test_'
    'no_module_file__'
    'unrecognized_command_in_dist_files_tuple')
def temp_fn_04():
    """Unrecognized command in the dist files tuple"""

    module_output_file_name = _create_temp_file_name()
    exception_caught = False
    try:
        _execute(
            module_id=helper.module_id,
            dist_files_tuple_array=[
                ('sdist', None, helper.sdist_file),
                #        ('bdist', None, bdist_file),
                ('bdist_funky_egg', None, helper.egg_file)],
            freeze_file=helper.full_requirements_file,
            module_file=module_output_file_name,
            force_dependency_rebuild=False,
            force_clean=False,
            expected_module_properties=helper.module_properties,
            expected_artifacts=(helper.sdist_artifact, helper.egg_artifact),
            expected_dependencies=(
                helper.colorama_dependency,
                helper.mock_dependency,
                helper.nose_dependency),
        )
    except ValueError:
        exception_caught = True
        #Make sure no trash module file is left behind
        assert not os.path.exists(module_output_file_name)

    assert exception_caught, "Expect ValueError to be encountered"


@set_fn_name(
    'test_'
    'no_module_file__'
    'empty_requirements_file__'
    'no_force_dependency_rebuild__'
    'no_force_clean')
def temp_fn_05():
    """
    An empty requirements file should result in a defined but empty
    collection of dependencies.

    Do not confuse an empty collection with a collection of None. A
    collection of None would imply no requirements file was processed.
    """

    module_output_file_name = _create_temp_file_name()
    _execute(
        module_id=helper.module_id,
        dist_files_tuple_array=[
            ('sdist', None, helper.sdist_file),
            #        ('bdist', None, bdist_file),
            ('bdist_egg', None, helper.egg_file)],
        freeze_file=helper.empty_requirements_file,
        module_file=module_output_file_name,
        force_dependency_rebuild=False,
        force_clean=False,
        expected_module_properties=helper.module_properties,
        expected_artifacts=(helper.sdist_artifact, helper.egg_artifact),
        expected_dependencies=()
    )
    os.unlink(module_output_file_name)


@set_fn_name(
    'test_'
    'existing_module_file__'
    'full_requirements_file__'
    'no_force_dependency_rebuild__'
    'no_force_clean')
def temp_fn_06():
    """pre-existing module file and full requirements file"""

    module_output_file_name = _create_temp_file_name()

    early_properties = {'skunk': 'stinks', 'raccoon': 'cleans food'}
    early_module = Module(
        id=helper.module_id,
        properties=early_properties,
        artifacts=(helper.bdist_artifact,),
        dependencies=(helper.colorama_dependency,))
    _write_module_file(early_module, module_output_file_name)

    #conditions prepared, now perform action under test and assert results
    _execute(
        module_id=helper.module_id,
        dist_files_tuple_array=[
            ('sdist', None, helper.sdist_file),
            #        ('bdist', None, bdist_file),
            ('bdist_egg', None, helper.egg_file)],
        freeze_file=helper.full_requirements_file,
        module_file=module_output_file_name,
        force_dependency_rebuild=False,
        force_clean=False,
        expected_module_properties=early_properties,
        expected_artifacts=(
            helper.bdist_artifact,
            helper.sdist_artifact,
            helper.egg_artifact),
        expected_dependencies=(helper.colorama_dependency,)
    )
    os.unlink(module_output_file_name)


@set_fn_name(
    'test_'
    'existing_module_file__'
    'non_matching_module_id')
def temp_fn_07():
    """pre-existing module file with non-matching module id"""

    module_output_file_name = _create_temp_file_name()

    early_properties = {'skunk': 'stinks', 'raccoon': 'cleans food'}
    early_module = Module(
        id=helper.alternate_module_id,
        properties=early_properties,
        artifacts=(helper.bdist_artifact,),
        dependencies=(helper.colorama_dependency,))
    _write_module_file(early_module, module_output_file_name)

    exception_caught = False

    #conditions prepared, now perform action under test and assert results
    try:
        _execute(
            module_id=helper.module_id,
            dist_files_tuple_array=[
                ('sdist', None, helper.sdist_file),
                #        ('bdist', None, bdist_file),
                ('bdist_egg', None, helper.egg_file)],
            freeze_file=helper.full_requirements_file,
            module_file=module_output_file_name,
            force_dependency_rebuild=False,
            force_clean=False,
            expected_module_properties=early_properties,
            expected_artifacts=(
                helper.bdist_artifact,
                helper.sdist_artifact,
                helper.egg_artifact),
            expected_dependencies=(helper.colorama_dependency,)
        )
    except ValueError:
        exception_caught = True

    assert exception_caught, "Expect ValueError to be encountered"
    os.unlink(module_output_file_name)


@set_fn_name(
    'test_'
    'existing_module_file__'
    'full_requirements_file__'
    'no_force_dependency_rebuild__'
    'force_clean')
def temp_fn_08():
    """pre-existing module file with force clean"""

    module_output_file_name = _create_temp_file_name()

    early_properties = {'skunk': 'stinks', 'raccoon': 'cleans food'}
    early_module = Module(
        id=helper.module_id,
        properties=early_properties,
        artifacts=(helper.bdist_artifact,),
        dependencies=(helper.colorama_dependency,))
    _write_module_file(early_module, module_output_file_name)

    #conditions prepared, now perform action under test and assert results
    _execute(
        module_id=helper.module_id,
        dist_files_tuple_array=[
            ('sdist', None, helper.sdist_file),
            #        ('bdist', None, bdist_file),
            ('bdist_egg', None, helper.egg_file)],
        freeze_file=helper.full_requirements_file,
        module_file=module_output_file_name,
        force_dependency_rebuild=False,
        force_clean=True,
        expected_module_properties=helper.module_properties,
        expected_artifacts=(helper.sdist_artifact, helper.egg_artifact),
        expected_dependencies=(
            helper.colorama_dependency,
            helper.mock_dependency,
            helper.nose_dependency)
    )
    os.unlink(module_output_file_name)


@set_fn_name(
    'test_'
    'existing_module_file__'
    'full_requirements_file__'
    'force_dependency_rebuild__'
    'no_force_clean')
def temp_fn_09():
    """
    pre-existing module file with incomplete dependencies but a forced
    dependency rebuild
    """

    module_output_file_name = _create_temp_file_name()

    early_properties = {'skunk': 'stinks', 'raccoon': 'cleans food'}
    early_module = Module(
        id=helper.module_id,
        properties=early_properties,
        artifacts=(helper.bdist_artifact,),
        dependencies=(helper.colorama_dependency,))
    _write_module_file(early_module, module_output_file_name)

    #conditions prepared, now perform action under test and assert results
    _execute(
        module_id=helper.module_id,
        dist_files_tuple_array=[
            ('sdist', None, helper.sdist_file),
            #        ('bdist', None, bdist_file),
            ('bdist_egg', None, helper.egg_file)],
        freeze_file=helper.full_requirements_file,
        module_file=module_output_file_name,
        force_dependency_rebuild=True,
        force_clean=False,
        expected_module_properties=early_properties,
        expected_artifacts=(
            helper.bdist_artifact,
            helper.sdist_artifact,
            helper.egg_artifact),
        expected_dependencies=(
            helper.colorama_dependency,
            helper.mock_dependency,
            helper.nose_dependency)
    )
    os.unlink(module_output_file_name)


@set_fn_name(
    'test_'
    'existing_module_file_with_no_artifacts__'
    'full_requirements_file__'
    'no_force_dependency_rebuild__'
    'no_force_clean')
def temp_fn_10():
    """
    pre-existing module file with no artifacts, matching id and
    different properties
    """

    module_output_file_name = _create_temp_file_name()

    early_properties = {'skunk': 'stinks', 'raccoon': 'cleans food'}
    early_module = Module(
        id=helper.module_id,
        properties=early_properties,
        artifacts=None,
        dependencies=(helper.colorama_dependency,))
    _write_module_file(early_module, module_output_file_name)

    #conditions prepared, now perform action under test and assert results
    _execute(
        module_id=helper.module_id,
        dist_files_tuple_array=[
            ('sdist', None, helper.sdist_file),
            #        ('bdist', None, bdist_file),
            ('bdist_egg', None, helper.egg_file)],
        freeze_file=helper.full_requirements_file,
        module_file=module_output_file_name,
        force_dependency_rebuild=False,
        force_clean=False,
        expected_module_properties=early_properties,
        expected_artifacts=(helper.sdist_artifact, helper.egg_artifact),
        expected_dependencies=(helper.colorama_dependency,)
    )
    os.unlink(module_output_file_name)


@set_fn_name(
    'test_'
    'existing_module_file_with_no_deps__'
    'full_requirements_file__'
    'no_force_dependency_rebuild__'
    'no_force_clean')
def temp_fn_11():
    """
    pre-existing module file with no dependencies, matching id and
    different properties
    """

    module_output_file_name = _create_temp_file_name()

    early_properties = {'skunk': 'stinks', 'raccoon': 'cleans food'}
    early_module = Module(
        id=helper.module_id,
        properties=early_properties,
        artifacts=(helper.bdist_artifact,),
        dependencies=None)
    _write_module_file(early_module, module_output_file_name)

    #conditions prepared, now perform action under test and assert results
    _execute(
        module_id=helper.module_id,
        dist_files_tuple_array=[
            ('sdist', None, helper.sdist_file),
            #        ('bdist', None, bdist_file),
            ('bdist_egg', None, helper.egg_file)],
        freeze_file=helper.full_requirements_file,
        module_file=module_output_file_name,
        force_dependency_rebuild=False,
        force_clean=False,
        expected_module_properties=early_properties,
        expected_artifacts=(
            helper.bdist_artifact,
            helper.sdist_artifact,
            helper.egg_artifact),
        expected_dependencies=(
            helper.colorama_dependency,
            helper.mock_dependency,
            helper.nose_dependency)
    )
    os.unlink(module_output_file_name)


@set_fn_name(
    'test_'
    'no_module_file__'
    'missing_requirements_file__'
    'no_force_dependency_rebuild__'
    'no_force_clean')
def temp_fn_12():
    """
    An empty requirements file should result in a defined but empty
    collection of dependencies.

    Do not confuse an empty collection with a collection of None. A
    collection of None would imply no requirements file was processed.
    """

    module_output_file_name = _create_temp_file_name()
    non_existent_requirements_file = _create_temp_file_name()
    exception_caught = False
    try:
        _execute(
            module_id=helper.module_id,
            dist_files_tuple_array=[
                ('sdist', None, helper.sdist_file),
                #        ('bdist', None, bdist_file),
                ('bdist_egg', None, helper.egg_file)],
            freeze_file=non_existent_requirements_file,
            module_file=module_output_file_name,
            force_dependency_rebuild=False,
            force_clean=False,
            expected_module_properties=helper.module_properties,
            expected_artifacts=(helper.sdist_artifact, helper.egg_artifact),
            expected_dependencies=()
        )
    except IOError as e:
        exception_caught = True

        #Make sure no trash module file is left behind
        assert not os.path.exists(module_output_file_name)
        eq_(e.filename, non_existent_requirements_file)

    assert exception_caught, "Expect IOError to be encountered"


def test_case_sensitive_dependencies():
    """
    Verify that artifact IDs of dependencies match the real project
    name, not the case-insensitive key.
    """

    class MockModuleBuilder(object):
        def __init__(self):
            self.__module_names = []

        def ensure_dependencies_defined(self):
            pass

        # noinspection PyShadowingBuiltins
        def add_dependency(self, type, id, sha1, md5):
            self.__module_names.append(id.artifact_id)

        def compare_modules(self, freeze_file):
            with open(freeze_file) as f:
                modules = f.read().splitlines()

            expected_set = frozenset([m.split('==')[0] for m in modules])
            actual_set = frozenset(self.__module_names)

            assert actual_set == expected_set, (
                '\nActual module names:\n    {}'
                '\nExpected module names:\n    {}'.format(
                    '\n    '.join(pprint.pformat(actual_set).splitlines()),
                    '\n    '.join(pprint.pformat(expected_set).splitlines())))

            eq_(actual_set, expected_set)

    generator = BuildInfoModuleGenerator(
        determine_dependency_checksums_fn=
        lambda artifact_id, version: (None, None))

    freeze_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "case-sensitive-requirements.txt")

    mock_module_builder = MockModuleBuilder()
    generator._reset_dependencies(freeze_file, mock_module_builder)
    mock_module_builder.compare_modules(freeze_file)
