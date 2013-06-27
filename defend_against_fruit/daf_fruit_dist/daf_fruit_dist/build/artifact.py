class Artifact(object):
    def __init__(self, type, name, sha1=None, md5=None):
        super(Artifact, self).__init__()
        self._type = type
        self._name = name
        self._sha1 = sha1
        self._md5 = md5

    def __repr__(self):
        return '''Artifact(type=%r, name=%r, sha1=%r, md5=%r)''' \
               % (self._type, self._name, self._sha1, self._md5)

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def sha1(self):
        return self._sha1

    @property
    def md5(self):
        return self._md5

    @classmethod
    def from_json_data(cls, json_data):
        return Artifact(
            type=json_data['type'],
            sha1=json_data['sha1'],
            md5=json_data['md5'],
            name=json_data['name'])

    @property
    def as_json_data(self):
        return {"type": self.type,
                "sha1": self.sha1,
                "md5": self.md5,
                "name": self.name}

    def __attrs(self):
        return self._type, self._name, self._sha1, self._md5

    def __hash__(self):
        return hash(self.__attrs())

    def __eq__(self, other):
        return (
            isinstance(other, Artifact) and
            self.__attrs() == other.__attrs())

    def __ne__(self, other):
        return not self == other
