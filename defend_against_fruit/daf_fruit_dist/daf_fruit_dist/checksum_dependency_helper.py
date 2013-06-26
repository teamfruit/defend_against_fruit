from pip.exceptions import DistributionNotFound


class ChecksumDependencyHelper(object):
    def __init__(
            self,
            determine_file_path_fn,
            determine_checksums_from_file_path_fn):

        """Construct checksum dependency helper instance.

        :param determine_file_path_fn: arguments must match
            (pkg_name=artifact_id, pkg_version=version) and must return
            the file path portion used in downloading the matching
            module.

        :param determine_checksums_from_file_path_fn: function taking a
            file_path and returning the Checksum named-tuple
        """
        self.determine_file_path_fn = determine_file_path_fn
        self.determine_checksums_from_file_path_fn = (
            determine_checksums_from_file_path_fn)

    def __call__(self, artifact_id, version):
        try:
            #determine_file_path_fn may throw a DistributionNotFound exception
            dependency_path = self.determine_file_path_fn(
                pkg_name=artifact_id,
                pkg_version=version)

            # determine_checksums_from_file_path_fn may throw an
            # RequestException but if so just let it bubble up.
            dependency_checksums = self.determine_checksums_from_file_path_fn(
                dependency_path)
            dependency_sha1 = dependency_checksums.sha1
            dependency_md5 = dependency_checksums.md5

        except DistributionNotFound:
            dependency_sha1 = None
            dependency_md5 = None

        return dependency_md5, dependency_sha1
