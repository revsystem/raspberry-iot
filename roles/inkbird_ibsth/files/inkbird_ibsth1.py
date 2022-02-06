# coding=UTF-8

from bluepy import btle
import struct

#Inkbird IBS-TH1データ取得クラス
class GetIBSTH1Data():
    def get_ibsth1_data(self, macaddr, sensortype):
        #デバイスに接続
        peripheral = btle.Peripheral(macaddr)
        #IBS-TH2のとき
        if sensortype == 'Inkbird_IBSTH2':
            characteristic = peripheral.readCharacteristic(0x24)
            return self._decodeSensorData_th2(characteristic)
        #IBS-TH1のとき
        elif sensortype == 'Inkbird_IBSTH1':
            characteristic = peripheral.readCharacteristic(0x28)
            return self._decodeSensorData_th1(characteristic)
        else:
            return None

    #IBS-TH2
    def _decodeSensorData_th2(self, valueBinary):
        (temp, humid, unknown1, unknown2, unknown3) = struct.unpack('<hhBBB', valueBinary)
        sensorValue = {
                'SensorType': 'Inkbird_IBSTH2',
                'Temperature': float(temp) / 100,
                'Humidity': float(humid) / 100,
                'unknown1': unknown1,
                'unknown2': unknown2,
                'unknown3': unknown3,
            }
        return sensorValue

    #IBS-TH1
    def _decodeSensorData_th1(self, valueBinary):
        (temp, humid, unknown1, unknown2, unknown3) = struct.unpack('<hhBBB', valueBinary)
        sensorValue = {
                'SensorType': 'Inkbird_IBSTH1',
                'Temperature': temp / 100,
                'Humidity': humid / 100,
                'unknown1': unknown1,
                'unknown2': unknown2,
                'unknown3': unknown3,
            }
        return sensorValue