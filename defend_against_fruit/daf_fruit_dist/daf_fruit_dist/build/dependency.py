from daf_fruit_dist.build.id import Id
from daf_fruit_dist.build.build_util import nested_object_from_json_data


class Dependency(object):
    def __init__(self, type, id, sha1=None, md5=None):
        super(Dependency, self).__init__()
        self._type = type
        self._id = id
        self._sha1 = sha1
        self._md5 = md5

    def __repr__(self):
        return '''Dependency(type=%r, id=%r, sha1=%r, md5=%r)'''\
               % (self._type, self._id, self._sha1, self._md5)

    @property
    def type(self):
        return self._type

    @property
    def id(self):
        return self._id

    @property
    def sha1(self):
        return self._sha1

    @property
    def md5(self):
        return self._md5

    @classmethod
    def from_json_data(cls, json_data):
        id = nested_object_from_json_data(json_data, 'id', Id.from_json_data)

        return Dependency(
            type=json_data['type'],
            sha1=json_data['sha1'],
            md5=json_data['md5'],
            id=id)

    @property
    def as_json_data(self):
        return {"type": self.type,
                "sha1": self.sha1,
                "md5": self.md5,
                "id": getattr(self.id, 'as_json_data', None)}

    def __attrs(self):
        return self._type, self._id, self._sha1, self._md5

    def __hash__(self):
        return hash(self.__attrs())

    def __eq__(self, other):
        return (
            isinstance(other, Dependency) and
            self.__attrs() == other.__attrs())

    def __ne__(self, other):
        return not self == other
