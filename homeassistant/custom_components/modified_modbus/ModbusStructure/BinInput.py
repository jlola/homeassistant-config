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
    def ValueOn(self):
        return self.valueOn
    
    @property
    def ValueOff(self):
        return self.valueOff
        
    def Parse(self,holdings):
        data = holdings[self.offset]        
        self.pinNumber = 0xFF & data
        self.valueOn = data | 0x0100
        self.valueOff = data & 0xFEFF
        
    @staticmethod
    def IsValueOn(value):
        if ((value & 0x0100) > 0):
            return True
        else:
            return False 
        
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
                     { "name" : f"binary_sensor{self.slave}.{self.PinNumber}",
                       "hub" : self._hub.ConfigName,
                       "slave" : self.slave,
                      "offset" : self.Offset,
                     "value_on" : self.ValueOn,
                     "value_off" : self.ValueOff
                     }
                ],                
            }
            
            return inputyaml
    
        
        
        