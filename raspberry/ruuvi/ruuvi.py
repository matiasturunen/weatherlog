from ble import BLEObserver as b

for d in b.getData(['CC:72:6B:45:B7:A2']):
    print(d)