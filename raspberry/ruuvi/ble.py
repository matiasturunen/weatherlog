from time import sleep
from bleson import get_provider, Observer, logger

from multiprocessing import Process, Manager
from queue import Queue
from logging import ERROR

logger.set_level(ERROR)

class BLEObserver(object):
    '''Bluetooth LE communications with bleson'''

    @staticmethod
    def _getDataBackground(queue, sharedData=''):
        (observer, q) = BLEObserver.start()

        for advertisement in BLEObserver.getQueueLines(q):
            if (sharedData['stop']):
                break
            try:
                mac = advertisement.address.address if advertisement.address is not None else None
                if (mac not in sharedData['whitelist']):
                    continue
                if (advertisement.mfg_data is None):
                    continue

                data = bytearray(advertisement.mfg_data)
                queue.put((mac, data.hex()))
            except GeneratorExit:
                break
            except Exception as e:
                print('Error happened:', e)
                continue

        BLEObserver.stop(observer)

    @staticmethod
    def start():
        adapter = get_provider().get_adapter()

        q = Queue()

        observer = Observer(adapter)
        observer.on_advertising_data = q.put # Put advertisement to queue

        observer.start()

        return (observer, q)

    @staticmethod
    def stop(observer):
        observer.stop()

    @staticmethod
    def getQueueLines(queue):
        try:
            while True:
                nextItem = queue.get()
                yield nextItem
        except KeyboardInterrupt as e:
            return
        except Exception as e:
            print('Exception while reading queue:', e)

    @staticmethod
    def getData(whitelist):
        '''Get data from whitelisted bluetooth LE devices'''
        m = Manager()
        q = m.Queue()

        sharedData = m.dict()
        sharedData['whitelist'] = whitelist
        sharedData['stop'] = False

        p = Process(target=BLEObserver._getDataBackground, args=(q, sharedData))
        p.start()

        try:
            while True:
                while not q.empty():
                    data = q.get()
                    yield data
                sleep(0.1) # sleep a bit
        except GeneratorExit:
            pass

        sharedData['stop'] = True
        p.join()
