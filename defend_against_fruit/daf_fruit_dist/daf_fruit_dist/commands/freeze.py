import glob
import os
import subprocess
from setuptools import Command
from daf_fruit_dist.file_management import \
    compute_requirements_filename_full_path


class freeze(Command):
    description = (
        'list all packages in the current environment in requirements.txt '
        'format')

    # This must be specified even though there are no user options.
    user_options = []

    # This must exist even though it does nothing.
    def initialize_options(self):
        pass

    # This must exist even though it does nothing.
    def finalize_options(self):
        pass

    def __pip_freeze(self, output_file):
        """
        Perform a 'pip freeze' and write the output (along with a
        comment) to the specified file.
        """
        with open(output_file, 'w') as f:
            f.write('# From: pip freeze' + os.linesep)
            # Absent this flush, the "pip freeze" contents appears
            # *before* the above comment.
            f.flush()
            subprocess.call(['pip', 'freeze'], stdout=f)

    def __freeze_eggs(self, output_file):
        """
        For every egg directory in the current working directory, append
        the egg's name and version to the specified output file.
        """
        for path in glob.glob('*.egg'):
            # Read the metadata from the egg into a string.
            with open(os.path.join(path, 'EGG-INFO', 'PKG-INFO')) as f:
                pkg_info = f.read()

            # Grab just the name and version from the metadata and store
            # them into a dictionary.
            metadata = dict(
                n.split(': ', 1) for
                n in pkg_info.splitlines() if
                n.startswith(('Name', 'Version')))

            # Append the egg's name and version (along with a comment)
            # to the output_file.
            with open(output_file, 'a') as f:
                f.write(
                    '{br}'
                    '# From: ./{egg_dir}{br}'
                    '{name}=={version}{br}'.format(
                        egg_dir=path,
                        name=metadata['Name'],
                        version=metadata['Version'],
                        br=os.linesep))

    def run(self):
        output_file = compute_requirements_filename_full_path(
            artifact_id=self.distribution.metadata.name,
            version=self.distribution.metadata.version)

        # 1. Perform a 'pip freeze' and write to output file. The
        #    captured packages are in site-packages.
        self.__pip_freeze(output_file)

        # 2. Append all eggs in the current directory to the output
        #    file. These packages do not appear in site-packages and are
        #    not caught by 'pip freeze' in the previous step. However,
        #    they are still part of the environment and should be listed.
        self.__freeze_eggs(output_file)

        # TODO: Capture packages in os.environ['PYTHONPATH']?

        # 3. Add output file to self.distribution.dist_files list.
        self.distribution.dist_files.append((
            'freeze',  # Distribution is the same as the command name
            None,  # No specific Python version
            output_file))   # Output filename
