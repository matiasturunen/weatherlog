import time

class Queuedata(object):
    data = None
    timestamp = None

    def __init__(self, data):
        self.data = data
        self.timestamp = time.time()
