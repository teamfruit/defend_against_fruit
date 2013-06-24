from daf_fruit_dist.build.build_util import nested_object_from_json_data
from daf_fruit_dist.build.agent import Agent
from daf_fruit_dist.build.build_retention import BuildRetention
from daf_fruit_dist.build.module import Module


class BuildInfo(object):
    def __init__(self, builder):
        super(BuildInfo, self).__init__()
        self._version = builder._version
        self._name = builder._name
        self._number = builder._number
        self._type = builder._type
        self._started = builder._started
        self._duration_millis = builder._duration_millis
        self._artifactory_principal = builder._artifactory_principal
        self._agent = builder._agent
        self._build_agent = builder._build_agent
        self._build_retention = builder._build_retention
        self._modules = tuple(builder._modules)

    @property
    def version(self):
        return self._version

    @property
    def name(self):
        return self._name

    @property
    def number(self):
        return self._number

    @property
    def type(self):
        return self._type

    @property
    def started(self):
        return self._started

    @property
    def duration_millis(self):
        return self._duration_millis

    @property
    def artifactory_principal(self):
        return self._artifactory_principal

    @property
    def agent(self):
        return self._agent

    @property
    def build_agent(self):
        return self._build_agent

    @property
    def build_retention(self):
        return self._build_retention

    @property
    def modules(self):
        return tuple(self._modules)

    @classmethod
    def from_json_data(cls, json_data):
        agent = nested_object_from_json_data(json_data, 'agent', Agent.from_json_data)
        build_agent = nested_object_from_json_data(json_data, 'buildAgent', Agent.from_json_data)
        build_retention = nested_object_from_json_data(json_data, 'buildRetention', BuildRetention.from_json_data)

        builder = BuildInfo.Builder(
            version=json_data['version'],
            name=json_data['name'],
            number=json_data['number'],
            type=json_data['type'],
            started=json_data['started'],
            duration_millis=json_data['durationMillis'],
            artifactory_principal=json_data['artifactoryPrincipal'],
            agent=agent,
            build_agent=build_agent,
            build_retention=build_retention
        )

        modules = [Module.from_json_data(x) for x in json_data['modules']]

        for module in modules:
            builder.add_module(module)

        return builder.build()

    @property
    def as_json_data(self):
        modules_as_json_data = [x.as_json_data for x in self.modules]

        return {"version": self.version,
                "name": self.name,
                "number": self.number,
                "type": self.type,
                "buildAgent": getattr(self.build_agent, 'as_json_data', None),
                "agent": getattr(self.agent, 'as_json_data', None),
                "started": self.started,
                "durationMillis": self.duration_millis,
                "artifactoryPrincipal": self.artifactory_principal,
                "buildRetention": getattr(self.build_retention, 'as_json_data', None),
                "modules": modules_as_json_data}

    def __attrs(self):
        return (self._version,
                self._name,
                self._number,
                self._type,
                self._started,
                self._duration_millis,
                self._artifactory_principal,
                self._agent,
                self._build_agent,
                self._build_retention,
                self._modules)

    def __hash__(self):
        return hash(self.__attrs())

    def __eq__(self, other):
        return isinstance(other, BuildInfo) and self.__attrs() == other.__attrs()

    def __ne__(self, other):
        return not self == other

    class Builder(object):
        def __init__(self,
                     version=None,
                     name=None,
                     number=None,
                     type=None,
                     started=None,
                     duration_millis=None,
                     artifactory_principal=None,
                     agent=None,
                     build_agent=None,
                     build_retention=None):
            super(BuildInfo.Builder, self).__init__()
            self._version = version
            self._name = name
            self._number = number
            self._type = type
            self._started = started
            self._duration_millis = duration_millis
            self._artifactory_principal = artifactory_principal
            self._agent = agent
            self._build_agent = build_agent
            self._build_retention = build_retention
            self._modules = []

        def add_module(self, module):
            self._modules.append(module)

        def build(self):
            return BuildInfo(builder=self)