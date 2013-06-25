from distutils import log
from setuptools import Command

from daf_fruit_dist.artifactory import artifactory_rest
from daf_fruit_dist.artifactory.repo_detail import read_options
from daf_fruit_dist.checksum_dependency_helper import ChecksumDependencyHelper
from daf_fruit_dist.pip_package_path_finder import PipPackagePathFinder
from daf_fruit_dist.build.constants import PYTHON_GROUP_ID
from daf_fruit_dist.build.id import Id
from daf_fruit_dist.build_info_module_generator import BuildInfoModuleGenerator
from daf_fruit_dist.file_management import \
    compute_requirements_filename_full_path, \
    compute_module_info_filename_full_path


class ModuleGeneratorCommand(Command):
    """
    Command for generating Artifactory module meta-data files for use in
    ``setup.py`` scripts.
    """

    # Description shown in setup.py --help-commands
    description = (
        'Build model portion of Artifactory build-info and save as json file '
        'in dist directory')

    # Options available for this command, tuples of ('longoption',
    # 'shortoption', 'help'). If the longoption name ends in a `=` it
    # takes an argument.
    user_options = [
        ('force-dependency-rebuild', None,
         'rebuild dependency meta-data information'),
        ('force-clean', None,
         'rebuild all meta-data information'),
        ('no-cert-verify', None,
         'do not verify authenticity of host cert when using SSL')]

    # Options that don't take arguments, simple true or false options.
    # These *must* be included in user_options too, but without an
    # equals sign.
    boolean_options = [
        'force-dependency-rebuild',
        'force-clean',
        'no-cert-verify']

    def initialize_options(self):
        # Set a default for each of your user_options (long option name)
        self.force_dependency_rebuild = 0
        self.force_clean = 0
        self.no_cert_verify = 0

    def finalize_options(self):
        # verify the arguments and raise DistutilOptionError if needed
        pass

    def _determine_module_id(self):
        return Id(
            group_id=PYTHON_GROUP_ID,
            artifact_id=self.distribution.metadata.name,
            version=self.distribution.metadata.version)

    def run(self):
        module_id = self._determine_module_id()
        self.announce(
            'Creating module_info file for module: {}'.format(module_id),
            level=log.INFO
        )

        # This command is never used interactively, so it doesn't make
        # sense to add support for passing in repo details like the
        # artifactory_upload command does. If that changes in the future
        # this command can always be enhanced at that time. The work
        # involved to add the options isn't so much in the code changes
        # to this command as in the test coverage that would need to be
        # written. It would also probably require refactoring the
        # commands to share a common base class. All this currently
        # falls under YAGNI (You're Not Going To Need It).

        verify_cert = not self.no_cert_verify
        repo_details = read_options()

        pip_package_path_finder = PipPackagePathFinder()

        def determine_checksums(file_path):
            return artifactory_rest.determine_checksums(
                username=repo_details.username,
                password=repo_details.password,
                repo_pull_id=repo_details.repo_pull_id,
                repo_base_url=repo_details.repo_base_url,
                file_path=file_path,
                verify_cert=verify_cert)

        checksum_dependency_helper = ChecksumDependencyHelper(
            determine_file_path_fn=pip_package_path_finder.determine_file_path,
            determine_checksums_from_file_path_fn=determine_checksums)

        build_info_module_generator = BuildInfoModuleGenerator(
            determine_dependency_checksums_fn=checksum_dependency_helper)

        requirements_file = compute_requirements_filename_full_path(
            artifact_id=module_id.artifact_id,
            version=module_id.version)

        module_info_file = compute_module_info_filename_full_path(
            artifact_id=module_id.artifact_id,
            version=module_id.version)

        build_info_module_generator.update(
            module_id=module_id,
            module_properties={},
            freeze_file=requirements_file,
            dist_files=self.distribution.dist_files,
            module_file=module_info_file,
            force_dependency_rebuild=bool(self.force_dependency_rebuild),
            force_clean=bool(self.force_clean))

        self.announce(
            'Module info file created at: {}'.format(module_info_file),
            level=log.INFO)