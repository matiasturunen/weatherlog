import time
import base64
import math
from ble import BLEObserver as b
from dataformats import DataFormats
from d5fdecoder import Df5Decoder

class Ruuvi(object):

    @staticmethod
    def getRuuviData(whitelist=[], searchTimeOut=5):
        startTime = time.time()

        dataIterator = b.getData(whitelist)

        for d in dataIterator:
            if (time.time() - startTime > searchTimeOut):
                dataIterator.send(StopIteration)
                continue

            (data, dataFormat) = DataFormats.convertData(d[1])
            if (data is not None):
                decoded = Ruuvi.decode(data, dataFormat)
                if (decoded is not None):
                    yield (d[0], decoded)

    @staticmethod
    def decode(data, dataFormat):
        if (dataFormat in [2,3,4]):
            print('Data type', dataformat, 'not supported.')
            return None
        else:
            return Df5Decoder().decode_data(data)


def main():
    for d in Ruuvi.getRuuviData(['CC:72:6B:45:B7:A2'], 10000):
        print('Ruuvi:', d[1])

if __name__ == '__main__':
    main()