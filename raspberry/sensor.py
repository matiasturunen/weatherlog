class Sensor(object):
    id = 0
    name = ''
    identifier = ''
    queue = None

    def __init__(self, id, name, identifier):
        self.id = id
        self.name = name
        self.identifier = identifier

