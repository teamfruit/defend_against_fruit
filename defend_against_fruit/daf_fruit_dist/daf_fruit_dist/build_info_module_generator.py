import json
import os
import pkg_resources
from build.constants import PYTHON_SDIST, PYTHON_BDIST, PYTHON_EGG
from build.constants import PYTHON_WHEEL, PYTHON_SPHINX, PYTHON_RPM
from build.constants import PYTHON_FREEZE, PYTHON_GROUP_ID
from build.id import Id
from build.module import Module
from file_management import write_to_file


class BuildInfoModuleGenerator(object):
    """
    Incrementally build up a module level meta-data file for later
    inclusion in an Artifactory build-info message.

    Setuptools/distribute commands are provided with an array of tuples
    accessed at self.distribution.dist_files.

    This along with other information in self.distribution provides the
    information necessary to create the artifacts portion of the build-
    info meta-data Artifactory needs. The caveat is only files built by
    commands within the same execution will be available.

    For example:
    prompt>python setup.py sdist bdist_egg my_custom_command
    prompt>python setup.py bdist_rpm my_custom_command

    In the second execution, my_custom_command will have access to a
    tuple like ("bdist_rpm", "2.7", "somepath/dist/pointy-stick-1.2.3.rpm")
    but will have no information about the sdist and bdist_egg files.

    To ensure the collection of a full set of Module information the
    current design simply writes a meta-data file into the dist
    directory. Each execution of the custom command enhances the meta-
    data file to incorporate new information.

    There are surely better ways to achieve a similar goal, but most of
    them involve customizing existing distribute commands or
    introspecting existing binaries in the dist directory.

    Customizing the existing distribute commands would effectively be a
    fork of the distribute code base, and therefore difficult to
    maintain. Even a monkey patch of the distribute commands would
    likely be a bit fragile.

    Similarly introspection turns out to not be sufficiently
    deterministic. The pkg-info in each distribution doesn't make it
    easy to tell the difference between a bdist and an sdist. It is
    possible to make a good guess, but that isn't really ideal.

    Continuous integration/deployment builds are already outside the
    scope of the distribute package. Furthermore, only a build within a
    continuous integration server should typically be able to upload
    artifacts to a build artifact repository such as Artifactory.
    Therefore, ensuring the continuous integration tooling always calls
    a specialized meta-data collecting command, along with any setup
    command producing a published build artifact, isn't all that bad.
    """

    def __init__(self, determine_dependency_checksums_fn):
        """Construct generator instance.

        :param determine_dependency_checksums_fn: Arguments must match
            (artifact_id, version) and must return an MD5, SHA1 tuple
        """
        super(BuildInfoModuleGenerator, self).__init__()

        self.determine_dependency_checksums_fn = (
            determine_dependency_checksums_fn)

        self._command_to_type_dict = {
            'sdist': PYTHON_SDIST,
            'bdist': PYTHON_BDIST,
            'bdist_dumb': PYTHON_BDIST,
            'bdist_egg': PYTHON_EGG,
            'bdist_wheel': PYTHON_WHEEL,
            'bdist_rpm': PYTHON_RPM,
            'build_sphinx': PYTHON_SPHINX,
            'build_sphinx_zip': PYTHON_SPHINX,
            'freeze': PYTHON_FREEZE
        }

    def update(self,
               module_id,
               module_properties,
               freeze_file,
               dist_files,
               module_file,
               force_dependency_rebuild=False,
               force_clean=False):

        module_builder = self._create_module_builder(
            module_id=module_id,
            module_properties=module_properties,
            module_file=module_file,
            ignore_previous_dependencies=force_dependency_rebuild,
            force_clean=force_clean)

        self._append_artifacts(dist_files, module_builder)

        if module_builder.dependencies is None:
            self._reset_dependencies(freeze_file, module_builder)

        module = module_builder.build()
        self._write_module_file(module, module_file)

    def _create_module_builder(
            self,
            module_id,
            module_properties,
            module_file,
            ignore_previous_dependencies,
            force_clean):

        if force_clean or (not os.path.exists(module_file)):
            module_builder = Module.Builder(
                id=module_id,
                properties=module_properties,
                treat_none_as_empty=False
            )
        else:
            with open(module_file, 'r') as f:
                json_string = f.read()

            json_data = json.loads(json_string)
            existing_module = Module.from_json_data(json_data)

            if module_id != existing_module.id:
                msg = (
                    "module id {} read from {} doesn't match specified value "
                    "of {}".format(
                        existing_module.id,
                        module_file,
                        module_id))
                raise ValueError(msg)

            module_builder = Module.Builder.from_another_module(
                module=existing_module,
                treat_none_as_empty=False,
                copy_dependencies=not ignore_previous_dependencies
            )

        return module_builder

    def _write_module_file(self, module, module_file):
        json_data = module.as_json_data
        json_string = json.dumps(json_data, sort_keys=True, indent=4)
        write_to_file(file_path=module_file, to_write=json_string)

    def _determine_type_from_command_name(self, command_name):
        lc_command_name = command_name.lower()
        if lc_command_name in self._command_to_type_dict:
            artifact_type = self._command_to_type_dict[lc_command_name]
        else:
            raise ValueError(
                "unrecognized artifact command: {}".format(command_name))

        return artifact_type

    def _append_artifacts(self, dist_files, module_builder):
        for cmd, py_version, artifact in dist_files:
            artifact_type = self._determine_type_from_command_name(cmd)
            module_builder.add_file_as_artifact(
                type=artifact_type, file=artifact)

    def _reset_dependencies(self, freeze_file, module_builder):
        requirements = self._parse_req_file(requirement_file=freeze_file)

        module_builder.ensure_dependencies_defined()
        for req in requirements:
            # There are two options for the artifact ID: req.key and
            # req.project_name. The req.key option is all lowercase,
            # while the req.project_name option respects the case of the
            # project. Since Artifactory has trouble locating build
            # dependencies when all lowercase names are specified,
            # req.project_name appears to be a better option here.
            artifact_id = req.project_name

            assignment, version = req.specs[0]

            dependency_id = Id(
                group_id=PYTHON_GROUP_ID,
                artifact_id=artifact_id,
                version=version)

            dependency_md5, dependency_sha1 = (
                self.determine_dependency_checksums_fn(artifact_id, version))

            module_builder.add_dependency(
                type=None,
                id=dependency_id,
                sha1=dependency_sha1,
                md5=dependency_md5)

    def _parse_req_file(self, requirement_file):
        requirements = []

        with open(requirement_file, 'r') as req_f:
            for line in req_f:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    requirements.append(
                        pkg_resources.Requirement.parse(stripped))

        return requirements
