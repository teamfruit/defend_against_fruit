import hashlib
import os
from fruit_dist.build.artifact import Artifact
from fruit_dist.build.dependency import Dependency
from fruit_dist.build.id import Id
from fruit_dist.build.build_util import nested_object_from_json_data, \
    get_attr_as_tuple_unless_none, get_attr_as_list_unless_none
from fruit_dist.file_management import get_file_digests


class Module(object):
    def __repr__(self):
        return '''Module(id=%r, properties=%r, artifacts=%r, dependencies=%r)'''\
               % (self._id, self._properties, self._artifacts, self._dependencies)

    def __init__(self, id, properties, artifacts, dependencies):
        super(Module, self).__init__()
        self._id = id
        self._properties = properties
        self._artifacts = artifacts
        self._dependencies = dependencies

    @property
    def id(self):
        return self._id

    @property
    def properties(self):
        return self._properties

    @property
    def artifacts(self):
        return self._artifacts

    @property
    def dependencies(self):
        return self._dependencies

    @classmethod
    def from_json_data(cls, json_data):
        artifacts_tuple = None
        if 'artifacts' in json_data:
            artifacts_tuple = tuple([Artifact.from_json_data(x) for x in json_data['artifacts']])

        dependencies_tuple = None
        if 'dependencies' in json_data:
            dependencies_tuple = tuple([Dependency.from_json_data(x) for x in json_data['dependencies']])

        id = nested_object_from_json_data(json_data, 'id', Id.from_json_data)

        return Module(
            id=id,
            properties=json_data['properties'],
            artifacts=artifacts_tuple,
            dependencies=dependencies_tuple)

    @property
    def as_json_data(self):
        json_data = {
            "properties": self.properties,
            "id": getattr(self.id, 'as_json_data', None)
        }

        if self.artifacts is not None:
            json_data["artifacts"] = [x.as_json_data for x in self.artifacts]

        if self.dependencies is not None:
            json_data["dependencies"] = [x.as_json_data for x in self.dependencies]

        return json_data

    def __attrs(self):
        frozen_artifacts = None
        if self._artifacts is not None:
            frozen_artifacts = frozenset(self._artifacts)

        frozen_dependencies = None
        if self._dependencies is not None:
            frozen_dependencies = frozenset(self._dependencies)

        return self._id, frozenset(self._properties), frozen_artifacts, frozen_dependencies

    def __hash__(self):
        return hash(self.__attrs())

    def __eq__(self, other):
        return isinstance(other, Module) and self.__attrs() == other.__attrs()

    def __ne__(self, other):
        return not self == other

    class Builder(object):
        def __init__(
                self,
                id=None,
                properties=None,
                artifacts=None,
                dependencies=None,
                treat_none_as_empty=True
        ):
            super(Module.Builder, self).__init__()
            self._id = id
            self._properties = properties
            self._treat_none_as_empty = treat_none_as_empty

            #Artifacts and Dependency objects are effectively immutable.
            #Consequently there isn't really an encapsulation violation if we just
            #assign the collection directly.
            if artifacts is not None:
                self._artifacts = artifacts
            elif treat_none_as_empty:
                self._artifacts = []
            else:
                self._artifacts = None

            if dependencies is not None:
                self._dependencies = dependencies
            elif treat_none_as_empty:
                self._dependencies = []
            else:
                self._dependencies = None

        @property
        def id(self):
            return self._id

        @property
        def dependencies(self):
            return self._dependencies

        @property
        def artifacts(self):
            return self._artifacts

        @id.setter
        def id(self, value):
            self._id = value

        def add_artifact(self, type, name, sha1=None, md5=None):
            artifact = Artifact(type=type, name=name, sha1=sha1, md5=md5)
            self.ensure_artifacts_defined()
            self._artifacts.append(artifact)

        def add_file_as_artifact(self, type, file):
            full_path = os.path.abspath(file)
            name = os.path.basename(full_path)
            md5, sha1 = get_file_digests(full_path, digests=(hashlib.md5(), hashlib.sha1()))
            artifact = Artifact(type=type, name=name, sha1=sha1.hexdigest(), md5=md5.hexdigest())
            self.ensure_artifacts_defined()
            self._artifacts.append(artifact)

        def add_dependency(self, type, id, sha1=None, md5=None):
            dependency = Dependency(type, id, sha1, md5)
            self.ensure_dependencies_defined()
            self._dependencies.append(dependency)

        def ensure_dependencies_defined(self):
            """Ensure dependencies are defined even if only an empty collection."""

            if self._dependencies is None:
                self._dependencies = []

        def ensure_artifacts_defined(self):
            """Ensure artifacts are defined even if only an empty collection."""

            if self._artifacts is None:
                self._artifacts = []

        def build(self):
            return Module(
                id=self._id,
                properties=self._properties,
                artifacts=get_attr_as_tuple_unless_none(self, '_artifacts'),
                dependencies=get_attr_as_tuple_unless_none(self, '_dependencies'))

        @classmethod
        def from_another_module(cls, module, treat_none_as_empty=True, copy_dependencies=True):
            dependencies = None
            if copy_dependencies:
                dependencies = get_attr_as_list_unless_none(module, 'dependencies')

            return Module.Builder(
                id=module.id,
                properties=module.properties,
                artifacts=get_attr_as_list_unless_none(module, 'artifacts'),
                dependencies=dependencies,
                treat_none_as_empty=treat_none_as_empty
            )
