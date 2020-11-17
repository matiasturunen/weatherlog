import time
import base64
import math
from .ble import BLEObserver as b
from .dataformats import DataFormats
from .d5fdecoder import Df5Decoder

class Ruuvi(object):

    @staticmethod
    def getRuuviData(whitelist="", searchTimeOut=5):
        startTime = time.time()

        dataIterator = b.getData(whitelist)
        
        for d in dataIterator:
            try:
                if (time.time() - startTime > searchTimeOut):
                    dataIterator.send(StopIteration)
                    continue

                (data, dataFormat) = DataFormats.convertData(d[1])
                if (data is not None):
                    decoded = Ruuvi.decode(data, dataFormat)
                    if (decoded is not None):
                        yield (d[0], decoded)
            except StopIteration:
                print('ITER STOP')
                break
            except Exception as e:
                print('Error happened:', e)
                continue

    @staticmethod
    def decode(data, dataFormat):
        if (dataFormat in [2,3,4]):
            print('Data type', dataformat, 'not supported.')
            return None
        else:
            return Df5Decoder().decode_data(data)

    @staticmethod
    def getSingle(mac, queue, searchTimeOut=5):
        ruuviList = []
        ruuvigen = Ruuvi.getRuuviData(mac, searchTimeOut)
        for x in ruuvigen:
            ruuviList.append(x[1])
            ruuvigen.send(StopIteration)
            break
        if len(ruuviList) > 0:
            queue.put(ruuviList[0])
        else:
            pass

def main():
    for d in Ruuvi.getRuuviData(['CC:72:6B:45:B7:A2'], 10000):
        print('Ruuvi:', d[1])

if __name__ == '__main__':
    main()