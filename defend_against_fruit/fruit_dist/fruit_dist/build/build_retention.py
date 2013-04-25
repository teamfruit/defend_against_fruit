class BuildRetention(object):
    def __init__(self,
                 count=None,
                 delete_build_artifacts=None,
                 build_numbers_not_to_be_discarded=None):
        super(BuildRetention, self).__init__()
        self._count = count
        self._delete_build_artifacts = delete_build_artifacts
        self._build_numbers_not_to_be_discarded = build_numbers_not_to_be_discarded

    def __repr__(self):
        return '''BuildRetention(count=%r, delete_build_artifacts=%r, build_numbers_not_to_be_discarded=%r)''' \
               % (self._count, self._delete_build_artifacts, self._build_numbers_not_to_be_discarded)

    @property
    def count(self):
        return self._count

    @property
    def delete_build_artifacts(self):
        return self._delete_build_artifacts

    @property
    def build_numbers_not_to_be_discarded(self):
        return self._build_numbers_not_to_be_discarded

    @classmethod
    def from_json_data(cls, json_data):
        return BuildRetention(
            count=json_data['count'],
            delete_build_artifacts=json_data['deleteBuildArtifacts'],
            build_numbers_not_to_be_discarded=json_data['buildNumbersNotToBeDiscarded'])

    @property
    def as_json_data(self):
        return {'count': self.count,
                'deleteBuildArtifacts': self.delete_build_artifacts,
                'buildNumbersNotToBeDiscarded': self.build_numbers_not_to_be_discarded}

    def __attrs(self):
        return self._count, self._delete_build_artifacts, frozenset(self._build_numbers_not_to_be_discarded)

    def __hash__(self):
        return hash(self.__attrs())

    def __eq__(self, other):
        return isinstance(other, BuildRetention) and self.__attrs() == other.__attrs()

    def __ne__(self, other):
        return not self == other
