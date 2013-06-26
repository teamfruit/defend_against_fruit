class Id(object):
    def __init__(self, group_id, artifact_id, version):
        super(Id, self).__init__()
        self._group_id = group_id
        self._artifact_id = artifact_id
        self._version = version

    def __repr__(self):
        return '''Id(group_id=%r, artifact_id=%r, version=%r)'''\
               % (self._group_id, self._artifact_id, self._version)

    @property
    def group_id(self):
        return self._group_id

    @property
    def artifact_id(self):
        return self._artifact_id

    @property
    def version(self):
        return self._version

    @classmethod
    def from_json_data(cls, json_data):
        group_id, artifact_id, version = json_data.split(":")
        return Id(
            group_id=group_id,
            artifact_id=artifact_id,
            version=version)

    @property
    def as_json_data(self):
        id_as_string = ":".join((
            self.group_id,
            self.artifact_id,
            self.version))
        return id_as_string

    def __attrs(self):
        return self._group_id, self._artifact_id, self._version

    def __hash__(self):
        return hash(self.__attrs())

    def __eq__(self, other):
        return isinstance(other, Id) and self.__attrs() == other.__attrs()

    def __ne__(self, other):
        return not self == other
