class PromotionRequest(object):
    def __init__(self,
                 status,
                 ci_user,
                 timestamp,
                 target_repo,
                 comment=None,
                 dry_run=False,
                 copy=False,
                 artifacts=True,
                 dependencies=False,
                 scopes=None,
                 properties=None,
                 fail_fast=True):
        """Construct a PromotionRequest data container.

        :param status: new build status (any string, e.g. "staged")
        :param comment: An optional comment describing the reason for promotion.
        :param ci_user: The user that invoked promotion from the CI server
        :param timestamp: ISO8601 formated time the promotion command was sent do Artifactory.
        :param dry_run: Run without executing any operation in Artifactory but get the results to
            check if the operation can succeed.
        :param target_repo: Optional repository to move or copy the build's artifacts
            and/or dependencies (e.g.:"libs-release-local")
        :param copy: Whether to copy instead of move, when a target repository is specified.
        :param artifacts: Whether to move/copy the build's artifacts.
        :param dependencies: Whether to move/copy the build's dependencies.
        :param scopes: An array of dependency scopes to include when "dependencies" is true.
            (e.g.["compile", "runtime"])
        :param properties: A list of properties to attach to the build's artifacts
            (regardless if "target_repo" is used).
        :param fail_fast: Fail and abort the operation upon receiving an error.
        """

        super(PromotionRequest, self).__init__()
        self._status = status
        self._comment = comment
        self._ci_user = ci_user
        self._timestamp = timestamp
        self._target_repo = target_repo
        self._dry_run = dry_run
        self._copy = copy
        self._artifacts = artifacts
        self._dependencies = dependencies
        self._scopes = scopes
        self._properties = properties
        self._fail_fast = fail_fast

    @property
    def status(self):
        return self._status

    @property
    def comment(self):
        return self._comment

    @property
    def ci_user(self):
        return self._ci_user

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def target_repo(self):
        return self._target_repo

    @property
    def dry_run(self):
        return self._dry_run

    @property
    def copy(self):
        return self._copy

    @property
    def artifacts(self):
        return self._artifacts

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def scopes(self):
        return self._scopes

    @property
    def properties(self):
        return self._properties

    @property
    def fail_fast(self):
        return self._fail_fast

    @classmethod
    def from_json_data(cls, json_data):
        return PromotionRequest(
            status=json_data['status'],
            comment=json_data['comment'],
            ci_user=json_data['ciUser'],
            timestamp=json_data['timestamp'],
            target_repo=json_data['targetRepo'],
            dry_run=json_data['dryRun'],
            copy=json_data['copy'],
            artifacts=json_data['artifacts'],
            dependencies=json_data['dependencies'],
            scopes=json_data['scopes'],
            properties=json_data['properties']
        )

    @property
    def as_json_data(self):
        json_data = {
            "status": self.status,
            "comment": self.comment,
            "ciUser": self.ci_user,
            "timestamp": self.timestamp,
            "dryRun": self.dry_run,
            "targetRepo": self.target_repo,
            "copy": self.copy,
            "artifacts": self.artifacts,
            "dependencies": self.dependencies,
            "scopes": self.scopes,
            "properties": self.properties,
            "failFast": self.fail_fast,
        }

        return json_data

    def __attrs(self):
        hashable_attributes = (
            self._status,
            self._comment,
            self._ci_user,
            self._timestamp,
            self._target_repo,
            self._dry_run,
            self._copy,
            self._artifacts,
            self._dependencies,
            tuple(self._scopes),
            frozenset(self._properties),
            self._fail_fast)

        return hashable_attributes

    def __hash__(self):
        return hash(self.__attrs())

    def __eq__(self, other):
        return isinstance(other, PromotionRequest) and self.__attrs() == other.__attrs()

    def __ne__(self, other):
        return not self == other