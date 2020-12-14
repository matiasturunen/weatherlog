import time

B = (0,5,104)
X = (245,245,15)

class Phase:
    pixels = [(0,0,0)] * 64
    def __init__(self, d):
        self.pixels = d


class Moon:

    phases = []
    speed = 2

    def __init__(self, speed):
        self.speed = speed
        self.phases.append(Phase([
            B,B,X,X,B,B,B,B,
            B,X,X,B,B,B,B,B,
            X,X,B,B,B,B,B,B,
            X,X,B,B,B,B,B,B,
            X,X,B,B,B,B,B,B,
            X,X,B,B,B,B,B,B,
            B,X,X,B,B,B,B,B,
            B,B,X,X,B,B,B,B
        ]))

        self.phases.append(Phase([
            B,B,X,X,B,B,B,B,
            B,X,X,X,B,B,B,B,
            X,X,X,X,B,B,B,B,
            X,X,X,X,B,B,B,B,
            X,X,X,X,B,B,B,B,
            X,X,X,X,B,B,B,B,
            B,X,X,X,B,B,B,B,
            B,B,X,X,B,B,B,B
        ]))

        self.phases.append(Phase([
            B,B,X,X,B,B,B,B,
            B,X,X,X,X,B,B,B,
            X,X,X,X,X,X,B,B,
            X,X,X,X,X,X,B,B,
            X,X,X,X,X,X,B,B,
            X,X,X,X,X,X,B,B,
            B,X,X,X,X,B,B,B,
            B,B,X,X,B,B,B,B
        ]))

        self.phases.append(Phase([
            B,B,X,X,X,X,B,B,
            B,X,X,X,X,X,X,B,
            X,X,X,X,X,X,X,X,
            X,X,X,X,X,X,X,X,
            X,X,X,X,X,X,X,X,
            X,X,X,X,X,X,X,X,
            B,X,X,X,X,X,X,B,
            B,B,X,X,X,X,B,B
        ]))

        self.phases.append(Phase([
            B,B,B,B,X,X,B,B,
            B,B,B,X,X,X,X,B,
            B,B,X,X,X,X,X,X,
            B,B,X,X,X,X,X,X,
            B,B,X,X,X,X,X,X,
            B,B,X,X,X,X,X,X,
            B,B,B,X,X,X,X,B,
            B,B,B,B,X,X,B,B
        ]))

        self.phases.append(Phase([
            B,B,B,B,X,X,B,B,
            B,B,B,B,X,X,X,B,
            B,B,B,B,X,X,X,X,
            B,B,B,B,X,X,X,X,
            B,B,B,B,X,X,X,X,
            B,B,B,B,X,X,X,X,
            B,B,B,B,X,X,X,B,
            B,B,B,B,X,X,B,B
        ]))

        self.phases.append(Phase([
            B,B,B,B,X,X,B,B,
            B,B,B,B,B,X,X,B,
            B,B,B,B,B,B,X,X,
            B,B,B,B,B,B,X,X,
            B,B,B,B,B,B,X,X,
            B,B,B,B,B,B,X,X,
            B,B,B,B,B,X,X,B,
            B,B,B,B,X,X,B,B
        ]))

        self.phases.append(Phase([
            B,B,B,B,B,B,B,B,
            B,B,B,B,B,B,B,B,
            B,B,B,B,B,B,B,B,
            B,B,B,B,B,B,B,B,
            B,B,B,B,B,B,B,B,
            B,B,B,B,B,B,B,B,
            B,B,B,B,B,B,B,B,
            B,B,B,B,B,B,B,B
        ]))

    def play(self, sense):
        for phase in self.phases:
            sense.set_pixels(phase.pixels)
            time.sleep(1/self.speed)
