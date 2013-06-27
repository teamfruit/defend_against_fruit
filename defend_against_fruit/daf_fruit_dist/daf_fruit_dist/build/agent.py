class Agent(object):
    def __init__(self, name, version):
        super(Agent, self).__init__()
        self._name = name
        self._version = version

    def __repr__(self):
        return '''Agent(name=%r, version=%r)'''\
               % (self._name, self._version)

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @classmethod
    def from_json_data(cls, json_data):
        return Agent(
            name=json_data['name'],
            version=json_data['version'])

    @property
    def as_json_data(self):
        return {'name': self.name,
                'version': self.version}

    def __attrs(self):
        return self._name, self._version

    def __hash__(self):
        return hash(self.__attrs())

    def __eq__(self, other):
        return isinstance(other, Agent) and self.__attrs() == other.__attrs()

    def __ne__(self, other):
        return not self == other
