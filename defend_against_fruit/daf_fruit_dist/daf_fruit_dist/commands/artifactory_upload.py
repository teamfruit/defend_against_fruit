from distutils.errors import DistutilsOptionError
from distutils import log
from functools import partial
from setuptools import Command
from daf_fruit_dist.artifactory import artifactory_rest
from daf_fruit_dist.artifactory import repo_detail
from daf_fruit_dist.file_management import compute_repo_path_from_module_name


class artifactory_upload(Command):
    description = (
        'upload package to an Artifactory server in the simple PyPI layout')

    user_options = [
        ('repo-base-url=', None,
         'base URL of repository'),
        ('repo-push-id=', None,
         'repository to which build artifacts should be deployed (e.g. '
         'pypi-teamfruit-l-local)'),
        ('repo-user=', None,
         'username for the repository (HTTP basic auth)'),
        ('repo-pass=', None,
         'password for the repository (HTTP basic auth)'),
        ('no-cert-verify', None,
         'do not verify authenticity of host cert when using SSL')]

    boolean_options = [
        'no-cert-verify',
    ]

    def initialize_options(self):
        self.repo_base_url = ''
        self.repo_push_id = ''
        self.repo_user = ''
        self.repo_pass = ''
        self.no_cert_verify = 0
        self.resource = None

    def _check_repo_details(self, repo_details):
        if not repo_details.repo_base_url:
            raise DistutilsOptionError('No repository specified!')
        if not repo_details.repo_push_id:
            raise DistutilsOptionError('No repo_push_id specified!')
        if not repo_details.username:
            raise DistutilsOptionError('No repo username specified!')
        if not repo_details.password:
            raise DistutilsOptionError('No repo password specified!')

    def finalize_options(self):
        repo_details = repo_detail.read_options(
            repo_base_url=self.repo_base_url,
            repo_push_id=self.repo_push_id,
            username=self.repo_user,
            password=self.repo_pass)

        self.announce(
            'Repository details: '
            'repo_base_url="{}", '
            'repo_push_id="{}" '
            'username="{}"'.format(
                repo_details.repo_base_url,
                repo_details.repo_push_id,
                repo_details.username),
            level=log.INFO
        )

        self._check_repo_details(repo_details)

        verify_cert = not self.no_cert_verify

        path = compute_repo_path_from_module_name(
            self.distribution.metadata.name)

        self.upload = partial(
            self.__upload,
            repo_base_url=repo_details.repo_base_url,
            repo_push_id=repo_details.repo_push_id,
            path=path,
            username=repo_details.username,
            password=repo_details.password,
            verify_cert=verify_cert)

    def run(self):
        if not self.distribution.dist_files:
            raise DistutilsOptionError(
                'No dist file created in earlier command')

        for dist, python_version, filename in self.distribution.dist_files:
            self.upload(filename=filename)

    def __upload(
            self,
            filename,
            repo_base_url,
            repo_push_id,
            path,
            username=None,
            password=None,
            verify_cert=True):

        self.announce('Uploading: {}/{}/{}/{}'.format(
            repo_base_url, repo_push_id, path, filename),
            level=log.INFO)

        return artifactory_rest.deploy_file(
            filename=filename,
            repo_base_url=repo_base_url,
            repo_push_id=repo_push_id,
            path=path,
            username=username,
            password=password,
            verify_cert=verify_cert)
