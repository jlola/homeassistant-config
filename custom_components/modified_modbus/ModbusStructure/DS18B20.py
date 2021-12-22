'''
Created on Sep 24, 2020

@author: pc
'''
from pickletools import uint2
from ..ModifiedModbus.Helper import Helper
from ..const import CONF_HOLDINGS_TYPE,CONF_DS18B20,CONF_OWID,CONF_HOLDINGS


OFFSET_ID12 = 0
OFFSET_ID34 = 1
OFFSET_ID56 = 2
OFFSET_ID78 = 3
OFFSET_VALUE = 4
OFFSET_ERROR = 5
OW_DEVICES_OFFSET = 5
OW_COUNT_DEVICES_OFFSET = 1
OW_SCAN_OFFSET = 0


class OneWireHeader(object):
    def __init__(self,slave, offset):
        self._detectedDS18B20 = 0
        self._offset = offset
        self._slave = slave
    
    def Parse(self,data:list):
        self._detectedDS18B20 = data[self._offset + OW_COUNT_DEVICES_OFFSET]            
        
    @property
    def CountDevices(self):
        return self._detectedDS18B20
        
        
    def GetFirstDS18B20Offset(self):
        return self._offset + OW_DEVICES_OFFSET
        

class DS18B20(object):
    '''
    
    '''
    def __init__(self,hub, slave, offset):
        '''
        Constructor
        '''        
        self.slave = slave
        self._hub = hub
        self._offset = offset
        self.value:int = 0
        self.owid = []
        self.owHeaderOffset = 0
        
    @property
    def Offset(self):
        return self._offset
    
    def Parse(self,owHeaderOffset, data:list):
        self.owHeaderOffset = owHeaderOffset
        self.owid.append(data[self._offset+OFFSET_ID12])
        self.owid.append(data[self._offset+OFFSET_ID34])
        self.owid.append(data[self._offset+OFFSET_ID56])
        self.owid.append(data[self._offset+OFFSET_ID78])
        self.error = data[self._offset+OFFSET_ERROR]
        self.value = self.GetValue(data[self._offset+OFFSET_VALUE])
        
    def GetValue(self,val):
        bts = self.int_to_bytes(val)
        return int.from_bytes(bts, 'big', signed=True)
        
    def int_to_bytes(self,x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')
        
    @property
    def OneWireHeaderOffset(self):
        return self.owHeaderOffset
        
    @property
    def Value(self):
        return self.value/100.0
    
    @property
    def OwId(self):
        bts = Helper.convertHoldingsToBytes(self.owid)
        strbts = bts.hex()
        return strbts
    
    def IsSameId(self,owid):        
        return owid == self.OwId
    
    @staticmethod
    def HoldingsSize() -> uint2:
        '''
        Size of inputs struct in bytes
        '''
        return 6
    
    def GenerateYaml(self):
        sensor = {
            "platform" : "modified_modbus",                 
            CONF_HOLDINGS : [
                 { 
                   "name" : f"{self.slave}.ds18b20_{self.OwId}",
                   "hub" : self._hub.ConfigName,
                   "slave" : self.slave,
                   CONF_HOLDINGS_TYPE : CONF_DS18B20,                       
                   "device_class" : "temperature",
                   "unit_of_measurement" : '°C',
                   CONF_OWID: self.OwId                       
                 }
            ],                
        }
        
        return sensor
    
    
        