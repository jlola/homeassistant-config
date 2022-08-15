'''
Created on Sep 13, 2020

@author: pc
'''
from pickletools import uint1,uint2
from builtins import staticmethod

class BinInput(object):
    '''
    binnary inputs
    '''

    def __init__(self,hub, slave, offset):
        '''
        Constructor
        '''
        self._hub = hub
        self.slave = slave
        self.offset = offset
        self.pinNumber:uint1 = 0
        self.value:bool = False
        self.quality:bool = False
        self.latch:bool = False
        self.latchDirection = False
        self.valueOn = 0
        self.valueOff = 0
        self.bit = None
    
    @staticmethod
    def HoldingsSize() -> uint1:
        '''
        Size of inputs struct in bytes
        '''
        return 1
    
    @property
    def Offset(self):
        return self.offset
    
    @property
    def PinNumber(self):
        return self.pinNumber
    
    @property
    def Bit(self):
        return self.bit
    
    def Set(self,valueOn,valueOff,bit):
        self._bit = bit
        self.valueOff = valueOff
        self.valueOn = valueOn
    
    '''parse for homeis modules'''
    def Parse(self,holdings):
        data = holdings[self.offset]        
        self.pinNumber = 0xFF & data
        self.bit = 8
        self.valueOn = 1#f"{self.offset}.{self.bit}"#data | 0x0100
        self.valueOff = 0#f"{self.offset}.{self.bit}"#data & 0xFEFF
                                            
    def GenerateYaml(self):        
#         binary_sensor:
#           - platform: modified_modbus
#             holdings:
#               - name: Sensor1
#                 hub: default
#                 slave: 4
#                 address: 100
#                 value_on: 1254
#                 value_off: 158
                    
            inputyaml = {
                "platform" : "modified_modbus",                 
                "holdings" : [
                     { "name" : f"binary_sensor_{self.slave}_{self.PinNumber}",
                       "hub" : self._hub.ConfigName,
                       "slave" : self.slave,
                       "offset" : self.Offset,
                       "value_on" : self.valueOn,
                       "value_off" : self.valueOff,
                       "bit" : self.bit
                     }
                ],                
            }
            
            return inputyaml
    
        
        
        