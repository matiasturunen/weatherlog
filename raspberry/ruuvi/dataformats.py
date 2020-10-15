#####
# From https://github.com/ttu/ruuvitag-sensor/blob/master/ruuvitag_sensor/data_formats.py
#####

class DataFormats(object):
    
    @staticmethod
    def convertData(data):
        result = DataFormats._getDataFormat24(data)
        if (result is not None):
            return (result, 2)
        
        result = DataFormats._getDataFormat3(data)
        if (result is not None):
            return (result, 3)
        
        result = DataFormats._getDataFormat5(data)
        if (result is not None):
            return (result, 5)
        
        return (None, None)

    def _getDataFormat24(data):
        try:
            base16_split = [data[i:i + 2] for i in range(0, len(data), 2)]
            selected_hexs = filter(lambda x: int(x, 16) < 128, base16_split)
            characters = [chr(int(c, 16)) for c in selected_hexs]
            data = ''.join(characters)

            # take only part after ruu.vi/#
            index = data.find('ruu.vi/#')
            if index > -1:
                return data[(index + 8):]

            return None
        except:
            return None

    def _getDataFormat3(data):
        # Search of FF990403 (Manufacturer Specific Data (FF) /
        # Ruuvi Innovations ltd (9904) / Format 3 (03))
        try:
            if '990403' not in data:
                return None

            payload_start = data.index('990403') + 4
            return data[payload_start:]
        except:
            return None

    def _getDataFormat5(data):
        # Search of FF990405 (Manufacturer Specific Data (FF) /
        # Ruuvi Innovations ltd (9904) / Format 5 (05))
        try:
            if '990405' not in data:
                return None

            payload_start = data.index('990405') + 4
            return data[payload_start:]
        except:
            return None
