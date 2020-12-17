class Sensor(object):
    id = 0
    name = ''
    identifier = ''
    queue = None
    proc = None

    def __init__(self, id, name, identifier):
        self.id = id
        self.name = name
        self.identifier = identifier


    def isRunning(self):
        if (self.proc is not None):
            return self.proc.is_alive()
        return False